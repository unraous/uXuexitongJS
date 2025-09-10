from PySide6 import QtCore, QtWidgets, QtGui

class GradientLabel(QtWidgets.QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setText(text)
        self._scale = 1.0
        self.setFont(QtGui.QFont(self.font().family(), 18))
        self.setMinimumHeight(40)
        self.setStyleSheet("background: transparent;")




    def setScale(self, scale):
        self._scale = scale
        self.update()

    def getScale(self):
        return self._scale

    scale = QtCore.Property(float, getScale, setScale)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.save()

        font = self.font()
        rect = self.rect()
        text = self.text()
        metrics = QtGui.QFontMetrics(font)
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
       
        '''
        # 画label边框（红色）
        painter.setPen(QtGui.QPen(QtGui.QColor("red"), 1, QtCore.Qt.DashLine))
        painter.drawRect(rect.adjusted(0, 0, -1, -1))
        '''
       
        # 以label中心为缩放中心
        center = rect.center()
        painter.translate(center)
        painter.scale(self._scale, self._scale)
        painter.translate(-center)

        # 文字基线y
        x = (rect.width() - text_width) / 2
        y = (rect.height() + text_height) / 2 - metrics.descent()
        
        '''
        # 画文字包围框（绿色）
        painter.setPen(QtGui.QPen(QtGui.QColor("green"), 1, QtCore.Qt.DashLine))
        painter.drawRect(QtCore.QRectF(x, y - text_height, text_width, text_height))
        '''
       
        # 渐变和绘制
        gradient = QtGui.QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QtGui.QColor("#89ddff"))
        gradient.setColorAt(0.25, QtGui.QColor("#dcf7b5"))
        gradient.setColorAt(0.7, QtGui.QColor("#f9b7a4"))
        gradient.setColorAt(1.0, QtGui.QColor("#ffffff"))
        painter.setPen(QtCore.Qt.NoPen)
        path = QtGui.QPainterPath()
        path.addText(x, y, font, text)
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawPath(path)
        painter.restore()


    def fade_in(self, duration=800):
        if not hasattr(self, "opacity_effect"):
            self.opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        anim = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(duration)
        anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
        self._fade_anim = anim  # 防止被回收

