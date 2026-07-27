"""自动化答题模块"""

__all__ = ["answer_questions"]

import json
import logging
import shutil
from pathlib import Path

import aiofiles

from ..utils import get_path_config as get_path
from ._core_of_answer import answer_questions_file, extract_simple_answers
from ._create_map import create_font_mapping
from ._depry_question import decode_questions
from ._extract_html import extract_font_from_html, extract_questions_from_html


async def answer_questions() -> None:
    """答题完整流程"""
    std_font_path: Path = get_path(True, "std_font")

    html_path: Path = get_path(False, "original_questions")
    ttf_path: Path = get_path(False, "obf_font")
    mapping_json_path: Path = get_path(False, "obf_mapping")
    questions_path: Path = get_path(False, "questions")
    decoded_json_path: Path = get_path(False, "decoded")
    answered_json_path: Path = get_path(False, "qa_pairs")
    simplified_json_path: Path = get_path(False, "answers")

    async with aiofiles.open(html_path, encoding="utf-8") as f:
        html_content = await f.read()
    font_extracted: bool = extract_font_from_html(html_content, ttf_path)

    questions = extract_questions_from_html(html_content)
    if not questions:
        raise ValueError("未从 HTML 中提取到任何题目, 页面结构可能已变更")

    async with aiofiles.open(questions_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(questions, ensure_ascii=False, indent=2))

    logging.info("题目已保存到 %s, 共 %d 题", questions_path, len(questions))

    if font_extracted:
        create_font_mapping(ttf_path, std_font_path, mapping_json_path)
        decode_questions(questions_path, decoded_json_path, mapping_json_path)
    else:
        # 未提取到加密字体时不能沿用旧映射表, 否则会把正常汉字“解密”成乱码
        logging.warning("未提取到加密字体, 跳过解密步骤")
        shutil.copyfile(questions_path, decoded_json_path)

    answer_questions_file(decoded_json_path, answered_json_path)
    extract_simple_answers(answered_json_path, simplified_json_path)
