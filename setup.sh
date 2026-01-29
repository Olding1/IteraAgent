#!/bin/bash
# Agent Zero 一键安装脚本 (Linux/Mac)
# ==========================================

set -e

echo ""
echo "========================================"
echo "  Agent Zero 一键安装"
echo "========================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.8 或更高版本"
    exit 1
fi

echo "[信息] 找到 Python:"
python3 --version
echo ""

# 运行 Python 安装脚本
echo "[信息] 开始安装..."
python3 setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "[成功] 安装完成！"
    echo ""
else
    echo ""
    echo "[错误] 安装失败"
    exit 1
fi
