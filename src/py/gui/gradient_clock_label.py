"""时钟类"""
from datetime import datetime

from PySide6 import QtCore

from .gradient_label import GradientLabel

class GradientClockLabel(GradientLabel):
    """时钟label"""
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFont(self.font())  # 可自定义字体
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        """时间更新"""
        now = datetime.now()
        self.setText(now.strftime("%H:%M:%S"))
