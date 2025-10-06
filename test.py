import sys
from pathlib import Path

print(Path.cwd())

def static_path(*relative_path: str) -> Path:
    """开发/打包双环境的静态路径适配"""
    root: Path = Path(getattr(sys, '_MEIPASS', str(Path.cwd())))
    return root.joinpath(*relative_path)

print(static_path("src", "app", "utils", "file_path.py"))
