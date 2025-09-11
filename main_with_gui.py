"""GUI模式启动入口"""

import datetime
import logging
import os
import sys

from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QIcon

from src.py.gui import MainWindow
from src.py.utils.path import resource_path, writable_path

def ensure_path(path: str) -> None:
    """确保文件存在，如果不存在则创建一个空文件"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logging.info("已创建文件: %s", path)
    else:
        logging.info("文件已存在: %s", path)

FILES_PATH: list[str] = [
    os.path.join("data", "config", "openai.json"),
    os.path.join("data", "temp", "html", "test.html"),
    os.path.join("data", "temp", "ttf", "font-cxsecret.ttf"),
    os.path.join("data", "temp", "json", "font_cxsecret_mapping.json"),
    os.path.join("data", "temp", "json", "questions.json"),
    os.path.join("data", "temp", "json", "questions_decoded.json"),
    os.path.join("data", "temp", "json", "questions_answered.json"),
    os.path.join("data", "temp", "json", "answer_simplified.json"),
    os.path.join("data", "config", "settings.json"),
    # ...其它可写文件
]

def setup_logging() -> None:
    """日志配置函数"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = writable_path(os.path.join("data", "log", "py", f"python_{timestamp}.log"))
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        # 保证日志同时输出到文件和控制台
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    logging.info("日志已初始化，路径: %s", log_path)

def app_init(argv: list[str]) -> QtWidgets.QApplication:
    """初始化Qt应用"""
    app: QtWidgets.QApplication = QtWidgets.QApplication(argv)
    app.setWindowIcon(QIcon(resource_path(os.path.join("data", "static", "ico", "the_icon.ico"))))
    font_path: str = resource_path(os.path.join("data", "static", "ttf", "orbitron.ttf"))
    font_id: int = QtGui.QFontDatabase.addApplicationFont(font_path)
    family: str = ""
    if font_id == -1:
        logging.warning("加载字体失败，将使用默认字体 Microsoft YaHei")
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
        os.makedirs(writable_path(os.path.join("data", "log", "py")), exist_ok=True)
        for rel_path in FILES_PATH:
            ensure_path(writable_path(rel_path))
        app: QtWidgets.QApplication = app_init(sys.argv)
        win: MainWindow = MainWindow()
        win.show()
        logging.info("应用已启动")
        sys.exit(app.exec())
    except Exception as e:
        logging.exception("应用出现严重错误: %s", e)
        raise

if __name__ == "__main__":
    main()
