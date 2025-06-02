# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


import threading
import asyncio
import websockets
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
import time

from utils.auto_answer.html_2_answer import html_to_answer
import config

USER_AGNET = config.USER_AGENT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 拼接 main.js 的绝对路径
js_path = os.path.join(BASE_DIR, '..', 'js', 'main.js')
js_path = os.path.abspath(js_path)  # 转为绝对路径
test_path = os.path.join(BASE_DIR, '..', 'data', 'temp', 'html', 'test.html')
ans_path = os.path.join(BASE_DIR, '..', 'data', 'temp', 'json', 'answer_simplified.json')

print("main.js 路径为：", js_path)

with open(js_path, 'r', encoding='utf-8') as f:
    js_code = f.read()

user_agent = USER_AGNET if USER_AGNET else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
options = Options()
options.set_preference("general.useragent.override", user_agent)

def start_ws_server():
    async def handler(websocket):
        async for msg in websocket:
            try:
                data = json.loads(msg)
                if data.get("type") == "testDocHtml":
                    html_str = data.get("html", "")
                    print("收到HTML内容，长度：", len(html_str))
                    with open(test_path, "w", encoding="utf-8") as f:
                        f.write(html_str)
                    # input("HTML已保存到 test.html，按回车继续...")
                    html_to_answer(test_path)
                    
                    with open(ans_path, "r", encoding="utf-8") as f:
                        ans_json = f.read()
                    await websocket.send(ans_json)
                else:
                    print("收到非HTML消息：", data)
            except Exception:
                print("收到异常消息：", msg)

    async def main():
        async with websockets.serve(handler, "localhost", 8765):
            print("WebSocket服务器已启动 ws://localhost:8765")
            await asyncio.Future()

    asyncio.run(main())

ws_thread = threading.Thread(target=start_ws_server, daemon=True)
ws_thread.start()

driver = None
browser_tried = []

try:
    driver = webdriver.Firefox(options=options)
    print("已成功启动 Firefox 浏览器")
except Exception as e:
    print("Firefox 启动失败：", e)
    browser_tried.append("Firefox")
    try:
        from selenium.webdriver.edge.options import Options as EdgeOptions
        edge_options = EdgeOptions()
        edge_options.use_chromium = True
        edge_options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Edge(options=edge_options)
        print("已成功启动 Edge 浏览器")
    except Exception as e2:
        print("Edge 启动失败：", e2)
        browser_tried.append("Edge")
        try:
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            chrome_options = ChromeOptions()
            chrome_options.add_argument(f"user-agent={user_agent}")
            driver = webdriver.Chrome(options=chrome_options)
            print("已成功启动 Chrome 浏览器")
        except Exception as e3:
            print("Chrome 启动失败：", e3)
            browser_tried.append("Chrome")
            raise RuntimeError(f"所有浏览器均启动失败，已尝试：{browser_tried}")

if driver is None:
    raise RuntimeError(f"所有浏览器均启动失败，已尝试：{browser_tried}")

driver.get("https://mooc1.chaoxing.com")  # 先访问主域，才能设置 Cookie




input("欢迎使用此脚本，请登录后打开至目标课程界面（即达到旧版用来粘贴脚本的页面即可），准备完成后按回车以继续...\n")

driver.execute_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")

time.sleep(2)

driver.execute_script(
    "DEFAULT_TEST_OPTION = 1;\n" + js_code
)


input("脚本已注入，按回车关闭浏览器以强制退出脚本...\n")

driver.quit()