"""app.auto_answer._depry_question 单元测试"""

import json
from pathlib import Path

from app.auto_answer._depry_question import decode_questions, decode_text, load_decode_map

DECODE_MAP = {"甲": "中", "乙": "国"}


def write_json(path: Path, data: object) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_load_decode_map(tmp_path: Path) -> None:
    mapping_path = write_json(tmp_path / "mapping.json", DECODE_MAP)

    assert load_decode_map(mapping_path) == DECODE_MAP


def test_load_decode_map_accepts_pair_array(tmp_path: Path) -> None:
    mapping_path = write_json(tmp_path / "mapping.json", [["甲", "中"], ["乙", "国"]])

    assert load_decode_map(mapping_path) == DECODE_MAP


def test_decode_text_replaces_mapped_characters() -> None:
    assert decode_text("甲乙", DECODE_MAP) == "中国"


def test_decode_text_keeps_unmapped_characters() -> None:
    assert decode_text("甲丙 A1", DECODE_MAP) == "中丙 A1"


def test_decode_text_handles_empty_input() -> None:
    assert decode_text("", DECODE_MAP) == ""
    assert decode_text(None, DECODE_MAP) == ""  # type: ignore[arg-type]


def test_decode_questions_writes_decoded_file(tmp_path: Path) -> None:
    mapping_path = write_json(tmp_path / "mapping.json", DECODE_MAP)
    input_path = write_json(
        tmp_path / "questions.json",
        [{"题号": "1.", "题干": "甲", "选项": ["甲A", "乙B"]}],
    )
    output_path = tmp_path / "decoded.json"

    decode_questions(input_path, output_path, mapping_path)

    decoded = json.loads(output_path.read_text(encoding="utf-8"))
    assert decoded == [{"题号": "1.", "题干": "中", "选项": ["中A", "国B"]}]


def test_decode_questions_fills_missing_fields(tmp_path: Path) -> None:
    mapping_path = write_json(tmp_path / "mapping.json", DECODE_MAP)
    input_path = write_json(tmp_path / "questions.json", [{"题号": "1."}])
    output_path = tmp_path / "decoded.json"

    decode_questions(input_path, output_path, mapping_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {"题号": "1.", "题干": "", "选项": []}
    ]


def test_decode_questions_with_empty_question_list(tmp_path: Path) -> None:
    mapping_path = write_json(tmp_path / "mapping.json", DECODE_MAP)
    input_path = write_json(tmp_path / "questions.json", [])
    output_path = tmp_path / "decoded.json"

    decode_questions(input_path, output_path, mapping_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == []
