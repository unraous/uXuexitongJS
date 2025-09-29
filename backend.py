import itertools
from PySide6.QtCore import QObject, Slot, Signal, QThread
from worker import Worker

class Backend(QObject):
    # 1. 信号只传递完成的 jobId
    workFinished = Signal(int)
    _execute = Signal(int, str, list) # jobId, taskName, args

    def __init__(self, parent=None):
        super().__init__(parent)
        # 2. 创建一个无限的、线程安全的 jobId 生成器
        self._job_id_counter = itertools.count(1)
        
        # 3. 不再需要 _active_qml_object
        # self._active_qml_object = None

        self._thread = QThread()
        self._worker = Worker()
        self._worker.moveToThread(self._thread)
        self._execute.connect(self._worker.execute_task)
        self._worker.finished.connect(self.on_work_finished)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    @Slot(str, list, result=int)
    def execute(self, task_name: str, args: list) -> int:
        """
        不再接收 QML 对象，而是返回一个唯一的 jobId。
        """
        job_id = next(self._job_id_counter)
        print(f"分发新任务，Job ID: {job_id}")
        
        if self._thread.isRunning():
            self._execute.emit(job_id, task_name, args)
        else:
            print("错误: 工作线程未运行。")
        
        return job_id

    # 5. on_work_finished 只负责转发 jobId
    @Slot(int)
    def on_work_finished(self, job_id: int):
        print(f"后端收到任务完成通知，Job ID: {job_id}")
        self.workFinished.emit(job_id)

    def cleanup(self):
        self._thread.quit()
        self._thread.wait() 