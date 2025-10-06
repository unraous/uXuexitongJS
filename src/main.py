"""程序入口"""
import datetime
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QtMsgType, QUrl, qInstallMessageHandler
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from app import TaskManager, utils


def qt_message_handler(msg_type, _, message):
    """统一 Qt 日志格式到 Python logging"""
    qt_level = {
        QtMsgType.QtDebugMsg: logging.INFO,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL
    }.get(msg_type, logging.INFO)
    logging.log(qt_level, "[QML] %s", message)

def setup_logging() -> None:
    """日志初始化"""
    timestamp: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path: Path = utils.writable_path(
        "UXS", "log", "py", f"python_{timestamp}.log"
    )

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
    qInstallMessageHandler(qt_message_handler)
    logging.info("日志初始化成功(路径: %s)", log_path)

def ensure_files(
    path_dict: dict[str, list[str]],
    path_method: Callable[..., Path],
    task: Callable[[Path], None]
) -> None:
    """载入必要路径并确保所有路径存在"""
    path: list[str]
    for path in path_dict.values():
        task(path_method(*path))

if __name__ == "__main__":
    setup_logging()
    utils.init_config()

    ensure_files(
        utils.global_config.get("path_groups", {}).get("writable", {}),
        utils.writable_path,
        utils.ensure_file
    )
    ensure_files(
        utils.global_config.get("path_groups", {}).get("static", {}),
        utils.static_path,
        utils.check_file
    )

    os.environ['QML_XHR_ALLOW_FILE_READ'] = '1'  # 授权 QML 读取资源文件
    application = QApplication([])
    application.setWindowIcon(QIcon(
        str(utils.static_path("src", "resources", "ico", "the_icon.ico"))
    ))

    backend = TaskManager()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load(QUrl.fromLocalFile(
        utils.static_path("src", "gui", "main.qml")
    ))
    if not engine.rootObjects():
        logging.critical("GUI 加载失败, 程序自动退出")
        sys.exit(1)

    application.aboutToQuit.connect(backend.close)
    application.exec()
