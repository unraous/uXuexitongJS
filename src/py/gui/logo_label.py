"""Logo标签模块"""

from PySide6 import QtWidgets, QtGui, QtCore


class LogoLabel(QtWidgets.QLabel):
    """Logo标签类"""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)  # 让控件背景透明
        self.setPixmap(QtGui.QPixmap(image_path))
        self.setScaledContents(True)
        self.setFixedSize(130, 130)
