"""主操作面板，包含进度条和按钮等控件"""
import time
import random
import threading
import os
import json
import asyncio

import websockets

from PySide6 import QtWidgets, QtCore, QtGui
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from src.auto_answer import answer_questions
from src.utils import resource_path, writable_path

from .gradient_button import GradientButton
from .gradient_label import GradientLabel
from .setting import SettingsButton, SettingsPanel, load_settings


class MainActionPanel(QtWidgets.QWidget):
    """主操作面板类，包含进度条和按钮等控件"""
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
        self.progress_bar.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.progress_bar.setRange(0, 300)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(12)
        self.progress_bar.setFixedHeight(260)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
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
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QtGui.QFont(title_label.font().family(), 18, QtGui.QFont.Weight.Bold))
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
                label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
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
        self.js_path = resource_path("src/js/main.js")  # 只读资源仍用 resource_path
        self.ques_path = writable_path("data/temp/html/question.html")
        self.ans_path = writable_path("data/temp/json/answer_simplified.json")
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
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
        except FileNotFoundError as e:
            print("加载 main.js 失败：", e)
            raise

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

                            answer_questions()

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
                    except Exception as e:
                        print("收到异常消息：", e)

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
        self.anim.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
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
