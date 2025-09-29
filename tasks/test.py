import time
from PySide6.QtCore import QObject

class TextTasks(QObject):
    """所有与文本处理相关的业务逻辑"""

    def task_a(self, text: str):
        print(f"执行文本任务A: 收到文本 '{text}'")
        time.sleep(2)
        print("文本任务A 完成。")

    def task_c(self, text: str, mode: str):
        print(f"执行文本任务C: 模式为 '{mode}', 文本为 '{text}'")
        time.sleep(1)
        print("文本任务C 完成。")

class NumericTasks(QObject):
    """所有与数值计算相关的业务逻辑"""

    def task_b(self, value: int):
        print(f"执行数值任务B: 收到数字 '{value}'，将执行 {value} 次循环。")
        for i in range(value):
            time.sleep(0.5)
            print(f"  循环 {i+1}/{value}")
        print("数值任务B 完成。")