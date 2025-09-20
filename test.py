from PySide6.QtCore import QObject, Slot, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

class Backend(QObject):
    @Slot()
    def say_hello(self):
        print("Hello from Python!")

app = QApplication([])
engine = QQmlApplicationEngine()
engine.load(QUrl("qml/main.qml"))

backend = Backend()

# 关键：主动赋值 QML property
window = engine.rootObjects()[0]
window.setProperty("backend", backend)

app.exec()