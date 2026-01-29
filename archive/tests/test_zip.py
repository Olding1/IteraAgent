"""
测试 ZIP 打包导出功能

将 Agent 打包为 ZIP 文件，方便分享和部署
"""

from pathlib import Path
from src.utils.export_utils import export_to_zip, get_agent_size

print("="*60)
print("🧪 测试 ZIP 打包导出功能")
print("="*60)

# 检查可用的 Agent
print("\n1️⃣ 查找可用的 Agent...")
agents_dir = Path("agents")

if not agents_dir.exists():
    print(f"❌ agents 目录不存在: {agents_dir.absolute()}")
    print("   请确保在项目根目录运行此脚本")
    exit(1)

available_agents = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

if not available_agents:
    print("❌ 没有找到可用的 Agent")
    print("   请先创建一个 Agent 或使用现有的 Agent")
    exit(1)

print(f"✅ 找到 {len(available_agents)} 个 Agent:")
for i, agent in enumerate(available_agents, 1):
    print(f"   {i}. {agent.name}")

# 选择第一个 Agent 进行测试
agent_path = available_agents[0]
print(f"\n2️⃣ 使用 Agent: {agent_path.name}")

# 计算大小
print("\n3️⃣ 计算 Agent 大小...")
try:
    size = get_agent_size(agent_path)
    print(f"✅ Agent 大小: {size}")
except Exception as e:
    print(f"⚠️ 计算大小失败: {e}")

# 导出为 ZIP
print("\n4️⃣ 导出为 ZIP...")
output_path = Path("test_export.zip")

try:
    zip_path = export_to_zip(agent_path, output_path)
    print(f"✅ ZIP 导出成功!")
    print(f"   文件位置: {zip_path.absolute()}")

    # 显示文件大小
    file_size = zip_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    print(f"   文件大小: {file_size:,} 字节 ({file_size_mb:.2f} MB)")

    # 列出 ZIP 内容
    print("\n5️⃣ ZIP 文件内容:")
    print("-"*60)
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        file_list = zipf.namelist()
        print(f"   总文件数: {len(file_list)}")
        print(f"\n   前 20 个文件:")
        for i, filename in enumerate(file_list[:20], 1):
            file_info = zipf.getinfo(filename)
            print(f"   {i:3d}. {filename} ({file_info.file_size} 字节)")
        if len(file_list) > 20:
            print(f"\n   ... (还有 {len(file_list) - 20} 个文件)")
    print("-"*60)

    print("\n✅ 测试完成！")
    print(f"\n💡 提示: 你可以解压 {output_path} 来查看完整内容")

except Exception as e:
    print(f"❌ 导出失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
