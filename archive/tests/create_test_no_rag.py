"""
创建测试 Dify YAML（不包含 RAG 节点）

用于验证是否是 RAG/Code 节点导致的问题
"""

from pathlib import Path
from src.exporters import export_to_dify
from src.schemas import GraphStructure, NodeDef, EdgeDef, PatternConfig, StateSchema, StateField

print("=" * 60)
print("🧪 创建测试 Dify YAML（不包含 RAG）")
print("=" * 60)

# 创建 Graph（LLM + Tool，不包含 RAG）
print("\n1️⃣ 创建 Graph（LLM + Tool，不包含 RAG）...")
graph = GraphStructure(
    pattern=PatternConfig(
        pattern_type="sequential",
        description="这是一个测试 Agent，用于演示 Dify 导出功能",
        max_iterations=1,
    ),
    state_schema=StateSchema(
        fields=[StateField(name="messages", type="List[BaseMessage]", description="对话历史")]
    ),
    nodes=[
        NodeDef(id="agent", type="llm", role_description="主要的 LLM Agent，负责理解用户需求"),
        NodeDef(id="search", type="tool", config={"tool_name": "tavily_search"}),
    ],
    edges=[EdgeDef(source="agent", target="search")],
    entry_point="agent",
)
print("✅ Graph 创建成功")

# 导出
print("\n2️⃣ 导出为 Dify YAML...")
output_path = Path("test_no_rag_dify.yml")
dify_path = export_to_dify(graph, "测试Agent（无RAG）", output_path)

print(f"✅ YAML 已生成: {dify_path}")
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
print("   3. 导入 DSL → 上传 test_no_rag_dify.yml")
print("   4. 如果成功，说明问题确实出在 RAG/Code 节点")

print("\n" + "=" * 60)
