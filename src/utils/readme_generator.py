"""
README 生成器

自动生成 Agent 的 README.md 文档
"""

from jinja2 import Template
from pathlib import Path
from typing import Dict, Optional
from ..schemas.graph_structure import GraphStructure


class ReadmeGenerator:
    """README 生成器"""

    @staticmethod
    def generate(
        agent_name: str,
        graph: GraphStructure,
        output_path: Path,
        test_results: Optional[Dict] = None,
        rag_config: Optional[Dict] = None
    ) -> Path:
        """
        生成 README.md

        Args:
            agent_name: Agent 名称
            graph: Graph 结构
            output_path: 输出文件路径
            test_results: 测试结果（可选）
            rag_config: RAG 配置（可选）

        Returns:
            输出文件路径
        """
        # 加载模板
        template_path = Path(__file__).parent.parent / "templates" / "readme_template.md.j2"

        with open(template_path, 'r', encoding='utf-8') as f:
            template = Template(f.read())

        # 生成 Mermaid 图
        mermaid_graph = ReadmeGenerator._generate_mermaid(graph)

        # 提取工具列表
        tools = [node.id for node in graph.nodes if node.type == "tool"]

        # 检查是否有 RAG
        has_rag = any(node.type == "rag" for node in graph.nodes)

        # 准备测试结果
        pass_rate = test_results.get("pass_rate", 0) if test_results else 0
        avg_response_time = test_results.get("avg_response_time", 0) if test_results else 0

        # 渲染模板
        readme_content = template.render(
            agent_name=agent_name,
            description=graph.pattern.description or f"{agent_name} - AI Agent",
            pattern=graph.pattern,
            mermaid_graph=mermaid_graph,
            pass_rate=pass_rate,
            avg_response_time=avg_response_time,
            has_rag=has_rag,
            rag_config=rag_config or {},
            tools=tools
        )

        # 写入文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        return output_path

    @staticmethod
    def _generate_mermaid(graph: GraphStructure) -> str:
        """
        生成 Mermaid 图表代码

        Args:
            graph: Graph 结构

        Returns:
            Mermaid 代码
        """
        lines = ["graph TD"]

        # 节点类型配置
        node_type_emoji = {
            "llm": "🤖",
            "tool": "🔧",
            "rag": "📚",
            "conditional": "🔀",
            "custom": "📦"
        }

        # 添加节点
        for node in graph.nodes:
            emoji = node_type_emoji.get(node.type, "📦")
            node_label = f"{emoji} {node.id}"

            # 根据类型选择形状
            if node.type == "conditional":
                lines.append(f'    {node.id}{{{node_label}}}')
            elif node.type == "llm":
                lines.append(f'    {node.id}([{node_label}])')
            else:
                lines.append(f'    {node.id}[{node_label}]')

        # 添加普通边
        for edge in graph.edges:
            lines.append(f"    {edge.source} --> {edge.target}")

        # 添加条件边
        for cond_edge in graph.conditional_edges:
            for key, target in cond_edge.branches.items():
                if target == "END":
                    # 创建 END 节点
                    if "END" not in [node.id for node in graph.nodes]:
                        lines.insert(1, '    END([🏁 END])')
                    label = "结束" if key == "end" else key
                    lines.append(f'    {cond_edge.source} -->|{label}| END')
                else:
                    lines.append(f'    {cond_edge.source} -->|{key}| {target}')

        return "\n".join(lines)


# 便捷函数
def generate_readme(
    agent_name: str,
    graph: GraphStructure,
    output_path: Path,
    test_results: Optional[Dict] = None,
    rag_config: Optional[Dict] = None
) -> Path:
    """
    生成 README.md

    Args:
        agent_name: Agent 名称
        graph: Graph 结构
        output_path: 输出文件路径
        test_results: 测试结果（可选）
        rag_config: RAG 配置（可选）

    Returns:
        输出文件路径
    """
    return ReadmeGenerator.generate(
        agent_name=agent_name,
        graph=graph,
        output_path=output_path,
        test_results=test_results,
        rag_config=rag_config
    )
