---

## 🀄 Majsoul Auto Login Bot

一个使用 `Selenium + OpenCV + Docker + Xvfb` 的雀魂自动登录工具，支持多用户登录、截图模板匹配、模拟点击，支持定时执行（可随机延迟防止检测）。

---

### 📦 功能特性

* 🧠 使用 OpenCV 多尺度模板匹配模拟鼠标点击
* 🔐 多账号登录（账号&密码通过环境变量传入）
* 🖥️ 虚拟显示 `Xvfb` 支持无图形界面部署（如服务器）
* ⏰ 自动定时执行，支持每日随机延迟（模拟真实操作）
* 📢 登录成功/异常自动通知（支持自定义通知接口）

---

### 🧱 目录结构

```
.
├── Dockerfile             # 构建环境
├── seleniumMaj.py         # 主程序
├── requirements.txt       # Python依赖
├── entrypoint.sh          # 每次执行入口脚本，支持随机延迟
├── crontab.txt            # 定时任务定义
├── sources/               # 模板图像（登录按钮、输入框等）
└── results/               # 截图结果保存目录（可自动创建）
```

---

### 🚀 快速开始

#### 1. 克隆项目

```bash
git clone https://github.com/K423-14/Majsoul-Auto-Login-Bot.git
cd Majsoul-Auto-Login-Bot
```

#### 2. 构建镜像

```bash
docker build -t majsoul-bot .
```

#### 3. 运行容器

```bash
docker run -d \
  -e USER_ACCOUNTS="your_account1&your_password1#your_account2&your_password2" \
  --name majsoul-bot \
  majsoul-bot
```

> ✅ 账号与密码通过环境变量传入，格式为：`账号&密码#账号&密码`
> 可以配置多个账号，多个使用 # 分割...

---

### 🛠 自定义定时任务

你可以在 `crontab.txt` 中修改定时执行策略，例如每天 2 次：

```cron
0 4 * * * root /entrypoint.sh >> /var/log/cron.log 2>&1
30 14 * * * root /entrypoint.sh >> /var/log/cron.log 2>&1
```

---

### 📢 通知系统

登录成功或失败会通过 `send_notification()` 自动调用远程通知接口，你可以替换为你自己的 webhook 或通知逻辑。

---

### 📌 注意事项

* 支持部署在无 GUI 的 Linux 服务器或容器中
* 脚本采用模拟点击方式，确保模板图准确匹配你的屏幕元素

---

### 📜 License

MIT License

---

如需支持或定制功能，欢迎提交 issue 或联系作者 🙌

---