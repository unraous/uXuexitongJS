from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QIcon
import sys
import os
import logging
import datetime


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
            if path.endswith("settings.json") and "config" in path.replace("\\", "/"):
                default_settings = {
                    "Log": False,
                    "ForceSpd": False,
                    "Pace": 5
                }
                with open(path, "w", encoding="utf-8") as f:
                    import json
                    json.dump(default_settings, f, ensure_ascii=False, indent=2)

            print(f"已创建文件: {path}")
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
    "data/config/settings.json",
    # ...其它可写文件
]



for rel_path in NEED_FILES:
    ensure_empty_file(writable_path(rel_path))
    
from src.py.utils.gui.cyber_window import CyberWindow



def setup_logging():
    """设置日志记录器，捕获所有print输出到文件"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = writable_path(f"data/log/py/python_{timestamp}.log")
    
    # 创建一个自定义的输出流类，同时写入控制台和日志文件
    class TeeOutput:
        def __init__(self, file_path, original_stdout):
            self.file = open(file_path, 'w', encoding='utf-8')
            self.original_stdout = original_stdout
            
        def write(self, message):
            self.original_stdout.write(message)
            self.file.write(message)
            self.file.flush()  # 立即写入，不缓存
            
        def flush(self):
            self.original_stdout.flush()
            self.file.flush()
            
        def close(self):
            if self.file:
                self.file.close()
                self.file = None
    
    # 保存原始的标准输出
    original_stdout = sys.stdout
    
    # 替换标准输出为我们的自定义输出
    sys.stdout = TeeOutput(log_path, original_stdout)
    
    print(f"日志已初始化，路径: {log_path}")
    return log_path

os.makedirs(writable_path("data/log/py"), exist_ok=True)

for rel_path in NEED_FILES:
    ensure_empty_file(writable_path(rel_path))

# 设置日志记录
log_file_path = setup_logging()

def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setWindowIcon(QIcon('the_icon.ico'))
        font_id = QtGui.QFontDatabase.addApplicationFont(font_path)
        family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Microsoft YaHei"
        app.setFont(QtGui.QFont(family, 12))
        win = CyberWindow()
        win.show()
        logging.info("应用已启动")
        sys.exit(app.exec())
    except Exception as e:
        logging.exception(f"应用出现严重错误: {e}")
        raise

if __name__ == "__main__":
    main()