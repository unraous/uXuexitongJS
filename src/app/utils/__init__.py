"""工具模块, 包含文件路径和配置管理等功能"""

__all__: list[str] = [
    "check_file",
    "ensure_file",
    "get_path_config",
    "global_config",
    "init_config",
    "read_json",
    "read_text",
    "save_config",
    "static_path",
    "writable_path",
    "write_json",
    "write_json_async",
    "write_text",
]

from .config import get_path_config, global_config, init_config, save_config
from .file_io import read_json, read_text, write_json, write_json_async, write_text
from .file_path import check_file, ensure_file, static_path, writable_path
