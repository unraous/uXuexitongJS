"""app.utils.file_path 单元测试"""

import logging
import sys
from pathlib import Path

import pytest

from app.utils.file_path import check_file, ensure_file, static_path, writable_path


def test_static_path_uses_cwd_in_dev(temp_cwd: Path) -> None:
    assert static_path("src", "a.txt") == temp_cwd / "src" / "a.txt"


def test_static_path_uses_meipass_when_frozen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert static_path("res", "b.txt") == tmp_path / "res" / "b.txt"


def test_static_path_without_arguments_returns_root(temp_cwd: Path) -> None:
    assert static_path() == temp_cwd


def test_writable_path_creates_parent_directories(temp_cwd: Path) -> None:
    path = writable_path("data", "temp", "json", "x.json")

    assert path == temp_cwd / "data" / "temp" / "json" / "x.json"
    assert path.parent.is_dir()
    assert not path.exists()


def test_writable_path_is_idempotent(temp_cwd: Path) -> None:
    first = writable_path("data", "x.json")
    second = writable_path("data", "x.json")

    assert first == second
    assert first.parent.is_dir()


def test_ensure_file_creates_missing_file(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    path = tmp_path / "temp.txt"

    with caplog.at_level(logging.INFO):
        ensure_file(path)

    assert path.is_file()
    assert "创建成功" in caplog.text


def test_ensure_file_keeps_existing_content(tmp_path: Path) -> None:
    path = tmp_path / "temp.txt"
    path.write_text("data", encoding="utf-8")

    ensure_file(path)

    assert path.read_text(encoding="utf-8") == "data"


def test_check_file_warns_when_missing(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        check_file(tmp_path / "missing.ttf")

    assert "不存在" in caplog.text


def test_check_file_warns_when_empty(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    path = tmp_path / "empty.ttf"
    path.touch()

    with caplog.at_level(logging.WARNING):
        check_file(path)

    assert "为空" in caplog.text


def test_check_file_accepts_normal_file(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    path = tmp_path / "ok.ttf"
    path.write_text("content", encoding="utf-8")

    with caplog.at_level(logging.INFO):
        check_file(path)

    assert "状态正常" in caplog.text
    assert not [record for record in caplog.records if record.levelno >= logging.WARNING]
