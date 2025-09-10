"""自制按钮基类"""
from PySide6 import QtCore, QtWidgets, QtGui

class AnimatedButton(QtWidgets.QPushButton):
    """动画按钮基类"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setGraphicsEffect(QtWidgets.QGraphicsOpacityEffect(self))
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("border: none;")
        self._bg_color = QtGui.QColor("#00000000")
        self._fg_color = QtGui.QColor("#444a57")
        self._hover_bg = QtGui.QColor("#444a57")
        self._hover_fg = QtGui.QColor("#ffffff")
        self._normal_bg = QtGui.QColor("#00000000")
        self._normal_fg = QtGui.QColor("#444a57")
        self._bg_anim = QtCore.QVariantAnimation(self)
        self._bg_anim.valueChanged.connect(self._on_bg_anim)
        self._fg_anim = QtCore.QVariantAnimation(self)
        self._fg_anim.valueChanged.connect(self._on_fg_anim)

    def _on_bg_anim(self, value):
        self._bg_color = value
        self.update()

    def _on_fg_anim(self, value):
        self._fg_color = value
        self.update()

    # 为保证Qt的特定事件命名规范，enterEvent等函数名格式不严格符合PEP8
    def enterEvent(self, event): # pylint: disable=invalid-name
        """鼠标进入事件"""
        self._animate(self._hover_bg, self._hover_fg)
        super().enterEvent(event)

    def leaveEvent(self, event): # pylint: disable=invalid-name
        """鼠标离开事件"""
        self._animate(self._normal_bg, self._normal_fg)
        super().leaveEvent(event)

    def _animate(self, bg, fg):
        """背/前景动画"""
        self._bg_anim.stop()
        self._bg_anim.setStartValue(self._bg_color)
        self._bg_anim.setEndValue(bg)
        self._bg_anim.setDuration(200)
        self._bg_anim.start()
        self._fg_anim.stop()
        self._fg_anim.setStartValue(self._fg_color)
        self._fg_anim.setEndValue(fg)
        self._fg_anim.setDuration(200)
        self._fg_anim.start()

    def paintEvent(self, _): # pylint: disable=invalid-name
        """渲染事件"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(self._bg_color)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        painter.setPen(self._fg_color)
        painter.setFont(self.font())
        painter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, self.text())