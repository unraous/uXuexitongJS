"""路径/文件相关函数"""

import os
import sys
import logging

from typing import Final, Optional

WTB_PATH: dict[str, str] = {}
"""可写路径列表，存储程序运行时需要确保存在的文件路径"""
RSC_PATH: dict[str, str] = {}
"""资源路径列表，存储程序运行时需要确保存在的只读资源路径"""

_PROJECT_ROOT: Final[str] = os.path.abspath(os.getcwd())


def resource_path(relative_path: str) -> str:
    """开发/打包双环境的资源路径适配"""
    base_path: Optional[str] = getattr(sys, '_MEIPASS', None)
    if base_path and os.path.exists(base_path):
        return os.path.join(base_path, relative_path)
    # 退回到相对于脚本的路径
    return os.path.join(_PROJECT_ROOT, relative_path)

def writable_path(relative_path: str) -> str:
    """返回当前工作目录下的可写路径，并自动创建父目录"""
    abs_path = os.path.join(os.getcwd(), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path

def ensure_file(path: str) -> None:
    """确保文件存在，如果不存在则创建一个空文件"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('')
        logging.info("已创建文件: %s", os.path.basename(path))
    else:
        logging.info("文件已存在: %s", os.path.basename(path))

def check_file(path: str) -> None:
    """检查文件是否正常，如果不正常则抛出警告"""
    if not os.path.exists(path):
        logging.warning("文件%s不存在，可能影响程序表现", os.path.basename(path))
    elif os.path.getsize(path) == 0:
        logging.warning("文件%s为空，可能影响程序表现", os.path.basename(path))
    else:
        logging.info("文件%s正常", os.path.basename(path))
