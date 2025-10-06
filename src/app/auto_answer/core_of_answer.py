"""答题逻辑核心, 调用OpenAI接口获取答案"""

import json
import logging
import time
from pathlib import Path

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from ..utils import global_config


def get_openai_client(config: dict[str, str]) -> tuple[OpenAI, str]:
    """获取OpenAI客户端和模型设置"""
    api_key: str = config.get("api_key", "")
    base_url: str = config.get("base_url", "")
    model: str = config.get("model", "")

    client: OpenAI = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    return client, model

def chat_with_openai(
    messages: list[ChatCompletionMessageParam],
    model: str | None = None
) -> str:
    """OpenAI交互接口"""

    client: OpenAI
    default_model: str
    client, default_model = get_openai_client(global_config.get("openai", {}))
    if model is None:
        model = default_model
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        timeout=40,
    )
    return str(completion.choices[0].message.content)

def answer_questions_batch(questions: list[dict[str, str]], retry: int = 3) -> str:
    """批量请求AI回答题目, 返回答案string"""

    prompt: str = "".join(
        f"{idx}. 题干:{q['题干']}\n选项:{q['选项']}\n"
        for idx, q in enumerate(questions, 1)
    )

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": """
            你是一个中文高效答题助手。
            现在请依次回答以下题目, 每题只输出“题号:答案”, 不要解释, 每题一行, 题号请用题目原题号,多选题直接把选项字母拼接(如51:A, 44:ACD)
            同时对于有错别字和语句不通的题目, 尝试利用形近字猜测原题意, 同时注意不要输出“ERROR”, 必须保证每次至少输出一个选项。
         """
        },
        {"role": "user", "content": prompt}
    ]

    for i in range(retry):
        try:
            answer: str = chat_with_openai(messages)
            return answer.strip()
        except (TimeoutError, ConnectionError) as e:
            logging.warning("批量请求失败 (第%d次): %s", i + 1, e)

    logging.warning("批量请求多次失败, 返回默认选项A")
    # 如果全部请求失败则全选A
    fallback: str = "\n".join([f"{q.get('题号', idx+1)}:A" for idx, q in enumerate(questions)])
    return fallback

def answer_questions_file(
    input_json_path: Path,
    output_json_path: Path,
    batch_size: int = 10
) -> None:
    """从文件读取题目, 批量请求AI并写入带答案的json"""

    with input_json_path.open(encoding="utf-8") as f:
        questions: list[dict[str, str]] = json.load(f)

    for batch_start in range(0, len(questions), batch_size):
        batch: list[dict[str, str]] = questions[batch_start:batch_start+batch_size]
        logging.info("正在批量回答第 %d~%d 题", batch_start+1, min(batch_start+batch_size, len(questions)))
        batch_answer: str = answer_questions_batch(batch)
        logging.info("AI批量答案: %s", batch_answer)
        answer_map = {}
        for line in batch_answer.splitlines():
            if ":" in line:
                tid, ans = line.split(":", 1)
                answer_map[tid.strip()] = ans.strip()
        if set(answer_map.keys()) == {str(i) for i in range(1, len(batch)+1)}:
            answers = [answer_map[str(i)] for i in range(1, len(batch)+1)]
            for q, a in zip(batch, answers, strict=False):
                q["AI答案"] = a
        else:
            for q in batch:
                q["AI答案"] = answer_map.get(q["题号"], "ERROR")
        time.sleep(2)
    with output_json_path.open("w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)
    logging.info("已生成 %s", output_json_path)

def extract_simple_answers(input_json_path: Path, output_json_path: Path) -> None:
    """简化答案, 生成最终json"""
    with input_json_path.open(encoding="utf-8") as f:
        questions: list[dict[str, str]] = json.load(f)

    result: list[dict[str, str]] = [{
        "题号": q["题号"],
        "答案": q.get("AI答案", "")
    } for q in questions if "AI答案" in q]

    with output_json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    logging.info("已生成 %s", output_json_path)
