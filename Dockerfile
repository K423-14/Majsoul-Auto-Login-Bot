FROM python:3.10-slim

# 安装依赖
RUN apt-get update && \
    apt-get install -y xvfb chromium-driver chromium wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置 Chrome 和 ChromeDriver 路径
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# 设置工作目录
WORKDIR /app

# 拷贝项目文件
COPY requirements.txt .
COPY seleniumMaj.py .
COPY sources ./sources

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 添加定时启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 安装 cron 和 bash (用于定时)
RUN apt-get update && apt-get install -y cron

# 复制 cron 配置
COPY crontab.txt /etc/cron.d/dailyjob
RUN chmod 0644 /etc/cron.d/dailyjob && crontab /etc/cron.d/dailyjob

# 启动 cron 和后台服务
CMD ["bash", "-c", "cron && tail -f /dev/null"]
