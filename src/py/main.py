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


cookie_str = """fid=193; _uid=341921830; _d=1748263678039; UID=341921830; vc3=BKViqMrSDlYGwHI25nMcL8yT3%2FLs0t7MRFGqYQEbr5gHilkYnS9wNN%2FJph3q4hbvbG8x1j5FAlsb54U58S7e%2FCWRZrcHvi0o9RaHhPIByUju8PnJFkpFXMg3wqJ60m4U7NSrKzgmyhx4p2aI8dFM7nSE3JNkpg2KOs5QBrsbfds%3Da51fdd5ceb676206cf142193e2cda472; uf=b2d2c93beefa90dcc5cca0e422da616fc1d6515ee9c2203a77cbfbb52e70a880b0fd89aa7ae44d2d69225eea218755dbc49d67c0c30ca5043ad701c8b4cc548c0234d89f51c3dccfbeb9b25df8545daf713028f1ec42bf71b1188854805578ccce71fc6e59483dd31147cb7c4f7a0d3c0e6626e58d6891607e630b53a9d42d2ce9fdc681bdf07734; cx_p_token=214d25aa4a798bc4cc43ce0df6c9485a; p_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIzNDE5MjE4MzAiLCJsb2dpblRpbWUiOjE3NDgyNjM2NzgwNDAsImV4cCI6MTc0ODg2ODQ3OH0.18CdO-_gU53O0Qid_iq30nwJoF4FKiUCJ4uvMcW_SAQ; xxtenc=4807beab172611266f5ce283f927bd95; DSSTASH_LOG=C_38-UN_120-US_341921830-T_1748263678041; k8s=1748783509.144.9248.907606; jrose=4BC684B6BECCF8F750A103C733BD3B15.mooc-536300739-f1g2v; route=f537d772be8122bff9ae56a564b98ff6"""

for item in cookie_str.split(";"):
    name, value = item.strip().split("=", 1)
    cookie_dict = {
        "name": name,
        "value": value,
        "domain": ".chaoxing.com"
    }
    try:
        driver.add_cookie(cookie_dict)
    except Exception as e:
        print(f"添加 cookie {name} 失败: {e}")

driver.get("https://mooc1.chaoxing.com/mycourse/studentstudy?chapterId=869952226&courseId=248046494&clazzid=118872772&cpi=405841762&enc=d957912715df6fc2f6d7b24db3f90882&mooc2=1&openc=2892e6b9b3356785dc0fd19d71941f9d")




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