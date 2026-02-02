"""
测试 README 自动生成功能

根据 Graph 结构自动生成完整的 README.md 文档
"""

from pathlib import Path
from src.utils.readme_generator import generate_readme
from src.schemas import GraphStructure, NodeDef, EdgeDef, PatternConfig, StateSchema, StateField

print("=" * 60)
print("🧪 测试 README 自动生成功能")
print("=" * 60)

# 创建一个更完整的示例 Graph
print("\n1️⃣ 创建示例 Graph...")
graph = GraphStructure(
    pattern=PatternConfig(
        pattern_type="reflection",
        description="这是一个带反思机制的 AI Agent，可以自我改进和优化回答",
        max_iterations=3,
    ),
    state_schema=StateSchema(
        fields=[
            StateField(name="query", type="str", description="用户查询"),
            StateField(name="response", type="str", description="Agent 响应"),
            StateField(name="reflection", type="str", description="反思结果"),
        ]
    ),
    nodes=[
        NodeDef(
            id="agent",
            type="llm",
            role_description="主要的 LLM Agent，负责理解用户需求并生成初步回答",
        ),
        NodeDef(id="reflect", type="llm", role_description="反思节点，评估回答质量并提出改进建议"),
        NodeDef(
            id="search",
            type="tool",
            config={"tool_name": "tavily_search"},
            role_description="搜索工具，用于获取最新信息",
        ),
        NodeDef(id="rag", type="rag", role_description="知识库检索，从本地文档中查找相关信息"),
    ],
    edges=[
        EdgeDef(source="agent", target="search"),
        EdgeDef(source="search", target="rag"),
        EdgeDef(source="rag", target="reflect"),
    ],
    entry_point="agent",
)
print("✅ Graph 创建成功")
print(f"   节点数: {len(graph.nodes)}")
print(f"   边数: {len(graph.edges)}")
print(f"   状态字段数: {len(graph.state_schema.fields)}")

# 准备测试结果数据
print("\n2️⃣ 准备测试结果数据...")
test_results = {"pass_rate": 95.5, "avg_response_time": 1250}
print(f"✅ 测试通过率: {test_results['pass_rate']}%")
print(f"✅ 平均响应时间: {test_results['avg_response_time']}ms")

# 准备 RAG 配置数据
print("\n3️⃣ 准备 RAG 配置数据...")
rag_config = {"chunk_size": 500, "k_retrieval": 3, "splitter": "recursive"}
print(f"✅ Chunk Size: {rag_config['chunk_size']}")
print(f"✅ K Retrieval: {rag_config['k_retrieval']}")

# 生成 README
print("\n4️⃣ 生成 README.md...")
output_path = Path("TEST_README.md")

try:
    readme_path = generate_readme(
        agent_name="测试Agent",
        graph=graph,
        output_path=output_path,
        test_results=test_results,
        rag_config=rag_config,
    )

    print(f"✅ README 生成成功!")
    print(f"   文件位置: {readme_path.absolute()}")

    # 显示文件大小
    file_size = readme_path.stat().st_size
    print(f"   文件大小: {file_size} 字节")

    # 显示内容
    print("\n5️⃣ README 内容预览:")
    print("=" * 60)
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

        # 显示前 50 行
        for i, line in enumerate(lines[:50], 1):
            print(f"{i:3d} | {line}")

        if len(lines) > 50:
            print(f"\n... (还有 {len(lines) - 50} 行)")
    print("=" * 60)

    # 统计信息
    print("\n6️⃣ README 统计信息:")
    print(f"   总行数: {len(lines)}")
    print(f"   总字符数: {len(content)}")

    # 检查关键部分
    print("\n7️⃣ 检查关键部分:")
    key_sections = [
        "# 测试Agent",
        "## 🏗️ 架构",
        "## 🚀 快速开始",
        "## 🧪 运行测试",
        "## 📤 导出到 Dify",
        "```mermaid",
    ]

    for section in key_sections:
        if section in content:
            print(f"   ✅ {section}")
        else:
            print(f"   ❌ {section} (未找到)")

    print("\n✅ 测试完成！")
    print(f"\n💡 提示: 你可以打开 {output_path} 查看完整的 README")

except Exception as e:
    print(f"❌ 生成失败: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
