"""
节点映射器

将 IteraAgent 节点映射为 Dify 节点
"""

from typing import Dict
from ...schemas.graph_structure import NodeDef
from .schema import DifyNode, DifyNodeData


class NodeMapper:
    """IteraAgent -> Dify 节点映射器"""

    # 工具名称映射表
    TOOL_MAPPING = {
        "tavily_search": {"provider_id": "tavily", "tool_name": "tavily_search", "supported": True},
        "duckduckgo_search": {
            "provider_id": "duckduckgo",
            "tool_name": "duckduckgo_search",
            "supported": True,
        },
        "wikipedia": {
            "provider_id": "wikipedia",
            "tool_name": "wikipedia_search",
            "supported": True,
        },
        "google_search": {"provider_id": "google", "tool_name": "google_search", "supported": True},
        "bing_search": {"provider_id": "bing", "tool_name": "bing_search", "supported": True},
        "arxiv": {"provider_id": "arxiv", "tool_name": "arxiv_search", "supported": True},
        "pubmed": {"provider_id": "pubmed", "tool_name": "pubmed_search", "supported": True},
        "wolfram_alpha": {
            "provider_id": "wolframalpha",
            "tool_name": "wolfram_alpha",
            "supported": True,
        },
        "youtube": {"provider_id": "youtube", "tool_name": "youtube_search", "supported": True},
        # 其他工具标记为不支持
    }

    @staticmethod
    def map_llm_node(node: NodeDef, node_id: str, position: Dict[str, int]) -> DifyNode:
        """
        映射 LLM 节点

        Args:
            node: IteraAgent 节点定义
            node_id: Dify 节点 ID
            position: 节点位置

        Returns:
            Dify 节点
        """
        return DifyNode(
            id=node_id,
            data=DifyNodeData(
                title=node.id,
                type="llm",
                desc=node.role_description or "",
                model={"provider": "openai", "name": "gpt-4o"},  # 默认模型
                prompt_template=[
                    {
                        "role": "system",
                        "text": node.role_description or "You are a helpful assistant.",
                    }
                ],
            ),
            position=position,
        )

    @staticmethod
    def map_rag_node(node: NodeDef, node_id: str, position: Dict[str, int]) -> DifyNode:
        """
        映射 RAG 节点

        ⚠️ 注意：由于 Dify 的 knowledge-retrieval 节点在 dataset_ids 为空时会导致前端崩溃，
        我们将 RAG 节点转换为 Code 节点，提示用户手动配置。

        Args:
            node: IteraAgent 节点定义
            node_id: Dify 节点 ID
            position: 节点位置

        Returns:
            Dify 节点（Code 类型，提示用户手动配置）
        """
        return DifyNode(
            id=node_id,
            data=DifyNodeData(
                title="⚠️ Knowledge Retrieval (需配置)",
                type="code",
                desc="⚠️ RAG 节点需要在 Dify 中手动配置知识库。请删除此节点并添加 Knowledge Retrieval 节点。",
                code="# ⚠️ 此节点需要手动配置\n# 步骤:\n# 1. 删除此 Code 节点\n# 2. 添加 Knowledge Retrieval 节点\n# 3. 绑定知识库\n# 4. 连接到下一个节点\nresult = 'Please configure knowledge base'",
                outputs={"result": {"type": "string", "children": None}},
            ),
            position=position,
            width=300,
            height=120,
        )

    @staticmethod
    def map_tool_node(node: NodeDef, node_id: str, position: Dict[str, int]) -> DifyNode:
        """
        映射工具节点

        Args:
            node: IteraAgent 节点定义
            node_id: Dify 节点 ID
            position: 节点位置

        Returns:
            Dify 节点
        """
        tool_name = node.config.get("tool_name") if node.config else node.id

        # 查找映射
        mapping = NodeMapper.TOOL_MAPPING.get(tool_name)

        if mapping and mapping["supported"]:
            # 支持的工具
            return DifyNode(
                id=node_id,
                data=DifyNodeData(
                    title=tool_name,
                    type="tool",
                    provider_id=mapping["provider_id"],
                    tool_name=mapping["tool_name"],
                    tool_parameters={},
                ),
                position=position,
            )
        else:
            # 不支持的工具 - 转为 Code 节点提示
            return DifyNode(
                id=node_id,
                data=DifyNodeData(
                    title=f"⚠️ Unsupported Tool: {tool_name}",
                    type="code",
                    desc=f"IteraAgent 使用了 {tool_name}，但 Dify 不支持。请手动替换为等效工具。",
                    code=f"# TODO: 替换为 Dify 支持的工具\n# 原工具: {tool_name}\nresult = 'Not implemented'",
                    outputs={"result": {"type": "string", "children": None}},
                ),
                position=position,
                width=300,
                height=120,
            )

    @staticmethod
    def map_conditional_node(node: NodeDef, node_id: str, position: Dict[str, int]) -> DifyNode:
        """
        映射条件节点

        Args:
            node: IteraAgent 节点定义
            node_id: Dify 节点 ID
            position: 节点位置

        Returns:
            Dify 节点
        """
        return DifyNode(
            id=node_id,
            data=DifyNodeData(
                title=f"Condition: {node.id}",
                type="if-else",
                desc="条件路由节点",
                conditions=[],  # 将在转换器中填充
            ),
            position=position,
        )

    @staticmethod
    def map_custom_node(node: NodeDef, node_id: str, position: Dict[str, int]) -> DifyNode:
        """
        映射自定义节点

        Args:
            node: IteraAgent 节点定义
            node_id: Dify 节点 ID
            position: 节点位置

        Returns:
            Dify 节点
        """
        return DifyNode(
            id=node_id,
            data=DifyNodeData(
                title=f"Custom: {node.id}",
                type="code",
                desc=f"自定义节点类型: {node.type}",
                code=f"# 自定义节点: {node.id}\n# 类型: {node.type}\nresult = 'Custom node'",
                outputs={"result": {"type": "string", "children": None}},
            ),
            position=position,
        )
