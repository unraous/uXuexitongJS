# -*- coding: utf-8 -*-
"""将HTML文件转换为答案的完整流程"""
import  os

from src.py.auto_answer.extract_html import extract_font_from_html, extract_questions_from_html
from src.py.auto_answer.create_map import create_font_mapping
from src.py.auto_answer.depry_question import decode_questions
from src.py.auto_answer.core_of_answer import answer_questions_file, extract_simple_answers

from src.py.utils.path import resource_path

thtml_path = resource_path("data/temp/html/test.html")

def writable_path(relative_path):
    """返回当前工作目录下的可写路径，并自动创建父目录"""
    abs_path = os.path.join(os.getcwd(), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path

def html_to_answer(
    html_path,
    std_font_path = resource_path("data/static/ttf/simsun.ttf"),
    ttf_path = writable_path("data/temp/ttf/font-cxsecret.ttf"),
    mapping_json = writable_path("data/temp/json/font_cxsecret_mapping.json"),
    questions_json = writable_path("data/temp/json/questions.json"),
    decoded_json = writable_path("data/temp/json/questions_decoded.json"),
    answered_json = writable_path("data/temp/json/questions_answered.json"),
    simplified_json = writable_path("data/temp/json/answer_simplified.json")
):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    extract_font_from_html(html_content, ttf_path)

    questions = extract_questions_from_html(html_content)
    with open(questions_json, "w", encoding="utf-8") as f:
        import json
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"题目已保存到 {questions_json}")
    create_font_mapping(ttf_path, std_font_path, mapping_json)
    decode_questions(questions_json, decoded_json, mapping_json)
    
    answer_questions_file(decoded_json, answered_json)
    extract_simple_answers(answered_json, simplified_json)

if __name__ == "__main__":
    # 请根据实际路径修改
    html_to_answer(html_path=thtml_path)