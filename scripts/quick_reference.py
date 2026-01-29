"""
🚀 Phase 5 功能快速参考

这是一个快速参考脚本，展示所有核心功能的使用方法
"""

from pathlib import Path
from src.schemas import GraphStructure, NodeDef, EdgeDef, PatternConfig, StateSchema, StateField
from src.exporters import export_to_dify, validate_for_dify
from src.utils.export_utils import export_to_zip
from src.utils.readme_generator import generate_readme

print("="*70)
print("🚀 Agent Zero Phase 5 - 功能快速参考")
print("="*70)

# ============================================================
# 1. 创建一个简单的 Graph
# ============================================================
print("\n【1】创建 Graph")
print("-"*70)

graph = GraphStructure(
    pattern=PatternConfig(
        pattern_type='sequential',
        description='智能助手 Agent',
        max_iterations=5
    ),
    state_schema=StateSchema(
        fields=[
            StateField(name='messages', type='List[BaseMessage]', description='对话历史')
        ]
    ),
    nodes=[
        NodeDef(id='agent', type='llm', role_description='主 AI 助手'),
        NodeDef(id='search', type='tool', config={'tool_name': 'tavily_search'})
    ],
    edges=[
        EdgeDef(source='agent', target='search')
    ],
    entry_point='agent'
)

print("✅ Graph 创建完成")
print(f"   - 节点数: {len(graph.nodes)}")
print(f"   - 边数: {len(graph.edges)}")
print(f"   - 入口点: {graph.entry_point}")

# ============================================================
# 2. 验证 Graph（导出前检查）
# ============================================================
print("\n【2】验证 Graph")
print("-"*70)

valid, warnings = validate_for_dify(graph)
print(f"验证结果: {'✅ 通过' if valid else '❌ 失败'}")

if warnings:
    print("\n警告信息:")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")
else:
    print("  无警告")

# ============================================================
# 3. 导出到 Dify
# ============================================================
print("\n【3】导出到 Dify")
print("-"*70)

output_dir = Path('quick_test_output')
output_dir.mkdir(exist_ok=True)

dify_path = export_to_dify(
    graph=graph,
    agent_name='快速测试Agent',
    output_path=output_dir / 'quick_test_dify.yml'
)

print(f"✅ Dify YAML 已生成")
print(f"   路径: {dify_path}")
print(f"   大小: {dify_path.stat().st_size} 字节")

# ============================================================
# 4. 生成 README
# ============================================================
print("\n【4】生成 README")
print("-"*70)

readme_path = generate_readme(
    agent_name='快速测试Agent',
    graph=graph,
    output_path=output_dir / 'README.md',
    test_results={'total': 5, 'passed': 5, 'failed': 0}
)

print(f"✅ README 已生成")
print(f"   路径: {readme_path}")
print(f"   大小: {readme_path.stat().st_size} 字节")

# ============================================================
# 5. 查看生成的文件
# ============================================================
print("\n【5】生成的文件")
print("-"*70)

files = list(output_dir.glob('*'))
for file in files:
    size_kb = file.stat().st_size / 1024
    print(f"  📄 {file.name} ({size_kb:.2f} KB)")

# ============================================================
# 6. 显示 YAML 内容（前 30 行）
# ============================================================
print("\n【6】YAML 内容预览（前 30 行）")
print("-"*70)

with open(dify_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:30], 1):
        print(f"{i:3d} | {line.rstrip()}")

if len(lines) > 30:
    print(f"... (还有 {len(lines) - 30} 行)")

# ============================================================
# 总结
# ============================================================
print("\n" + "="*70)
print("📊 快速参考总结")
print("="*70)

print("""
✅ 核心功能演示完成！

📦 生成的文件:
  - quick_test_dify.yml  (Dify 导出文件)
  - README.md            (自动生成的文档)

🎯 下一步操作:

1️⃣  导入到 Dify:
   - 访问 https://cloud.dify.ai
   - 创建应用 → Chatflow
   - 导入 DSL → 上传 quick_test_dify.yml

2️⃣  查看文档:
   - 打开 quick_test_output/README.md

3️⃣  集成到你的代码:
   - 参考 PHASE5_INTEGRATION_GUIDE.md
   - 查看示例代码

📚 相关文档:
  - PHASE5_INTEGRATION_GUIDE.md  (完整集成指南)
  - Phase5完成总结.md            (功能总览)
  - DIFY_RAG_FIX.md              (RAG 节点说明)

💡 常用 API:

  # 导出到 Dify
  from src.exporters import export_to_dify
  export_to_dify(graph, 'MyAgent', 'output.yml')

  # 验证 Graph
  from src.exporters import validate_for_dify
  valid, warnings = validate_for_dify(graph)

  # 生成 README
  from src.utils.readme_generator import generate_readme
  generate_readme(agent_name, description, graph, output_path)

  # ZIP 打包
  from src.utils.export_utils import export_to_zip
  export_to_zip(agent_path, output_path)

🎉 Phase 5 功能已就绪，开始使用吧！
""")

print("="*70)
