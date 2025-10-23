"""主程序模块"""

__all__: list[str] = [
    "TaskManager",
]

import inspect
import itertools
import logging
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QThread, Signal, Slot

from ._config_manager import Configuration
from ._driver_manager import CourseHandler


class TaskExecutor(QObject):
    """业务执行器类, 运行在独立线程中, 负责业务的注册和执行。"""

    def __init__(self, parent=None, finish: Callable[[int, object], Any] = lambda _, __: None):
        super().__init__(parent)
        self._task_registry: dict[str, object] = {}
        self._finish: Callable[[int, object], Any] | None = finish  # 新增回调

        self._register_tasks()
        logging.info("已注册业务列表: %s", list(self._task_registry.keys()))

    def _register_tasks(self) -> None:
        """注册所有业务类的方法到任务列表"""
        handlers: list[object] = [  # 在此处添加新的业务类
            Configuration(),
            CourseHandler(),
        ]
        for handler in handlers:
            for name, _ in inspect.getmembers(handler, predicate=inspect.ismethod):
                if not name.startswith('_'):
                    if name in self._task_registry:
                        logging.warning("业务%s已存在, 原有业务将被覆盖", name)
                    self._task_registry[name] = handler

    @Slot(int, str, list)
    def exec(self, job_id: int, task_name: str, args: list) -> None:
        """执行指定业务"""
        handler = self._task_registry.get(task_name)
        result: Any = None
        if handler is None:
            logging.error("未找到业务%s", task_name)
        else:
            task_method = getattr(handler, task_name)
            result = task_method(*args)

        if self._finish:
            self._finish(job_id, result)

    def shutdown(self) -> None:
        """关闭业务执行器, 释放资源"""
        self.exec(0, "driver_quit", [])
        self._task_registry.clear()
        self._finish = None
        logging.info("业务执行器已关闭, 业务列表已清空。")



class TaskManager(QObject):
    """业务管理器, 负责管理工作线程和业务分发"""
    finished: Signal = Signal(int, object)
    _execute: Signal = Signal(int, str, list)  # jobId, taskName, args

    def __init__(self, parent=None):
        super().__init__(parent)
        self._job_id_counter = itertools.count(1)
        self._thread = QThread()
        self._executor = TaskExecutor(finish=self.on_finished)

        self._executor.moveToThread(self._thread)
        self._execute.connect(self._executor.exec)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()
        self._results: dict[int, object] = {}

    def _show_result(self, result: object, max_length: int = 10, encrypt: bool = False) -> str:
        """格式化结果显示内容"""
        result_str = str(result)
        if encrypt:
            return "sk-******"
        if len(result_str) > max_length:
            return result_str[:max_length] + "..."
        return result_str

    @Slot(str, list, result=int)
    def dispatch(self, task_name: str, args: list) -> int:
        """分发业务到工作线程并返回业务ID"""
        job_id = next(self._job_id_counter)
        logging.info("执行业务 '%s' (ID: %d)", task_name, job_id)
        if self._thread.isRunning():
            self._execute.emit(job_id, task_name, args)
        else:
            logging.error("工作线程未启动。")
        return job_id

    @Slot(int, object)
    def on_finished(self, job_id: int, result: object) -> None:
        """业务完成回调"""
        logging.info("业务(ID: %d)完成", job_id)
        self._results[job_id] = result
        self.finished.emit(job_id, result)

    @Slot(int, result=str)
    def get_result(self, job_id: int) -> str:
        """获取指定ID的业务结果"""
        result = str(self._results.pop(job_id, ""))
        encrypt = result.startswith("sk-")  # 防止apikey暴露在日志里
        logging.info("获取结果成功(ID: %d): %s",
            job_id,
            self._show_result(result=result, encrypt=encrypt)
        )
        return result

    def close(self) -> None:
        """清理工作线程和业务执行器"""
        self._thread.quit()
        self._executor.shutdown()
        logging.info("程序已退出")
