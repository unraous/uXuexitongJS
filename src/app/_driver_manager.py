"""浏览器驱动模块"""
import asyncio
import dataclasses
import json
import logging
import secrets
import threading
import time
from pathlib import Path

import aiofiles
import websockets
from selenium import webdriver
from selenium.common.exceptions import NoSuchDriverException, WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from .auto_answer import answer_questions
from .utils import get_path_config, global_config, save_config


@dataclasses.dataclass
class CourseSettings:
    """刷课相关设置"""
    browser: str
    url: dict[str, str]
    user_cookies: str
    restore_cookies: bool
    force_speed: bool
    speed: float

def load_settings() -> CourseSettings:
    """从 global_config 加载刷课相关设置"""
    ac_cfg: dict = global_config.get("auto_course", {})
    return CourseSettings(
        browser=ac_cfg.get("browser", ""),
        url={
            key: ac_cfg.get(f"{key}_url", "")
            for key in ["home", "login", "history"]
        },
        user_cookies=ac_cfg.get("user_cookies", ""),
        restore_cookies=ac_cfg.get("restore_cookies", True),
        force_speed=ac_cfg.get("force_speed", False),
        speed=ac_cfg.get("speed", 2.0),
    )

class CourseHandler:
    """网课处理类, 包含selenium浏览器驱动启动和 AI 答题所需的JS/PY 双向 WebSocket 服务"""
    def __init__(self):
        self._driver: webdriver.Firefox | webdriver.Edge | webdriver.Chrome
        self._ws_thread: threading.Thread
        self._mouse_thread: threading.Thread
        self._settings = load_settings()
        self._script_code: str

    async def _messenger(self, websocket: websockets.ServerConnection) -> None:
        """WebSocket 消息处理器"""
        que_path: Path = get_path_config(False, "original_questions")
        ans_path: Path = get_path_config(False, "answers")
        async for msg in websocket:
            data: dict = json.loads(msg)
            if data.get("type") == "testDocHtml":
                html_str: str = data.get("html", "")
                logging.info("收到问题HTML, 长度: %d", len(html_str))

                async with aiofiles.open(que_path, "w", encoding="utf-8") as f:
                    await f.write(html_str)
                logging.info("HTML已保存到 %s", que_path)

                await answer_questions()

                async with aiofiles.open(ans_path, encoding="utf-8") as f:
                    ans_json = await f.read()
                await websocket.send(ans_json)
            else:
                logging.info("收到非HTML消息: %s", data)

    def _launch_websocket(self):
        """启动 WebSocket 服务器"""
        async def run(port: int = 8765):
            async with websockets.serve(self._messenger, "localhost", port):
                logging.info("WebSocket服务器已启动 ws://localhost:%d", port)
                await asyncio.Future()
        asyncio.run(run())

    def _init_driver(
        self,
        headless: bool = True,
        browser: str = "Firefox"
    ) -> webdriver.Firefox | webdriver.Edge | webdriver.Chrome:
        """初始化浏览器驱动"""
        driver_map: dict = {
            "Firefox": (webdriver.Firefox, FirefoxOptions),
            "Edge": (webdriver.Edge, EdgeOptions),
            "Chrome": (webdriver.Chrome, ChromeOptions),
        }

        driver_cls, options_cls = driver_map.get(browser, driver_map["Firefox"])
        options: FirefoxOptions | EdgeOptions | ChromeOptions = options_cls()

        if isinstance(options, FirefoxOptions):
            options.set_preference("intl.accept_languages", "zh-CN")
        else:
            options.add_argument("--lang=zh-CN")
        if headless:
            options.add_argument("--headless")
        return driver_cls(options=options)

    def _parse_cookies(self, cookie_str: str) -> list:
        """将标准 cookie 字符串解析为 selenium cookies 列表"""
        cookies = []
        for item in cookie_str.split(';'):
            if '=' in item:
                name, value = item.strip().split('=', 1)
                cookies.append({'name': name, 'value': value})
        return cookies

    def _inject_cookies(self) -> None:
        """注入用户 Cookie"""
        if self._settings.user_cookies.strip() == "":
            logging.info("用户 Cookie 为空, 跳过注入")
            return

        cookies = self._parse_cookies(self._settings.user_cookies)
        for cookie in cookies:
            self._driver.add_cookie(cookie)
        logging.info("已成功设置 %d 个 Cookie", len(cookies))

    def _init_script(self) -> str:
        """初始化 JS 脚本"""
        script_path: Path = get_path_config(True, "js_script")
        logging.info("正在加载脚本: %s", script_path)
        with Path(script_path).open(encoding="utf-8") as f:
            main_script: str = f.read()

        logging.info("脚本已加载, 长度: %d", len(main_script))
        options: str = f"""
            const LAUNCH_OPTION = 1;
            const FORCE_SPEED = {str(self._settings.force_speed).lower()};
            const SPEED = {self._settings.speed};
        """
        return "\n".join([options, main_script])

    def _launch_ws_server(self) -> None:
        """启动 WebSocket 服务器线程"""
        self._ws_thread = threading.Thread(target=self._launch_websocket, daemon=True)
        self._ws_thread.start()

    def _cookies_to_str(self, cookies: list) -> str:
        """将 selenium cookies 列表转为标准 cookie 字符串"""
        return "; ".join([f"{c['name']}={c['value']}" for c in cookies])

    def _verify_browser(self, browser: str) -> None:
        """测试浏览器是否正常工作"""
        self._driver = self._init_driver(headless=False, browser=browser)
        self._driver.get("about:blank")
        logging.info("已成功启动%s浏览器", browser)
        self._settings.browser = browser
        global_config["auto_course"]["browser"] = browser
        save_config()

    def _open_website(self) -> None:
        try:
            self._driver.get(self._settings.url["home"])
            logging.info("已打开主页面: %s", self._settings.url["home"])
            if self._settings.restore_cookies and self._settings.user_cookies.strip() != "":
                self._inject_cookies()
                time.sleep(0.5)
                if len(self._settings.url["history"]) > 0:
                    self._driver.get(self._settings.url["history"])
                    logging.info("已打开历史页面: %s", self._settings.url["history"])
                else:
                    logging.warning("历史页面 URL 为空, 无法打开历史页面")
            else:
                logging.info("历史为空或记忆功能未开启, 进入默认登录界面")
                self._driver.get(self._settings.url["login"])
        except WebDriverException as e:
            logging.error("访问页面失败: %s, 请检查网络连接并重启应用", e)

    def refresh_settings(self) -> None:
        """刷新配置"""
        self._settings = load_settings()

    def launch_driver(self) -> None:
        """初始化浏览器驱动"""
        logging.info(
            "未指定浏览器内核, 尝试依次启动 Firefox、Edge、Chrome"
            if self._settings.browser == ""
            else "尝试启动指定的 %s 浏览器", self._settings.browser
        )

        for browser in (
            ["Firefox", "Edge", "Chrome"] if self._settings.browser == ""
            else [self._settings.browser]
        ):
            try:
                self._verify_browser(browser)
                break
            except NoSuchDriverException:
                logging.warning("%s内核启动失败", browser)
        self._open_website()

    def launch_script(self) -> None:
        """启动并注入js脚本"""
        self._script_code = self._init_script()
        self._launch_ws_server()

        handles = self._driver.window_handles
        self._driver.switch_to.window(handles[-1])
        time.sleep(2)
        self._driver.execute_script(self._script_code)
        logging.info("js脚本注入成功")

    def pretend_active(self) -> None:
        """模拟鼠标活动, 防止被检测为挂机"""
        def mouse_action():
            while True:
                handles = self._driver.window_handles
                self._driver.switch_to.window(handles[-1])

                # 模拟鼠标滚轮轻微滚动(向下/向上)
                scroll_value = secrets.randbelow(101) - 50  # -50 to 50
                self._driver.execute_script(
                    "window.scrollBy(0, arguments[0]);",
                    scroll_value
                )
                time.sleep(secrets.randbelow(31) + 30)  # 30 to 60
        self._mouse_thread = threading.Thread(target=mouse_action, daemon=True)
        self._mouse_thread.start()

    def driver_quit(self) -> None:
        """关闭浏览器驱动"""
        if hasattr(self, "_driver"):
            try:
                handles = self._driver.window_handles
                self._driver.switch_to.window(handles[-1])
                if self._settings.restore_cookies:
                    global_config["auto_course"]["user_cookies"] = self._cookies_to_str(
                        self._driver.get_cookies()
                    )
                    global_config["auto_course"]["history_url"] = self._driver.current_url
                    logging.info("已保存最新的 cookies 和 history_url 至配置文件")
                    save_config()

            except WebDriverException:
                logging.error("驱动被人为关闭, 保存 cookies 和 history_url 失败")
            finally:
                self._driver.quit()
                logging.info("浏览器驱动已关闭")
        else:
            logging.info("浏览器驱动未启动")
