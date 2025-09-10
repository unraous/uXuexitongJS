"""GUI启动块"""
import datetime
import logging
import os
import sys

from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QIcon

from src.py.gui.cyber_window import CyberWindow
from src.py.utils.path import resource_path, writable_path

def ensure_path(path: str) -> None:
    """确保文件存在，如果不存在则创建一个空文件"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logging.info("已创建文件: %s", path)
    else:
        logging.info("文件已存在: %s", path)

NEED_FILES: list[str] = [
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

def setup_logging() -> None:
    """使用标准logging模块设置日志"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = writable_path(f"data/log/py/python_{timestamp}.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',

        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    logging.info("日志已初始化，路径: %s", log_path)

def app_init(argv: list[str]) -> QtWidgets.QApplication:
    """初始化Qt应用"""
    app: QtWidgets.QApplication = QtWidgets.QApplication(argv)
    app.setWindowIcon(QIcon(resource_path("data/static/ico/the_icon.ico")))
    font_path: str = resource_path("data/static/ttf/orbitron.ttf")
    font_id: int = QtGui.QFontDatabase.addApplicationFont(font_path)
    family: str = ""
    if font_id == -1:
        logging.warning("无法加载字体，切换为默认字体: Microsoft YaHei")
        family = "Microsoft YaHei"
    else:
        logging.info("Orbitron字体成功加载")
        family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
    app.setFont(QtGui.QFont(family, 12))

    logging.info("应用初始化完成")
    return app

def main() -> None:
    """程序入口"""
    try:
        setup_logging()
        os.makedirs(writable_path("data/log/py"), exist_ok=True)
        for rel_path in NEED_FILES:
            ensure_path(writable_path(rel_path))
        app: QtWidgets.QApplication = app_init(sys.argv)
        win: CyberWindow = CyberWindow()
        win.show()
        logging.info("应用已启动")
        sys.exit(app.exec())
    except Exception as e:
        logging.exception("应用出现严重错误: %s", e)
        raise

if __name__ == "__main__":
    main()
