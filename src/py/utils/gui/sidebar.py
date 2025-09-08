from PySide6 import QtWidgets, QtCore, QtGui
from src.py.utils.gui.gradient_label import GradientLabel
from src.py.utils.gui.gradient_button import GradientButton 
import importlib.util
import os



class AcrylicCover(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self._opacity = 1.0
        self.anim = QtCore.QPropertyAnimation(self, b"opacity", self)
        self.anim.setDuration(400)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def getOpacity(self):
        return self._opacity

    def setOpacity(self, value):
        self._opacity = value
        self.update()

    opacity = QtCore.Property(float, getOpacity, setOpacity)

    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setEndValue(0.0)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().leaveEvent(event)

    def resizeEvent(self, event):
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setOpacity(self._opacity)
        rect = self.rect()

        # 渐变色，仿照你的qss
        grad = QtGui.QRadialGradient(
            rect.width() * 0.2, rect.height() * -0.3, rect.width() * 1.2,
            rect.width() * 0.2, rect.height() * -0.3
        )
        grad.setColorAt(0, QtGui.QColor("#232946"))
        grad.setColorAt(0.3, QtGui.QColor("#393e5c"))
        grad.setColorAt(0.7, QtGui.QColor("#22223b"))
        grad.setColorAt(1, QtGui.QColor("#181926"))

        painter.setBrush(grad)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(rect)  # 直接画矩形



class ExpandingLineEdit(QtWidgets.QLineEdit):
    def __init__(self, text="", min_width=300, parent=None):
        super().__init__(text, parent)
        self._min_width = min_width
        self.setMinimumWidth(self._min_width)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setText(text)
        self.setCursorPosition(0)  # 光标在最左侧


    def focusInEvent(self, event):
        super().focusInEvent(event)
        # 不再动态调整宽度

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        # 不再动态调整宽度

class SidebarWidget(QtWidgets.QWidget):
    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.config_path = config_path
        self.setFixedWidth(400)  # ← 这里设置了600，和主窗口/右侧面板宽度要协调
        self.setStyleSheet("""
            background: transparent;
            border-top-left-radius: 30px;
            border-bottom-left-radius: 30px;
        """)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        config = self.load_config()

        # 标题
        title = GradientLabel("OPENAI_CONFIG", self)
        title.setFixedHeight(40)
        title.setFont(QtGui.QFont(title.font().family(), 18, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        # 表单区用 QGridLayout
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(16)
        self.fields = {}

        api_label = GradientLabel("API_KEY", self)
        api_label.setAlignment(QtCore.Qt.AlignCenter)
        api_label.setMinimumWidth(170)
        api_edit = ExpandingLineEdit(config.get("API_KEY", ""), min_width=180)
        grid.addWidget(api_label, 0, 0)
        grid.addWidget(api_edit, 0, 1)
        self.fields["API_KEY"] = api_edit

        # 添加亚克力遮罩
        self.api_acrylic = AcrylicCover(api_edit)
        self.api_acrylic.setGeometry( 0, 0, api_edit.width(), api_edit.height())  # 更大
        self.api_acrylic.raise_()
        api_edit.installEventFilter(self)


        # BASE_URL
        baseurl_label = GradientLabel("BASE_URL", self)
        baseurl_label.setAlignment(QtCore.Qt.AlignCenter)
        baseurl_label.setMinimumWidth(170)
        baseurl_edit = ExpandingLineEdit(config.get("BASE_URL", ""), min_width=180)
        grid.addWidget(baseurl_label, 1, 0)
        grid.addWidget(baseurl_edit, 1, 1)
        self.fields["BASE_URL"] = baseurl_edit

        # MODEL
        model_label = GradientLabel("MODEL", self)
        model_label.setAlignment(QtCore.Qt.AlignCenter)
        model_label.setMinimumWidth(170)
        model_edit = ExpandingLineEdit(config.get("MODEL", ""), min_width=180)
        grid.addWidget(model_label, 2, 0)
        grid.addWidget(model_edit, 2, 1)
        self.fields["MODEL"] = model_edit

        # 设置左侧label列宽度
        grid.setColumnMinimumWidth(0, 170)  # 保证label不会被截断
        grid.setColumnStretch(1, 1)         # 右侧文本框自适应拉伸

        layout.addLayout(grid)

        # 保存按钮
        btn_save = GradientButton("SAVE")  # 使用自定义按钮类
        btn_save.setFixedHeight(36)
        btn_save.clicked.connect(lambda: [self.save_config(), btn_save.show_tip("APPLY SUCCEED!")])
        layout.addWidget(btn_save)
        layout.addStretch(1)

    def load_config(self):
        # 动态加载 config.py 并返回字典
        config = {}
        if os.path.exists(self.config_path):
            spec = importlib.util.spec_from_file_location("config", self.config_path)
            cfg = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cfg)
            for key in dir(cfg):
                if key.isupper():
                    config[key] = getattr(cfg, key)
        return config

    def save_config(self):
        # 保存到 config.py
        lines = []
        lines.append(f'API_KEY = "{self.fields["API_KEY"].text()}"')
        lines.append(f'BASE_URL = "{self.fields["BASE_URL"].text()}"')
        lines.append(f'MODEL = "{self.fields["MODEL"].text()}"')
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
