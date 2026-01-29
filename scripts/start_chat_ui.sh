#!/bin/bash
# Chat UI 启动脚本 (Linux/Mac)

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "============================================================"
echo -e "${BLUE}   启动 Agent Zero Chat UI${NC}"
echo "============================================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] 未找到 Python${NC}"
    exit 1
fi

# 检查 streamlit 是否安装
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] Streamlit 未安装${NC}"
    echo ""
    echo "请先运行: python3 install_dependencies.py"
    echo "或手动安装: pip3 install streamlit plotly"
    exit 1
fi

echo -e "${GREEN}[信息] 正在启动 Chat UI...${NC}"
echo ""
echo "浏览器将自动打开，或手动访问:"
echo "  http://localhost:8501"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""
echo "============================================================"
echo ""

# 使用 python -m 方式启动
python3 -m streamlit run app_chat.py
