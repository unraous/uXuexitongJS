import os
import sys
import datetime
from PySide6 import QtCore, QtWidgets, QtGui
from custom_titlebar import CustomTitleBar
from gradient_label import GradientLabel
from logo_label import LogoLabel
from gradient_clock_label import GradientClockLabel
from sidebar import SidebarWidget
from main_action_panel import MainActionPanel
import webbrowser

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
class CyberWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self._first_show = True
        self._minimizing = False
        self._is_closing = False
        self.resize(900, 600)

        # 主内容区
        self.bg = QtWidgets.QWidget(self)
        self.bg.setStyleSheet("""
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

        # 主内容区布局
        bg_layout = QtWidgets.QVBoxLayout(self.bg)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)

        # 顶部 titlebar
        self.titlebar = CustomTitleBar(self)
        bg_layout.addWidget(self.titlebar)

        # 内容区（用 QHBoxLayout 实现靠右）
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setContentsMargins(30, 70, 0, 0)
        content_layout.setSpacing(0)

        # 左侧表单
        config_path = os.path.join(os.getcwd(), "config.py")
        self.form_widget = SidebarWidget(
            config_path=config_path,
            parent=self.bg
        )
        self.form_widget.setFixedWidth(400)
        self.form_widget.setStyleSheet("""
            background: #f5f6fa;
            border-top-left-radius: 30px;
            border-bottom-left-radius: 30px;
            border: none;
        """)
        self.form_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.form_widget)
        self.form_widget.setGraphicsEffect(self.form_opacity_effect)
        self.form_opacity_effect.setOpacity(0.0)

        # 右侧主操作面板
        self.action_panel = MainActionPanel(self.bg)
        self.action_panel.setContentsMargins(0, 0, 60, 220)

        # 新增：右侧主操作面板透明度特效
        self.action_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.action_panel)
        self.action_panel.setGraphicsEffect(self.action_opacity_effect)
        self.action_opacity_effect.setOpacity(0.0)

        # 水平布局：左侧表单 | 拉伸 | 右侧操作面板
        content_layout.addWidget(self.form_widget)
        content_layout.addStretch()
        content_layout.addWidget(self.action_panel)

        bg_layout.addLayout(content_layout)

        # 主窗口布局
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.bg)

        # 添加logo容器
        self.logo_container = QtWidgets.QWidget(self.bg)
        self.logo_container.setAttribute(QtCore.Qt.WA_TranslucentBackground)  
        self.logo_container.setFixedSize(135, 135)

        # 给容器加透明度特效
        self.logo_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.logo_container)
        self.logo_container.setGraphicsEffect(self.logo_opacity_effect)
        self.logo_opacity_effect.setOpacity(0.0)

        # 添加logo本体
        logo_path = resource_path(os.path.join("data", "static", "png", "logo_gradient.png"))
        self.logo = LogoLabel(logo_path, self.logo_container)
        self.logo.move(0, 0)
        self.logo.show()
        self.logo_container.hide()  # 初始隐藏

        # 动画用的标题
        self.animated_title = GradientLabel("uXueXiTong", self.bg)
        self.animated_title.setFixedHeight(40)
        font_metrics = QtGui.QFontMetrics(self.animated_title.font())
        text_width = font_metrics.horizontalAdvance("Cyberpunk Window")
        self.animated_title.setFixedWidth(text_width + 20)  # 适当加点padding
        self.animated_title.setAlignment(QtCore.Qt.AlignCenter)
        self.animated_title.setStyleSheet("background: transparent;")
        self.animated_title.hide()

        # 添加渐变时钟（初始隐藏）
        self.clock_label = GradientClockLabel(self.bg)
        self.clock_label.setGeometry(20, 40, 320, 80)
        self.clock_label.hide()  # 先隐藏

        # 右下角版本号和作者（用自定义 GradientLabel）
        self.version_label = GradientLabel("v1.2.4  by Unraous", self.bg)
        self.version_label.setStyleSheet("""
            font-size: 13px;
            background: transparent;
        """)
        self.version_label.adjustSize()

        # GitHub 图标（放大、无背景、偏左）
        github_icon_path = resource_path(os.path.join("data", "static", "svg", "github-mark.svg"))
        self.github_label = QtWidgets.QLabel(self.bg)
        pixmap = QtGui.QPixmap(github_icon_path)
        # 放大到32x32像素
        self.github_label.setPixmap(pixmap.scaled(32, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.github_label.setCursor(QtCore.Qt.PointingHandCursor)
        self.github_label.setStyleSheet("background: transparent;")  # 去掉背景
        self.github_label.adjustSize()

        # 点击打开 GitHub 链接
        def open_github(event):
            webbrowser.open("https://github.com/unraous/uXuexitongJS")
        self.github_label.mousePressEvent = open_github

        # 右下角布局
        spacing = 12  # 图标与文字间距
        total_width = self.version_label.width() + self.github_label.width() + spacing
        x = self.bg.width() - total_width - 48  # 偏左（数值越大越靠左）
        y = self.bg.height() - max(self.version_label.height(), self.github_label.height()) - 18
        self.github_label.move(x, y + 4)
        self.version_label.move(x + self.github_label.width() + spacing, y)
        self.github_label.raise_()
        self.version_label.raise_()

        # 保证窗口大小变化时位置也跟着变
        def update_version_label_pos():
            total_width = self.version_label.width() + self.github_label.width() + spacing
            x = self.bg.width() - total_width - 48
            y = self.bg.height() - max(self.version_label.height(), self.github_label.height()) - 18
            self.github_label.move(x, y + 4)
            self.version_label.move(x + self.github_label.width() + spacing, y)
        self.bg.resizeEvent = lambda event: (update_version_label_pos(), QtWidgets.QWidget.resizeEvent(self.bg, event))


    def showEvent(self, event):
        super().showEvent(event)
        self.setWindowOpacity(0.0)
        self._fadein = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self._fadein.setStartValue(0.0)
        self._fadein.setEndValue(1.0)
        self._fadein.setDuration(800)
        self._fadein.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self._fadein.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
        if not self._first_show:
            return
        self._first_show = False

        GROUP1_TIME = 2000
        GROUP2_TIME = 1000

        # 1. logo 动画
        # 计算中心坐标
        center_x = (self.bg.width() - self.logo_container.width()) // 2
        center_y = (self.bg.height() - self.logo_container.height()) // 2 - 55
        self.logo_container._base_y = center_y  # 你可以加这个属性用于动画
        self.logo_container.move(center_x, center_y + 60)
        self.logo_container.show()

        # yOffset 动画要加到 logo_container 上
        self.logo_container._y_offset = 0  # 初始化

        # 动画
        self.move_anim_logo = QtCore.QPropertyAnimation(self.logo_container, b"pos")
        self.move_anim_logo.setStartValue(QtCore.QPoint(center_x, center_y + 60))
        self.move_anim_logo.setEndValue(QtCore.QPoint(center_x, center_y))
        self.move_anim_logo.setDuration(GROUP1_TIME)
        self.move_anim_logo.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        # 透明度动画保持不变
        self.opacity_anim_logo = QtCore.QPropertyAnimation(self.logo_opacity_effect, b"opacity")
        self.opacity_anim_logo.setStartValue(0.0)
        self.opacity_anim_logo.setEndValue(1.0)
        self.opacity_anim_logo.setDuration(GROUP1_TIME)
        self.opacity_anim_logo.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        self.group_logo = QtCore.QParallelAnimationGroup(self)
        self.group_logo.addAnimation(self.move_anim_logo)
        self.group_logo.addAnimation(self.opacity_anim_logo)
        self.group_logo.start()
        

        # 2. 动画标题
        center_x2 = (self.bg.width() - self.animated_title.width()) // 2
        center_y2 = (self.bg.height() - self.animated_title.height()) // 2 + 30
        self.animated_title.move(center_x2, center_y2 + 75)
        self.animated_title.show()
        opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.animated_title)
        self.animated_title.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0.0)

        move_anim = QtCore.QPropertyAnimation(self.animated_title, b"pos")
        move_anim.setStartValue(QtCore.QPoint(center_x2, center_y2 + 75))
        move_anim.setEndValue(QtCore.QPoint(center_x2, center_y2))
        move_anim.setDuration(GROUP1_TIME)
        move_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        opacity_anim = QtCore.QPropertyAnimation(opacity_effect, b"opacity")
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setDuration(GROUP1_TIME)
        opacity_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        scale_anim = QtCore.QPropertyAnimation(self.animated_title, b"scale")
        scale_anim.setStartValue(1.0)
        scale_anim.setEndValue(1.25)  
        scale_anim.setDuration(GROUP1_TIME)
        scale_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)


        group1 = QtCore.QParallelAnimationGroup(self)
        group1.addAnimation(move_anim)
        group1.addAnimation(opacity_anim)
        group1.addAnimation(scale_anim)

        def start_move_to_title():
            # 1. 先让 logo 渐隐消失
            self.logo_fadeout = QtCore.QPropertyAnimation(self.logo_opacity_effect, b"opacity")
            self.logo_fadeout.setStartValue(1.0)
            self.logo_fadeout.setEndValue(0.0)
            self.logo_fadeout.setDuration(500)
            self.logo_fadeout.setEasingCurve(QtCore.QEasingCurve.InCubic)

            def after_logo_fadeout():
                # 2. logo消失后再执行 group2
                target_label = self.titlebar.title
                target_center_global = target_label.mapToGlobal(target_label.rect().center())
                target_center = self.bg.mapFromGlobal(target_center_global)
                animated_rect = self.animated_title.geometry()
                animated_half = QtCore.QPoint(animated_rect.width() // 2, animated_rect.height() // 2)
                target_pos = target_center - animated_half

                move2 = QtCore.QPropertyAnimation(self.animated_title, b"pos")
                move2.setStartValue(self.animated_title.pos())
                move2.setEndValue(target_pos)
                move2.setDuration(GROUP2_TIME)
                move2.setEasingCurve(QtCore.QEasingCurve.OutCubic)

                opacity2 = QtCore.QPropertyAnimation(opacity_effect, b"opacity")
                opacity2.setStartValue(1.0)
                opacity2.setEndValue(1.0)
                opacity2.setDuration(GROUP2_TIME)

                scale_anim2 = QtCore.QPropertyAnimation(self.animated_title, b"scale")
                scale_anim2.setStartValue(1.25)
                scale_anim2.setEndValue(1)
                scale_anim2.setDuration(GROUP2_TIME)
                scale_anim2.setEasingCurve(QtCore.QEasingCurve.OutCubic)

                group2 = QtCore.QParallelAnimationGroup(self)
                group2.addAnimation(move2)
                group2.addAnimation(opacity2)
                group2.addAnimation(scale_anim2)
                def finish():
                    self.animated_title.hide()
                    self.titlebar.title.setText("uXueXiTong")
                    self.clock_label.setScale(2)
                    label_width = self.clock_label.width()
                    label_height = self.clock_label.height()
                    parent_width = self.bg.width()
                    parent_height = self.bg.height()
                    x = (parent_width - label_width) // 2
                    y = parent_height - label_height - 30
                    self.clock_label.setGeometry(x, y, label_width, label_height)
                    self.clock_label.show()
                    self.clock_label.fade_in()
                    self.form_widget.setVisible(True)
                    self.anim_form = QtCore.QPropertyAnimation(self.form_opacity_effect, b"opacity")
                    self.anim_form.setStartValue(0.0)
                    self.anim_form.setEndValue(1.0)
                    self.anim_form.setDuration(800)
                    self.anim_form.setEasingCurve(QtCore.QEasingCurve.OutCubic)
                    self.anim_form.start()

                    # 右侧主操作面板淡入动画
                    self.action_panel.setVisible(True)
                    self.anim_action = QtCore.QPropertyAnimation(self.action_opacity_effect, b"opacity")
                    self.anim_action.setStartValue(0.0)
                    self.anim_action.setEndValue(1.0)
                    self.anim_action.setDuration(800)
                    self.anim_action.setEasingCurve(QtCore.QEasingCurve.OutCubic)
                    self.anim_action.start()

                    # 动画结束后移除所有透明度特效
                    def remove_all_effects():
                        self.action_panel.setGraphicsEffect(None)
                        self.form_widget.setGraphicsEffect(None)
                        self.clock_label.setGraphicsEffect(None)
                    self.anim_action.finished.connect(remove_all_effects)

                group2.finished.connect(finish)
                group2.start()

            self.logo_fadeout.finished.connect(after_logo_fadeout)
            self.logo_fadeout.start()

        group1.finished.connect(start_move_to_title)
        group1.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 动画结束后才需要调整
        if self.clock_label.isVisible():
            scale = 2  # 或你实际用的缩放
            self.clock_label.setScale(scale)
            font_metrics = self.clock_label.fontMetrics()
            text_width = font_metrics.horizontalAdvance(self.clock_label.text())
            text_height = font_metrics.height()
            label_width = int(text_width * scale) + 20
            label_height = int(text_height * scale) + 10
            parent_width = self.bg.width()
            parent_height = self.bg.height()
            x = (parent_width - label_width) // 2
            y = parent_height - label_height - 30
            self.clock_label.setGeometry(x, y, label_width, label_height)
        
    def closeEvent(self, event):
        if self._is_closing:
            event.accept()
            return

        self._is_closing = True
        try:
            if hasattr(self, "action_panel") and hasattr(self.action_panel, "driver") and self.action_panel.driver:
                if self.action_panel.log_option:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_path = writable_path(f"data/log/js/js_{timestamp}.log")
                    with open(log_path, "w", encoding="utf-8") as f:
                        for entry in self.action_panel.log_entries:
                            f.write(str(entry) + "\n")
                self.action_panel.driver.quit()
        except Exception as e:
            print(f"关闭浏览器异常: {e}")
        # 下沉动画
        move_anim = QtCore.QPropertyAnimation(self, b"pos")
        start_pos = self.pos()
        end_pos = QtCore.QPoint(start_pos.x() - 640, start_pos.y()) 
        move_anim.setStartValue(start_pos)
        move_anim.setEndValue(end_pos)
        move_anim.setDuration(800)
        move_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        # 透明度动画
        fade_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)
        fade_anim.setDuration(800)
        fade_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        group = QtCore.QParallelAnimationGroup(self)
        group.addAnimation(move_anim)
        group.addAnimation(fade_anim)

        def on_finished():
            self.close()

        group.finished.connect(on_finished)
        group.start()
        if self.action_panel.settings_panel:
                    self.action_panel.settings_panel.fade_out()
        event.ignore()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized and not self._minimizing:
                # 只在用户主动最小化时播放动画
                self._minimizing = True
                self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized)
                self._fadeout_min = QtCore.QPropertyAnimation(self, b"windowOpacity")
                self._fadeout_min.setStartValue(1.0)
                self._fadeout_min.setEndValue(0.0)
                self._fadeout_min.setDuration(400)
                self._fadeout_min.setEasingCurve(QtCore.QEasingCurve.OutCubic)
                def do_minimize():
                    self.setWindowState(QtCore.Qt.WindowMinimized)
                    self.setWindowOpacity(1.0)
                    self._minimizing = False
                self._fadeout_min.finished.connect(do_minimize)
                self._fadeout_min.start()
                if self.action_panel.settings_panel:
                    self.action_panel.settings_panel.fade_out()


