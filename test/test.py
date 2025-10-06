
import os
import sys

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    os.environ['QML_XHR_ALLOW_FILE_READ'] = '1'
    application = QApplication([])
    engine = QQmlApplicationEngine()
    engine.load(QUrl("test/test.qml"))
    if not engine.rootObjects():
        sys.exit(1)

    application.exec()
