"""
最终测试：验证 Dify 导出功能

测试三种场景：
1. 简单 LLM 节点
2. LLM + Tool 节点
3. LLM + Tool + RAG 节点（RAG 会被跳过）
"""

from pathlib import Path
from src.exporters import export_to_dify, validate_for_dify
from src.schemas import GraphStructure, NodeDef, EdgeDef, PatternConfig, StateSchema, StateField

print("=" * 60)
print("🧪 Dify 导出功能最终测试")
print("=" * 60)

# 测试 1: 简单 LLM
print("\n【测试 1】简单 LLM 节点")
print("-" * 60)
graph1 = GraphStructure(
    pattern=PatternConfig(
        pattern_type="sequential", description="简单的 AI 助手", max_iterations=1
    ),
    state_schema=StateSchema(
        fields=[StateField(name="messages", type="List[BaseMessage]", description="对话历史")]
    ),
    nodes=[NodeDef(id="agent", type="llm", role_description="AI 助手")],
    edges=[],
    entry_point="agent",
)

valid, warnings = validate_for_dify(graph1)
print(f"验证结果: {'✅ 通过' if valid else '❌ 失败'}")
if warnings:
    for w in warnings:
        print(f"  ⚠️  {w}")

output1 = export_to_dify(graph1, "简单AI助手", Path("test_simple.yml"))
print(f"✅ 已生成: {output1} ({output1.stat().st_size} 字节)")

# 测试 2: LLM + Tool
print("\n【测试 2】LLM + Tool 节点")
print("-" * 60)
graph2 = GraphStructure(
    pattern=PatternConfig(
        pattern_type="sequential", description="带搜索的 AI 助手", max_iterations=1
    ),
    state_schema=StateSchema(
        fields=[StateField(name="messages", type="List[BaseMessage]", description="对话历史")]
    ),
    nodes=[
        NodeDef(id="agent", type="llm", role_description="AI 助手"),
        NodeDef(id="search", type="tool", config={"tool_name": "tavily_search"}),
    ],
    edges=[EdgeDef(source="agent", target="search")],
    entry_point="agent",
)

valid, warnings = validate_for_dify(graph2)
print(f"验证结果: {'✅ 通过' if valid else '❌ 失败'}")
if warnings:
    for w in warnings:
        print(f"  ⚠️  {w}")

output2 = export_to_dify(graph2, "带搜索的AI助手", Path("test_with_tool.yml"))
print(f"✅ 已生成: {output2} ({output2.stat().st_size} 字节)")

# 测试 3: LLM + Tool + RAG
print("\n【测试 3】LLM + Tool + RAG 节点（RAG 会被跳过）")
print("-" * 60)
graph3 = GraphStructure(
    pattern=PatternConfig(
        pattern_type="sequential", description="完整功能的 AI 助手", max_iterations=1
    ),
    state_schema=StateSchema(
        fields=[StateField(name="messages", type="List[BaseMessage]", description="对话历史")]
    ),
    nodes=[
        NodeDef(id="agent", type="llm", role_description="AI 助手"),
        NodeDef(id="search", type="tool", config={"tool_name": "tavily_search"}),
        NodeDef(id="rag", type="rag"),
    ],
    edges=[EdgeDef(source="agent", target="search"), EdgeDef(source="search", target="rag")],
    entry_point="agent",
)

valid, warnings = validate_for_dify(graph3)
print(f"验证结果: {'✅ 通过' if valid else '❌ 失败'}")
if warnings:
    for w in warnings:
        print(f"  ⚠️  {w}")

output3 = export_to_dify(graph3, "完整AI助手", Path("test_with_rag.yml"))
print(f"✅ 已生成: {output3} ({output3.stat().st_size} 字节)")

# 总结
print("\n" + "=" * 60)
print("📊 测试总结")
print("=" * 60)
print(f"✅ 测试 1 (简单LLM): {output1.name} - {output1.stat().st_size} 字节")
print(f"✅ 测试 2 (LLM+Tool): {output2.name} - {output2.stat().st_size} 字节")
print(f"✅ 测试 3 (LLM+Tool+RAG): {output3.name} - {output3.stat().st_size} 字节")

print("\n💡 导入说明:")
print("   1. 访问 https://cloud.dify.ai")
print("   2. 创建应用 → Chatflow")
print("   3. 导入 DSL → 上传生成的 YAML 文件")
print("   4. 对于包含 RAG 的导出，需要手动添加 Knowledge Retrieval 节点")

print("\n" + "=" * 60)
