"""app.utils.config 单元测试"""

import logging
from pathlib import Path

import pytest

from app.utils import config as config_module

DEFAULT_TOML = """
[openai]
model = "kimi"

[path_groups.writable]
answers = ["data", "temp", "answers.json"]

[path_groups.static]
std_font = ["src", "resources", "ttf", "simsun.ttf"]
"""


@pytest.fixture
def config_paths(temp_cwd: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    """把默认/用户配置路径重定向到临时目录"""
    default_path = temp_cwd / "default_config.toml"
    default_path.write_text(DEFAULT_TOML, encoding="utf-8")
    config_path = temp_cwd / "data" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(config_module, "DEFAULT_CONFIG_PATH", default_path)
    monkeypatch.setattr(config_module, "CONFIG_PATH", config_path)
    return {"default": default_path, "config": config_path}


def test_init_config_creates_config_from_default(
    config_paths: dict[str, Path], clean_config: dict
) -> None:
    config_module.init_config()

    assert config_paths["config"].read_text(encoding="utf-8") == DEFAULT_TOML
    assert clean_config["openai"]["model"] == "kimi"


def test_init_config_loads_existing_config(
    config_paths: dict[str, Path], clean_config: dict
) -> None:
    config_paths["config"].write_text('[openai]\nmodel = "gpt"\n', encoding="utf-8")

    config_module.init_config()

    assert clean_config["openai"]["model"] == "gpt"
    # 已存在的配置不应被默认配置覆盖
    assert config_paths["config"].read_text(encoding="utf-8") == '[openai]\nmodel = "gpt"\n'


def test_init_config_clears_stale_entries(
    config_paths: dict[str, Path], clean_config: dict
) -> None:
    clean_config["stale"] = "value"

    config_module.init_config()

    assert "stale" not in clean_config


def test_get_path_config_writable(
    config_paths: dict[str, Path], temp_cwd: Path, clean_config: dict
) -> None:
    config_module.init_config()

    path = config_module.get_path_config(False, "answers")

    assert path == temp_cwd / "data" / "temp" / "answers.json"
    assert path.parent.is_dir()


def test_get_path_config_static(
    config_paths: dict[str, Path], temp_cwd: Path, clean_config: dict
) -> None:
    config_module.init_config()

    path = config_module.get_path_config(True, "std_font")

    assert path == temp_cwd / "src" / "resources" / "ttf" / "simsun.ttf"


def test_get_path_config_unknown_name_returns_root(
    config_paths: dict[str, Path], temp_cwd: Path, clean_config: dict
) -> None:
    config_module.init_config()

    assert config_module.get_path_config(True, "unknown") == temp_cwd


def test_save_config_round_trip(config_paths: dict[str, Path], clean_config: dict) -> None:
    config_module.init_config()
    clean_config["openai"]["model"] = "new-model"

    config_module.save_config()
    config_module.init_config()

    assert clean_config["openai"]["model"] == "new-model"


def test_save_config_logs_permission_error(
    config_paths: dict[str, Path],
    clean_config: dict,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_permission_error(*_args, **_kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "open", raise_permission_error)

    with caplog.at_level(logging.ERROR):
        config_module.save_config()

    assert "保存配置文件失败" in caplog.text
