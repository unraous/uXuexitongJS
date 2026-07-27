"""app.auto_answer._extract_html 单元测试"""

import base64
import logging
from pathlib import Path

import pytest

from app.auto_answer._extract_html import extract_font_from_html, extract_questions_from_html

FONT_BYTES = b"\x00\x01\x00\x00fake-ttf-payload"


def build_font_html(base64_str: str, family: str = "font-cxsecret") -> str:
    return f"""
    <style>
    @font-face {{
        font-family: '{family}';
        font-style: normal;
        src: url('data:application/font-ttf;charset=utf-8;base64,{base64_str}');
    }}
    </style>
    """


QUESTION_HTML = """
<div class="TiMu newTiMu">
    <div class="Cy_TItle">
        <i class="fl">1.</i>
        <span class="newZy_TItle">【单选题】</span>
    </div>
    <div class="fontLabel">这是<span>题干</span></div>
    <ul>
        <li><a>A</a>选项一</li>
        <li><a>B</a>选项二</li>
    </ul>
</div>
<div class="TiMu newTiMu">
    <div class="fontLabel">只有题干</div>
</div>
"""


def test_extract_font_from_html_writes_ttf(tmp_path: Path) -> None:
    output = tmp_path / "obf_font.ttf"
    html = build_font_html(base64.b64encode(FONT_BYTES).decode())

    assert extract_font_from_html(html, output) is True
    assert output.read_bytes() == FONT_BYTES


def test_extract_font_from_html_supports_double_quoted_family(tmp_path: Path) -> None:
    output = tmp_path / "obf_font.ttf"
    html = build_font_html(base64.b64encode(FONT_BYTES).decode()).replace(
        "'font-cxsecret'", '"font-cxsecret"'
    )

    assert extract_font_from_html(html, output) is True
    assert output.read_bytes() == FONT_BYTES


def test_extract_font_from_html_ignores_other_font_family(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    output = tmp_path / "obf_font.ttf"
    html = build_font_html(base64.b64encode(FONT_BYTES).decode(), family="some-other-font")

    with caplog.at_level(logging.WARNING):
        result = extract_font_from_html(html, output)

    assert result is False
    assert not output.exists()
    assert "未检测到" in caplog.text


def test_extract_font_from_html_without_font_face(tmp_path: Path) -> None:
    assert extract_font_from_html("<html></html>", tmp_path / "obf_font.ttf") is False


def test_extract_questions_parses_all_fields() -> None:
    questions = extract_questions_from_html(QUESTION_HTML)

    assert len(questions) == 2
    assert questions[0] == {
        "题号": "1.",
        "题型": "【单选题】",
        "题干": "这是题干",
        "选项": ["A选项一", "B选项二"],
    }


def test_extract_questions_defaults_for_missing_fields() -> None:
    questions = extract_questions_from_html(QUESTION_HTML)

    assert questions[1] == {"题号": "", "题型": "", "题干": "只有题干", "选项": []}


def test_extract_questions_ignores_unrelated_divs() -> None:
    assert extract_questions_from_html('<div class="other">x</div>') == []


def test_extract_questions_from_empty_html() -> None:
    assert extract_questions_from_html("") == []
