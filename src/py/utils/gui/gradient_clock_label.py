from PySide6 import QtCore
from datetime import datetime
from gradient_label import GradientLabel

class GradientClockLabel(GradientLabel):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFont(self.font())  # 可自定义字体
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        now = datetime.now()
        self.setText(now.strftime("%H:%M:%S"))