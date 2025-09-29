
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

from backend import Backend

app = QApplication([])
backend = Backend()
engine = QQmlApplicationEngine()
engine.rootContext().setContextProperty("backend", backend)

engine.load(QUrl("qml/main.qml"))


# 在应用退出时调用清理函数
app.aboutToQuit.connect(backend.cleanup)

app.exec()