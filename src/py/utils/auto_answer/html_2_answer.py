# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract_html import extract_font_from_html, extract_questions_from_html
from create_map import create_font_mapping
from depry_question import decode_questions
from core_of_answer import answer_questions_file, extract_simple_answers

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

thtml_path = os.path.join(BASE_DIR, "../../../data/temp/html/test.html")

def html_to_answer(
    html_path,
    std_font_path = os.path.join(BASE_DIR, "../../../data/static/ttf/simsun.ttf"),
    ttf_path = os.path.join(BASE_DIR, "../../../data/temp/ttf/font-cxsecret.ttf"),
    mapping_json = os.path.join(BASE_DIR, "../../../data/temp/json/font_cxsecret_mapping.json"),
    questions_json = os.path.join(BASE_DIR, "../../../data/temp/json/questions.json"),
    decoded_json = os.path.join(BASE_DIR, "../../../data/temp/json/questions_decoded.json"),
    answered_json = os.path.join(BASE_DIR, "../../../data/temp/json/questions_answered.json"),
    simplified_json = os.path.join(BASE_DIR, "../../../data/temp/json/answer_simplified.json")
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