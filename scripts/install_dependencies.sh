#!/bin/bash
# Agent Zero v8.0 - Phase 5 依赖一键安装脚本 (Linux/Mac)

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "============================================================"
echo -e "${BLUE}   Agent Zero v8.0 - Phase 5 依赖安装${NC}"
echo "============================================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] 未找到 Python，请先安装 Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}[信息] 检测到 Python 版本:${NC}"
python3 --version
echo ""

# 升级 pip
echo -e "${BLUE}[步骤 1] 升级 pip...${NC}"
python3 -m pip install --upgrade pip
echo ""

# 安装核心依赖
echo -e "${BLUE}[步骤 2] 安装核心依赖...${NC}"
echo ""
python3 -m pip install "pydantic>=2.0.0"
python3 -m pip install "PyYAML>=6.0.0"
python3 -m pip install "Jinja2>=3.0.0"
echo ""

# 询问是否安装 UI 依赖
echo -e "${BLUE}[步骤 3] 是否安装 UI 依赖（Streamlit）？${NC}"
echo ""
read -p "安装 UI 依赖？(y/n): " install_ui

if [[ "$install_ui" == "y" || "$install_ui" == "Y" ]]; then
    echo ""
    echo "安装 UI 依赖..."
    python3 -m pip install "streamlit>=1.30.0"
    python3 -m pip install "plotly>=5.0.0"
    echo ""
else
    echo ""
    echo -e "${YELLOW}跳过 UI 依赖安装${NC}"
    echo ""
fi

# 询问是否安装可选依赖
echo -e "${BLUE}[步骤 4] 是否安装可选依赖？${NC}"
echo ""
read -p "安装可选依赖？(y/n): " install_optional

if [[ "$install_optional" == "y" || "$install_optional" == "Y" ]]; then
    echo ""
    echo "安装可选依赖..."
    python3 -m pip install "requests>=2.31.0"
    python3 -m pip install "aiohttp>=3.9.0"
    python3 -m pip install "loguru>=0.7.0"
    echo ""
else
    echo ""
    echo -e "${YELLOW}跳过可选依赖安装${NC}"
    echo ""
fi

# 完成
echo "============================================================"
echo -e "${GREEN}   安装完成！${NC}"
echo "============================================================"
echo ""
echo "下一步:"
echo "  1. 运行快速测试: python3 quick_reference.py"
if [[ "$install_ui" == "y" || "$install_ui" == "Y" ]]; then
    echo "  2. 启动 UI 界面: streamlit run app.py"
fi
echo "  3. 查看文档: PHASE5_USAGE_SUMMARY.md"
echo ""
echo "============================================================"
