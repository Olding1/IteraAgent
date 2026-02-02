"""
Phase 5 功能使用示例

演示如何使用 Phase 5 新增的 UI 组件、HITL 控制和导出功能
"""

import streamlit as st
from pathlib import Path


# 示例 1: 使用日志查看器
def example_log_viewer():
    """日志查看器示例"""
    st.header("示例 1: 日志查看器")

    from src.ui.components import LogViewer, log_info, log_warning, log_error, log_success

    # 创建日志查看器
    if "log_viewer" not in st.session_state:
        st.session_state.log_viewer = LogViewer()

    # 添加一些示例日志
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("添加 INFO"):
            log_info("这是一条信息日志")

    with col2:
        if st.button("添加 WARNING"):
            log_warning("这是一条警告日志")

    with col3:
        if st.button("添加 ERROR"):
            log_error("这是一条错误日志")

    with col4:
        if st.button("添加 SUCCESS"):
            log_success("这是一条成功日志")

    # 渲染日志查看器
    st.session_state.log_viewer.render(height=300, enable_filter=True, auto_scroll=True)


# 示例 2: Graph 可视化
def example_graph_visualizer():
    """Graph 可视化示例"""
    st.header("示例 2: Graph 可视化")

    from src.ui.components import visualize_graph
    from src.schemas import GraphStructure, NodeDef, EdgeDef, PatternConfig, StateSchema

    # 创建一个示例 Graph
    graph = GraphStructure(
        pattern=PatternConfig(
            pattern_type="sequential", description="简单的顺序执行模式", max_iterations=1
        ),
        state_schema=StateSchema(fields=[]),
        nodes=[
            NodeDef(id="agent", type="llm", role_description="主要的 LLM 节点"),
            NodeDef(id="search", type="tool", config={"tool_name": "tavily_search"}),
            NodeDef(id="rag", type="rag"),
        ],
        edges=[EdgeDef(source="agent", target="search"), EdgeDef(source="search", target="rag")],
        entry_point="agent",
    )

    # 可视化
    visualize_graph(graph, height=400)


# 示例 3: Token 统计
def example_token_stats():
    """Token 统计示例"""
    st.header("示例 3: Token 统计")

    from src.ui.components import show_token_stats

    # 模拟统计数据
    stats = {
        "total_calls": 15,
        "total_input_tokens": 12500,
        "total_output_tokens": 3800,
        "total_cost_usd": 0.0725,
    }

    # 显示统计
    show_token_stats(stats, mode="full")


# 示例 4: Blueprint Review
def example_blueprint_review():
    """Blueprint Review 示例"""
    st.header("示例 4: Blueprint Review")

    from src.ui.pages import show_blueprint_review
    from src.schemas import GraphStructure, NodeDef, PatternConfig, StateSchema

    # 创建示例 Graph
    graph = GraphStructure(
        pattern=PatternConfig(
            pattern_type="reflection", description="带反思的执行模式", max_iterations=3
        ),
        state_schema=StateSchema(fields=[]),
        nodes=[
            NodeDef(id="agent", type="llm", role_description="主 Agent"),
            NodeDef(id="reflect", type="llm", role_description="反思节点"),
        ],
        edges=[EdgeDef(source="agent", target="reflect")],
        entry_point="agent",
    )

    # 显示审查页面
    approved, feedback = show_blueprint_review(graph=graph, agent_name="示例 Agent")

    if approved is not None:
        if approved:
            st.success(f"✅ 用户批准了蓝图！反馈: {feedback or '无'}")
        else:
            st.error(f"❌ 用户拒绝了蓝图。反馈: {feedback}")


# 示例 5: 导出功能
def example_export():
    """导出功能示例"""
    st.header("示例 5: 导出功能")

    st.subheader("5.1 ZIP 导出")

    agent_path = st.text_input("Agent 路径", "agents/AI新闻每日摘要生成器")

    if st.button("导出为 ZIP"):
        from src.utils.export_utils import export_to_zip, get_agent_size

        try:
            # 获取大小
            size = get_agent_size(Path(agent_path))
            st.info(f"Agent 大小: {size}")

            # 导出
            output_path = Path("exports") / f"{Path(agent_path).name}.zip"
            zip_path = export_to_zip(Path(agent_path), output_path)

            st.success(f"✅ 导出成功: {zip_path}")

            # 提供下载
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="⬇️ 下载 ZIP", data=f, file_name=zip_path.name, mime="application/zip"
                )
        except Exception as e:
            st.error(f"❌ 导出失败: {e}")

    st.divider()

    st.subheader("5.2 Dify YAML 导出")

    if st.button("导出为 Dify YAML"):
        from src.exporters import export_to_dify, validate_for_dify
        from src.schemas import GraphStructure, NodeDef, PatternConfig, StateSchema

        # 创建示例 Graph
        graph = GraphStructure(
            pattern=PatternConfig(
                pattern_type="sequential", description="示例 Agent", max_iterations=1
            ),
            state_schema=StateSchema(fields=[]),
            nodes=[
                NodeDef(id="agent", type="llm", role_description="主 Agent"),
                NodeDef(id="search", type="tool", config={"tool_name": "tavily_search"}),
            ],
            edges=[EdgeDef(source="agent", target="search")],
            entry_point="agent",
        )

        # 验证
        valid, warnings = validate_for_dify(graph)

        if warnings:
            st.warning("⚠️ 警告:")
            for warning in warnings:
                st.text(f"  • {warning}")

        # 导出
        try:
            output_path = Path("exports") / "example_dify.yml"
            dify_path = export_to_dify(graph, "示例Agent", output_path)

            st.success(f"✅ Dify YAML 导出成功: {dify_path}")

            # 显示内容
            with open(dify_path, "r", encoding="utf-8") as f:
                yaml_content = f.read()

            st.code(yaml_content, language="yaml")

            # 提供下载
            st.download_button(
                label="⬇️ 下载 Dify YAML",
                data=yaml_content,
                file_name="example_dify.yml",
                mime="text/yaml",
            )
        except Exception as e:
            st.error(f"❌ 导出失败: {e}")


# 主函数
def main():
    st.title("🚀 Agent Zero Phase 5 功能演示")

    st.markdown(
        """
    本页面演示 Phase 5 新增的功能：
    - 🎨 UI 组件（日志、图表、统计）
    - 📐 Blueprint Review
    - 📦 导出功能（ZIP、Dify YAML）
    """
    )

    st.divider()

    # 选择示例
    example = st.selectbox(
        "选择示例", ["日志查看器", "Graph 可视化", "Token 统计", "Blueprint Review", "导出功能"]
    )

    st.divider()

    # 运行对应示例
    if example == "日志查看器":
        example_log_viewer()
    elif example == "Graph 可视化":
        example_graph_visualizer()
    elif example == "Token 统计":
        example_token_stats()
    elif example == "Blueprint Review":
        example_blueprint_review()
    elif example == "导出功能":
        example_export()


if __name__ == "__main__":
    main()
