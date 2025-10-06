"""
文件路径相关的工具函数
"""
import logging
import sys
from pathlib import Path


def static_path(*relative_path: str) -> Path:
    """开发/打包双环境的静态路径适配"""
    root: Path = Path(getattr(sys, '_MEIPASS', str(Path.cwd()))).absolute()
    return root.joinpath(*relative_path)

def writable_path(*relative_path: str) -> Path:
    """返回可写入路径并保证父目录存在"""
    abs_path = Path.cwd().joinpath(*relative_path)
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    return abs_path

def ensure_file(path: Path) -> None:
    """确保文件存在, 不存在则创建一个空文件(path应对应临时文件)"""
    if path.exists():
        logging.info("文件 '%s' 已存在", path.name)
    else:
        path.touch(exist_ok=True)
        logging.info("文件 '%s' 创建成功", path.name)

def check_file(path: Path) -> None:
    """检查文件是否正常, 如果不正常则抛出警告(path应对应资源文件)"""
    if not path.exists():
        logging.warning("资源文件 '%s' 不存在, 可能影响程序表现", path.name)
    elif path.stat().st_size == 0:
        logging.warning("资源文件 '%s' 为空, 可能影响程序表现", path.name)
    else:
        logging.info("资源文件 '%s' 状态正常", path.name)
