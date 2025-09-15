"""路径/文件相关函数"""

import os
import sys
import logging

from typing import Optional

WTB_PATH: dict[str, str] = {}
"""可写路径字典，存储程序运行时需要确保存在的动态文件路径(目前主要是答题相关的临时文件)，格式为 {file_keywords: path} """
RSC_PATH: dict[str, str] = {}
"""资源路径字典，存储程序运行时需要确保存在的资源路径，格式为 {file_keywords: path} """


def resource_path(relative_path: str) -> str:
    """开发/打包双环境的资源路径适配"""
    base_path: Optional[str] = getattr(sys, '_MEIPASS', None)
    return os.path.join(
        base_path if base_path and os.path.exists(base_path) else os.path.abspath(os.getcwd()),
        relative_path
    )

def writable_path(relative_path: str) -> str:
    """保证可写路径存在并将其返回"""
    abs_path = os.path.join(os.getcwd(), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path

def ensure_file(path: str) -> None:
    """确保文件存在，不存在则创建一个空文件(path应对应临时文件)"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('')
        logging.info("已创建文件: %s", os.path.basename(path))
    else:
        logging.info("文件已存在: %s", os.path.basename(path))

def check_file(path: str) -> None:
    """检查文件是否正常，如果不正常则抛出警告(path应对应资源文件)"""
    if not os.path.exists(path):
        logging.warning("资源文件 %s 不存在，可能影响程序表现", os.path.basename(path))
    elif os.path.getsize(path) == 0:
        logging.warning("资源文件 %s 为空，可能影响程序表现", os.path.basename(path))
    else:
        logging.info("资源文件 %s 状态正常", os.path.basename(path))
