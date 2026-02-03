"""
Agent Zero Phase 5 - Streamlit UI 演示应用

完整的 Agent 构建、可视化和导出界面
"""

import streamlit as st
from pathlib import Path
from src.ui.components import (
    log_info,
    log_success,
    log_error,
    visualize_graph,
    show_token_stats,
)
from src.schemas import GraphStructure, NodeDef, EdgeDef, PatternConfig, StateSchema, StateField
from src.exporters import export_to_dify, validate_for_dify
from src.utils.readme_generator import generate_readme

# 页面配置
st.set_page_config(page_title="Agent Zero - Phase 5 Demo", page_icon="🤖", layout="wide")

# 初始化 session state
if "graph" not in st.session_state:
    st.session_state.graph = None
if "export_done" not in st.session_state:
    st.session_state.export_done = False

# 标题
st.title("🤖 Agent Zero - Phase 5 功能演示")
st.markdown("---")

# ============================================================
# 侧边栏：Agent 配置
# ============================================================
with st.sidebar:
    st.header("⚙️ Agent 配置")

    # 基本信息
    st.subheader("基本信息")
    agent_name = st.text_input("Agent 名称", "智能助手")
    agent_desc = st.text_area("描述", "这是一个智能助手，可以搜索信息并回答问题")

    # 节点配置
    st.subheader("节点配置")
    use_llm = st.checkbox("LLM 节点", value=True, help="主要的 AI 助手节点")
    use_tool = st.checkbox("Tool 节点", value=True, help="搜索工具节点")
    use_rag = st.checkbox("RAG 节点", value=False, help="知识库检索节点（导出时会被跳过）")

    # 工具选择
    if use_tool:
        tool_name = st.selectbox(
            "选择工具",
            ["tavily_search", "duckduckgo_search", "wikipedia", "google_search"],
            help="选择要使用的搜索工具",
        )
    else:
        tool_name = "tavily_search"

    # 高级配置
    with st.expander("高级配置"):
        max_iterations = st.slider("最大迭代次数", 1, 10, 5)
        pattern_type = st.selectbox("设计模式", ["sequential", "parallel", "conditional"])

    st.markdown("---")

    # 创建按钮
    if st.button("🚀 创建 Agent", type="primary", use_container_width=True):
        st.session_state.create_agent = True
        st.session_state.export_done = False
        st.rerun()

    # 重置按钮
    if st.button("🔄 重置", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ============================================================
# 主区域：分 Tab 显示
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Graph 可视化", "📝 日志", "💰 Token 统计", "📤 导出"])

# Tab 1: Graph 可视化
with tab1:
    st.header("📊 Agent Graph 可视化")

    if "create_agent" in st.session_state and st.session_state.create_agent:
        # 构建 Graph
        nodes = []
        edges = []

        if use_llm:
            nodes.append(
                NodeDef(
                    id="agent",
                    type="llm",
                    role_description=f"{agent_name}，负责理解用户需求并提供帮助",
                )
            )

        if use_tool:
            nodes.append(NodeDef(id="search", type="tool", config={"tool_name": tool_name}))
            if use_llm:
                edges.append(EdgeDef(source="agent", target="search"))

        if use_rag:
            nodes.append(NodeDef(id="knowledge", type="rag"))
            if use_tool:
                edges.append(EdgeDef(source="search", target="knowledge"))
            elif use_llm:
                edges.append(EdgeDef(source="agent", target="knowledge"))

        # 创建 Graph
        graph = GraphStructure(
            pattern=PatternConfig(
                pattern_type=pattern_type, description=agent_desc, max_iterations=max_iterations
            ),
            state_schema=StateSchema(
                fields=[
                    StateField(name="messages", type="List[BaseMessage]", description="对话历史"),
                    StateField(name="user_id", type="str", description="用户ID"),
                ]
            ),
            nodes=nodes,
            edges=edges,
            entry_point="agent" if use_llm else (nodes[0].id if nodes else None),
        )

        st.session_state.graph = graph

        # 可视化
        if graph.nodes:
            visualize_graph(graph, height=500)

            # 显示统计信息
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("节点数", len(graph.nodes))
            with col2:
                st.metric("边数", len(graph.edges))
            with col3:
                st.metric("入口点", graph.entry_point or "无")
            with col4:
                st.metric("最大迭代", max_iterations)

            # 显示节点详情
            with st.expander("📋 节点详情"):
                for i, node in enumerate(graph.nodes, 1):
                    st.markdown(f"**{i}. {node.id}** ({node.type})")
                    if node.role_description:
                        st.caption(f"描述: {node.role_description}")
                    if node.config:
                        st.json(node.config)
                    st.markdown("---")
        else:
            st.warning("⚠️ 请至少选择一个节点类型")
    else:
        st.info("👈 请在侧边栏配置并创建 Agent")

# Tab 2: 日志
with tab2:
    st.header("📝 执行日志")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🧪 模拟执行", use_container_width=True):
            st.session_state.run_simulation = True

    if "run_simulation" in st.session_state and st.session_state.run_simulation:
        log_info(f"开始构建 Agent: {agent_name}")
        log_info(f"设计模式: {pattern_type}")
        log_success("Graph 结构创建完成")

        if use_llm:
            log_info("初始化 LLM 节点...")
            log_success("LLM 节点就绪")

        if use_tool:
            log_info(f"初始化搜索工具: {tool_name}")
            log_success("搜索工具就绪")

        if use_rag:
            log_info("连接知识库...")
            log_success("知识库连接成功")

        log_success(f"✅ {agent_name} 构建完成！")
        st.session_state.run_simulation = False

# Tab 3: Token 统计
with tab3:
    st.header("💰 Token 消耗统计")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("📊 显示统计", use_container_width=True):
            st.session_state.show_stats = True

    if "show_stats" in st.session_state and st.session_state.show_stats:
        # 模拟 Token 统计数据
        mock_stats = {
            "total_tokens": 15000,
            "prompt_tokens": 10000,
            "completion_tokens": 5000,
            "total_cost": 0.045,
            "model_stats": {
                "gpt-4o": {
                    "total_tokens": 15000,
                    "prompt_tokens": 10000,
                    "completion_tokens": 5000,
                    "cost": 0.045,
                }
            },
        }

        show_token_stats(mock_stats, mode="full")
        st.session_state.show_stats = False

# Tab 4: 导出
with tab4:
    st.header("📤 导出 Agent")

    if st.session_state.graph:
        # 验证 Graph
        st.subheader("🔍 验证 Graph")
        valid, warnings = validate_for_dify(st.session_state.graph)

        if valid:
            st.success("✅ Graph 验证通过")
        else:
            st.error("❌ Graph 验证失败")

        if warnings:
            st.warning("⚠️ 警告信息:")
            for warning in warnings:
                st.markdown(f"- {warning}")

        st.markdown("---")

        # 导出选项
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📤 导出到 Dify")

            if st.button("导出 Dify YAML", type="primary", use_container_width=True):
                try:
                    output_dir = Path("exports") / agent_name.replace(" ", "_")
                    output_dir.mkdir(parents=True, exist_ok=True)

                    # 导出 Dify YAML
                    dify_path = export_to_dify(
                        graph=st.session_state.graph,
                        agent_name=agent_name,
                        output_path=output_dir / f'{agent_name.replace(" ", "_")}_dify.yml',
                    )

                    st.success(f"✅ 导出成功: {dify_path}")
                    st.session_state.dify_path = dify_path
                    st.session_state.export_done = True

                except Exception as e:
                    st.error(f"❌ 导出失败: {e}")

            # 显示导出的文件
            if st.session_state.export_done and "dify_path" in st.session_state:
                dify_path = st.session_state.dify_path

                # 文件信息
                st.info(
                    f"📄 文件: {dify_path.name}\n\n📊 大小: {dify_path.stat().st_size / 1024:.2f} KB"
                )

                # 显示内容
                with st.expander("📄 查看 YAML 内容"):
                    with open(dify_path, "r", encoding="utf-8") as f:
                        yaml_content = f.read()
                    st.code(yaml_content, language="yaml")

                # 下载按钮
                with open(dify_path, "r", encoding="utf-8") as f:
                    yaml_content = f.read()

                st.download_button(
                    label="⬇️ 下载 YAML",
                    data=yaml_content,
                    file_name=dify_path.name,
                    mime="text/yaml",
                    use_container_width=True,
                )

        with col2:
            st.subheader("📝 生成 README")

            if st.button("生成 README", use_container_width=True):
                try:
                    output_dir = Path("exports") / agent_name.replace(" ", "_")
                    output_dir.mkdir(parents=True, exist_ok=True)

                    # 生成 README
                    readme_path = generate_readme(
                        agent_name=agent_name,
                        graph=st.session_state.graph,
                        output_path=output_dir / "README.md",
                        test_results={"total": 10, "passed": 10, "failed": 0},
                    )

                    st.success(f"✅ README 已生成: {readme_path}")
                    st.session_state.readme_path = readme_path

                except Exception as e:
                    st.error(f"❌ 生成失败: {e}")

            # 显示 README
            if "readme_path" in st.session_state:
                readme_path = st.session_state.readme_path

                with st.expander("📄 查看 README"):
                    with open(readme_path, "r", encoding="utf-8") as f:
                        readme_content = f.read()
                    st.markdown(readme_content)

                # 下载按钮
                with open(readme_path, "r", encoding="utf-8") as f:
                    readme_content = f.read()

                st.download_button(
                    label="⬇️ 下载 README",
                    data=readme_content,
                    file_name="README.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        # 使用说明
        st.markdown("---")
        st.subheader("📖 使用说明")

        with st.expander("💡 如何导入到 Dify"):
            st.markdown(
                """
            ### 📋 导入步骤

            1. **访问 Dify**
               - 打开 [Dify Cloud](https://cloud.dify.ai)
               - 或访问你的本地 Dify 部署

            2. **创建应用**
               - 点击"创建应用"
               - 选择 **Chatflow** 类型

            3. **导入 DSL**
               - 点击"导入 DSL"
               - 上传刚才下载的 YAML 文件

            4. **配置节点**
               - 配置 LLM 节点的 API Key
               - 配置工具节点的 API Key（如 Tavily）
               - 如果有 RAG 节点，需要手动添加 Knowledge Retrieval 节点

            5. **测试运行**
               - 点击"调试"按钮
               - 输入测试问题
               - 验证功能是否正常

            ### ⚠️ 注意事项

            - **RAG 节点**: 导出时会被自动跳过，需要在 Dify 中手动添加 Knowledge Retrieval 节点
            - **API Keys**: 确保在 Dify 中配置了所需的 API Keys
            - **工具配置**: 检查工具节点是否在 Dify 中可用
            """
            )
    else:
        st.info("👈 请先在侧边栏创建 Agent")

# ============================================================
# 底部：信息栏
# ============================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📚 文档")
    st.markdown(
        """
    - [使用总结](PHASE5_USAGE_SUMMARY.md)
    - [集成指南](PHASE5_INTEGRATION_GUIDE.md)
    - [文档索引](PHASE5_DOCUMENTATION_INDEX.md)
    """
    )

with col2:
    st.markdown("### 🧪 测试")
    st.code("python quick_reference.py", language="bash")
    st.code("python test_dify_final.py", language="bash")

with col3:
    st.markdown("### 💡 快速 API")
    st.code(
        """
from src.exporters import export_to_dify
export_to_dify(graph, 'MyAgent', 'output.yml')
    """,
        language="python",
    )

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🤖 Agent Zero v8.0 Phase 5 | "
    "Built with ❤️ using Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
