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
    
    # 创建一个自定义的输出流类，仅写入日志文件
    class FileOnlyOutput:
        def __init__(self, file_path):
            self.file = open(file_path, 'w', encoding='utf-8')
            
        def write(self, message):
            self.file.write(message)
            self.file.flush()  # 立即写入，不缓存
            
        def flush(self):
            self.file.flush()
            
        def close(self):
            if self.file:
                self.file.close()
                self.file = None
    
    # 创建一个既写入控制台又写入文件的输出类
    class TeeOutput:
        def __init__(self, file_path, original_stdout):
            self.file = open(file_path, 'w', encoding='utf-8')
            self.original_stdout = original_stdout
            
        def write(self, message):
            if self.original_stdout:  # 检查是否为None
                try:
                    self.original_stdout.write(message)
                except Exception:
                    pass  # 忽略输出到控制台的错误
            self.file.write(message)
            self.file.flush()
            
        def flush(self):
            if self.original_stdout:
                try:
                    self.original_stdout.flush()
                except Exception:
                    pass
            self.file.flush()
            
        def close(self):
            if self.file:
                self.file.close()
                self.file = None
    
    # 根据环境选择合适的输出方式
    try:
        # 尝试获取原始输出
        original_stdout = sys.stdout
        
        # 检查是否在打包环境或没有有效输出
        if hasattr(sys, '_MEIPASS') or original_stdout is None:
            # 打包环境下，只记录到文件
            sys.stdout = FileOnlyOutput(log_path)
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"日志已初始化 (仅文件模式)，路径: {log_path}\n")
        else:
            # 非打包环境，同时输出到控制台和文件
            sys.stdout = TeeOutput(log_path, original_stdout)
            print(f"日志已初始化 (Tee模式)，路径: {log_path}")
    except Exception as e:
        # 出错时回退到只写文件
        try:
            sys.stdout = FileOnlyOutput(log_path)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"日志初始化出错: {e}，使用仅文件模式\n")
        except Exception:
            pass  # 如果连这都失败了，就放弃日志记录
            
    return log_path

os.makedirs(writable_path("data/log/py"), exist_ok=True)

for rel_path in NEED_FILES:
    ensure_empty_file(writable_path(rel_path))

# 设置日志记录
log_file_path = setup_logging()

def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setWindowIcon(QIcon(resource_path("the_icon.ico")))
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