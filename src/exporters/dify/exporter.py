"""
Dify 导出器

提供将 Agent Zero Graph 导出为 Dify YAML 的功能
"""

import yaml
from pathlib import Path
from ...schemas.graph_structure import GraphStructure
from .converter import AgentZeroToDifyConverter


class DifyExporter:
    """Dify 导出器"""

    @staticmethod
    def export_to_yaml(graph: GraphStructure, agent_name: str, output_path: Path) -> Path:
        """
        导出为 Dify YAML

        Args:
            graph: Graph 结构
            agent_name: Agent 名称
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        # 转换
        converter = AgentZeroToDifyConverter(graph, agent_name)
        dify_app = converter.convert()

        # 序列化为 YAML
        yaml_content = yaml.dump(
            dify_app.model_dump(exclude_none=True),
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )

        # 写入文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        return output_path

    @staticmethod
    def export_to_string(graph: GraphStructure, agent_name: str) -> str:
        """
        导出为 YAML 字符串

        Args:
            graph: Graph 结构
            agent_name: Agent 名称

        Returns:
            YAML 字符串
        """
        converter = AgentZeroToDifyConverter(graph, agent_name)
        dify_app = converter.convert()

        return yaml.dump(
            dify_app.model_dump(exclude_none=True),
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )

    @staticmethod
    def validate_graph(graph: GraphStructure) -> tuple[bool, list[str]]:
        """
        验证 Graph 是否可以导出为 Dify

        Args:
            graph: Graph 结构

        Returns:
            (是否有效, 警告列表)
        """
        warnings = []

        # 检查不支持的工具
        from .mapper import NodeMapper

        for node in graph.nodes:
            if node.type == "tool":
                tool_name = node.config.get("tool_name") if node.config else node.id
                mapping = NodeMapper.TOOL_MAPPING.get(tool_name)

                if not mapping or not mapping.get("supported"):
                    warnings.append(f"工具 '{tool_name}' 在 Dify 中不支持，将转换为 Code 节点")

        # 检查 RAG 节点
        has_rag = any(node.type == "rag" for node in graph.nodes)
        if has_rag:
            warnings.append(
                "包含 RAG 节点，将被跳过。导入 Dify 后需要手动添加 Knowledge Retrieval 节点并绑定知识库"
            )

        # 检查复杂条件边
        if graph.conditional_edges:
            warnings.append(
                f"包含 {len(graph.conditional_edges)} 个条件边，将使用 Code Node + If-Else 组合实现"
            )

        # 总是返回 True，因为我们可以转换所有节点（即使有警告）
        return True, warnings


# 便捷函数
def export_to_dify(graph: GraphStructure, agent_name: str, output_path: Path) -> Path:
    """
    导出为 Dify YAML

    Args:
        graph: Graph 结构
        agent_name: Agent 名称
        output_path: 输出文件路径

    Returns:
        输出文件路径
    """
    return DifyExporter.export_to_yaml(graph, agent_name, output_path)


def validate_for_dify(graph: GraphStructure) -> tuple[bool, list[str]]:
    """
    验证是否可以导出为 Dify

    Args:
        graph: Graph 结构

    Returns:
        (是否有效, 警告列表)
    """
    return DifyExporter.validate_graph(graph)
