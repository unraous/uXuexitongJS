"""工具模块，包含文件路径和配置管理等功能"""

__all__: list[str] = [
    "resource_path",
    "writable_path",
    "ensure_file",
    "check_file",
    "init_config",
    "save_config",
    "global_config",
    "WTB_PATH",
    "RSC_PATH",
]

from .file_path import resource_path, writable_path, ensure_file, check_file, WTB_PATH, RSC_PATH
from .config import init_config, save_config, global_config
