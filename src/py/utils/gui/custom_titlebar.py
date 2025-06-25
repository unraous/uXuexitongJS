from PySide6 import QtCore, QtWidgets, QtGui
from gradient_label import GradientLabel
from animated_button import AnimatedButton

class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet("background: transparent;")
        self._mouse_pos = None

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
            btn.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
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
        main_layout.addSpacerItem(QtWidgets.QSpacerItem(btn_total_width, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))

        main_layout.addWidget(self.title, alignment=QtCore.Qt.AlignCenter)
        main_layout.addStretch(1)  # 右弹性

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(0)
        btn_layout.addWidget(self.btn_min)
        btn_layout.addWidget(self.btn_close)
        main_layout.addLayout(btn_layout)
        print('')

    def _on_minimize(self):
        if self.window():
            self.window().showMinimized()

    def _on_close(self):
        if self.window():
            self.window().close()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._mouse_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._mouse_pos and event.buttons() & QtCore.Qt.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._mouse_pos)

    def mouseReleaseEvent(self, event):
        self._mouse_pos = None