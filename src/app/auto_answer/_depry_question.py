"""对题目中的加密汉字进行解密"""

import re
from pathlib import Path

from ..utils import read_json, write_json


def load_decode_map(mapping_path: Path) -> dict:
    """加载解密映射表"""
    return dict(read_json(mapping_path))


def decode_text(text: str, decode_map: dict) -> str:
    """解密文本中的加密汉字"""

    def repl(m):
        c = m.group(0)
        return decode_map.get(c, c)

    return re.sub(r"[\u4e00-\u9fff]", repl, text or "")


def decode_questions(input_json: Path, output_json: Path, mapping_json: Path):
    """解密题目JSON文件中的加密汉字"""
    decode_map = load_decode_map(mapping_json)
    data = read_json(input_json)
    for q in data:
        q["题干"] = decode_text(q.get("题干", ""), decode_map)
        q["选项"] = [decode_text(opt, decode_map) for opt in q.get("选项", [])]
    write_json(output_json, data)
