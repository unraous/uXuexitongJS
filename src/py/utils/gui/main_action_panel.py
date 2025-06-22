from PySide6 import QtWidgets, QtCore, QtGui, QtSvg
from gradient_button import GradientButton
from gradient_label import GradientLabel

import threading
import asyncio
import websockets
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from selenium.webdriver.common.action_chains import ActionChains

import time
import random
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_answer.html_2_answer import html_to_answer

def resource_path(relative_path):
    """兼容PyInstaller和源码运行的资源路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    # 项目根目录
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), relative_path)

def writable_path(relative_path):
    """返回当前工作目录下的可写路径，并自动创建父目录"""
    abs_path = os.path.join(os.getcwd(), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path

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
        self.label.setStyleSheet("background: transparent;")
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
        self.extra_widget.setStyleSheet("background: transparent;")
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
        self.setStyleSheet("background: transparent;")
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


class MainActionPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(400)
        self.setStyleSheet("""
            background: #f5f6fa;
            border-top-right-radius: 30px;
            border-bottom-right-radius: 30px;
            border: none;
        """)

        # 主横向布局
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # 进度条
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setOrientation(QtCore.Qt.Vertical)
        self.progress_bar.setRange(0, 300)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(12)
        self.progress_bar.setFixedHeight(260)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: transparent;
                border-radius: 6px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #89ddff, stop:0.5 #dcf7b5, stop:1 #f9b7a4
                );
                border-radius: 6px;
            }
        """)
        self.progress_bar.setInvertedAppearance(True)
        main_layout.addWidget(self.progress_bar)

        # 按钮竖直布局
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch(1)

        title_label = GradientLabel("Control Panel", self)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setFont(QtGui.QFont(title_label.font().family(), 18, QtGui.QFont.Bold))
        title_label.setMinimumHeight(40)
        btn_layout.addWidget(title_label)

        self.buttons = []
        self.btn_texts = [
            "LAUNCH",
            "INJECT",
            "AUTO CLICK"
        ]
        self.label_texts = [
            "请登陆并到达课程界面",
            "请关闭浏览器弹窗"
        ]
        for i, text in enumerate(self.btn_texts):
            btn = GradientButton(text, self)
            btn.setFixedHeight(40)
            btn.setFixedWidth(200)
            btn.clicked.connect(lambda _, idx=i: self.on_step_button_clicked(idx))
            self.buttons.append(btn)
            btn_layout.addWidget(btn)
            if i < len(self.btn_texts) - 1:
                label = GradientLabel(self.label_texts[i], self)
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setFont(QtGui.QFont("微软雅黑", 13))
                label.setMinimumHeight(24)
                btn_layout.addWidget(label)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout, 1)

        # 业务相关变量
        self.driver = None
        self.keep_alive_thread = None
        self.ws_thread = None
        self.js_code = ""
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.js_path = resource_path("js/main.js")  # 只读资源仍用 resource_path
        self.test_path = writable_path("data/temp/html/test.html")
        self.ans_path = writable_path("data/temp/json/answer_simplified.json")
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        self.setting_path = writable_path("data/config/settings.json")
        self.log_option = False
        self.log_entries = []
        self.load_js_code()
        self.start_ws_server()

        settings_icon_path = resource_path(os.path.join("data", "static", "svg", "gear-solid-gradient.svg"))
        self.settings_button = SettingsButton(settings_icon_path, size=32, parent=self)
        self.settings_button.move(self.width() - self.settings_button.width() - 50, 20)
        self.settings_button.mousePressEvent = self.show_settings_panel  # 添加点击事件

        self.settings_panel = None  # 用于后续引用

    def load_js_code(self):
        try:
            with open(self.js_path, 'r', encoding='utf-8') as f:
                self.js_code = f.read()
        except Exception as e:
            print("加载 main.js 失败：", e)
            self.js_code = ""

    def start_ws_server(self):
        def ws_thread_func():
            async def handler(websocket):
                async for msg in websocket:
                    try:
                        data = json.loads(msg)
                        if data.get("type") == "testDocHtml":
                            html_str = data.get("html", "")
                            print("收到HTML内容，长度：", len(html_str))
                            try:
                                with open(self.test_path, "w", encoding="utf-8") as f:
                                    f.write(html_str)
                                print("HTML已保存到 test.html")
                            except Exception as e:
                                print(f"无法写入 test.html：{e}")
                                await websocket.send(json.dumps({"error": f"无法写入 test.html：{e}"}))
                                return

                            html_to_answer(self.test_path)

                            try:
                                with open(self.ans_path, "r", encoding="utf-8") as f:
                                    ans_json = f.read()
                            except Exception as e:
                                print(f"无法读取答案文件：{e}")
                                await websocket.send(json.dumps({"error": f"无法读取答案文件：{e}"}))
                                return
                            await websocket.send(ans_json)
                        else:
                            print("收到非HTML消息：", data)
                    except Exception:
                        print("收到异常消息")

            async def main():
                async with websockets.serve(handler, "localhost", 8765):
                    print("WebSocket服务器已启动 ws://localhost:8765")
                    await asyncio.Future()
            asyncio.run(main())
        self.ws_thread = threading.Thread(target=ws_thread_func, daemon=True)
        self.ws_thread.start()

    def on_step_button_clicked(self, idx):
        if idx == 0:
            self.launch_browser()
        elif idx == 1:
            self.inject_script()
        elif idx == 2:
            self.start_keep_alive()
        self.set_step(idx + 1)

    def launch_browser(self):
        options = Options()
        options.set_preference("general.useragent.override", self.user_agent)
        # 启用 WebDriver BiDi
        options.set_capability("webSocketUrl", True)
        browser_tried = []
        try:
            self.driver = webdriver.Firefox(options=options)
            print("已成功启动 Firefox 浏览器")
        except Exception as e:
            print("Firefox 启动失败：", e)
            browser_tried.append("Firefox")
            try:
                from selenium.webdriver.edge.options import Options as EdgeOptions
                edge_options = EdgeOptions()
                edge_options.use_chromium = True
                edge_options.add_argument(f"user-agent={self.user_agent}")
                edge_options.set_capability("webSocketUrl", True)  # 启用 BiDi

                self.driver = webdriver.Edge(options=edge_options)
                print("已成功启动 Edge 浏览器")
            except Exception as e2:
                print("Edge 启动失败：", e2)
                browser_tried.append("Edge")
                try:
                    from selenium.webdriver.chrome.options import Options as ChromeOptions
                    chrome_options = ChromeOptions()
                    chrome_options.add_argument(f"user-agent={self.user_agent}")
                    chrome_options.set_capability("webSocketUrl", True)  # 启用 BiDi
                    self.driver = webdriver.Chrome(options=chrome_options)
                    print("已成功启动 Chrome 浏览器")
                except Exception as e3:
                    print("Chrome 启动失败：", e3)
                    browser_tried.append("Chrome")
                    QtWidgets.QMessageBox.critical(self, "错误", f"所有浏览器均启动失败，已尝试：{browser_tried}")
                    return

        if self.driver is None:
            QtWidgets.QMessageBox.critical(self, "错误", f"所有浏览器均启动失败，已尝试：{browser_tried}")
            return

        self.driver.get("https://mooc1.chaoxing.com")  # 先访问主域，才能设置 Cookie

        # 切换到最后一个窗口
        

   

    def inject_script(self):
        if not self.driver:
            QtWidgets.QMessageBox.warning(self, "警告", "请先启动浏览器并登录！")
            return
        try:
            time.sleep(2)
            handles = self.driver.window_handles
            self.driver.switch_to.window(handles[-1])

            # 1. 读取设置
            settings = load_settings(self.setting_path)
            self.log_option = settings.get("Log", True)
            

            if self.log_option:
                print("日志记录已启用")
                self.driver.script.add_console_message_handler(self.log_entries.append)

            else:
                print("日志记录已禁用")


            force_spd_val = settings.get("ForceSpd", True)
            pace_val = settings.get("Pace", 5)

            # 2. 构造注入的 JS 变量
            js_vars = f"""
                DEFAULT_FORCE_SPD = {str(force_spd_val).lower()};
                DEFAULT_PACE = {pace_val};
            """

            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            self.driver.execute_script(
                "DEFAULT_TEST_OPTION = 1;\n" + js_vars + "\n" + self.js_code
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"脚本注入失败：{e}")

    def start_keep_alive(self):
        if not self.driver:
            QtWidgets.QMessageBox.warning(self, "警告", "请先启动浏览器！")
            return
        def move_mouse():
            while True:
                try:
                    x = random.randint(100, 500)
                    y = random.randint(100, 500)
                    ActionChains(self.driver).move_by_offset(x, y).perform()
                    ActionChains(self.driver).move_by_offset(-x, -y).perform()
                except Exception as e:
                    print(f"鼠标移动异常: {e}")
                    break
                time.sleep(60)
        self.keep_alive_thread = threading.Thread(target=move_mouse, daemon=True)
        self.keep_alive_thread.start()
        # QtWidgets.QMessageBox.information(self, "提示", "防挂机已开启，脚本将持续运行，直到你手动关闭浏览器。")

    # 进度条和按钮动画等原有代码不变
    def set_step(self, step_idx):
        start_value = self.progress_bar.value()
        end_value = step_idx * 100
        self._progress_anim_value = start_value
        self.anim = QtCore.QPropertyAnimation(self, b"_progress_anim_value", self)
        self.anim.setStartValue(start_value)
        self.anim.setEndValue(end_value)
        self.anim.setDuration(800)
        self.anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.anim.start()
        for i, btn in enumerate(self.buttons):
            if i < step_idx - 1:
                btn.setText(f" complete ")
                btn.setEnabled(False)
            elif i == step_idx - 1:
                self.animate_button_text_change(btn, f" complete ", disable_after=True)
            else:
                btn.setText(self.btn_texts[i])
                btn.setEnabled(i == step_idx)

    @QtCore.Property(float)
    def _progress_anim_value(self):
        return getattr(self, "__progress_anim_value", 0)

    @_progress_anim_value.setter
    def _progress_anim_value(self, value):
        self.progress_bar.setValue(int(round(value)))

    def animate_button_text_change(self, btn, new_text, disable_after=False):
        if hasattr(btn, "start_swap_animation"):
            btn.start_swap_animation()
        effect = btn.graphicsEffect()
        if not isinstance(effect, QtWidgets.QGraphicsOpacityEffect):
            effect = QtWidgets.QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(effect)
        effect.setOpacity(1.0)
        anim = QtCore.QPropertyAnimation(effect, b"opacity", btn)
        anim.setDuration(400)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)

        def on_fade_out():
            btn.setText(new_text)
            if hasattr(btn, "set_swapped"):
                btn.set_swapped(True)
            anim2 = QtCore.QPropertyAnimation(effect, b"opacity", btn)
            anim2.setDuration(400)
            anim2.setStartValue(0.0)
            anim2.setEndValue(1.0)
            def on_fade_in_finished():
                btn.setGraphicsEffect(None)
                if disable_after:
                    btn.setEnabled(False)
                btn._anim = None
                btn._anim2 = None
                if hasattr(btn, "end_swap_animation"):
                    btn.end_swap_animation()
            anim2.finished.connect(on_fade_in_finished)
            anim2.start()
            btn._anim2 = anim2

        anim.finished.connect(on_fade_out)
        anim.start()
        btn._anim = anim

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.settings_button.move(self.width() - self.settings_button.width() - 50, 20)

    def show_settings_panel(self, event):
        if self.settings_panel is None or not self.settings_panel.isVisible():
            self.settings_panel = SettingsPanel(self)
            # 获取主面板在屏幕上的左上角坐标
            global_pos = self.mapToGlobal(QtCore.QPoint(0, 0))
            # 计算设置面板居中显示的坐标
            x = global_pos.x() + 40
            y = global_pos.y()
            self.settings_panel.move(x, y)
            self.settings_panel.fade_in()
        event.accept()