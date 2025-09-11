"""答题逻辑核心，调用OpenAI接口获取答案"""
import os
import json
import time
import logging

from typing import Optional

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.py.utils import writable_path

def get_user_config() -> dict[str, str]:
    """从JSON文件读取用户配置"""

    config_path = os.path.join(os.getcwd(), "data", "config", "openai.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError("openai.json 不存在，请先配置。")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config: dict[str, str] = json.load(f)
        return config
    except Exception as e:
        raise ValueError("openai.json 格式错误，请检查JSON语法。") from e

def get_openai_client() -> tuple[OpenAI, str]:
    """获取OpenAI客户端和模型设置"""

    config: dict[str, str] = get_user_config()
    api_key: str = config.get("API_KEY", "")
    base_url: str = config.get("BASE_URL", "")
    model: str = config.get("MODEL", "")

    client: OpenAI = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    return client, model

def chat_with_openai(
    messages: list[ChatCompletionMessageParam],
    model: Optional[str] = None
) -> str:
    """OpenAI交互接口"""

    client: OpenAI
    default_model: str
    client, default_model = get_openai_client()
    if model is None:
        model = default_model
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        timeout=40,
    )
    return str(completion.choices[0].message.content)

def answer_questions_batch(questions, retry=3):
    """批量请求AI回答题目，返回答案string"""

    prompt: str = ""
    for idx, q in enumerate(questions, 1):
        prompt += f"{idx}. 题干：{q['题干']}\n选项：{q['选项']}\n"
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": """
            你是一个中国高效答题助手。
            现在请依次回答以下题目，每题只输出“题号:答案”，不要解释，每题一行，题号请用题目原题号,多选题直接把选项字母拼接（如51:A，44:ACD）
            同时对于有错别字和语句不通的题目，尝试利用形近字猜测原题意，同时注意不要输出“ERROR”，必须保证每次至少输出一个选项。
         """
        },
        {"role": "user", "content": prompt}
    ]
    for i in range(retry):
        try:
            answer: str = str(chat_with_openai(messages))
            return answer.strip()
        except (TimeoutError, ConnectionError) as e:
            logging.warning("批量请求出错 (第%d次): %s", i + 1, e)
    logging.warning("批量请求多次失败，返回默认答案")
    # 如果全部请求失败则全选A
    fallback: str = "\n".join([f"{q.get('题号', idx+1)}:A" for idx, q in enumerate(questions)])
    return fallback

def answer_questions_file(input_json, output_json, batch_size=10):
    """从文件读取题目，批量请求AI并写入带答案的json"""

    with open(input_json, "r", encoding="utf-8") as f:
        questions: list[dict[str, str]] = json.load(f)

    for batch_start in range(0, len(questions), batch_size):
        batch: list[dict[str, str]] = questions[batch_start:batch_start+batch_size]
        logging.info("正在批量回答第 %d~%d 题", batch_start+1, min(batch_start+batch_size, len(questions)))
        batch_answer: str = answer_questions_batch(batch)
        logging.info("AI批量答案：%s", batch_answer)
        answer_map = {}
        for line in batch_answer.splitlines():
            if ":" in line:
                tid, ans = line.split(":", 1)
                answer_map[tid.strip()] = ans.strip()
        if set(answer_map.keys()) == {str(i) for i in range(1, len(batch)+1)}:
            answers = [answer_map[str(i)] for i in range(1, len(batch)+1)]
            for q, a in zip(batch, answers):
                q["AI答案"] = a
        else:
            for q in batch:
                q["AI答案"] = answer_map.get(q["题号"], "ERROR")
        time.sleep(2)
    with open(writable_path(output_json), "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    logging.info("已生成 %s", output_json)

def extract_simple_answers(input_json, output_json):
    """简化答案，生成最终json"""
    with open(input_json, "r", encoding="utf-8") as f:
        questions: list[dict[str, str]] = json.load(f)
    result: list[dict[str, str]] = []
    for q in questions:
        result.append({
            "题号": q["题号"],
            "答案": q.get("AI答案", "")
        })
    with open(writable_path(output_json), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logging.info("已生成 %s", output_json)
