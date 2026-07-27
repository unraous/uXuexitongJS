"""app.auto_answer.answer_questions 流程单元测试"""

import json
from pathlib import Path

import pytest

from app import auto_answer

HTML = '<div class="TiMu newTiMu"><div class="fontLabel">题干</div></div>'


@pytest.fixture
def flow_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    """把流程用到的所有路径重定向到临时目录"""
    paths = {
        name: tmp_path / f"{name}.tmp"
        for name in (
            "std_font",
            "original_questions",
            "obf_font",
            "obf_mapping",
            "questions",
            "decoded",
            "qa_pairs",
            "answers",
        )
    }
    paths["original_questions"].write_text(HTML, encoding="utf-8")
    monkeypatch.setattr(auto_answer, "get_path", lambda _static, name: paths[name])
    return paths


@pytest.mark.asyncio
async def test_answer_questions_runs_full_pipeline(
    flow_paths: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        auto_answer,
        "extract_font_from_html",
        lambda html, ttf: calls.append(f"font:{len(html)}:{ttf.name}") or True,
    )
    monkeypatch.setattr(
        auto_answer,
        "extract_questions_from_html",
        lambda _html: [{"题号": "1.", "题型": "", "题干": "题干", "选项": []}],
    )
    monkeypatch.setattr(
        auto_answer, "create_font_mapping", lambda *_args: calls.append("mapping") or {}
    )
    monkeypatch.setattr(auto_answer, "decode_questions", lambda *_args: calls.append("decode"))
    monkeypatch.setattr(auto_answer, "answer_questions_file", lambda *_args: calls.append("answer"))
    monkeypatch.setattr(
        auto_answer, "extract_simple_answers", lambda *_args: calls.append("simplify")
    )

    await auto_answer.answer_questions()

    assert calls == [f"font:{len(HTML)}:obf_font.tmp", "mapping", "decode", "answer", "simplify"]


@pytest.mark.asyncio
async def test_answer_questions_saves_extracted_questions(
    flow_paths: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    questions = [{"题号": "1.", "题型": "【单选题】", "题干": "题干", "选项": ["A"]}]
    monkeypatch.setattr(auto_answer, "extract_font_from_html", lambda *_args: True)
    monkeypatch.setattr(auto_answer, "extract_questions_from_html", lambda _html: questions)
    monkeypatch.setattr(auto_answer, "create_font_mapping", lambda *_args: {})
    monkeypatch.setattr(auto_answer, "decode_questions", lambda *_args: None)
    monkeypatch.setattr(auto_answer, "answer_questions_file", lambda *_args: None)
    monkeypatch.setattr(auto_answer, "extract_simple_answers", lambda *_args: None)

    await auto_answer.answer_questions()

    saved = json.loads(flow_paths["questions"].read_text(encoding="utf-8"))
    assert saved == questions


@pytest.mark.asyncio
async def test_answer_questions_passes_paths_in_order(
    flow_paths: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    received: dict[str, tuple] = {}
    monkeypatch.setattr(auto_answer, "extract_font_from_html", lambda *_args: True)
    monkeypatch.setattr(auto_answer, "extract_questions_from_html", lambda _html: [])
    monkeypatch.setattr(
        auto_answer,
        "create_font_mapping",
        lambda *args: received.__setitem__("mapping", args) or {},
    )
    monkeypatch.setattr(
        auto_answer, "decode_questions", lambda *args: received.__setitem__("decode", args)
    )
    monkeypatch.setattr(
        auto_answer, "answer_questions_file", lambda *args: received.__setitem__("answer", args)
    )
    monkeypatch.setattr(
        auto_answer, "extract_simple_answers", lambda *args: received.__setitem__("simplify", args)
    )

    await auto_answer.answer_questions()

    assert received["mapping"] == (
        flow_paths["obf_font"],
        flow_paths["std_font"],
        flow_paths["obf_mapping"],
    )
    assert received["decode"] == (
        flow_paths["questions"],
        flow_paths["decoded"],
        flow_paths["obf_mapping"],
    )
    assert received["answer"] == (flow_paths["decoded"], flow_paths["qa_pairs"])
    assert received["simplify"] == (flow_paths["qa_pairs"], flow_paths["answers"])
