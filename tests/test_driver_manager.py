"""app._driver_manager 单元测试(不启动真实浏览器)"""

import logging
from pathlib import Path

import pytest
from selenium.common.exceptions import NoSuchDriverException, WebDriverException

from app import _driver_manager as driver_manager
from app._driver_manager import CourseHandler, CourseSettings, load_settings

AUTO_COURSE_CONFIG = {
    "browser": "Edge",
    "home_url": "https://home",
    "login_url": "https://login",
    "history_url": "https://history",
    "user_cookies": "a=1; b=2",
    "restore_cookies": False,
    "force_speed": True,
    "speed": 1.5,
}


class FakeDriver:
    """记录调用的 selenium driver 替身"""

    def __init__(self, cookies: list[dict] | None = None, current_url: str = "https://current"):
        self.visited: list[str] = []
        self.added_cookies: list[dict] = []
        self.executed_scripts: list[str] = []
        self.window_handles = ["h1", "h2"]
        self.switch_to = self
        self.switched: list[str] = []
        self.quit_called = False
        self._cookies = cookies if cookies is not None else [{"name": "a", "value": "1"}]
        self.current_url = current_url

    def get(self, url: str) -> None:
        self.visited.append(url)

    def add_cookie(self, cookie: dict) -> None:
        self.added_cookies.append(cookie)

    def get_cookies(self) -> list[dict]:
        return self._cookies

    def execute_script(self, script: str, *_args) -> None:
        self.executed_scripts.append(script)

    def window(self, handle: str) -> None:
        self.switched.append(handle)

    def quit(self) -> None:
        self.quit_called = True


@pytest.fixture
def handler(clean_config: dict) -> CourseHandler:
    clean_config["auto_course"] = dict(AUTO_COURSE_CONFIG)
    return CourseHandler()


def test_load_settings_reads_config(clean_config: dict) -> None:
    clean_config["auto_course"] = dict(AUTO_COURSE_CONFIG)

    settings = load_settings()

    assert settings == CourseSettings(
        browser="Edge",
        url={"home": "https://home", "login": "https://login", "history": "https://history"},
        user_cookies="a=1; b=2",
        restore_cookies=False,
        force_speed=True,
        speed=1.5,
    )


def test_load_settings_defaults_without_config(clean_config: dict) -> None:
    settings = load_settings()

    assert settings.browser == ""
    assert settings.url == {"home": "", "login": "", "history": ""}
    assert settings.restore_cookies is True
    assert settings.force_speed is False
    assert settings.speed == 2.0


def test_refresh_settings_picks_up_changes(handler: CourseHandler, clean_config: dict) -> None:
    clean_config["auto_course"]["speed"] = 4.0

    handler.refresh_settings()

    assert handler._settings.speed == 4.0


@pytest.mark.parametrize(
    ("cookie_str", "expected"),
    [
        ("a=1; b=2", [{"name": "a", "value": "1"}, {"name": "b", "value": "2"}]),
        ("  a=1  ", [{"name": "a", "value": "1"}]),
        ("a=1=2", [{"name": "a", "value": "1=2"}]),
        ("invalid; a=1", [{"name": "a", "value": "1"}]),
        ("", []),
    ],
)
def test_parse_cookies(handler: CourseHandler, cookie_str: str, expected: list[dict]) -> None:
    assert handler._parse_cookies(cookie_str) == expected


def test_cookies_to_str(handler: CourseHandler) -> None:
    cookies = [{"name": "a", "value": "1"}, {"name": "b", "value": "2"}]

    assert handler._cookies_to_str(cookies) == "a=1; b=2"


def test_cookies_to_str_round_trip(handler: CourseHandler) -> None:
    assert handler._cookies_to_str(handler._parse_cookies("a=1; b=2")) == "a=1; b=2"


def test_inject_cookies_adds_each_cookie(handler: CourseHandler) -> None:
    handler._driver = FakeDriver()

    handler._inject_cookies()

    assert handler._driver.added_cookies == [
        {"name": "a", "value": "1"},
        {"name": "b", "value": "2"},
    ]


def test_inject_cookies_skips_empty_cookie_string(handler: CourseHandler) -> None:
    handler._settings.user_cookies = "   "
    handler._driver = FakeDriver()

    handler._inject_cookies()

    assert handler._driver.added_cookies == []


def test_init_script_prepends_options(
    handler: CourseHandler, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    script_path = tmp_path / "script.js"
    script_path.write_text("console.log('run');", encoding="utf-8")
    monkeypatch.setattr(driver_manager, "get_path_config", lambda _static, _name: script_path)

    script = handler._init_script()

    assert "globalThis.LAUNCH_OPTION = 1;" in script
    assert "globalThis.FORCE_SPEED = true;" in script
    assert "globalThis.SPEED = 1.5;" in script
    assert script.endswith("console.log('run');")


def test_open_website_uses_history_when_cookies_restored(handler: CourseHandler) -> None:
    handler._settings.restore_cookies = True
    handler._driver = FakeDriver()

    handler._open_website()

    assert handler._driver.visited == ["https://home", "https://history"]
    assert handler._driver.added_cookies


def test_open_website_falls_back_to_login(handler: CourseHandler) -> None:
    handler._driver = FakeDriver()

    handler._open_website()

    assert handler._driver.visited == ["https://home", "https://login"]
    assert handler._driver.added_cookies == []


def test_open_website_warns_on_empty_history_url(
    handler: CourseHandler, caplog: pytest.LogCaptureFixture
) -> None:
    handler._settings.restore_cookies = True
    handler._settings.url["history"] = ""
    handler._driver = FakeDriver()

    with caplog.at_level(logging.WARNING):
        handler._open_website()

    assert handler._driver.visited == ["https://home"]
    assert "历史页面 URL 为空" in caplog.text


def test_open_website_logs_web_driver_exception(
    handler: CourseHandler, caplog: pytest.LogCaptureFixture
) -> None:
    class BrokenDriver(FakeDriver):
        def get(self, url: str) -> None:
            raise WebDriverException("no network")

    handler._driver = BrokenDriver()

    with caplog.at_level(logging.ERROR):
        handler._open_website()

    assert "访问页面失败" in caplog.text


def test_launch_driver_tries_all_browsers_when_unset(
    handler: CourseHandler, monkeypatch: pytest.MonkeyPatch
) -> None:
    handler._settings.browser = ""
    attempted: list[str] = []

    def fake_verify(browser: str) -> None:
        attempted.append(browser)
        raise NoSuchDriverException("missing")

    monkeypatch.setattr(handler, "_verify_browser", fake_verify)
    monkeypatch.setattr(handler, "_open_website", lambda: None)

    handler.launch_driver()

    assert attempted == ["Firefox", "Edge", "Chrome"]


def test_launch_driver_stops_after_successful_browser(
    handler: CourseHandler, monkeypatch: pytest.MonkeyPatch
) -> None:
    handler._settings.browser = ""
    attempted: list[str] = []
    opened: list[bool] = []

    def fake_verify(browser: str) -> None:
        attempted.append(browser)
        if browser == "Firefox":
            raise NoSuchDriverException("missing")

    monkeypatch.setattr(handler, "_verify_browser", fake_verify)
    monkeypatch.setattr(handler, "_open_website", lambda: opened.append(True))

    handler.launch_driver()

    assert attempted == ["Firefox", "Edge"]
    assert opened == [True]


def test_verify_browser_persists_choice(
    handler: CourseHandler, clean_config: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    saved: list[bool] = []
    monkeypatch.setattr(driver_manager, "save_config", lambda: saved.append(True))
    monkeypatch.setattr(handler, "_init_driver", lambda headless, browser: FakeDriver())

    handler._verify_browser("Chrome")

    assert handler._settings.browser == "Chrome"
    assert clean_config["auto_course"]["browser"] == "Chrome"
    assert saved == [True]


def test_driver_quit_without_driver_is_noop(
    handler: CourseHandler, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO):
        handler.driver_quit()

    assert "浏览器驱动未启动" in caplog.text


def test_driver_quit_saves_cookies_and_history(
    handler: CourseHandler, clean_config: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    handler._settings.restore_cookies = True
    handler._driver = FakeDriver(cookies=[{"name": "s", "value": "1"}], current_url="https://last")
    saved: list[bool] = []
    monkeypatch.setattr(driver_manager, "save_config", lambda: saved.append(True))

    handler.driver_quit()

    assert clean_config["auto_course"]["user_cookies"] == "s=1"
    assert clean_config["auto_course"]["history_url"] == "https://last"
    assert saved == [True]
    assert handler._driver.quit_called


def test_driver_quit_skips_saving_when_disabled(
    handler: CourseHandler, clean_config: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    handler._driver = FakeDriver()
    saved: list[bool] = []
    monkeypatch.setattr(driver_manager, "save_config", lambda: saved.append(True))

    handler.driver_quit()

    assert saved == []
    assert clean_config["auto_course"]["user_cookies"] == "a=1; b=2"
    assert handler._driver.quit_called


def test_driver_quit_handles_closed_browser(
    handler: CourseHandler, caplog: pytest.LogCaptureFixture
) -> None:
    class ClosedDriver(FakeDriver):
        @property
        def window_handles(self):  # type: ignore[override]
            raise WebDriverException("closed")

        @window_handles.setter
        def window_handles(self, _value) -> None:
            return

    handler._driver = ClosedDriver()

    with caplog.at_level(logging.ERROR):
        handler.driver_quit()

    assert "驱动被人为关闭" in caplog.text
    assert handler._driver.quit_called


@pytest.mark.parametrize(
    ("browser", "expected"), [("Firefox", "Firefox"), ("Edge", "Edge"), ("Chrome", "Chrome")]
)
def test_init_driver_selects_requested_browser(
    handler: CourseHandler, monkeypatch: pytest.MonkeyPatch, browser: str, expected: str
) -> None:
    created: list[tuple[str, object]] = []

    for name in ("Firefox", "Edge", "Chrome"):
        monkeypatch.setattr(
            driver_manager.webdriver,
            name,
            lambda options, _name=name: created.append((_name, options)) or FakeDriver(),
        )

    handler._init_driver(headless=True, browser=browser)

    assert created[0][0] == expected
    assert "--headless" in created[0][1].arguments


def test_init_driver_falls_back_to_firefox(
    handler: CourseHandler, monkeypatch: pytest.MonkeyPatch
) -> None:
    created: list[str] = []
    monkeypatch.setattr(
        driver_manager.webdriver,
        "Firefox",
        lambda options: created.append("Firefox") or FakeDriver(),
    )

    handler._init_driver(headless=False, browser="Safari")

    assert created == ["Firefox"]


def test_init_driver_sets_chinese_locale_preference(
    handler: CourseHandler, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: list[object] = []
    monkeypatch.setattr(
        driver_manager.webdriver, "Chrome", lambda options: captured.append(options) or FakeDriver()
    )

    handler._init_driver(headless=False, browser="Chrome")

    assert "--lang=zh-CN" in captured[0].arguments
    assert "--headless" not in captured[0].arguments


def test_launch_ws_server_starts_daemon_thread(
    handler: CourseHandler, monkeypatch: pytest.MonkeyPatch
) -> None:
    started: list[dict] = []

    class FakeThread:
        def __init__(self, target, daemon):
            self.target = target
            self.daemon = daemon

        def start(self):
            started.append({"target": self.target, "daemon": self.daemon})

    monkeypatch.setattr(driver_manager.threading, "Thread", FakeThread)

    handler._launch_ws_server()

    assert started[0]["daemon"] is True
    assert started[0]["target"] == handler._launch_websocket


def test_launch_websocket_serves_messenger(
    handler: CourseHandler, monkeypatch: pytest.MonkeyPatch
) -> None:
    served: list[tuple] = []

    class FakeServer:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_exc_info):
            return False

    def fake_serve(handler_fn, host, port):
        served.append((handler_fn, host, port))
        return FakeServer()

    class StopServer(Exception):
        pass

    class FakeFuture:
        def __await__(self):
            raise StopServer
            yield  # pragma: no cover - 使函数成为生成器

    monkeypatch.setattr(driver_manager.websockets, "serve", fake_serve)
    monkeypatch.setattr(driver_manager.asyncio, "Future", FakeFuture)

    with pytest.raises(StopServer):
        handler._launch_websocket()

    assert served == [(handler._messenger, "localhost", 8765)]


def test_pretend_active_scrolls_and_sleeps(
    handler: CourseHandler, monkeypatch: pytest.MonkeyPatch
) -> None:
    handler._driver = FakeDriver()
    targets: list = []

    class FakeThread:
        def __init__(self, target, daemon):
            self.target = target
            self.daemon = daemon

        def start(self):
            targets.append(self.target)

    class StopLoop(Exception):
        pass

    def fake_sleep(_seconds):
        raise StopLoop

    monkeypatch.setattr(driver_manager.threading, "Thread", FakeThread)
    monkeypatch.setattr(driver_manager.time, "sleep", fake_sleep)

    handler.pretend_active()
    with pytest.raises(StopLoop):
        targets[0]()

    assert handler._driver.executed_scripts == ["window.scrollBy(0, arguments[0]);"]
    assert handler._driver.switched == ["h2"]


@pytest.mark.asyncio
async def test_messenger_answers_html_message(
    handler: CourseHandler, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    que_path = tmp_path / "question.html"
    ans_path = tmp_path / "answers.json"
    ans_path.write_text('[{"题号": "1", "答案": "A"}]', encoding="utf-8")
    monkeypatch.setattr(
        driver_manager,
        "get_path_config",
        lambda _static, name: que_path if name == "original_questions" else ans_path,
    )

    answered: list[bool] = []

    async def fake_answer_questions() -> None:
        answered.append(True)

    monkeypatch.setattr(driver_manager, "answer_questions", fake_answer_questions)
    websocket = FakeWebSocket(['{"type": "testDocHtml", "html": "<html></html>"}'])

    await handler._messenger(websocket)

    assert que_path.read_text(encoding="utf-8") == "<html></html>"
    assert answered == [True]
    assert websocket.sent == ['[{"题号": "1", "答案": "A"}]']


@pytest.mark.asyncio
async def test_messenger_ignores_other_messages(
    handler: CourseHandler, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(driver_manager, "get_path_config", lambda _static, name: tmp_path / name)
    websocket = FakeWebSocket(['{"type": "ping"}'])

    await handler._messenger(websocket)

    assert websocket.sent == []


class FakeWebSocket:
    """最小化的 websocket 连接替身"""

    def __init__(self, messages: list[str]):
        self.messages = messages
        self.sent: list[str] = []

    def __aiter__(self):
        return self._iterate()

    async def _iterate(self):
        for message in self.messages:
            yield message

    async def send(self, message: str) -> None:
        self.sent.append(message)


def test_launch_script_injects_code(
    handler: CourseHandler, monkeypatch: pytest.MonkeyPatch
) -> None:
    handler._driver = FakeDriver()
    monkeypatch.setattr(handler, "_init_script", lambda: "console.log(1);")
    monkeypatch.setattr(handler, "_launch_ws_server", lambda: None)
    monkeypatch.setattr(driver_manager.time, "sleep", lambda _seconds: None)

    handler.launch_script()

    assert handler._driver.executed_scripts == ["console.log(1);"]
    assert handler._driver.switched == ["h2"]
