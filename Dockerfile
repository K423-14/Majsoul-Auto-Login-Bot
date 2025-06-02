FROM python:3.10-slim

# 安装必要依赖（不包含 chromium 本体）
RUN apt-get update && apt-get install -y \
    xvfb cron wget curl unzip fonts-liberation libnss3 libxss1 libasound2 \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY seleniumMaj.py .
COPY entrypoint.sh /entrypoint.sh
COPY crontab.txt /etc/cron.d/dailyjob
COPY sources ./sources

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN chmod +x /entrypoint.sh && \
    chmod 0644 /etc/cron.d/dailyjob && \
    crontab /etc/cron.d/dailyjob

CMD ["bash", "-c", "cron && tail -f /var/log/cron.log"]
