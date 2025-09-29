import inspect
from PySide6.QtCore import QObject, Slot, Signal

from tasks import handlers

class Worker(QObject):
    """
    Worker 现在完全与 QML 解耦，只负责执行任务并通知完成。
    """
    finished = Signal(int) # 1. 信号只传递 jobId

    def __init__(self, parent=None):
        super().__init__(parent)
        self._task_registry = {}

        # 2. 调用自动注册方法
        self._register_tasks()
        print(f"自动化注册完成，已注册的任务: {list(self._task_registry.keys())}")

    def _register_tasks(self):
        """
        自动扫描处理器列表，并注册所有符合规范的公共方法作为任务。
        """
        for handler in handlers:
            # 3. 使用 inspect.getmembers 查找所有的方法
            for name, _ in inspect.getmembers(handler, predicate=inspect.ismethod):
                # 4. 约定：所有不以下划线 "_" 开头的公共方法都视为一个任务
                if not name.startswith('_'):
                    if name in self._task_registry:
                        print(f"警告: 任务名 '{name}' 重复，后一个将覆盖前一个。")
                    # 5. 将任务名和它所属的处理器实例存入注册表
                    self._task_registry[name] = handler

    @Slot(int, str, list)
    def execute_task(self, job_id: int, task_name: str, args: list): # 2. 接收 jobId
        handler = self._task_registry.get(task_name)
        if not handler:
            print(f"错误: 任务 '{task_name}' 未被注册。")
            self.finished.emit(job_id) # 即使失败也要发射信号
            return
        try:
            task_method = getattr(handler, task_name)
            task_method(*args)
        except Exception as e:
            print(f"执行任务 '{task_name}' 时发生错误: {e}")
        
        # 3. 完成后，将收到的 jobId 原样发射回去
        self.finished.emit(job_id)
