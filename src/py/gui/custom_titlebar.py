"""自定义标题栏"""
from PySide6 import QtCore, QtWidgets, QtGui

from .gradient_label import GradientLabel
from .animated_button import AnimatedButton

class CustomTitleBar(QtWidgets.QWidget):
    """自定义标题栏类"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet("background: transparent;")
        self._mouse_pos: QtCore.QPoint

        # 先创建控件
        self.title = GradientLabel("", self)
        self.title.setFixedHeight(50)
        font_metrics = QtGui.QFontMetrics(self.title.font())
        self.title.setFixedWidth(font_metrics.horizontalAdvance("Cyberpunk Window") + 20)
        self.title.setStyleSheet("background: transparent;")

        self.btn_min = AnimatedButton("-", self)
        self.btn_min.setFixedSize(22, 22)
        self.btn_min.clicked.connect(self._on_minimize)

        self.btn_close = AnimatedButton("×", self)
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.clicked.connect(self._on_close)

        for btn in (self.btn_min, self.btn_close):
            btn.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #444a57;
                    border: none;
                    font-size: 16px;
                }
            """)

        # 主布局
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(24, 10, 24, 0)
        main_layout.setSpacing(0)

        main_layout.addStretch(1)  # 左弹性

        # 加一个 spacer，宽度为按钮总宽度的一半
        btn_total_width = self.btn_min.width() + self.btn_close.width()
        main_layout.addSpacerItem(QtWidgets.QSpacerItem(
            btn_total_width,
            0,
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Minimum
        ))

        main_layout.addWidget(self.title, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch(1)  # 右弹性

        # 按钮布局，靠右
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(0)
        btn_layout.addWidget(self.btn_min)
        btn_layout.addWidget(self.btn_close)
        main_layout.addLayout(btn_layout)

    def _on_minimize(self):
        if self.window():
            self.window().showMinimized()

    def _on_close(self):
        if self.window():
            self.window().close()

    # 为保证Qt的特定事件命名规范，mousePressEvent等函数名格式不严格符合PEP8
    def mousePressEvent(self, event): # pylint: disable=invalid-name
        """记录鼠标位置"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._mouse_pos: QtCore.QPoint = (
                event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event): # pylint: disable=invalid-name
        """拖动窗口"""
        if self._mouse_pos and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._mouse_pos)
