"""app._config_manager 单元测试"""

import logging

import pytest

from app._config_manager import Configuration


def test_set_config_top_level(clean_config: dict) -> None:
    Configuration().set_config(["speed"], 2.0)

    assert clean_config["speed"] == 2.0


def test_set_config_creates_missing_nested_dicts(clean_config: dict) -> None:
    Configuration().set_config(["auto_course", "advanced", "speed"], 3.0)

    assert clean_config == {"auto_course": {"advanced": {"speed": 3.0}}}


def test_set_config_replaces_non_dict_intermediate(clean_config: dict) -> None:
    clean_config["auto_course"] = "not-a-dict"

    Configuration().set_config(["auto_course", "browser"], "Edge")

    assert clean_config["auto_course"] == {"browser": "Edge"}


def test_set_config_warns_on_type_change(
    clean_config: dict, caplog: pytest.LogCaptureFixture
) -> None:
    clean_config["auto_course"] = {"speed": 2.0}

    with caplog.at_level(logging.WARNING):
        Configuration().set_config(["auto_course", "speed"], "fast")

    assert "类型变化" in caplog.text
    assert clean_config["auto_course"]["speed"] == "fast"


def test_set_config_keeps_silent_on_same_type(
    clean_config: dict, caplog: pytest.LogCaptureFixture
) -> None:
    clean_config["auto_course"] = {"speed": 2.0}

    with caplog.at_level(logging.WARNING):
        Configuration().set_config(["auto_course", "speed"], 4.0)

    assert not caplog.records


def test_get_config_returns_nested_value(clean_config: dict) -> None:
    clean_config["openai"] = {"model": "kimi"}

    assert Configuration().get_config("openai", "model") == "kimi"


def test_get_config_returns_sub_dict(clean_config: dict) -> None:
    clean_config["openai"] = {"model": "kimi"}

    assert Configuration().get_config("openai") == {"model": "kimi"}


def test_get_config_missing_key_returns_empty_string(
    clean_config: dict, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING):
        result = Configuration().get_config("openai", "model")

    assert result == ""
    assert "不在配置字典中" in caplog.text


def test_get_config_through_non_dict_returns_empty_string(clean_config: dict) -> None:
    clean_config["openai"] = "kimi"

    assert Configuration().get_config("openai", "model") == ""


def test_commit_config_delegates_to_save_config(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[bool] = []
    monkeypatch.setattr("app._config_manager.save_config", lambda: calls.append(True), raising=True)

    Configuration().commit_config()

    assert calls == [True]


def test_set_then_get_round_trip(clean_config: dict) -> None:
    configuration = Configuration()
    configuration.set_config(["openai", "api_key"], "sk-test")

    assert configuration.get_config("openai", "api_key") == "sk-test"
