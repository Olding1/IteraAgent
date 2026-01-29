"""
Graph 可视化组件

提供 LangGraph 结构的可视化展示，支持 Mermaid 图表渲染
"""

import streamlit as st
from typing import Dict, List, Optional
from ...schemas.graph_structure import GraphStructure, NodeDef


class GraphVisualizer:
    """Graph 可视化组件"""

    # 节点类型对应的 emoji 和样式
    NODE_TYPE_CONFIG = {
        "llm": {"emoji": "🤖", "style": "fill:#e1f5ff,stroke:#01579b,stroke-width:2px"},
        "tool": {"emoji": "🔧", "style": "fill:#fff3e0,stroke:#e65100,stroke-width:2px"},
        "rag": {"emoji": "📚", "style": "fill:#f3e5f5,stroke:#4a148c,stroke-width:2px"},
        "conditional": {"emoji": "🔀", "style": "fill:#fff9c4,stroke:#f57f17,stroke-width:2px"},
        "custom": {"emoji": "📦", "style": "fill:#e0e0e0,stroke:#424242,stroke-width:2px"},
    }

    @staticmethod
    def render_mermaid(graph: GraphStructure) -> str:
        """
        生成 Mermaid 图表代码

        Args:
            graph: Graph 结构

        Returns:
            Mermaid 代码字符串
        """
        lines = ["graph TD"]

        # 添加节点定义
        for node in graph.nodes:
            config = GraphVisualizer.NODE_TYPE_CONFIG.get(
                node.type, {"emoji": "📦", "style": ""}
            )
            emoji = config["emoji"]

            # 节点标签：emoji + ID
            node_label = f"{emoji} {node.id}"

            # 根据节点类型选择形状
            if node.type == "conditional":
                # 条件节点使用菱形
                lines.append(f'    {node.id}{{{node_label}}}')
            elif node.type == "llm":
                # LLM 节点使用圆角矩形
                lines.append(f'    {node.id}([{node_label}])')
            else:
                # 其他节点使用矩形
                lines.append(f'    {node.id}[{node_label}]')

            # 添加样式
            if config["style"]:
                lines.append(f'    style {node.id} {config["style"]}')

        # 添加普通边
        for edge in graph.edges:
            lines.append(f"    {edge.source} --> {edge.target}")

        # 添加条件边
        for cond_edge in graph.conditional_edges:
            for key, target in cond_edge.branches.items():
                # 处理 END 节点
                if target == "END":
                    # 创建一个虚拟的 END 节点
                    if "END" not in [node.id for node in graph.nodes]:
                        lines.insert(1, '    END([🏁 END])')
                        lines.insert(2, '    style END fill:#ffebee,stroke:#c62828,stroke-width:2px')
                    label = "结束" if key == "end" else key
                    lines.append(f'    {cond_edge.source} -->|{label}| END')
                else:
                    label = key
                    lines.append(f'    {cond_edge.source} -->|{label}| {target}')

        return "\n".join(lines)

    @staticmethod
    def display(graph: GraphStructure, height: int = 600):
        """
        显示 Graph 可视化

        Args:
            graph: Graph 结构
            height: 图表高度（像素）
        """
        st.subheader("📊 Agent Graph 结构")

        # 生成 Mermaid 代码
        mermaid_code = GraphVisualizer.render_mermaid(graph)

        # 使用 tabs 显示代码和图表
        tab1, tab2 = st.tabs(["📈 图表", "📝 Mermaid 代码"])

        with tab1:
            # 使用 st.components 渲染 Mermaid
            try:
                import streamlit.components.v1 as components

                mermaid_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                    <script>
                        mermaid.initialize({{
                            startOnLoad: true,
                            theme: 'default',
                            flowchart: {{
                                useMaxWidth: true,
                                htmlLabels: true,
                                curve: 'basis'
                            }}
                        }});
                    </script>
                </head>
                <body>
                    <div class="mermaid">
                        {mermaid_code}
                    </div>
                </body>
                </html>
                """

                components.html(mermaid_html, height=height, scrolling=True)
            except Exception as e:
                st.error(f"渲染图表失败: {e}")
                st.info("💡 提示: 请查看 'Mermaid 代码' 标签页复制代码到 Mermaid 在线编辑器")

        with tab2:
            st.code(mermaid_code, language="mermaid")
            st.caption("💡 可以复制代码到 [Mermaid Live Editor](https://mermaid.live) 查看")

    @staticmethod
    def display_node_details(graph: GraphStructure):
        """
        显示节点详细信息

        Args:
            graph: Graph 结构
        """
        st.subheader("🔍 节点详情")

        for node in graph.nodes:
            config = GraphVisualizer.NODE_TYPE_CONFIG.get(
                node.type, {"emoji": "📦", "style": ""}
            )

            with st.expander(f"{config['emoji']} {node.id} ({node.type})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**节点 ID:**")
                    st.code(node.id)

                    st.markdown("**节点类型:**")
                    st.code(node.type)

                with col2:
                    if node.role_description:
                        st.markdown("**角色描述:**")
                        st.text_area(
                            "角色描述",
                            node.role_description,
                            height=100,
                            key=f"role_{node.id}",
                            label_visibility="collapsed"
                        )

                if node.config:
                    st.markdown("**配置信息:**")
                    st.json(node.config)

    @staticmethod
    def display_edge_details(graph: GraphStructure):
        """
        显示边详细信息

        Args:
            graph: Graph 结构
        """
        st.subheader("🔗 连接详情")

        # 普通边
        if graph.edges:
            st.markdown("**普通边:**")
            for i, edge in enumerate(graph.edges, 1):
                st.text(f"{i}. {edge.source} → {edge.target}")

        # 条件边
        if graph.conditional_edges:
            st.markdown("**条件边:**")
            for i, cond_edge in enumerate(graph.conditional_edges, 1):
                st.markdown(f"**{i}. 条件: {cond_edge.condition}**")
                st.text(f"   源节点: {cond_edge.source}")

                if cond_edge.condition_logic:
                    with st.expander("查看条件逻辑"):
                        st.code(cond_edge.condition_logic, language="python")

                st.text("   分支:")
                for key, target in cond_edge.branches.items():
                    st.text(f"      • {key} → {target}")

    @staticmethod
    def display_pattern_info(graph: GraphStructure):
        """
        显示设计模式信息

        Args:
            graph: Graph 结构
        """
        st.subheader("🎨 设计模式")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("模式类型", graph.pattern.pattern_type)

        with col2:
            st.metric("最大迭代次数", graph.pattern.max_iterations or "无限制")

        with col3:
            st.metric("节点数量", len(graph.nodes))

        if graph.pattern.description:
            st.markdown("**模式描述:**")
            st.info(graph.pattern.description)

    @staticmethod
    def display_state_schema(graph: GraphStructure):
        """
        显示状态 Schema 信息

        Args:
            graph: Graph 结构
        """
        st.subheader("📋 状态 Schema")

        if not graph.state_schema.fields:
            st.info("无状态字段定义")
            return

        # 创建表格数据
        table_data = []
        for field in graph.state_schema.fields:
            table_data.append({
                "字段名": field.name,
                "类型": field.type,
                "描述": field.description or "-",
                "Reducer": field.reducer or "default"
            })

        st.table(table_data)

    @staticmethod
    def display_full_graph_info(graph: GraphStructure):
        """
        显示完整的 Graph 信息（包含所有细节）

        Args:
            graph: Graph 结构
        """
        # 设计模式信息
        GraphVisualizer.display_pattern_info(graph)

        st.divider()

        # Graph 可视化
        GraphVisualizer.display(graph)

        st.divider()

        # 节点详情
        GraphVisualizer.display_node_details(graph)

        st.divider()

        # 边详情
        GraphVisualizer.display_edge_details(graph)

        st.divider()

        # 状态 Schema
        GraphVisualizer.display_state_schema(graph)


# 便捷函数
def visualize_graph(graph: GraphStructure, height: int = 600):
    """
    快速可视化 Graph

    Args:
        graph: Graph 结构
        height: 图表高度
    """
    GraphVisualizer.display(graph, height)


def show_full_graph_info(graph: GraphStructure):
    """
    显示完整的 Graph 信息

    Args:
        graph: Graph 结构
    """
    GraphVisualizer.display_full_graph_info(graph)
