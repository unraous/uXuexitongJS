"""app.auto_answer._create_map 单元测试"""

import json
from pathlib import Path

import pytest
from PIL import Image

from app.auto_answer import _create_map as create_map

STD_FONT_PATH = Path(__file__).resolve().parents[1] / "src" / "resources" / "ttf" / "simsun.ttf"


class _FakeHash:
    """可控距离的哈希替身"""

    def __init__(self, value: int):
        self.value = value

    def __sub__(self, other: "_FakeHash") -> int:
        return abs(self.value - other.value)


def fake_multi_hash(value: int) -> tuple[_FakeHash, ...]:
    return (_FakeHash(value), _FakeHash(value), _FakeHash(value))


def test_common_chars_contains_frequent_characters() -> None:
    assert {"的", "一", "是"} <= create_map.COMMON_CHARS


def test_glyph_to_img_renders_grayscale_square() -> None:
    img = create_map.glyph_to_img(STD_FONT_PATH, "的", size=32)

    assert isinstance(img, Image.Image)
    assert img.mode == "L"
    assert img.size == (32, 32)
    # 渲染出的字形应当在纯白背景上留下深色像素
    assert min(img.getdata()) < 255


def test_multi_hash_returns_three_hashes() -> None:
    hashes = create_map.multi_hash(create_map.glyph_to_img(STD_FONT_PATH, "的", size=32))

    assert len(hashes) == 3


def test_multi_hash_is_deterministic() -> None:
    img = create_map.glyph_to_img(STD_FONT_PATH, "一", size=32)

    assert create_map.multi_hash(img) == create_map.multi_hash(img)


def test_hash_distance_is_zero_for_identical_hashes() -> None:
    hashes = create_map.multi_hash(create_map.glyph_to_img(STD_FONT_PATH, "的", size=32))

    assert create_map.hash_distance(hashes, hashes) == 0


def test_hash_distance_sums_component_distances() -> None:
    assert create_map.hash_distance(fake_multi_hash(10), fake_multi_hash(4)) == 18


def test_std_worker_skips_uncommon_characters(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(create_map, "glyph_to_img", lambda *_args, **_kwargs: None)

    assert create_map.std_worker(ord("Z"), STD_FONT_PATH) is None


def test_std_worker_returns_char_and_hashes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(create_map, "glyph_to_img", lambda *_args, **_kwargs: "image")
    monkeypatch.setattr(create_map, "multi_hash", lambda _img: fake_multi_hash(1))

    result = create_map.std_worker(ord("的"), STD_FONT_PATH)

    assert result is not None
    assert result[0] == "的"
    assert len(result[1]) == 3


def test_enc_worker_picks_closest_standard_glyph(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(create_map, "glyph_to_img", lambda *_args, **_kwargs: "image")
    monkeypatch.setattr(create_map, "multi_hash", lambda _img: fake_multi_hash(10))
    std_hashes = {"远": fake_multi_hash(0), "近": fake_multi_hash(9)}

    assert create_map.enc_worker(0xE000, STD_FONT_PATH, std_hashes) == (chr(0xE000), "近")


def test_enc_worker_returns_none_without_standard_hashes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(create_map, "glyph_to_img", lambda *_args, **_kwargs: "image")
    monkeypatch.setattr(create_map, "multi_hash", lambda _img: fake_multi_hash(10))

    assert create_map.enc_worker(0xE000, STD_FONT_PATH, {}) is None


def test_create_font_mapping_writes_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeCmap:
        def getBestCmap(self):  # noqa: N802 - 与 fontTools 接口保持一致
            return self.cmap

    def fake_ttfont(path: Path):
        table = FakeCmap()
        table.cmap = {0xE000: "uniE000"} if path.name == "enc.ttf" else {ord("的"): "uni7684"}
        return {"cmap": table}

    monkeypatch.setattr(create_map, "TTFont", fake_ttfont)
    monkeypatch.setattr(create_map, "glyph_to_img", lambda *_args, **_kwargs: "image")
    monkeypatch.setattr(create_map, "multi_hash", lambda _img: fake_multi_hash(1))
    output_json = tmp_path / "mapping.json"

    mapping = create_map.create_font_mapping(
        tmp_path / "enc.ttf", tmp_path / "std.ttf", output_json
    )

    assert mapping == {chr(0xE000): "的"}
    assert json.loads(output_json.read_text(encoding="utf-8")) == mapping
