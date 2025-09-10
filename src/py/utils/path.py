"""路径配置相关函数"""

import os
import sys
from typing import Final

PROJECT_ROOT: Final = os.path.abspath(os.getcwd())

def resource_path(relative_path: str) -> str:
    """开发/打包双环境的资源路径适配"""
    base_path = getattr(sys, '_MEIPASS', None)
    if base_path and os.path.exists(base_path):
        return os.path.join(base_path, relative_path)
    # 退回到相对于脚本的路径
    return os.path.join(PROJECT_ROOT, relative_path)

def writable_path(relative_path: str) -> str:
    """返回当前工作目录下的可写路径，并自动创建父目录"""
    abs_path = os.path.join(os.getcwd(), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path
