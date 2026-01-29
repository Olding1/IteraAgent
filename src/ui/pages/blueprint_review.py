"""
Blueprint Review UI 页面

提供 Graph 结构的审查界面，允许用户在编译前审查和批准蓝图
"""

import streamlit as st
from typing import Optional, Tuple
from ...schemas.graph_structure import GraphStructure
from ...schemas.simulation_result import SimulationResult
from ..components.graph_visualizer import GraphVisualizer


class BlueprintReviewPage:
    """Blueprint 审查页面"""

    @staticmethod
    def show(
        graph: GraphStructure,
        simulation: Optional[SimulationResult] = None,
        agent_name: str = "Agent"
    ) -> Tuple[bool, Optional[str]]:
        """
        显示 Blueprint 审查页面

        Args:
            graph: Graph 结构
            simulation: 仿真结果（可选）
            agent_name: Agent 名称

        Returns:
            (是否批准, 反馈信息)
        """
        st.title(f"📐 Blueprint 审查 - {agent_name}")

        st.info("💡 请仔细审查 Agent 的设计蓝图，确认无误后点击批准按钮")

        # 创建 tabs
        tabs = st.tabs(["📊 Graph 结构", "🎬 仿真结果", "⚙️ 配置信息", "📋 完整信息"])

        # Tab 1: Graph 结构
        with tabs[0]:
            BlueprintReviewPage._show_graph_tab(graph)

        # Tab 2: 仿真结果
        with tabs[1]:
            if simulation:
                BlueprintReviewPage._show_simulation_tab(simulation)
            else:
                st.info("未提供仿真结果")

        # Tab 3: 配置信息
        with tabs[2]:
            BlueprintReviewPage._show_config_tab(graph)

        # Tab 4: 完整信息
        with tabs[3]:
            BlueprintReviewPage._show_full_info_tab(graph, simulation)

        st.divider()

        # 审批区域
        return BlueprintReviewPage._show_approval_section()

    @staticmethod
    def _show_graph_tab(graph: GraphStructure):
        """显示 Graph 结构 Tab"""
        # 使用 GraphVisualizer 显示图表
        GraphVisualizer.display(graph, height=600)

        st.divider()

        # 节点详情
        GraphVisualizer.display_node_details(graph)

        st.divider()

        # 边详情
        GraphVisualizer.display_edge_details(graph)

    @staticmethod
    def _show_simulation_tab(simulation: SimulationResult):
        """显示仿真结果 Tab"""
        st.subheader("🎬 仿真执行轨迹")

        # 显示执行轨迹
        if simulation.execution_trace:
            st.text_area(
                "执行轨迹",
                simulation.execution_trace,
                height=400,
                label_visibility="collapsed"
            )
        else:
            st.info("无执行轨迹")

        st.divider()

        # 显示问题
        if simulation.issues:
            st.warning(f"⚠️ 发现 {len(simulation.issues)} 个问题")

            for i, issue in enumerate(simulation.issues, 1):
                severity_emoji = {
                    "critical": "🔴",
                    "warning": "🟡",
                    "info": "🔵"
                }
                emoji = severity_emoji.get(issue.severity, "⚪")

                with st.expander(f"{emoji} 问题 {i}: {issue.description[:50]}..."):
                    st.markdown(f"**严重程度:** {issue.severity}")
                    st.markdown(f"**描述:** {issue.description}")

                    if issue.location:
                        st.markdown(f"**位置:** {issue.location}")

                    if issue.suggestion:
                        st.markdown(f"**建议:** {issue.suggestion}")
        else:
            st.success("✅ 未发现问题")

    @staticmethod
    def _show_config_tab(graph: GraphStructure):
        """显示配置信息 Tab"""
        # 设计模式
        GraphVisualizer.display_pattern_info(graph)

        st.divider()

        # 状态 Schema
        GraphVisualizer.display_state_schema(graph)

        st.divider()

        # 统计信息
        st.subheader("📈 统计信息")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("节点数量", len(graph.nodes))

        with col2:
            st.metric("普通边数量", len(graph.edges))

        with col3:
            st.metric("条件边数量", len(graph.conditional_edges))

        with col4:
            st.metric("状态字段数量", len(graph.state_schema.fields))

        # 节点类型分布
        st.subheader("🔍 节点类型分布")

        node_types = {}
        for node in graph.nodes:
            node_types[node.type] = node_types.get(node.type, 0) + 1

        for node_type, count in node_types.items():
            st.text(f"• {node_type}: {count}")

    @staticmethod
    def _show_full_info_tab(graph: GraphStructure, simulation: Optional[SimulationResult]):
        """显示完整信息 Tab"""
        st.subheader("📄 完整 JSON 数据")

        # Graph JSON
        with st.expander("Graph 结构 JSON", expanded=False):
            st.json(graph.model_dump())

        # Simulation JSON
        if simulation:
            with st.expander("仿真结果 JSON", expanded=False):
                st.json(simulation.model_dump())

    @staticmethod
    def _show_approval_section() -> Tuple[bool, Optional[str]]:
        """
        显示审批区域

        Returns:
            (是否批准, 反馈信息)
        """
        st.subheader("✅ 审批决策")

        # 反馈输入
        feedback = st.text_area(
            "反馈信息（可选）",
            placeholder="如果拒绝，请说明原因或提出修改建议...",
            height=100
        )

        # 按钮
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            approve_btn = st.button("✅ 批准并构建", type="primary", use_container_width=True)

        with col2:
            reject_btn = st.button("❌ 拒绝", type="secondary", use_container_width=True)

        with col3:
            st.caption("批准后将开始编译和构建 Agent")

        # 处理按钮点击
        if approve_btn:
            return (True, feedback if feedback else None)
        elif reject_btn:
            return (False, feedback if feedback else "用户拒绝")
        else:
            return (None, None)


# 便捷函数
def show_blueprint_review(
    graph: GraphStructure,
    simulation: Optional[SimulationResult] = None,
    agent_name: str = "Agent"
) -> Tuple[bool, Optional[str]]:
    """
    显示 Blueprint 审查页面

    Args:
        graph: Graph 结构
        simulation: 仿真结果（可选）
        agent_name: Agent 名称

    Returns:
        (是否批准, 反馈信息)
    """
    return BlueprintReviewPage.show(graph, simulation, agent_name)
