"""
文件读写的公共工具函数
统一 JSON/文本的同步与异步读写, 避免各模块重复实现
"""

import json
import logging
from pathlib import Path
from typing import Any

import aiofiles

ENCODING: str = "utf-8"


def read_json(path: Path) -> Any:
    """读取 JSON 文件"""
    with path.open(encoding=ENCODING) as f:
        return json.load(f)


def write_json(path: Path, data: Any, indent: int = 2) -> None:
    """写入 JSON 文件"""
    with path.open("w", encoding=ENCODING) as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    logging.info("已生成 %s", path)


async def read_text(path: Path) -> str:
    """异步读取文本文件"""
    async with aiofiles.open(path, encoding=ENCODING) as f:
        return await f.read()


async def write_text(path: Path, content: str) -> None:
    """异步写入文本文件"""
    async with aiofiles.open(path, "w", encoding=ENCODING) as f:
        await f.write(content)
    logging.info("已生成 %s", path)


async def write_json_async(path: Path, data: Any, indent: int = 2) -> None:
    """异步写入 JSON 文件"""
    await write_text(path, json.dumps(data, ensure_ascii=False, indent=indent))
