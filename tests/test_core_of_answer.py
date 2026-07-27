"""app.auto_answer._core_of_answer 单元测试"""

import json
from pathlib import Path

import pytest
from openai import OpenAIError

from app.auto_answer import _core_of_answer as core

QUESTIONS = [
    {"题号": "1", "题干": "一加一等于几", "选项": ["A.1", "B.2"]},
    {"题号": "2", "题干": "地球是圆的吗", "选项": ["A.对", "B.错"]},
]


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """答题流程中的节流等待在测试中无意义"""
    monkeypatch.setattr(core.time, "sleep", lambda _seconds: None)


def write_questions(path: Path, questions: list[dict]) -> Path:
    path.write_text(json.dumps(questions, ensure_ascii=False), encoding="utf-8")
    return path


def test_get_openai_client_uses_config() -> None:
    client, model = core.get_openai_client(
        {"api_key": "sk-test", "base_url": "https://example.com/v1", "model": "kimi"}
    )

    assert model == "kimi"
    assert client.api_key == "sk-test"
    assert str(client.base_url).startswith("https://example.com/v1")


def test_get_openai_client_defaults_on_empty_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")

    client, model = core.get_openai_client({})

    assert model == ""
    assert client.api_key == ""


def test_chat_with_openai_uses_default_model(
    clean_config: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    clean_config["openai"] = {"api_key": "sk-test", "base_url": "", "model": "kimi"}
    captured: dict = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return _completion("1:A")

    monkeypatch.setattr(core, "get_openai_client", lambda _cfg: (_FakeClient(fake_create), "kimi"))

    assert core.chat_with_openai([{"role": "user", "content": "hi"}]) == "1:A"
    assert captured["model"] == "kimi"
    assert captured["timeout"] == 40


def test_chat_with_openai_respects_explicit_model(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return _completion("ok")

    monkeypatch.setattr(core, "get_openai_client", lambda _cfg: (_FakeClient(fake_create), "kimi"))

    core.chat_with_openai([{"role": "user", "content": "hi"}], model="gpt-4o")

    assert captured["model"] == "gpt-4o"


def test_answer_questions_batch_returns_stripped_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    prompts: list[str] = []

    def fake_chat(messages, model=None):
        prompts.append(str(messages[1]["content"]))
        return "  1:A\n2:B  "

    monkeypatch.setattr(core, "chat_with_openai", fake_chat)

    assert core.answer_questions_batch(QUESTIONS) == "1:A\n2:B"
    assert "1. 题干:一加一等于几" in prompts[0]
    assert "2. 题干:地球是圆的吗" in prompts[0]


def test_answer_questions_batch_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts: list[int] = []

    def fake_chat(_messages, model=None):
        attempts.append(1)
        if len(attempts) < 3:
            raise TimeoutError("timeout")
        return "1:A\n2:B"

    monkeypatch.setattr(core, "chat_with_openai", fake_chat)

    assert core.answer_questions_batch(QUESTIONS) == "1:A\n2:B"
    assert len(attempts) == 3


def test_answer_questions_batch_falls_back_to_default_answers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_chat(_messages, model=None):
        raise OpenAIError("boom")

    monkeypatch.setattr(core, "chat_with_openai", fake_chat)

    assert core.answer_questions_batch(QUESTIONS, retry=2) == "1:A\n2:A"


def test_answer_questions_batch_fallback_uses_index_without_number(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_chat(_messages, model=None):
        raise ConnectionError("offline")

    monkeypatch.setattr(core, "chat_with_openai", fake_chat)

    result = core.answer_questions_batch([{"题干": "x", "选项": ["A"]}], retry=1)

    assert result == "1:A"


def test_answer_questions_file_maps_sequential_answers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path = write_questions(tmp_path / "decoded.json", QUESTIONS)
    output_path = tmp_path / "qa_pairs.json"
    monkeypatch.setattr(core, "answer_questions_batch", lambda _batch: "1:A\n2:B")

    core.answer_questions_file(input_path, output_path)

    answered = json.loads(output_path.read_text(encoding="utf-8"))
    assert [q["AI答案"] for q in answered] == ["A", "B"]


def test_answer_questions_file_maps_by_question_number(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    questions = [{"题号": "7", "题干": "x", "选项": ["A"]}]
    input_path = write_questions(tmp_path / "decoded.json", questions)
    output_path = tmp_path / "qa_pairs.json"
    monkeypatch.setattr(core, "answer_questions_batch", lambda _batch: "7:CD")

    core.answer_questions_file(input_path, output_path)

    assert json.loads(output_path.read_text(encoding="utf-8"))[0]["AI答案"] == "CD"


def test_answer_questions_file_marks_unmatched_answers_as_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    questions = [{"题号": "7", "题干": "x", "选项": ["A"]}]
    input_path = write_questions(tmp_path / "decoded.json", questions)
    output_path = tmp_path / "qa_pairs.json"
    monkeypatch.setattr(core, "answer_questions_batch", lambda _batch: "无法作答")

    core.answer_questions_file(input_path, output_path)

    assert json.loads(output_path.read_text(encoding="utf-8"))[0]["AI答案"] == "ERROR"


def test_answer_questions_file_splits_batches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    questions = [{"题号": str(i), "题干": "x", "选项": ["A"]} for i in range(1, 6)]
    input_path = write_questions(tmp_path / "decoded.json", questions)
    output_path = tmp_path / "qa_pairs.json"
    batch_sizes: list[int] = []

    def fake_batch(batch):
        batch_sizes.append(len(batch))
        return "\n".join(f"{idx}:A" for idx in range(1, len(batch) + 1))

    monkeypatch.setattr(core, "answer_questions_batch", fake_batch)

    core.answer_questions_file(input_path, output_path, batch_size=2)

    assert batch_sizes == [2, 2, 1]


def test_extract_simple_answers_keeps_answered_questions(tmp_path: Path) -> None:
    input_path = write_questions(
        tmp_path / "qa_pairs.json",
        [
            {"题号": "1", "题干": "x", "AI答案": "A"},
            {"题号": "2", "题干": "y"},
        ],
    )
    output_path = tmp_path / "answers.json"

    core.extract_simple_answers(input_path, output_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [{"题号": "1", "答案": "A"}]


def test_extract_simple_answers_with_no_answers(tmp_path: Path) -> None:
    input_path = write_questions(tmp_path / "qa_pairs.json", [{"题号": "1", "题干": "x"}])
    output_path = tmp_path / "answers.json"

    core.extract_simple_answers(input_path, output_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == []


class _FakeCompletions:
    def __init__(self, create):
        self.create = create


class _FakeChat:
    def __init__(self, create):
        self.completions = _FakeCompletions(create)


class _FakeClient:
    """最小化的 OpenAI 客户端替身"""

    def __init__(self, create):
        self.chat = _FakeChat(create)


class _Message:
    def __init__(self, content: str):
        self.content = content


class _Choice:
    def __init__(self, content: str):
        self.message = _Message(content)


def _completion(content: str):
    return type("Completion", (), {"choices": [_Choice(content)]})()
