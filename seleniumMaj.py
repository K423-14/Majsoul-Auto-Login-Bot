import os
import time
import subprocess
import cv2
import numpy as np
import requests
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('selenium_log.txt'), logging.StreamHandler()])

# 发送通知函数
def send_notification(group_id="897778072", message="测试消息"):
   """
   Sends a notification message to a specific group using a GET request.
   """
   url = f"http://123.56.43.107:16578/send_group_msg?group_id={group_id}&message={message}"

   headers = {
      'Authorization': 'zZShk37ZSZu8F5yu8m'
   }

   try:
       response = requests.request("GET", url, headers=headers)
       logging.info(f"通知发送成功: {response.text}")
   except Exception as e:
       logging.error(f"通知发送失败: {e}")

# 启动虚拟显示
def start_virtual_display():
    display_num = ":99"  # 设置虚拟显示编号
    subprocess.Popen(["Xvfb", display_num, "-screen", "0", "1920x1080x24"])  # 启动 Xvfb 虚拟显示
    time.sleep(2)  # 等待 Xvfb 启动
    os.environ["DISPLAY"] = display_num

# 使用 Selenium 创建 Chrome 驱动
def create_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    
    # WebGL相关配置
    options.add_argument("--enable-webgl")
    options.add_argument("--use-gl=angle")
    options.add_argument("--use-angle=swiftshader")
    options.add_argument("--enable-accelerated-2d-canvas")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument("--ignore-gpu-blocklist")
    options.add_argument("--ignore-gpu-blacklist")
    options.add_argument("--disable-gpu-sandbox")
    
    # 其他稳定性配置
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    
    # 用户代理
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")

    return webdriver.Chrome(options=options)

# 使用 OpenCV 模板匹配查找截图中的元素
def multi_scale_template_match(screenshot_path, template_path, threshold=0.8, scales=np.linspace(0.5, 1.5, 20)):
    screenshot = cv2.imread(screenshot_path, 0)
    template_orig = cv2.imread(template_path, 0)

    if screenshot is None or template_orig is None:
        logging.error(f"读取图片失败: {screenshot_path} 或 {template_path}")
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
        logging.info(f"匹配成功，匹配值: {max_val:.3f}, 位置: {center}")
        return center
    else:
        logging.error(f"在多个尺度下模板匹配失败: {template_path}")
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
        time.sleep(20)  # 等待切换完成
    else:
        logging.error("❌ 未找到位置，详情查看截图")
        driver.save_screenshot("error_screenshot.png")

# 登录函数，支持多个用户
def login(driver, screenshot_path, account_template, password_template, login_template, user_env_var):
    user_data = os.getenv(user_env_var)
    if not user_data:
        logging.error(f"没有找到用户数据环境变量: {user_env_var}")
        return

    account, password = user_data.split('&')  # 用&符号分隔账号和密码
    logging.info(f"🔑 开始登录用户: {account}")

    click_element(driver, screenshot_path, account_template)
    driver.execute_cdp_cmd("Input.insertText", {"text": account})
    time.sleep(20)

    click_element(driver, screenshot_path, password_template)
    driver.execute_cdp_cmd("Input.insertText", {"text": password})
    time.sleep(20)

    click_element(driver, screenshot_path, login_template)
    time.sleep(120)  # 等待登录完成
    logging.info(f"✅ 用户 {account} 登录成功")
    send_notification(message=f"用户 {account} 登录成功")

def main():
    start_virtual_display()
    driver = create_driver()
    
    try:
        logging.info("🌐 正在访问雀魂...")
        driver.get("https://game.maj-soul.com/")

        logging.info("⏳ 等待页面加载...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "canvas"))
        )
        time.sleep(120)  # 等待渲染

        sources_path = "sources"
        if not os.path.exists(sources_path):
            logging.error("❌ 模板图片路径不存在，请检查 sources 文件夹")
            return

        account_template = sources_path + "/account_label.png"
        password_template = sources_path + "/password_label.png"
        login_template = sources_path + "/login_button.png"

        result_path = "results"
        if not os.path.exists(result_path):
            os.makedirs(result_path)
            logging.info(f"✅ 创建结果目录: {result_path}")
        screenshot_path = os.path.join(result_path, "majsoul_screenshot.png")
        driver.save_screenshot(screenshot_path)

        logging.info("🔄 切换线路...")
        click_element(driver, screenshot_path, account_template)

        # 多用户登录，使用环境变量分隔符#，例如 USER_ACCOUNTS 环境变量包含多个账号#密码对
        user_accounts = os.getenv("USER_ACCOUNTS", "")  # 从环境变量获取所有账号密码对
        if not user_accounts:
            logging.error("❌ 没有找到用户数据环境变量: USER_ACCOUNTS")
        else:
            for user_data in user_accounts.split("#"):  # 使用 # 分隔多个账号密码对
                if user_data.strip():  # 确保数据非空
                    login(driver, screenshot_path, account_template, password_template, login_template, user_data)

    except Exception as e:
        logging.error(f"❌ 执行过程中出现错误: {e}")
        send_notification(message=f"执行错误: {e}")
    
    finally:
        logging.info("🔄 正在关闭浏览器...")
        try:
            driver.quit()
            logging.info("✅ 浏览器已关闭")
        except Exception as e:
            logging.error(f"❌ 关闭浏览器时出错: {e}")
            send_notification(message=f"关闭浏览器时出错: {e}")

if __name__ == "__main__":
    main()
