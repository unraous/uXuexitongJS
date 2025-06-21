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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchWindowException


import time
import random

from utils.auto_answer.html_2_answer import html_to_answer

# USER_AGNET = config.USER_AGENT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 拼接 main.js 的绝对路径
js_path = os.path.join(BASE_DIR, '..', 'js', 'main.js')
js_path = os.path.abspath(js_path)  # 转为绝对路径
test_path = os.path.join(BASE_DIR, '..', 'data', 'temp', 'html', 'test.html')
ans_path = os.path.join(BASE_DIR, '..', 'data', 'temp', 'json', 'answer_simplified.json')

print("main.js 路径为：", js_path)

with open(js_path, 'r', encoding='utf-8') as f:
    js_code = f.read()

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
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
                    try:
                        with open(test_path, "w", encoding="utf-8") as f:
                            f.write(html_str)
                        print("HTML已保存到 test.html")
                    except Exception as e:
                        print(f"无法写入 test.html：{e}")
                        await websocket.send(json.dumps({"error": f"无法写入 test.html：{e}"}))
                        return

                    html_to_answer(test_path)

                    try:
                        with open(ans_path, "r", encoding="utf-8") as f:
                            ans_json = f.read()
                    except Exception as e:
                        print(f"无法读取答案文件：{e}")
                        await websocket.send(json.dumps({"error": f"无法读取答案文件：{e}"}))
                        return
                    await websocket.send(ans_json)
                else:
                    print("收到非HTML消息：", data)
            except Exception:
                print("收到异常消息")

    async def main():
        async with websockets.serve(handler, "localhost", 8765):
            print("WebSocket服务器已启动 ws://localhost:8765")
            await asyncio.Future()

    asyncio.run(main())


def keep_mouse_active(driver, interval=60):
    def move_mouse():
        while driver.service.is_connectable():
            try:
                # 随机坐标，范围可根据页面大小调整
                x = random.randint(100, 500)
                y = random.randint(100, 500)
                ActionChains(driver).move_by_offset(x, y).perform()
                ActionChains(driver).move_by_offset(-x, -y).perform()
            except Exception as e:
                print(f"鼠标移动异常: {e}")
            time.sleep(interval)
    t = threading.Thread(target=move_mouse, daemon=True)
    t.start()


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



# 获取所有窗口句柄
handles = driver.window_handles
# 切换到最后一个（最新的）窗口
driver.switch_to.window(handles[-1])


try:
    driver.current_window_handle  # 检查窗口是否还在ut("请在新窗口中打开目标课程页面（即达到旧版用来粘贴脚本的页面），准备完成后按回车以继续...\n")

    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    time.sleep(2)

    driver.execute_script(
        "DEFAULT_TEST_OPTION = 1;\n" + js_code
    )


    input("脚本已注入，请关闭弹窗后再次回车以开启防挂机...\n")

    keep_mouse_active(driver) 

    input("防挂机已开启，脚本将持续运行，直到你手动关闭浏览器或按 Enter/Ctrl+C 终止脚本。\n")

    driver.quit()

except NoSuchWindowException:
    print("窗口已关闭或失效，无法注入脚本")
