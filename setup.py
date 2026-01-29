#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Zero 一键安装脚本
自动安装所有依赖并配置环境
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_info(text: str):
    """打印信息"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text: str):
    """打印警告"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    """打印错误"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def check_python_version():
    """检查 Python 版本"""
    print_info("检查 Python 版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"需要 Python 3.8 或更高版本，当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print_success(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """检查 pip 是否可用"""
    print_info("检查 pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      check=True, capture_output=True)
        print_success("pip 已安装")
        return True
    except subprocess.CalledProcessError:
        print_error("pip 未安装或不可用")
        return False

def upgrade_pip():
    """升级 pip"""
    print_info("升级 pip 到最新版本...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                      check=True, capture_output=True)
        print_success("pip 已升级")
        return True
    except subprocess.CalledProcessError as e:
        print_warning(f"pip 升级失败: {e}")
        return False

def install_requirements():
    """安装依赖"""
    print_info("安装项目依赖...")

    # 只需要安装 requirements.txt，它包含所有核心依赖
    req_file = "requirements.txt"

    if not os.path.exists(req_file):
        print_error(f"未找到 {req_file}")
        return False

    print_info(f"安装 {req_file} 中的依赖...")
    print_info("这可能需要几分钟时间，请耐心等待...")

    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file],
                      check=True)
        print_success(f"{req_file} 安装完成")
    except subprocess.CalledProcessError as e:
        print_error(f"{req_file} 安装失败: {e}")
        return False

    # 询问是否安装开发依赖
    print()
    response = input(f"{Colors.OKCYAN}是否安装开发依赖 (用于测试、类型检查、文档生成)? (y/N): {Colors.ENDC}").strip().lower()
    if response == 'y':
        dev_req_file = "requirements-dev.txt"
        if os.path.exists(dev_req_file):
            print_info(f"安装 {dev_req_file} 中的依赖...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", dev_req_file],
                              check=True)
                print_success(f"{dev_req_file} 安装完成")
            except subprocess.CalledProcessError as e:
                print_warning(f"{dev_req_file} 安装失败: {e}")
        else:
            print_warning(f"未找到 {dev_req_file}")

    return True

def setup_env_file():
    """配置 .env 文件"""
    print_info("配置环境变量...")

    env_file = Path(".env")
    env_template = Path(".env.template")

    if env_file.exists():
        print_warning(".env 文件已存在")
        response = input(f"{Colors.WARNING}是否覆盖? (y/N): {Colors.ENDC}").strip().lower()
        if response != 'y':
            print_info("保留现有 .env 文件")
            return True

    if not env_template.exists():
        print_error(".env.template 文件不存在")
        return False

    # 复制模板
    shutil.copy(env_template, env_file)
    print_success(".env 文件已创建")

    # 交互式配置
    print_info("\n开始配置 API 密钥...")
    print_info("提示: 直接按回车跳过，稍后可手动编辑 .env 文件")

    configs = {
        "BUILDER_PROVIDER": {
            "prompt": "Builder Provider (openai/anthropic/azure)",
            "default": "openai"
        },
        "BUILDER_MODEL": {
            "prompt": "Builder Model (例如: gpt-4o)",
            "default": "gpt-4o"
        },
        "BUILDER_API_KEY": {
            "prompt": "Builder API Key",
            "default": ""
        },
        "BUILDER_BASE_URL": {
            "prompt": "Builder Base URL (可选，使用默认则留空)",
            "default": ""
        },
        "RUNTIME_PROVIDER": {
            "prompt": "Runtime Provider (openai/anthropic/azure)",
            "default": "openai"
        },
        "RUNTIME_MODEL": {
            "prompt": "Runtime Model (例如: gpt-3.5-turbo)",
            "default": "gpt-3.5-turbo"
        },
        "RUNTIME_API_KEY": {
            "prompt": "Runtime API Key (留空则使用 Builder API Key)",
            "default": ""
        },
        "EMBEDDING_PROVIDER": {
            "prompt": "Embedding Provider (ollama/openai)",
            "default": "ollama"
        },
        "EMBEDDING_MODEL": {
            "prompt": "Embedding Model (例如: nomic-embed-text)",
            "default": "nomic-embed-text"
        },
        "EMBEDDING_BASE_URL": {
            "prompt": "Embedding Base URL (例如: http://localhost:11434)",
            "default": "http://localhost:11434"
        },
        "JUDGE_PROVIDER": {
            "prompt": "Judge Provider (openai/anthropic/azure)",
            "default": "openai"
        },
        "JUDGE_MODEL": {
            "prompt": "Judge Model (例如: gpt-4o)",
            "default": "gpt-4o"
        },
        "JUDGE_API_KEY": {
            "prompt": "Judge API Key (留空则使用 Builder API Key)",
            "default": ""
        }
    }

    # 读取现有配置
    env_content = env_file.read_text(encoding='utf-8')

    print()
    for key, config in configs.items():
        value = input(f"{Colors.OKCYAN}{config['prompt']} [{config['default']}]: {Colors.ENDC}").strip()
        if not value:
            value = config['default']

        # 更新配置
        if value:
            env_content = env_content.replace(f"{key}=", f"{key}={value}")

    # 写回文件
    env_file.write_text(env_content, encoding='utf-8')
    print_success("\n环境变量配置完成")

    return True

def create_directories():
    """创建必要的目录"""
    print_info("创建项目目录...")

    directories = [
        "agents",
        "exports",
        "logs",
        "data"
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

    print_success("项目目录创建完成")
    return True

def verify_installation():
    """验证安装"""
    print_info("验证安装...")

    try:
        # 测试导入核心模块
        import langchain
        import langgraph
        import pydantic
        import streamlit
        import yaml
        import jinja2

        print_success("核心依赖验证通过")
        return True
    except ImportError as e:
        print_error(f"依赖验证失败: {e}")
        return False

def print_next_steps():
    """打印后续步骤"""
    print_header("安装完成！")

    print(f"{Colors.OKGREEN}🎉 Agent Zero 已成功安装！{Colors.ENDC}\n")

    print(f"{Colors.BOLD}后续步骤:{Colors.ENDC}\n")

    print(f"{Colors.OKCYAN}1. 配置 API 密钥{Colors.ENDC}")
    print(f"   编辑 .env 文件，填入你的 API 密钥\n")

    print(f"{Colors.OKCYAN}2. 启动 Agent Zero{Colors.ENDC}")
    print(f"   {Colors.BOLD}CLI 模式:{Colors.ENDC}")
    print(f"   python start.py\n")

    print(f"   {Colors.BOLD}Web UI 模式:{Colors.ENDC}")
    print(f"   python scripts/start_ui.bat  (Windows)")
    print(f"   ./scripts/start_ui.sh        (Linux/Mac)\n")

    print(f"   {Colors.BOLD}Chat UI 模式:{Colors.ENDC}")
    print(f"   python scripts/start_chat_ui.bat  (Windows)")
    print(f"   ./scripts/start_chat_ui.sh        (Linux/Mac)\n")

    print(f"{Colors.OKCYAN}3. 查看文档{Colors.ENDC}")
    print(f"   README.md - 项目概览")
    print(f"   docs/ - 详细文档\n")

    print(f"{Colors.BOLD}需要帮助?{Colors.ENDC}")
    print(f"   GitHub Issues: https://github.com/yourusername/Agent_Zero/issues\n")

def main():
    """主函数"""
    print_header("Agent Zero 一键安装")

    print(f"{Colors.BOLD}欢迎使用 Agent Zero 安装向导！{Colors.ENDC}")
    print(f"此脚本将自动安装所有依赖并配置环境\n")

    # 检查 Python 版本
    if not check_python_version():
        sys.exit(1)

    # 检查 pip
    if not check_pip():
        sys.exit(1)

    # 升级 pip
    upgrade_pip()

    # 安装依赖
    print_header("安装依赖")
    if not install_requirements():
        print_error("依赖安装失败")
        sys.exit(1)

    # 配置环境
    print_header("配置环境")
    if not setup_env_file():
        print_error("环境配置失败")
        sys.exit(1)

    # 创建目录
    if not create_directories():
        print_error("目录创建失败")
        sys.exit(1)

    # 验证安装
    print_header("验证安装")
    if not verify_installation():
        print_warning("部分依赖验证失败，但安装可能仍然成功")

    # 打印后续步骤
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}安装已取消{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"安装过程中出现错误: {e}")
        sys.exit(1)
