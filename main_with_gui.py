"""GUI启动块"""

import datetime
import json
import logging
import os
import sys
from typing import Final

from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QIcon
from src.py.utils.gui.cyber_window import CyberWindow


PROJECT_ROOT: Final = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.join(PROJECT_ROOT, "src/py"))
sys.path.append(os.path.join(PROJECT_ROOT, "src/py/utils"))
sys.path.append(os.path.join(PROJECT_ROOT, "src/py/utils/gui"))
def resource_path(relative_path):
    """更安全地获取资源路径，适用于开发环境和打包环境"""
    base_path = getattr(sys, '_MEIPASS', None)
    if base_path and os.path.exists(base_path):
        return os.path.join(base_path, relative_path)
    # 退回到相对于脚本的路径
    return os.path.join(PROJECT_ROOT, relative_path)

font_path = resource_path("data/static/ttf/orbitron.ttf")


def writable_path(relative_path):
    """返回当前工作目录下的可写路径，并自动创建父目录"""
    abs_path = os.path.join(os.getcwd(), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path

def ensure_empty_file(path):
    """确保文件存在，如果不存在则创建一个空文件"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if path.endswith("settings.json") and "config" in path.replace("\\", "/"):
            default_settings = {
                "Log": False,
                "ForceSpd": False,
                "Pace": 5
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=2)

        print(f"已创建文件: {path}")
    else:
        print(f"文件已存在: {path}")

NEED_FILES = [
    "config.py",
    "data/temp/html/test.html",
    "data/temp/ttf/font-cxsecret.ttf",
    "data/temp/json/font_cxsecret_mapping.json",
    "data/temp/json/questions.json",
    "data/temp/json/questions_decoded.json",
    "data/temp/json/questions_answered.json",
    "data/temp/json/answer_simplified.json",
    "data/config/settings.json",
    # ...其它可写文件
]

def setup_logging():
    """使用标准logging模块设置日志"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = writable_path(f"data/log/py/python_{timestamp}.log")  
    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_path), exist_ok=True)  
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别
        format='%(asctime)s [%(levelname)s] %(message)s',  # 日志格式
        datefmt='%Y-%m-%d %H:%M:%S',  # 时间格式
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),  # 文件处理器
            logging.StreamHandler()  # 控制台处理器
        ]
    )

    logging.info("日志已初始化，路径: %s", log_path)

def main():
    """程序入口"""
    try:
        setup_logging()
        os.makedirs(writable_path("data/log/py"), exist_ok=True)
        for rel_path in NEED_FILES:
            ensure_empty_file(writable_path(rel_path))

        app = QtWidgets.QApplication(sys.argv)
        app.setWindowIcon(QIcon(resource_path("the_icon.ico")))
        font_id = QtGui.QFontDatabase.addApplicationFont(font_path)
        family: str = ""
        if font_id == -1:
            logging.warning("无法加载字体，切换为默认字体: Microsoft YaHei")
            family = "Microsoft YaHei"
        else:
            logging.info("字体成功加载: %s", font_path)
            family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
        
        app.setFont(QtGui.QFont(family, 12))
        win = CyberWindow()
        win.show()
        logging.info("应用已启动")
        sys.exit(app.exec())
    except Exception as e:
        logging.exception("应用出现严重错误: %s", e)
        raise

if __name__ == "__main__":
    main()