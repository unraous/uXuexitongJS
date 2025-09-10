import os
import sys
import json
import time
from openai import OpenAI

def writable_path(relative_path):
    """返回当前工作目录下的可写路径，并自动创建父目录"""
    abs_path = os.path.join(os.getcwd(), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path

def get_user_config():
    import importlib.util
    config_path = os.path.join(os.getcwd(), "config.py")
    if not os.path.exists(config_path):
        raise FileNotFoundError("config.py 不存在，请先配置。")
    spec = importlib.util.spec_from_file_location("config", config_path)
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    return cfg

def get_openai_client():
    config = get_user_config()
    API_KEY = getattr(config, "API_KEY", "")
    BASE_URL = getattr(config, "BASE_URL", "")
    MODEL = getattr(config, "MODEL", "")
    client = OpenAI(
        base_url = BASE_URL,
        api_key = API_KEY,
    )
    return client, MODEL

def chat_with_openrouter(messages, model=None):
    client, default_model = get_openai_client()
    if model is None:
        model = default_model
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        timeout=60,
    )
    return completion.choices[0].message.content

def answer_questions_batch(questions, retry=3):
    prompt = ""
    for idx, q in enumerate(questions, 1):
        prompt += f"{idx}. 题干：{q['题干']}\n选项：{q['选项']}\n"
    messages = [
        {"role": "system", "content": "你是一个中国高效答题助手。现在请依次回答以下题目，每题只输出“题号:答案”，不要解释，每题一行，题号请用题目原题号,多选题直接把选项字母拼接（如51:A，44:ACD）同时对于有错别字和语句不通的题目，尝试利用形近字猜测原题意，同时注意不要输出“ERROR”，必须保证每次至少输出一个选项。"},
        {"role": "user", "content": prompt}
    ]
    for i in range(retry):
        try:
            answer = chat_with_openrouter(messages)
            return answer.strip()
        except Exception as e:
            print(f"批量请求出错（第{i+1}次）：", e)
    fallback = "\n".join([f"{q.get('题号', idx+1)}:A" for idx, q in enumerate(questions)])
    return fallback  # 如果全部请求失败，返回一个默认答案

def answer_questions_file(input_json, output_json, batch_size=10):
    """
    从文件读取题目，批量请求AI并写入带答案的json
    """
    with open(input_json, "r", encoding="utf-8") as f:
        questions = json.load(f)

    total = len(questions)
    for batch_start in range(0, total, batch_size):
        batch = questions[batch_start:batch_start+batch_size]
        print(f"\n正在批量回答第 {batch_start+1}~{min(batch_start+batch_size, total)} 题")
        batch_answer = answer_questions_batch(batch)
        print("AI批量答案：", batch_answer)
        answer_map = {}
        for line in batch_answer.splitlines():
            if ":" in line:
                tid, ans = line.split(":", 1)
                answer_map[tid.strip()] = ans.strip()
        if set(answer_map.keys()) == set(str(i) for i in range(1, len(batch)+1)):
            answers = [answer_map[str(i)] for i in range(1, len(batch)+1)]
            for q, a in zip(batch, answers):
                q["AI答案"] = a
        else:
            for q in batch:
                q["AI答案"] = answer_map.get(q["题号"], "ERROR")
        time.sleep(2)
    with open(writable_path(output_json), "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"已生成 {output_json}")

def extract_simple_answers(input_json, output_json):
    """
    从带AI答案的题目json中提取简明答案列表
    """
    with open(input_json, "r", encoding="utf-8") as f:
        questions = json.load(f)
    result = []
    for q in questions:
        result.append({
            "题号": q["题号"],
            "答案": q.get("AI答案", "")
        })
    with open(writable_path(output_json), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"已生成 {output_json}")
