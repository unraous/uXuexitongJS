"""app.TaskExecutor / app.TaskManager 单元测试"""

import logging
from collections.abc import Iterator

import pytest
from PySide6.QtCore import QCoreApplication

import app as app_module
from app import TaskManager
from app._config_manager import Configuration


@pytest.fixture(scope="module")
def qt_app() -> Iterator[QCoreApplication]:
    """TaskManager 依赖 Qt 事件循环对象"""
    app = QCoreApplication.instance() or QCoreApplication([])
    yield app


@pytest.fixture
def executor(clean_config: dict) -> app_module.TaskExecutor:
    return app_module.TaskExecutor()


@pytest.fixture
def manager(qt_app: QCoreApplication, clean_config: dict) -> Iterator[TaskManager]:
    """提供 TaskManager 并保证工作线程被彻底回收"""
    instance = TaskManager()
    yield instance
    instance.close()
    instance._thread.wait(5000)


def test_register_tasks_collects_public_methods(executor: app_module.TaskExecutor) -> None:
    registry = executor._task_registry

    assert {"set_config", "get_config", "commit_config"} <= set(registry)
    assert {"launch_driver", "launch_script", "driver_quit", "refresh_settings"} <= set(registry)
    assert isinstance(registry["set_config"], Configuration)


def test_register_tasks_skips_private_methods(executor: app_module.TaskExecutor) -> None:
    assert not [name for name in executor._task_registry if name.startswith("_")]


def test_register_tasks_warns_on_duplicate_names(
    clean_config: dict, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(app_module, "CourseHandler", Configuration)

    with caplog.at_level(logging.WARNING):
        app_module.TaskExecutor()

    assert "已存在" in caplog.text


def test_exec_calls_task_and_reports_result(clean_config: dict) -> None:
    finished: list[tuple[int, object]] = []
    executor = app_module.TaskExecutor(
        finish=lambda job_id, result: finished.append((job_id, result))
    )
    clean_config["openai"] = {"model": "kimi"}

    executor.exec(7, "get_config", ["openai", "model"])

    assert finished == [(7, "kimi")]


def test_exec_unknown_task_reports_none(
    clean_config: dict, caplog: pytest.LogCaptureFixture
) -> None:
    finished: list[tuple[int, object]] = []
    executor = app_module.TaskExecutor(
        finish=lambda job_id, result: finished.append((job_id, result))
    )

    with caplog.at_level(logging.ERROR):
        executor.exec(1, "does_not_exist", [])

    assert finished == [(1, None)]
    assert "未找到业务" in caplog.text


def test_exec_without_callback_is_safe(executor: app_module.TaskExecutor) -> None:
    executor._finish = None

    executor.exec(1, "get_config", ["openai"])


def test_shutdown_clears_registry(executor: app_module.TaskExecutor) -> None:
    executor.shutdown()

    assert executor._task_registry == {}
    assert executor._finish is None


def test_dispatch_returns_incrementing_job_ids(manager: TaskManager) -> None:
    assert manager.dispatch("get_config", ["openai"]) == 1
    assert manager.dispatch("get_config", ["openai"]) == 2


def test_dispatch_logs_error_when_thread_stopped(
    manager: TaskManager, caplog: pytest.LogCaptureFixture
) -> None:
    manager._thread.quit()
    manager._thread.wait()

    with caplog.at_level(logging.ERROR):
        job_id = manager.dispatch("get_config", ["openai"])

    assert job_id == 1
    assert "工作线程未启动" in caplog.text


def test_on_finished_stores_result_and_emits_signal(manager: TaskManager) -> None:
    received: list[tuple[int, object]] = []
    manager.finished.connect(lambda job_id, result: received.append((job_id, result)))

    manager.on_finished(3, "value")

    assert received == [(3, "value")]
    assert manager._results[3] == "value"


def test_get_result_pops_stored_result(manager: TaskManager) -> None:
    manager.on_finished(5, {"a": 1})

    assert manager.get_result(5) == "{'a': 1}"
    assert manager.get_result(5) == ""


def test_close_stops_thread_and_executor(manager: TaskManager) -> None:
    manager.close()

    assert manager._executor._task_registry == {}
