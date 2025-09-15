"""配置文件读写模块"""

import os
import logging
import textwrap

from typing import Final, Any

import tomlkit


DEFAULT_CONFIG: Final[str] = textwrap.dedent(
    """    [metadata]
    version = "1.3.0"
    author = "unraous"

    # API相关配置

    [openai]
    api_key = ""
    base_url = ""
    model = ""

    # 刷课相关配置

    [auto_course]
    log_option = true
    force_spd = false
    spd = 1.0

    # 路径相关配置(value为列表，方便os.path.join)

    [path_groups.writable]
    html_path = ["data", "temp", "html", "question.html"]
    obf_font_path = ["data", "temp", "ttf", "font-cxsecret.ttf"]
    obf_font_mapping_path = ["data", "temp", "json", "font_cxsecret_mapping.json"]
    questions_path = ["data", "temp", "json", "questions.json"]
    questions_decoded_path = ["data", "temp", "json", "questions_decoded.json"]
    answered_path = ["data", "temp", "json", "questions_answered.json"]
    answer_simplified_path = ["data", "temp", "json", "answer_simplified.json"]

    [path_groups.resources]
    js_file_path = ["src", "js", "main.js"]
    orbitron_font_path = ["data", "static", "ttf", "orbitron.ttf"]
    simsun_font_path = ["data", "static", "ttf", "simsun.ttf"]
    icon_path = ["data", "static", "ico", "the_icon.ico"]
    settings_icon_path = ["data", "static", "svg", "gear-solid-gradient.svg"]

    """
)

CONFIG_PATH: Final[str] = os.path.join("data", "config.toml")

global_config: dict[str, Any] = {}
"""由配置toml生成的全局作用域字典"""

def init_config() -> None:
    """初始化，加载配置toml至 global_config"""
    logging.info("正在加载配置文件: %s", CONFIG_PATH)
    global_config.clear()

    try:
        with open(CONFIG_PATH, "rb") as f:
            global_config.update(tomlkit.load(f))
            logging.info("配置文件加载成功")

    except FileNotFoundError:
        logging.info("配置文件未找到，将创建默认配置文件")
        with open(CONFIG_PATH, "wb") as f:
            f.write(DEFAULT_CONFIG.encode("utf-8"))
            global_config.update(tomlkit.loads(DEFAULT_CONFIG))
            logging.info("默认配置文件已创建")

def save_config() -> None:
    """保存字典至配置toml"""
    with open(CONFIG_PATH, "wb") as f:
        f.write(tomlkit.dumps(global_config).encode("utf-8"))
        logging.info("配置文件已保存")
