#!/bin/bash

# 可选：随机延迟 0～600 秒，模拟用户行为
sleep $((RANDOM % 600))

# 执行脚本
python3 /app/seleniumMaj.py
