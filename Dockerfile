FROM python:3.10-slim

# 安装必要依赖（包括 chromium 相关依赖）& 安装中文字体（包含 simhei.ttf）
RUN apt-get update && apt-get install -y \
    xvfb wget curl unzip fonts-liberation libnss3 libxss1 libasound2 \
    libx11-6 libxkbcommon0 libgtk-3-0 libdrm2 libgbm1 \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 拷贝文件
COPY requirements.txt .
COPY seleniumMaj.py .
COPY entrypoint.sh .
COPY sources ./sources

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 设置可执行权限
RUN chmod +x /app/entrypoint.sh

# 设置入口脚本
ENTRYPOINT ["/app/entrypoint.sh"]
