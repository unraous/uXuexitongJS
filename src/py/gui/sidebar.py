"""左侧OPENAI参数配置模块"""
import json
import os

from typing import Optional

from PySide6 import QtWidgets, QtCore, QtGui

from .gradient_label import GradientLabel
from .gradient_button import GradientButton 


class ExpandingLineEdit(QtWidgets.QLineEdit):
    """可扩展的单行文本框类"""
    def __init__(self, text="", min_width=300, parent=None):
        super().__init__(text, parent)
        self._min_width = min_width
        self.setMinimumWidth(self._min_width)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.setText(text)
        self.setCursorPosition(0)  # 光标在最左侧


class AcrylicCover(QtWidgets.QWidget):
    """矩形密钥遮罩类"""
    def __init__(self, parent: ExpandingLineEdit):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self._opacity = 1.0
        self.anim = QtCore.QPropertyAnimation(self, b"opacity", self)
        self.anim.setDuration(400)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

    def get_opacity(self):
        """安全获取透明度"""
        return self._opacity if 0.0 <= self._opacity <= 1.0 else 1.0

    def set_opacity(self, value):
        """安全设置透明度并刷新渲染"""
        self._opacity = value if 0.0 <= value <= 1.0 else self._opacity
        self.update()

    opacity = QtCore.Property(float, get_opacity, set_opacity)

    # 为保证Qt的特定事件命名规范，enterEvent等函数名格式不严格符合PEP8
    def enterEvent(self, event): # pylint: disable=invalid-name
        """鼠标移入事件"""
        self.anim.stop()
        self.anim.setEndValue(0.0)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event): # pylint: disable=invalid-name
        """鼠标移出事件"""
        self.anim.stop()
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().leaveEvent(event)

    def resizeEvent(self, event): # pylint: disable=invalid-name
        """父控件大小变化时，调整自己大小(尽在被初始化时调用)"""

        parent_widget: Optional[QtWidgets.QWidget] = self.parentWidget()
        if isinstance(parent_widget, QtWidgets.QWidget):
            self.setGeometry(0, 0, parent_widget.width(), parent_widget.height())
        super().resizeEvent(event)

    def paintEvent(self, _: QtGui.QPaintEvent): # pylint: disable=invalid-name
        """渲染事件"""
        
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
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
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRect(rect)


class SidebarWidget(QtWidgets.QWidget):
    """左侧配置面板主类"""
    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.config_path = config_path
        self.setFixedWidth(400)
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
        title.setFont(QtGui.QFont(title.font().family(), 18, QtGui.QFont.Weight.Bold))
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 表单区用 QGridLayout
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(16)
        self.fields = {}

        api_label = GradientLabel("API_KEY", self)
        api_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
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
        baseurl_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        baseurl_label.setMinimumWidth(170)
        baseurl_edit = ExpandingLineEdit(config.get("BASE_URL", ""), min_width=180)
        grid.addWidget(baseurl_label, 1, 0)
        grid.addWidget(baseurl_edit, 1, 1)
        self.fields["BASE_URL"] = baseurl_edit

        # MODEL
        model_label = GradientLabel("MODEL", self)
        model_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
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
        # 从JSON文件加载配置
        config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                # 处理JSON解析错误
                print(f"配置文件 {self.config_path} 格式错误")
        return config

    def save_config(self):
        # 保存到JSON文件
        config = {
            "API_KEY": self.fields["API_KEY"].text(),
            "BASE_URL": self.fields["BASE_URL"].text(),
            "MODEL": self.fields["MODEL"].text()
        }
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)  # 使用缩进格式化JSON
