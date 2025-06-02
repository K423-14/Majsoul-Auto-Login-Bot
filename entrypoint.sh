#!/bin/bash

Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

echo "🎯 启动每日签到容器..."

while true; do
    echo "⏰ 当前时间: $(date)"

    # 生成 -3600 到 +3600 秒之间的随机偏移量
    OFFSET=$(( (RANDOM % 7201) - 3600 ))
    echo "🕹️ 随机偏移 $OFFSET 秒后开始执行脚本..."
    sleep $OFFSET

    # 执行签到脚本
    echo "🚀 开始执行 seleniumMaj.py..."
    python3 seleniumMaj.py
    echo "✅ 本次执行完成: $(date)"

    # 等待 12 小时（43200 秒）后进入下一轮（再次 ±1 小时偏移）
    echo "🕓 等待 12 小时后进入下一轮..."
    sleep 43200
done
