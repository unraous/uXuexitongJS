"""左侧OPENAI参数配置模块"""

from typing import Optional

from PySide6 import QtWidgets, QtCore, QtGui

from .gradient_label import GradientLabel
from .gradient_button import GradientButton

from src.py.utils.config import global_config, save_config


class ExpandingLineEdit(QtWidgets.QLineEdit):
    """可扩展的单行文本框类"""
    def __init__(self, text="", min_width=300, parent=None) -> None:
        super().__init__(text, parent)
        self._min_width = min_width
        self.setMinimumWidth(self._min_width)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.setText(text)
        self.setCursorPosition(0)  # 光标在最左侧


class AcrylicCover(QtWidgets.QWidget):
    """矩形密钥遮罩类"""
    def __init__(self, parent: ExpandingLineEdit) -> None:
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self._opacity = 1.0
        self.anim = QtCore.QPropertyAnimation(self, b"opacity", self)
        self.anim.setDuration(400)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

    def get_opacity(self) -> float:
        """读取透明度"""
        return self._opacity if 0.0 <= self._opacity <= 1.0 else 1.0

    def set_opacity(self, value: float) -> None:
        """写入透明度并刷新渲染"""
        self._opacity = value if 0.0 <= value <= 1.0 else self._opacity
        self.update()

    opacity = QtCore.Property(float, get_opacity, set_opacity)

    # 为保证Qt的特定事件命名规范，enterEvent等函数名格式不严格符合PEP8
    def enterEvent(self, event: QtGui.QEnterEvent) -> None: # pylint: disable=invalid-name
        """鼠标移入事件"""
        self.anim.stop()
        self.anim.setEndValue(0.0)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent) -> None: # pylint: disable=invalid-name
        """鼠标移出事件"""
        self.anim.stop()
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().leaveEvent(event)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None: # pylint: disable=invalid-name
        """父控件大小变化时，调整自己大小(仅在被初始化时调用)"""

        parent_widget: Optional[QtWidgets.QWidget] = self.parentWidget()
        if isinstance(parent_widget, QtWidgets.QWidget):
            self.setGeometry(0, 0, parent_widget.width(), parent_widget.height())
        super().resizeEvent(event)

    def paintEvent(self, _: QtGui.QPaintEvent) -> None: # pylint: disable=invalid-name
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
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedWidth(400)
        self.setStyleSheet("""
            background: transparent;
            border-top-left-radius: 30px;
            border-bottom-left-radius: 30px;
        """)
        layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        config: dict[str, str] = global_config.get("openai", {})

        # 标题
        title: GradientLabel = GradientLabel("OPENAI_CONFIG", self)
        title.setFixedHeight(40)
        title.setFont(QtGui.QFont(title.font().family(), 18, QtGui.QFont.Weight.Bold))
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 表单区用 QGridLayout
        grid: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(16)
        self.fields: dict[str, QtWidgets.QLineEdit] = {}

        api_label: GradientLabel = GradientLabel("API_KEY", self)
        api_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        api_label.setMinimumWidth(170)
        api_edit: ExpandingLineEdit = ExpandingLineEdit(
            config.get("API_KEY", ""),
            min_width=180
        )
        grid.addWidget(api_label, 0, 0)
        grid.addWidget(api_edit, 0, 1)
        self.fields["API_KEY"] = api_edit



        # BASE_URL
        baseurl_label: GradientLabel = GradientLabel("BASE_URL", self)
        baseurl_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        baseurl_label.setMinimumWidth(170)
        baseurl_edit: ExpandingLineEdit = ExpandingLineEdit(
            config.get("BASE_URL", ""),
            min_width=180
        )
        grid.addWidget(baseurl_label, 1, 0)
        grid.addWidget(baseurl_edit, 1, 1)
        self.fields["BASE_URL"] = baseurl_edit

        # MODEL
        model_label: GradientLabel = GradientLabel("MODEL", self)
        model_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        model_label.setMinimumWidth(170)
        model_edit: ExpandingLineEdit = ExpandingLineEdit(
            config.get("MODEL", ""),
            min_width=180
        )
        grid.addWidget(model_label, 2, 0)
        grid.addWidget(model_edit, 2, 1)
        self.fields["MODEL"] = model_edit

        # 添加亚克力遮罩
        self.api_acrylic: AcrylicCover = AcrylicCover(api_edit)
        self.api_acrylic.setGeometry( 0, 0, api_edit.width(), api_edit.height())  # 更大
        self.api_acrylic.raise_()
        api_edit.installEventFilter(self)
        # 设置左侧label列宽度
        grid.setColumnMinimumWidth(0, 170)
        grid.setColumnStretch(1, 1)

        layout.addLayout(grid)

        def update_config() -> None:
            """更新配置字典"""
            key: str
            line_edit: QtWidgets.QLineEdit
            for key, line_edit in self.fields.items():
                if isinstance(line_edit, QtWidgets.QLineEdit):
                    config[key.lower()] = line_edit.text()
            global_config["openai"] = config

        # 保存按钮
        btn_save = GradientButton("SAVE")  # 使用自定义按钮类
        btn_save.setFixedHeight(36)
        btn_save.clicked.connect(lambda: [update_config(), save_config(), btn_save.show_tip("APPLY SUCCEED!")])
        layout.addWidget(btn_save)
        layout.addStretch(1)

