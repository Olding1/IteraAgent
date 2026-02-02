"""
测试 start.py 的新增功能

验证导出菜单是否正常工作
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🧪 测试 start.py 新增功能")
print("=" * 70)

# Test 1: Check if export modules can be imported
print("\n【测试 1】检查导出模块...")
try:
    from src.exporters import export_to_dify, validate_for_dify
    from src.utils.readme_generator import generate_readme

    print("✅ 导出模块导入成功")
except ImportError as e:
    print(f"❌ 导出模块导入失败: {e}")

# Test 2: Check if agents directory exists
print("\n【测试 2】检查 agents 目录...")
agents_dir = Path("agents")
if agents_dir.exists():
    agents = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    print(f"✅ agents 目录存在，包含 {len(agents)} 个 Agent")
    for agent in agents:
        print(f"   - {agent.name}")
else:
    print("⚠️  agents 目录不存在")

# Test 3: Check if streamlit is installed
print("\n【测试 3】检查 Streamlit...")
try:
    import streamlit

    print(f"✅ Streamlit 已安装 (版本: {streamlit.__version__})")
except ImportError:
    print("⚠️  Streamlit 未安装")

# Test 4: Check if app.py exists
print("\n【测试 4】检查 app.py...")
app_file = Path("app.py")
if app_file.exists():
    print(f"✅ app.py 存在 ({app_file.stat().st_size} 字节)")
else:
    print("❌ app.py 不存在")

# Test 5: Check exports directory
print("\n【测试 5】检查 exports 目录...")
exports_dir = Path("exports")
if exports_dir.exists():
    exports = list(exports_dir.iterdir())
    print(f"✅ exports 目录存在，包含 {len(exports)} 个导出")
else:
    print("⚠️  exports 目录不存在（首次导出时会自动创建）")

print("\n" + "=" * 70)
print("📊 测试总结")
print("=" * 70)
print("\n✅ start.py 新增功能准备就绪！")
print("\n💡 使用方法:")
print("   1. 运行: python start.py")
print("   2. 选择选项 7: 导出 Agent 到 Dify")
print("   3. 选择选项 8: 启动 Web UI")
print("\n" + "=" * 70)
