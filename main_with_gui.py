from PySide6 import QtWidgets, QtGui
import sys
import os
# 项目根目录（src/py/上一级）
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.join(PROJECT_ROOT, "src/py"))
sys.path.append(os.path.join(PROJECT_ROOT, "src/py/utils"))
sys.path.append(os.path.join(PROJECT_ROOT, "src/py/utils/gui"))
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(PROJECT_ROOT, relative_path)

font_path = resource_path("data/static/ttf/orbitron.ttf")


def writable_path(relative_path):
    """返回当前工作目录下的可写路径，并自动创建父目录"""
    abs_path = os.path.join(os.getcwd(), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path

def ensure_empty_file(path):
    """确保文件存在，如果不存在则创建一个空文件"""
    try:
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                pass
            print(f"已创建空文件: {path}")
        else:
            print(f"文件已存在: {path}")
    except Exception as e:
        print(f"创建文件失败: {path}, 错误: {e}")

NEED_FILES = [
    "config.py",
    "data/temp/html/test.html",
    "data/temp/ttf/font-cxsecret.ttf",
    "data/temp/json/font_cxsecret_mapping.json",
    "data/temp/json/questions.json",
    "data/temp/json/questions_decoded.json",
    "data/temp/json/questions_answered.json",
    "data/temp/json/answer_simplified.json",
    # ...其它可写文件
]

for rel_path in NEED_FILES:
    ensure_empty_file(writable_path(rel_path))
    
from src.py.utils.gui.cyber_window import CyberWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    font_id = QtGui.QFontDatabase.addApplicationFont(font_path)
    family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Microsoft YaHei"
    app.setFont(QtGui.QFont(family, 12))
    win = CyberWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()