"""对题目中的加密汉字进行解密"""
import json
import re
from pathlib import Path


def load_decode_map(mapping_path: Path) -> dict:
    """加载解密映射表"""
    with mapping_path.open(encoding='utf-8') as f:
        decode_arr = json.load(f)
    return dict(decode_arr)

def decode_text(text: str, decode_map: dict) -> str:
    """解密文本中的加密汉字"""
    def repl(m):
        c = m.group(0)
        return decode_map.get(c, c)
    return re.sub(r'[\u4e00-\u9fff]', repl, text or '')

def decode_questions(input_json: Path, output_json: Path, mapping_json: Path):
    """解密题目JSON文件中的加密汉字"""
    decode_map = load_decode_map(mapping_json)
    with input_json.open(encoding='utf-8') as f:
        data = json.load(f)
    for q in data:
        q['题干'] = decode_text(q.get('题干', ''), decode_map)
        q['选项'] = [decode_text(opt, decode_map) for opt in q.get('选项', [])]
    with output_json.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'解密完成, 已输出 {output_json}')
