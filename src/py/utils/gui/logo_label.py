from PySide6 import QtWidgets, QtGui, QtCore

class LogoLabel(QtWidgets.QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 让控件背景透明
        self.setPixmap(QtGui.QPixmap(image_path))
        self.setScaledContents(True)
        self.setFixedSize(130, 130)  # 可根据logo实际大小调整
        # 不要在这里设置阴影
        # 用于动画的属性
        self._y_offset = 0

    def setYOffset(self, value):
        self._y_offset = value
        self.move(self.x(), self._base_y + self._y_offset)

    def getYOffset(self):
        return self._y_offset

    yOffset = QtCore.Property(int, getYOffset, setYOffset)