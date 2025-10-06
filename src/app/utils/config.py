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
CONFIG_PATH: Final[Path] = writable_path("UXS", "config.toml")

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
        with DEFAULT_CONFIG_PATH.open("r", encoding="utf-8") as default_f:
            default_content = default_f.read()
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            f.write(default_content)
        global_config.update(tomlkit.loads(default_content))
        logging.info("未找到配置文件, 已创建默认配置文件 (路径: %s)", CONFIG_PATH)

def get_path_config(static: bool, name: str) -> Path:
    """输入路径组名称和路径名称, 从配置中获取并返回对应绝对路径"""
    path_groups: dict = global_config.get("path_groups", {})
    result_path: Path = (
        static_path(*path_groups.get("static", {}).get(name, []))
        if static else writable_path(*path_groups.get("writable", {}).get(name, []))
    )
    logging.info("成功获取路径: {'%s' : %s}", name, result_path)
    return result_path

def save_config() -> None:
    """保存字典至配置toml"""
    try:
        with CONFIG_PATH.open("wb") as f:
            f.write(tomlkit.dumps(global_config).encode("utf-8"))
            logging.info("配置文件已保存")
    except PermissionError as e:  # 一般不会发生
        logging.error("保存配置文件失败,请检查路径正确性以及程序权限: %s", e)
