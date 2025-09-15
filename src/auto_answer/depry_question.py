import json
import re

def load_decode_map(mapping_path):
    with open(mapping_path, encoding='utf-8') as f:
        decode_arr = json.load(f)
    return dict(decode_arr)

def decode_text(text, decode_map):
    def repl(m):
        c = m.group(0)
        return decode_map.get(c, c)
    return re.sub(r'[\u4e00-\u9fff]', repl, text or '')

def decode_questions(input_json, output_json, mapping_json):
    decode_map = load_decode_map(mapping_json)
    with open(input_json, encoding='utf-8') as f:
        data = json.load(f)
    for q in data:
        q['题干'] = decode_text(q.get('题干', ''), decode_map)
        q['选项'] = [decode_text(opt, decode_map) for opt in q.get('选项', [])]
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'解密完成，已输出 {output_json}')