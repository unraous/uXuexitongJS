"""自动化答题模块"""

__all__ = ["answer_questions"]

import logging
import json

from src.utils import resource_path, writable_path

from .extract_html import extract_font_from_html, extract_questions_from_html
from .create_map import create_font_mapping
from .depry_question import decode_questions
from .core_of_answer import answer_questions_file, extract_simple_answers


def answer_questions(
) -> None:
    """答题完整流程"""
    std_font_path: str = resource_path("data/static/ttf/simsun.ttf")

    html_path: str = writable_path("data/temp/html/question.html")
    ttf_path: str = writable_path("data/temp/ttf/font-cxsecret.ttf")
    mapping_json_path: str = writable_path("data/temp/json/font_cxsecret_mapping.json")
    questions_path: str = writable_path("data/temp/json/questions.json")
    decoded_json_path: str = writable_path("data/temp/json/questions_decoded.json")
    answered_json_path: str = writable_path("data/temp/json/questions_answered.json")
    simplified_json_path: str = writable_path("data/temp/json/answer_simplified.json")

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    extract_font_from_html(html_content, ttf_path)

    questions = extract_questions_from_html(html_content)
    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    logging.info("题目已保存到 %s，共 %d 题", questions_path, len(questions))
    create_font_mapping(ttf_path, std_font_path, mapping_json_path)
    decode_questions(questions_path, decoded_json_path, mapping_json_path)

    answer_questions_file(decoded_json_path, answered_json_path)
    extract_simple_answers(answered_json_path, simplified_json_path)
