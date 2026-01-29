"""
创建中等复杂度的 Dify YAML（LLM + Tool，不包含 RAG）
"""

from pathlib import Path
from src.exporters import export_to_dify
from src.schemas import GraphStructure, NodeDef, EdgeDef, PatternConfig, StateSchema, StateField

print("="*60)
print("🧪 创建中等复杂度的 Dify YAML")
print("="*60)

# 创建 Graph（LLM + Tool）
print("\n1️⃣ 创建 Graph（LLM + Tool）...")
graph = GraphStructure(
    pattern=PatternConfig(
        pattern_type='sequential',
        description='带搜索功能的 AI 助手',
        max_iterations=1
    ),
    state_schema=StateSchema(
        fields=[StateField(name='messages', type='List[BaseMessage]', description='对话历史')]
    ),
    nodes=[
        NodeDef(id='agent', type='llm', role_description='主 AI 助手，负责理解用户需求'),
        NodeDef(id='search', type='tool', config={'tool_name': 'tavily_search'})
    ],
    edges=[
        EdgeDef(source='agent', target='search')
    ],
    entry_point='agent'
)
print("✅ Graph 创建成功")

# 导出
print("\n2️⃣ 导出为 Dify YAML...")
output_path = Path('medium_dify.yml')
dify_path = export_to_dify(graph, '带搜索的AI助手', output_path)

print(f"✅ 中等复杂度 YAML 已生成: {dify_path}")
print(f"   文件大小: {dify_path.stat().st_size} 字节")

# 显示内容
print("\n3️⃣ YAML 内容:")
print("-"*60)
with open(dify_path, 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)
print("-"*60)

print("\n✅ 完成！")
print("\n💡 使用方法:")
print("   1. 访问 https://cloud.dify.ai")
print("   2. 创建应用 → Chatflow")
print("   3. 导入 DSL → 上传 medium_dify.yml")
print("   4. 如果成功，说明问题出在 RAG 节点")

print("\n" + "="*60)
