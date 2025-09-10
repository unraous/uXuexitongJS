import os
import sys
import re
import base64
from bs4 import BeautifulSoup
import json

def resource_path(relative_path):
    """兼容PyInstaller和源码运行的资源路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    # 项目根目录
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), relative_path)

def writable_path(relative_path):
    """返回当前工作目录下的可写路径，并自动创建父目录"""
    abs_path = os.path.join(os.getcwd(), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path

def extract_font_from_html(html_content, output_ttf_path):
    """
    从 HTML 内容中提取 font-cxsecret 字体并保存为 ttf 文件
    output_ttf_path 应为 'data/temp/ttf/font-cxsecret.ttf' 这种根目录相对路径
    """
    pattern = re.compile(
        r"@font-face\s*{[^}]*font-family:\s*['\"]font-cxsecret['\"];[^}]*src:\s*url\('data:application/font-ttf;[^,]+,([^']+)'",
        re.DOTALL
    )
    match = pattern.search(html_content)
    if match:
        base64_str = match.group(1)
        font_bytes = base64.b64decode(base64_str)
        # 写入可写目录
        output_ttf_path = writable_path(output_ttf_path)
        with open(output_ttf_path, "wb") as f:
            f.write(font_bytes)
        print(f"已提取 base64 并保存为字体文件 {output_ttf_path}")
        return True
    else:
        print("未检测到 font-cxsecret 的 base64 字体数据")
        return False

def extract_questions_from_html(html_content):
    """
    从 HTML 内容中提取题目数据
    """
    soup = BeautifulSoup(html_content, "html.parser")
    questions = []
    for timu in soup.find_all("div", class_="TiMu newTiMu"):
        num = timu.find("i", class_="fl").text.strip()
        type_span = timu.find("span", class_="newZy_TItle")
        qtype = type_span.text.strip() if type_span else ""
        stem_div = timu.find("div", class_="fontLabel")
        stem = stem_div.get_text(separator="", strip=True) if stem_div else ""
        options = []
        for li in timu.find_all("li"):
            opt = li.get_text(separator="", strip=True)
            options.append(opt)
        questions.append({
            "题号": num,
            "题型": qtype,
            "题干": stem,
            "选项": options
        })
    return questions

