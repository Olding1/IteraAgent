"""
测试 Dify YAML 导出功能

这是 Phase 5 最重要的功能之一
"""

from pathlib import Path
from src.exporters import export_to_dify, validate_for_dify
from src.schemas import GraphStructure, NodeDef, EdgeDef, PatternConfig, StateSchema

print("=" * 60)
print("🧪 测试 Dify YAML 导出功能")
print("=" * 60)

# 创建示例 Graph
print("\n1️⃣ 创建示例 Graph...")
from src.schemas import StateField

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
        NodeDef(id="rag", type="rag", role_description="知识检索节点"),
    ],
    edges=[EdgeDef(source="agent", target="search"), EdgeDef(source="search", target="rag")],
    entry_point="agent",
)
print("✅ Graph 创建成功")

# 验证
print("\n2️⃣ 验证 Graph 是否可以导出为 Dify...")
valid, warnings = validate_for_dify(graph)
print(f"✅ 验证结果: {'有效' if valid else '无效'}")

if warnings:
    print("\n⚠️ 警告信息:")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")

# 导出
print("\n3️⃣ 导出为 Dify YAML...")
output_path = Path("test_dify_export.yml")
try:
    dify_path = export_to_dify(graph, "测试Agent", output_path)
    print(f"✅ Dify YAML 导出成功!")
    print(f"   文件位置: {dify_path.absolute()}")

    # 显示文件大小
    file_size = dify_path.stat().st_size
    print(f"   文件大小: {file_size} 字节")

    # 显示部分内容
    print("\n4️⃣ YAML 文件内容预览:")
    print("-" * 60)
    with open(dify_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # 显示前 30 行
        for i, line in enumerate(lines[:30], 1):
            print(f"{i:3d} | {line}", end="")
        if len(lines) > 30:
            print(f"\n... (还有 {len(lines) - 30} 行)")
    print("-" * 60)

    print("\n✅ 测试完成！")
    print(f"\n💡 提示: 你可以将 {output_path} 导入到 Dify 平台测试")
    print("   Dify 导入步骤:")
    print("   1. 访问 https://cloud.dify.ai")
    print("   2. 创建应用 → Chatflow")
    print("   3. 导入 DSL → 上传此 YAML 文件")

except Exception as e:
    print(f"❌ 导出失败: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
