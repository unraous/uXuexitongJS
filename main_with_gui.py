"""GUI模式启动入口"""

import datetime
import logging
import os
import sys

from typing import Callable

from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QIcon

import src.py.utils as utils

from src.py.gui import MainWindow


def setup_logging() -> None:
    """日志初始化"""
    timestamp: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path: str = utils.writable_path(
        os.path.join("data", "log", "py", f"python_{timestamp}.log")
    )

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
    """Qt应用初始化"""
    icon_path: str = utils.resource_path(utils.RSC_PATH["icon_path"])

    app: QtWidgets.QApplication = QtWidgets.QApplication(argv)
    app.setWindowIcon(QIcon(icon_path))
    font_path: str = utils.resource_path(os.path.join("data", "static", "ttf", "orbitron.ttf"))
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

def init_paths() -> None:
    """初始化路径列表"""
    path_dict: dict[str, str]
    path_groups: dict[str, list[str]]
    for path_dict, path_groups in [
        (utils.RSC_PATH, utils.global_config.get("path_groups", {}).get("resources", {})),
        (utils.WTB_PATH, utils.global_config.get("path_groups", {}).get("writable", {}))
    ]:
        processed_files = {
            key: os.path.join(*path_list) if isinstance(path_list, list) else path_list
            for key, path_list in path_groups.items()
        }

        path_dict.clear()
        path_dict.update(processed_files)

def ensure_files(path_dict: dict[str, str], method: Callable[[str], None]) -> None:
    """载入必要路径并确保所有路径存在"""
    path: str
    for path in path_dict.values():
        method(path)


def main() -> None:
    """程序入口"""
    try:
        setup_logging()
        utils.load_config()
        init_paths()
        
        ensure_files(utils.WTB_PATH, utils.ensure_file)
        ensure_files(utils.RSC_PATH, utils.check_file)

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
