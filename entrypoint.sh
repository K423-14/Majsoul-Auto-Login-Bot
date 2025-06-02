#!/bin/bash

Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

echo "🎯 启动每日签到容器..."

while true; do
    # 每日只执行一次
    echo "⏰ 当前时间: $(date)"

    # 生成 0~7200 秒之间的随机数（最多延迟 2 小时）
    RAND_SECONDS=$(( RANDOM % 7200 ))
    echo "🕹️ 延迟 $RAND_SECONDS 秒后开始执行脚本..."
    sleep $RAND_SECONDS

    # 执行签到脚本
    echo "🚀 开始执行 seleniumMaj.py..."
    python3 seleniumMaj.py
    echo "✅ 本次执行完成: $(date)"

    # 等待 24 小时（一天），再进行下一轮
    echo "🕓 等待 86400 秒，准备下一天的任务..."
    sleep 86400
done
