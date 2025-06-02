import os
import time
import subprocess
import cv2
import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 发送通知函数
def send_notification(group_id="897778072", message="测试消息"):
   """
   Sends a notification message to a specific group using a GET request.
   """
   # URL for the API endpoint
   url = f"http://123.56.43.107:16578/send_group_msg?group_id={group_id}&message={message}"

   payload={}
   headers = {
      'Authorization': 'zZShk37ZSZu8F5yu8m'
   }

   response = requests.request("GET", url, headers=headers, data=payload)

   print(response.text)


# 启动虚拟显示
def start_virtual_display():
    display_num = ":99"  # 设置虚拟显示编号
    subprocess.Popen(["Xvfb", display_num, "-screen", "0", "1920x1080x24"])  # 启动 Xvfb 虚拟显示
    time.sleep(2)  # 等待 Xvfb 启动
    os.environ["DISPLAY"] = display_num


# 使用 Selenium 创建 Chrome 驱动
def create_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")  # 如需 headless 可启用
    options.add_argument("--ignore-gpu-blocklist")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(options=options)



# 使用 OpenCV 模板匹配查找截图中的元素
def multi_scale_template_match(screenshot_path, template_path, threshold=0.8, scales=np.linspace(0.5, 1.5, 20)):
    screenshot = cv2.imread(screenshot_path, 0)
    template_orig = cv2.imread(template_path, 0)

    if screenshot is None or template_orig is None:
        print(f"读取图片失败: {screenshot_path} 或 {template_path}")
        return None

    best_match = None
    max_val = -1

    for scale in scales:
        template = cv2.resize(template_orig, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        if template.shape[0] > screenshot.shape[0] or template.shape[1] > screenshot.shape[1]:
            continue

        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, current_max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if current_max_val > max_val and current_max_val >= threshold:
            max_val = current_max_val
            best_match = (max_loc, template.shape[::-1])  # (x, y), (w, h)

    if best_match:
        pt, (w, h) = best_match
        center = (pt[0] + w // 2, pt[1] + h // 2)
        print(f"匹配成功，匹配值: {max_val:.3f}, 位置: {center}")
        return center
    else:
        print(f"在多个尺度下模板匹配失败: {template_path}")
        return None


# 使用 DevTools 协议模拟点击事件
def devtools_click(driver, x, y):
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mousePressed",
        "button": "left",
        "clickCount": 1,
        "x": x,
        "y": y
    })
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseReleased",
        "button": "left",
        "clickCount": 1,
        "x": x,
        "y": y
    })


# 找位置并点击函数
def click_element(driver, screenshot_path, template_path):
    pos = multi_scale_template_match(screenshot_path, template_path)
    if pos:
        devtools_click(driver, pos[0], pos[1])
        time.sleep(2)  # 等待切换完成
    else:
        print("❌ 未找到位置，详情查看截图")
        driver.save_screenshot("error_screenshot.png")


def main():
    start_virtual_display()
    driver = create_driver()
    
    try:
        # 访问雀魂网站
        print("🌐 正在访问雀魂...")
        driver.get("https://game.maj-soul.com/")

        # 等待游戏资源加载完成
        print("⏳ 等待页面加载...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "canvas"))
        )
        time.sleep(30)  # 等待渲
        # 模板图片路径
        sources_path = "sources"
        if not os.path.exists(sources_path):
            print("❌ 模板图片路径不存在，请检查 sources 文件夹")
            return
        account_template =  sources_path + "/account_label.png"    
        password_template = sources_path + "/password_label.png"  
        login_template = sources_path + "/login_button.png"       
        line_template = sources_path + "/line.png"  # 切换线路按钮模板
        access_template = sources_path + "/access_line.png"  # 线路切换按钮模板
        close_template = sources_path + "/close_button.png"  # 关闭线路切换按钮模板

        # 截图路径
        result_path = "results"
        if not os.path.exists(result_path):
            os.makedirs(result_path)
            print(f"✅ 创建结果目录: {result_path}")
        screenshot_path = os.path.join(result_path, "majsoul_screenshot.png")
        driver.save_screenshot(screenshot_path)

        # 切换线路
        print("🔄 切换线路...")
        click_element(driver, screenshot_path, line_template)
        time.sleep(10)  # 等待线路延迟检测完成
        line_switch_screenshot_path = os.path.join(result_path, "majsoul_line_switch.png")
        driver.save_screenshot(line_switch_screenshot_path)
        click_element(driver, line_switch_screenshot_path, access_template)
        click_element(driver, line_switch_screenshot_path, close_template)


        # 先定位账号输入框，点击并输入账号
        print("🔑 输入账号和密码并登陆...")
        click_element(driver, screenshot_path, account_template)
        driver.execute_cdp_cmd("Input.insertText", {"text": "你的账号"})  # 替换为你的账号
        time.sleep(2)  # 等待输入完成

        # 定位密码输入框，点击并输入密码
        click_element(driver, screenshot_path, password_template)
        driver.execute_cdp_cmd("Input.insertText", {"text": "你的密码"})  # 替换为你的密码
        time.sleep(2)  # 等待输入完成

        # 定位登录按钮，点击
        click_element(driver, screenshot_path, login_template)
        time.sleep(30)  # 等待登录完成
        driver.save_screenshot(result_path + "/majsoul_after_login.png")


    except Exception as e:
        print(f"❌ 执行过程中出现错误: {e}")
    
    finally:
        # 最后关闭浏览器
        print("🔄 正在关闭浏览器...")
        try:
            driver.quit()
            print("✅ 浏览器已关闭")
        except Exception as e:
            print(f"❌ 关闭浏览器时出错: {e}")


if __name__ == "__main__":
    main()
