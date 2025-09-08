import os
import json

from PySide6 import QtWidgets, QtCore, QtGui, QtSvg

from src.py.utils.gui.gradient_button import GradientButton
from src.py.utils.gui.gradient_label import GradientLabel

TRANSPARENT_BK = "background: transparent;"

def load_settings(path):
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
    
def save_settings(path, opt1, opt2):
    data = {
        "Log": opt1.isChecked(),
        "ForceSpd": opt2.isChecked(),
        "Pace": opt2.extraValue()
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def writable_path(relative_path):
    """返回当前工作目录下的可写路径，并自动创建父目录"""
    abs_path = os.path.join(os.getcwd(), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path


class CircleButton(QtWidgets.QAbstractButton):
    """可点击的圆环按钮，选中时填充"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(28, 28)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # 外圈
        pen = QtGui.QPen(QtGui.QColor("#888"), 2)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawEllipse(4, 4, 20, 20)
        # 内圈（选中时填充）
        if self.isChecked():
            # 使用渐变色填充内圈
            rect = QtCore.QRectF(9, 9, 10, 10)
            gradient = QtGui.QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
            gradient.setColorAt(0.0, QtGui.QColor("#89ddff"))
            gradient.setColorAt(1.0, QtGui.QColor("#dcf7b5"))
            painter.setBrush(QtGui.QBrush(gradient))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(rect)

class OptionWithExtra(QtWidgets.QWidget):
    """左侧内容，右侧圆环，支持附加栏"""
    def __init__(self, text, extra_label="", has_extra=False, parent=None):
        super().__init__(parent)
        self.has_extra = has_extra
        self.extra_label = extra_label

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 主行
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        self.label = QtWidgets.QLabel(text)
        # self.label.setFont(QtGui.QFont("微软雅黑", 12))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setMinimumWidth(80)
        self.label.setStyleSheet(TRANSPARENT_BK)
        self.circle = CircleButton()
        self.circle.clicked.connect(self.on_circle_clicked)
        row.addWidget(self.label)
        row.addStretch(1)
        row.addWidget(self.circle)
        self.main_layout.addLayout(row)

        # 附加栏
        self.extra_widget = QtWidgets.QWidget()
        extra_layout = QtWidgets.QHBoxLayout(self.extra_widget)
        extra_layout.setContentsMargins(20, 4, 10, 4)
        self.extra_widget.setStyleSheet(TRANSPARENT_BK)
        extra_layout.setSpacing(8)
        self.extra_label_widget = QtWidgets.QLabel(self.extra_label)
        self.extra_label_widget.setFont(QtGui.QFont(self.extra_label_widget.font().family(), 10))
        self.extra_line = QtWidgets.QFrame()
        self.extra_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.extra_line.setFixedHeight(1)
        self.extra_input = QtWidgets.QLineEdit()
        self.extra_input.setPlaceholderText("input")
        self.extra_input.setAlignment(QtCore.Qt.AlignCenter)
        self.extra_input.setFixedWidth(80)
        extra_layout.addWidget(self.extra_label_widget)
        extra_layout.addWidget(self.extra_line, 1)
        extra_layout.addWidget(self.extra_input)
        self.main_layout.addWidget(self.extra_widget)
        self.extra_widget.setVisible(False)
        # 初始化时根据勾选状态显示附加栏
        if self.has_extra:
            self.extra_widget.setVisible(self.circle.isChecked())

    def on_circle_clicked(self):
        if self.has_extra:
            self.extra_widget.setVisible(self.circle.isChecked())
        else:
            self.extra_widget.setVisible(False)

    def isChecked(self):
        return self.circle.isChecked()

    def extraValue(self):
        return self.extra_input.text() if self.has_extra else None


class SettingsButton(QtWidgets.QLabel):
    def __init__(self, svg_path, size=32, parent=None):
        super().__init__(parent)
        self._rotation = 0
        self._size = size
        self._svg_path = svg_path
        self._svg_renderer = QtSvg.QSvgRenderer(svg_path)
        self.setFixedSize(size, size)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setStyleSheet(TRANSPARENT_BK)
        self._update_pixmap()
        self.installEventFilter(self)

    @QtCore.Property(int)
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, angle):
        self._rotation = angle
        self._update_pixmap()

    def _update_pixmap(self):
        # 渲染SVG到pixmap
        pixmap = QtGui.QPixmap(self._size, self._size)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # 旋转中心点
        painter.translate(self._size / 2, self._size / 2)
        painter.rotate(self._rotation)
        painter.translate(-self._size / 2, -self._size / 2)
        self._svg_renderer.render(painter)
        painter.end()
        self.setPixmap(pixmap)

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QtCore.QEvent.Enter:
                self._start_rotation_animation(self._rotation, 120)
            elif event.type() == QtCore.QEvent.Leave:
                self._start_rotation_animation(self._rotation, 0)
        return super().eventFilter(obj, event)

    def _start_rotation_animation(self, start_angle, end_angle):
        self._animation = QtCore.QPropertyAnimation(self, b"rotation")
        self._animation.setDuration(400)
        self._animation.setStartValue(start_angle)
        self._animation.setEndValue(end_angle)
        self._animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self._animation.start()


class SettingsPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 400)
        self.content = QtWidgets.QWidget(self)
        self.content.setGeometry(0, 0, 320, 320)
        self.content.setStyleSheet("""
            QWidget {
                border: none;
                border-radius: 40px;
                background: qradialgradient(
                    cx:0.2, cy:-0.3, radius:1.2,
                    fx:0.2, fy:-0.3,
                    stop:0 #232946,
                    stop:0.3 #393e5c,
                    stop:0.7 #22223b,
                    stop:1 #181926
                );
            }
        """)
        self.setting_path = writable_path("data/config/settings.json")
        settings = load_settings(self.setting_path)
        layout = QtWidgets.QVBoxLayout(self.content)
        layout.setSpacing(18)
        title = GradientLabel("SETTING", self.content)
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont(title.font().family(), 16, QtGui.QFont.Bold))
        layout.addWidget(title)
        layout.addSpacing(10)
        # 可在此添加更多设置项
        close_btn = GradientButton("CLOSE", self.content)
        close_btn.setFixedWidth(160)
        close_btn.clicked.connect(lambda: save_settings(self.setting_path, opt1, opt2))
        close_btn.clicked.connect(self.fade_out)
        # 在你的面板里添加
        opt1 = OptionWithExtra("Log")
        opt2 = OptionWithExtra("ForceSpd", "Pace", has_extra=True)
        opt1.circle.setChecked(settings.get("Log", False))
        opt2.circle.setChecked(settings.get("ForceSpd", False))
        opt2.on_circle_clicked() 
        opt2.extra_input.setText(str(settings.get("Pace", "")))
        layout.addWidget(opt1)
        layout.addSpacing(10)
        layout.addWidget(opt2)
        layout.addStretch(1)
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignCenter)
        layout.addSpacing(10)

        # 初始透明
        self.setWindowOpacity(0.0)

    def fade_in(self):
        self.show()
        self.raise_()
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self.anim.start()

    def fade_out(self):
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self.anim.finished.connect(self.close)
        self.anim.start()
