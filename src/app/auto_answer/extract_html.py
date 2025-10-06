"""从 HTML 中提取题目和字体"""
import base64
import logging
import re
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import Tag


def extract_font_from_html(html_content: str, output_ttf_path: Path) -> bool:
    """从 HTML 内容中提取 font-cxsecret 字体并保存为 ttf 文件"""
    pattern = re.compile(
        r"""
        @font-face\s*\{              # @font-face 开始
        [^}]*                        # 任意非}字符
        font-family:\s*              # font-family 属性
        ['\"]font-cxsecret['\"]\s*;  # font-cxsecret 字体名
        [^}]*                        # 任意非}字符
        src:\s*url\(                 # src: url( 开始
        'data:application/font-ttf;  # data URI 前缀
        [^,]+,                       # charset 等参数
        ([^']+)                      # 捕获 base64 数据
        '                            # 结束引号
        """,
        re.VERBOSE | re.DOTALL,
    )
    match = pattern.search(html_content)
    if match:
        base64_str = match.group(1)
        font_bytes = base64.b64decode(base64_str)
        # 写入可写目录
        with output_ttf_path.open("wb") as f:
            f.write(font_bytes)
        logging.info("已提取 base64 并保存为字体文件 %s", output_ttf_path.name)
        return True

    logging.warning("未检测到 font-cxsecret 的 base64 字体数据")
    return False

def extract_questions_from_html(html_content: str) -> list[dict]:
    """从 HTML 内容中提取题目数据"""
    soup = BeautifulSoup(html_content, "html.parser")
    questions = []
    for q in soup.find_all("div", class_="TiMu newTiMu"):  # 很难想通直接拿拼音命名的理由
        if not isinstance(q, Tag):
            continue  # 跳过非Tag类型
        num_tag = q.find("i", class_="fl")
        num = num_tag.text.strip() if num_tag and num_tag.text else ""
        type_span = q.find("span", class_="newZy_TItle")
        qtype = type_span.text.strip() if type_span and type_span.text else ""
        stem_div = q.find("div", class_="fontLabel")
        stem = stem_div.get_text(separator="", strip=True) if stem_div else ""
        options = []
        for li in q.find_all("li"):
            opt = li.get_text(separator="", strip=True)
            options.append(opt)
        questions.append({
            "题号": num,
            "题型": qtype,
            "题干": stem,
            "选项": options
        })
    return questions
