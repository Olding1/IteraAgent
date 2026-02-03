"""
创建最简化的 Dify YAML 用于测试

只包含一个 LLM 节点，最小化可能的错误
"""

from pathlib import Path
from src.exporters import export_to_dify
from src.schemas import GraphStructure, NodeDef, PatternConfig, StateSchema, StateField

print("=" * 60)
print("🧪 创建最简化的 Dify YAML")
print("=" * 60)

# 创建最简单的 Graph（只有 LLM 节点）
print("\n1️⃣ 创建最简单的 Graph（只有 LLM 节点）...")
graph = GraphStructure(
    pattern=PatternConfig(
        pattern_type="sequential", description="最简单的测试 Agent", max_iterations=1
    ),
    state_schema=StateSchema(
        fields=[StateField(name="messages", type="List[BaseMessage]", description="对话历史")]
    ),
    nodes=[NodeDef(id="agent", type="llm", role_description="这是一个简单的 AI 助手")],
    edges=[],
    entry_point="agent",
)
print("✅ Graph 创建成功")

# 导出
print("\n2️⃣ 导出为 Dify YAML...")
output_path = Path("simple_dify.yml")
dify_path = export_to_dify(graph, "简单测试Agent", output_path)

print(f"✅ 简化版 YAML 已生成: {dify_path}")
print(f"   文件大小: {dify_path.stat().st_size} 字节")

# 显示内容
print("\n3️⃣ YAML 内容:")
print("-" * 60)
with open(dify_path, "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
print("-" * 60)

print("\n✅ 完成！")
print("\n💡 使用方法:")
print("   1. 访问 https://cloud.dify.ai")
print("   2. 创建应用 → Chatflow")
print("   3. 导入 DSL → 上传 simple_dify.yml")
print("   4. 如果还是失败，请查看浏览器控制台（F12）的错误信息")

print("\n" + "=" * 60)
