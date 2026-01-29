#!/usr/bin/env python
"""
Agent Zero v8.0 - Phase 5 依赖一键安装脚本

自动检测并安装所有必需的依赖
"""

import subprocess
import sys
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_colored(text, color):
    """彩色输出"""
    print(f"{color}{text}{Colors.END}")

def print_header(text):
    """打印标题"""
    print("\n" + "="*70)
    print_colored(text, Colors.BLUE)
    print("="*70)

def check_package(package_name):
    """检查包是否已安装"""
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print_header("🚀 Agent Zero v8.0 - Phase 5 依赖安装")

    # 定义依赖包
    core_packages = {
        'pydantic': 'pydantic>=2.0.0',
        'yaml': 'PyYAML>=6.0.0',
        'jinja2': 'Jinja2>=3.0.0',
    }

    ui_packages = {
        'streamlit': 'streamlit>=1.30.0',
        'plotly': 'plotly>=5.0.0',
    }

    optional_packages = {
        'requests': 'requests>=2.31.0',
        'aiohttp': 'aiohttp>=3.9.0',
        'loguru': 'loguru>=0.7.0',
    }

    # ============================================================
    # 1. 检查核心依赖
    # ============================================================
    print_header("📦 步骤 1: 检查核心依赖（必需）")

    core_missing = []
    for pkg_name, pkg_spec in core_packages.items():
        print(f"\n检查 {pkg_name}...", end=" ")
        if check_package(pkg_name):
            print_colored("✅ 已安装", Colors.GREEN)
        else:
            print_colored("❌ 未安装", Colors.RED)
            core_missing.append(pkg_spec)

    # 安装缺失的核心依赖
    if core_missing:
        print_colored(f"\n需要安装 {len(core_missing)} 个核心依赖", Colors.YELLOW)
        for pkg in core_missing:
            print(f"\n安装 {pkg}...")
            if install_package(pkg):
                print_colored(f"✅ {pkg} 安装成功", Colors.GREEN)
            else:
                print_colored(f"❌ {pkg} 安装失败", Colors.RED)
    else:
        print_colored("\n✅ 所有核心依赖已安装", Colors.GREEN)

    # ============================================================
    # 2. 检查 UI 依赖
    # ============================================================
    print_header("🎨 步骤 2: 检查 UI 依赖（可选）")

    ui_missing = []
    for pkg_name, pkg_spec in ui_packages.items():
        print(f"\n检查 {pkg_name}...", end=" ")
        if check_package(pkg_name):
            print_colored("✅ 已安装", Colors.GREEN)
        else:
            print_colored("❌ 未安装", Colors.RED)
            ui_missing.append(pkg_spec)

    if ui_missing:
        print_colored(f"\n⚠️  发现 {len(ui_missing)} 个 UI 依赖未安装", Colors.YELLOW)
        print("\nUI 依赖用于 Streamlit 界面，如果不需要可以跳过")

        response = input("\n是否安装 UI 依赖？(y/n): ").lower().strip()

        if response == 'y':
            for pkg in ui_missing:
                print(f"\n安装 {pkg}...")
                if install_package(pkg):
                    print_colored(f"✅ {pkg} 安装成功", Colors.GREEN)
                else:
                    print_colored(f"❌ {pkg} 安装失败", Colors.RED)
        else:
            print_colored("\n⏭️  跳过 UI 依赖安装", Colors.YELLOW)
    else:
        print_colored("\n✅ 所有 UI 依赖已安装", Colors.GREEN)

    # ============================================================
    # 3. 检查可选依赖
    # ============================================================
    print_header("🔧 步骤 3: 检查可选依赖")

    optional_missing = []
    for pkg_name, pkg_spec in optional_packages.items():
        print(f"\n检查 {pkg_name}...", end=" ")
        if check_package(pkg_name):
            print_colored("✅ 已安装", Colors.GREEN)
        else:
            print_colored("❌ 未安装", Colors.RED)
            optional_missing.append(pkg_spec)

    if optional_missing:
        print_colored(f"\n⚠️  发现 {len(optional_missing)} 个可选依赖未安装", Colors.YELLOW)
        print("\n可选依赖用于增强功能，不影响核心功能")

        response = input("\n是否安装可选依赖？(y/n): ").lower().strip()

        if response == 'y':
            for pkg in optional_missing:
                print(f"\n安装 {pkg}...")
                if install_package(pkg):
                    print_colored(f"✅ {pkg} 安装成功", Colors.GREEN)
                else:
                    print_colored(f"❌ {pkg} 安装失败", Colors.RED)
        else:
            print_colored("\n⏭️  跳过可选依赖安装", Colors.YELLOW)
    else:
        print_colored("\n✅ 所有可选依赖已安装", Colors.GREEN)

    # ============================================================
    # 4. 验证安装
    # ============================================================
    print_header("🔍 步骤 4: 验证安装")

    all_packages = {**core_packages, **ui_packages, **optional_packages}
    installed_count = 0
    total_count = len(all_packages)

    for pkg_name in all_packages.keys():
        if check_package(pkg_name):
            installed_count += 1

    print(f"\n已安装: {installed_count}/{total_count} 个依赖")

    # 核心依赖检查
    core_ok = all(check_package(pkg) for pkg in core_packages.keys())
    if core_ok:
        print_colored("✅ 核心依赖完整", Colors.GREEN)
    else:
        print_colored("❌ 核心依赖不完整", Colors.RED)

    # UI 依赖检查
    ui_ok = all(check_package(pkg) for pkg in ui_packages.keys())
    if ui_ok:
        print_colored("✅ UI 依赖完整（可使用 Streamlit）", Colors.GREEN)
    else:
        print_colored("⚠️  UI 依赖不完整（无法使用 Streamlit）", Colors.YELLOW)

    # ============================================================
    # 5. 完成
    # ============================================================
    print_header("🎉 安装完成")

    print("\n📦 已安装的功能:")
    if core_ok:
        print("  ✅ Dify 导出")
        print("  ✅ README 生成")
        print("  ✅ ZIP 打包")

    if ui_ok:
        print("  ✅ Streamlit UI")
        print("  ✅ 图表可视化")

    print("\n🚀 下一步:")
    print("  1. 运行快速测试: python quick_reference.py")
    if ui_ok:
        print("  2. 启动 UI 界面: streamlit run app.py")
    print("  3. 查看文档: PHASE5_USAGE_SUMMARY.md")

    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  安装已取消", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n\n❌ 安装出错: {e}", Colors.RED)
        sys.exit(1)
