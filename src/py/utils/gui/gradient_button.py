from PySide6 import QtCore, QtWidgets, QtGui


def lerp_color(c1, c2, t):
    """线性插值两个 QColor"""
    return QtGui.QColor(
        int(c1.red()   + (c2.red()   - c1.red())   * t),
        int(c1.green() + (c2.green() - c1.green()) * t),
        int(c1.blue()  + (c2.blue()  - c1.blue())  * t),
        int(c1.alpha() + (c2.alpha() - c1.alpha()) * t)
    )


class TipPopup(QtWidgets.QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setText(text)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFont(QtGui.QFont(self.font().family(), 11, QtGui.QFont.Bold))  # 字体更小
        self.setContentsMargins(10, 3, 10, 3)  # 内边距更小
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect()
        radius = rect.height() / 2

        # 渐变背景
        gradient = QtGui.QLinearGradient(0, 0, rect.width(), 0)
        gradient.setColorAt(0.0, QtGui.QColor("#89ddff"))
        gradient.setColorAt(0.3, QtGui.QColor("#dcf7b5"))
        gradient.setColorAt(0.7, QtGui.QColor("#f9b7a4"))
        gradient.setColorAt(1.0, QtGui.QColor("#ffffff"))

        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawPath(path)

        text_gradient = QtGui.QRadialGradient(
            rect.center(), rect.width() * 0.8,
            rect.center()
        )
        text_gradient.setColorAt(0.0, QtGui.QColor("#232946"))
        text_gradient.setColorAt(0.3, QtGui.QColor("#393e5c"))
        text_gradient.setColorAt(0.7, QtGui.QColor("#22223b"))
        text_gradient.setColorAt(1.0, QtGui.QColor("#181926"))
        painter.setPen(QtGui.QPen(QtGui.QBrush(text_gradient), 0))
        painter.setFont(self.font())
        painter.drawText(rect, QtCore.Qt.AlignCenter, self.text())

    def showAnimated(self, pos=None, duration=800):
        # 计算目标位置
        if pos is None:
            pos = self.pos()
        start_pos = QtCore.QPoint(pos.x(), pos.y() + 20)  # 起始位置稍微低一点
        end_pos = pos

        self.move(start_pos)
        self.show()
        self.raise_()

        # 透明度动画
        self.anim_opacity = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.anim_opacity.setStartValue(0.0)
        self.anim_opacity.setKeyValueAt(0.35, 1.0)
        self.anim_opacity.setKeyValueAt(0.75, 1.0)
        self.anim_opacity.setEndValue(0.0)
        self.anim_opacity.setDuration(duration)

        # 位移动画
        self.anim_pos = QtCore.QPropertyAnimation(self, b"pos", self)
        self.anim_pos.setStartValue(start_pos)  # 消失时再往上
        self.anim_pos.setEndValue(QtCore.QPoint(end_pos.x(), end_pos.y() - 20))
        self.anim_pos.setDuration(duration)
        self.anim_pos.setEasingCurve(QtCore.QEasingCurve.OutCubic) 

        # 并行动画组
        self.anim_group = QtCore.QParallelAnimationGroup(self)
        self.anim_group.addAnimation(self.anim_opacity)
        self.anim_group.addAnimation(self.anim_pos)
        self.anim_group.finished.connect(self.hide)
        self.anim_group.start()




class GradientButton(QtWidgets.QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFont(QtGui.QFont(self.font().family(), 16))
        self.setMinimumHeight(40)
        self.setStyleSheet("background: transparent; border: none;")
        self._radius = 20

        self._hover_progress = 0.0
        self._anim = QtCore.QPropertyAnimation(self, b"hoverProgress", self)
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self._swapped = False
        self._is_animating = False

    def set_swapped(self, swapped: bool):
        self._swapped = swapped
        # 互换时直接跳转，不做悬停动画
        if self._anim is not None:
            self._anim.stop()
        self._hover_progress = 0.0
        self.update()

    def start_swap_animation(self):
        self._is_animating = True

    def end_swap_animation(self):
        self._is_animating = False

    def enterEvent(self, event):
        if self._is_animating:
            return
        if self._anim is not None:
            self._anim.stop()
            self._anim.setStartValue(self._hover_progress)
            self._anim.setEndValue(1.0)
            self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._is_animating:
            return
        if self._anim is not None:
            self._anim.stop()
            self._anim.setStartValue(self._hover_progress)
            self._anim.setEndValue(0.0)
            self._anim.start()
        super().leaveEvent(event)

    def getHoverProgress(self):
        return self._hover_progress

    def setHoverProgress(self, value):
        self._hover_progress = value
        self.update()

    hoverProgress = QtCore.Property(float, getHoverProgress, setHoverProgress)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect()
        radius = self._radius

        # 渐变色插值
        if not self._swapped:
            # 悬停动画：背景渐变色插值
            base_colors = [
                QtGui.QColor("#89ddff"),
                QtGui.QColor("#dcf7b5"),
                QtGui.QColor("#f9b7a4"),
                QtGui.QColor("#ffffff"),
            ]
            hover_colors = [
                QtGui.QColor("#f9b7a4"),
                QtGui.QColor("#ffffff"),
                QtGui.QColor("#89ddff"),
                QtGui.QColor("#dcf7b5"),
            ]
            stops = [0, 0.25, 0.7, 1]
            bg_gradient = QtGui.QLinearGradient(rect.topLeft(), rect.topRight())
            for i, stop in enumerate(stops):
                c = lerp_color(base_colors[i], hover_colors[i], self._hover_progress)
                bg_gradient.setColorAt(stop, c)
            # 文字颜色保持不变
            text_brush = QtGui.QLinearGradient(rect.topLeft(), rect.topRight())
            text_brush.setColorAt(0, QtGui.QColor("#232946"))
            text_brush.setColorAt(0.3, QtGui.QColor("#393e5c"))
            text_brush.setColorAt(0.7, QtGui.QColor("#22223b"))
            text_brush.setColorAt(1, QtGui.QColor("#181926"))
        else:
            # 互换后：背景用原文字渐变，且无悬停动画
            bg_gradient = QtGui.QLinearGradient(rect.topLeft(), rect.topRight())
            bg_gradient.setColorAt(0, QtGui.QColor("#232946"))
            bg_gradient.setColorAt(0.3, QtGui.QColor("#393e5c"))
            bg_gradient.setColorAt(0.7, QtGui.QColor("#22223b"))
            bg_gradient.setColorAt(1, QtGui.QColor("#181926"))
            # 文字用原背景渐变
            text_brush = QtGui.QLinearGradient(rect.topLeft(), rect.topRight())
            text_brush.setColorAt(0, QtGui.QColor("#89ddff"))
            text_brush.setColorAt(0.25, QtGui.QColor("#dcf7b5"))
            text_brush.setColorAt(0.7, QtGui.QColor("#f9b7a4"))
            text_brush.setColorAt(1, QtGui.QColor("#ffffff"))

        # 绘制背景
        painter.setBrush(bg_gradient)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        # 绘制文字
        painter.setPen(QtGui.QPen(QtCore.Qt.transparent))
        font = self.font()
        painter.setFont(font)
        painter.setBrush(text_brush)
        painter.setPen(QtGui.QPen(QtGui.QBrush(text_brush), 0))
        painter.drawText(rect, QtCore.Qt.AlignCenter, self.text())

    def show_tip(self, text="APPLY SUCCEED!"):
        btn_rect = self.rect()
        btn_pos = self.mapToGlobal(QtCore.QPoint(0, 0))
        self._tip_popup = TipPopup(text, parent=None)  # 保存为成员变量
        self._tip_popup.adjustSize()
        x = btn_pos.x() + (btn_rect.width() - self._tip_popup.width()) // 2
        y = btn_pos.y() - self._tip_popup.height() - 8
        self._tip_popup.move(x, y)
        self._tip_popup.showAnimated()