"""
配置文件读写模块
负责加载、保存配置文件至全局字典 global_config
包含
"""

import logging
from pathlib import Path
from typing import Any, Final

import tomlkit

from .file_path import static_path, writable_path

DEFAULT_CONFIG_PATH: Final[Path] = static_path("src", "resources", "toml", "default_config.toml")
# 默认配置文件路径, 硬编码在此处, 如非必要请勿修改
CONFIG_PATH: Final[Path] = writable_path("data", "config.toml")

global_config: dict[str, Any] = {}
"""由配置toml生成的全局作用域字典"""


def init_config() -> None:
    """初始化配置toml至 global_config"""
    logging.info("正在加载配置文件 (路径: %s)", CONFIG_PATH)
    global_config.clear()

    try:
        with CONFIG_PATH.open("rb") as f:
            global_config.update(tomlkit.load(f))
            logging.info("配置文件加载成功 (路径: %s)", CONFIG_PATH)
    except FileNotFoundError:  # 程序首次运行时会发生
        _restore_default_config("未找到配置文件")
    except (OSError, tomlkit.exceptions.TOMLKitError):
        # 配置文件损坏或不可读时不能静默启动, 否则后续所有配置读取都会残缺
        logging.exception("配置文件无法读取或已损坏 (路径: %s)", CONFIG_PATH)
        _restore_default_config("配置文件已损坏")


def _restore_default_config(reason: str) -> None:
    """以默认配置重建配置文件"""
    try:
        with DEFAULT_CONFIG_PATH.open("r", encoding="utf-8") as default_f:
            default_content = default_f.read()
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            f.write(default_content)
    except OSError as e:
        raise RuntimeError(
            f"{reason}, 且无法写入默认配置 (默认配置: {DEFAULT_CONFIG_PATH}, 目标: {CONFIG_PATH})"
        ) from e

    global_config.update(tomlkit.loads(default_content))
    logging.info("%s, 已写入默认配置文件 (路径: %s)", reason, CONFIG_PATH)


def get_path_config(static: bool, name: str) -> Path:
    """输入路径组名称和路径名称, 从配置中获取并返回对应绝对路径"""
    path_groups: dict = global_config.get("path_groups", {})
    group: str = "static" if static else "writable"
    relative: list[str] = path_groups.get(group, {}).get(name, [])
    if not relative:  # 否则会静默返回工作目录本身, 导致后续读写落到错误位置
        raise KeyError(f"配置中不存在路径 path_groups.{group}.{name}")

    result_path: Path = static_path(*relative) if static else writable_path(*relative)
    logging.info("成功获取路径: {'%s' : %s}", name, result_path)
    return result_path


def save_config() -> None:
    """保存字典至配置toml"""
    try:
        with CONFIG_PATH.open("wb") as f:
            f.write(tomlkit.dumps(global_config).encode("utf-8"))
            logging.info("配置文件已保存")
    except OSError as e:  # 权限不足、路径不存在、磁盘已满等
        raise RuntimeError(f"保存配置文件失败, 请检查路径及权限: {CONFIG_PATH}") from e
