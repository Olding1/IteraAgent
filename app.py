"""
Agent Zero v8.0 - 完整功能 Streamlit UI

集成 start.py 的所有功能：
- 系统健康检查
- 新建 Agent (集成 factory)
- Agent 管理
- 测试和迭代优化
- 导出功能
- 设置
"""

import streamlit as st
import sys
from pathlib import Path
import asyncio
import json
from datetime import datetime
import subprocess

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Page config
st.set_page_config(
    page_title="Agent Zero v8.0",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# ============================================================
# Helper Functions
# ============================================================

def run_async(coro):
    """Run async function in Streamlit"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# ============================================================
# Sidebar Navigation
# ============================================================
with st.sidebar:
    st.title("🤖 Agent Zero v8.0")
    st.markdown("---")

    # Navigation
    page = st.radio(
        "导航",
        [
            "🏠 首页",
            "🏗️ 新建 Agent",
            "📦 Agent 管理",
            "🔄 测试优化",
            "📤 导出功能",
            "⚙️ 设置"
        ],
        key="navigation"
    )

    st.markdown("---")

    # Quick stats
    st.subheader("📊 快速统计")
    agents_dir = Path("agents")
    if agents_dir.exists():
        agents = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        st.metric("已生成 Agent", len(agents))
    else:
        st.metric("已生成 Agent", 0)

    exports_dir = Path("exports")
    if exports_dir.exists():
        exports = list(exports_dir.iterdir())
        st.metric("导出文件", len(exports))
    else:
        st.metric("导出文件", 0)

# ============================================================
# Page: 首页
# ============================================================
if page == "🏠 首页":
    st.title("🏠 Agent Zero 控制中心")
    st.markdown("---")

    # Welcome message
    st.markdown("""
    ### 欢迎使用 Agent Zero v8.0！

    这是一个完整的 Agent 构建和管理平台，提供：
    - 🏗️ Agent 创建和优化
    - 📦 Agent 管理和运行
    - 🔄 测试和迭代优化
    - 📤 导出到 Dify 平台
    - ⚙️ 系统配置管理
    """)

    # System health check
    st.subheader("📊 系统健康检查")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Builder API")
        env_file = Path(".env")
        if env_file.exists():
            st.success("✅ .env 文件存在")

            try:
                from dotenv import load_dotenv
                import os
                load_dotenv()

                builder_provider = os.getenv("BUILDER_PROVIDER", "openai")
                builder_model = os.getenv("BUILDER_MODEL", "gpt-4o")
                builder_key = os.getenv("BUILDER_API_KEY", "")

                st.info(f"提供商: {builder_provider}")
                st.info(f"模型: {builder_model}")

                if builder_key:
                    st.success("✅ API Key 已配置")
                else:
                    st.warning("⚠️ API Key 未配置")
            except Exception as e:
                st.error(f"❌ 加载配置失败: {e}")
        else:
            st.error("❌ .env 文件不存在")

    with col2:
        st.markdown("#### Runtime API")
        if env_file.exists():
            try:
                import os
                runtime_provider = os.getenv("RUNTIME_PROVIDER", "openai")
                runtime_model = os.getenv("RUNTIME_MODEL", "gpt-3.5-turbo")
                runtime_key = os.getenv("RUNTIME_API_KEY", "")

                st.info(f"提供商: {runtime_provider}")
                st.info(f"模型: {runtime_model}")

                if runtime_key:
                    st.success("✅ API Key 已配置")
                else:
                    st.warning("⚠️ API Key 未配置")
            except Exception as e:
                st.error(f"❌ 加载配置失败: {e}")

    st.markdown("---")

    # Quick actions
    st.subheader("🚀 快速操作")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🏗️ 新建 Agent", use_container_width=True, type="primary"):
            st.session_state.current_page = "create"
            st.rerun()

    with col2:
        if st.button("📦 管理 Agent", use_container_width=True):
            st.session_state.current_page = "manage"
            st.rerun()

    with col3:
        if st.button("🔄 测试优化", use_container_width=True):
            st.session_state.current_page = "optimize"
            st.rerun()

    with col4:
        if st.button("📤 导出", use_container_width=True):
            st.session_state.current_page = "export"
            st.rerun()

    # Recent activity
    st.markdown("---")
    st.subheader("📝 最近活动")

    if agents_dir.exists() and agents:
        st.markdown("**最近创建的 Agent:**")
        for agent in sorted(agents, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            mtime = datetime.fromtimestamp(agent.stat().st_mtime)
            st.markdown(f"- **{agent.name}** - {mtime.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.info("暂无 Agent")

# ============================================================
# Page: 新建 Agent
# ============================================================
elif page == "🏗️ 新建 Agent":
    st.title("🏗️ 新建 Agent")
    st.markdown("---")

    st.info("""
    ### 💡 使用命令行创建 Agent

    由于 Agent 创建过程涉及复杂的交互式流程，建议使用命令行工具：

    ```bash
    python start.py
    # 选择选项 1: 新建 Agent
    ```

    **创建流程**:
    1. 输入 Agent 需求描述
    2. 系统自动设计 Graph 结构
    3. 选择工具和配置
    4. 生成完整的 Agent 代码
    5. 运行测试验证

    **创建完成后**，返回此 UI 进行管理和导出。
    """)

    st.markdown("---")

    # Alternative: Simple form for basic agent creation
    with st.expander("🧪 实验性功能：简化创建（开发中）"):
        st.warning("此功能正在开发中，建议使用命令行工具创建 Agent")

        agent_name = st.text_input("Agent 名称", placeholder="例如：智能客服助手")
        agent_desc = st.text_area(
            "Agent 描述",
            placeholder="描述 Agent 的功能和用途...",
            height=100
        )

        col1, col2 = st.columns(2)
        with col1:
            use_rag = st.checkbox("使用 RAG（知识库）")
        with col2:
            use_tools = st.checkbox("使用工具（搜索等）")

        if st.button("创建 Agent", type="primary", disabled=True):
            st.info("此功能正在开发中，请使用命令行工具")

# ============================================================
# Page: Agent 管理
# ============================================================
elif page == "📦 Agent 管理":
    st.title("📦 Agent 管理")
    st.markdown("---")

    agents_dir = Path("agents")
    if not agents_dir.exists():
        st.warning("agents 目录不存在")
        st.stop()

    agents = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

    if not agents:
        st.info("暂无 Agent")
        st.markdown("""
        ### 💡 如何创建 Agent？

        使用命令行工具创建：
        ```bash
        python start.py
        # 选择选项 1: 新建 Agent
        ```
        """)
        st.stop()

    # Agent list
    st.subheader(f"已生成的 Agent ({len(agents)})")

    # Search and filter
    search = st.text_input("🔍 搜索 Agent", placeholder="输入 Agent 名称...")

    if search:
        agents = [a for a in agents if search.lower() in a.name.lower()]

    # Display agents
    for agent in agents:
        with st.expander(f"📁 {agent.name}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**路径:** `{agent}`")

                # Check files
                graph_file = agent / "graph.json"
                agent_file = agent / "agent.py"

                if graph_file.exists():
                    st.success("✅ graph.json")
                else:
                    st.error("❌ graph.json 缺失")

                if agent_file.exists():
                    st.success("✅ agent.py")
                else:
                    st.error("❌ agent.py 缺失")

                # Load graph info
                if graph_file.exists():
                    try:
                        with open(graph_file, 'r', encoding='utf-8') as f:
                            graph_data = json.load(f)

                        pattern = graph_data.get('pattern', {})
                        if isinstance(pattern, dict):
                            pattern_type = pattern.get('pattern_type', 'unknown')
                            description = pattern.get('description', '')
                        else:
                            pattern_type = str(pattern)
                            description = ''

                        nodes = graph_data.get('nodes', [])
                        edges = graph_data.get('edges', [])

                        st.info(f"**模式:** {pattern_type}")
                        if description:
                            st.info(f"**描述:** {description}")
                        st.info(f"**节点数:** {len(nodes)} | **边数:** {len(edges)}")
                    except Exception as e:
                        st.error(f"加载 graph.json 失败: {e}")

            with col2:
                if st.button("🔄 测试", key=f"test_{agent.name}", use_container_width=True):
                    st.session_state.selected_agent = agent.name
                    st.session_state.current_page = "optimize"
                    st.rerun()

                if st.button("📤 导出", key=f"export_{agent.name}", use_container_width=True):
                    st.session_state.selected_agent = agent.name
                    st.session_state.current_page = "export"
                    st.rerun()

                if st.button("▶️ 运行", key=f"run_{agent.name}", use_container_width=True):
                    st.info("运行功能开发中...")

# ============================================================
# Page: 测试优化
# ============================================================
elif page == "🔄 测试优化":
    st.title("🔄 测试和迭代优化")
    st.markdown("---")

    agents_dir = Path("agents")
    if not agents_dir.exists():
        st.warning("agents 目录不存在")
        st.stop()

    agents = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

    if not agents:
        st.info("暂无 Agent 可测试")
        st.stop()

    # Select agent
    st.subheader("1️⃣ 选择 Agent")

    default_index = 0
    if 'selected_agent' in st.session_state:
        try:
            default_index = [a.name for a in agents].index(st.session_state.selected_agent)
        except ValueError:
            pass

    selected_agent = st.selectbox(
        "选择要测试的 Agent",
        agents,
        format_func=lambda x: x.name,
        index=default_index
    )

    if not selected_agent:
        st.stop()

    st.success(f"✅ 已选择: {selected_agent.name}")

    # Check reports
    reports_dir = selected_agent / ".reports"
    if reports_dir.exists():
        history_file = reports_dir / "history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)

                iterations = history_data.get('iterations', [])
                st.info(f"📊 历史迭代: {len(iterations)} 次")

                if iterations:
                    latest = iterations[-1]
                    pass_rate = latest.get('pass_rate', 0)
                    st.metric("最新通过率", f"{pass_rate:.1%}")
            except Exception as e:
                st.warning(f"加载历史失败: {e}")

    st.markdown("---")

    # Test options
    st.subheader("2️⃣ 测试选项")

    st.info("""
    ### 💡 使用命令行进行测试优化

    由于测试和迭代优化涉及复杂的异步流程，建议使用命令行工具：

    ```bash
    python start.py
    # 选择选项 3: 重新测试现有 Agent
    ```

    **测试流程**:
    1. 运行 DeepEval 测试
    2. AI 智能分析测试结果
    3. 自动优化 Graph/RAG/Tools
    4. 重新编译和测试
    5. 生成详细报告

    **支持的优化**:
    - Graph 结构优化
    - RAG 参数调优
    - 工具选择优化
    - 依赖项修复
    """)

    # Quick test button (simplified)
    with st.expander("🧪 快速测试（简化版）"):
        st.warning("此功能仅运行测试，不包含自动优化")

        if st.button("运行测试", type="primary"):
            with st.spinner("正在运行测试..."):
                try:
                    # Run pytest
                    test_file = selected_agent / "tests" / "test_deepeval.py"
                    if test_file.exists():
                        result = subprocess.run(
                            [sys.executable, "-m", "pytest", str(test_file), "-v"],
                            cwd=str(selected_agent),
                            capture_output=True,
                            text=True,
                            timeout=300
                        )

                        st.code(result.stdout)

                        if result.returncode == 0:
                            st.success("✅ 测试通过！")
                        else:
                            st.error("❌ 测试失败")
                            st.code(result.stderr)
                    else:
                        st.error("未找到测试文件")
                except subprocess.TimeoutExpired:
                    st.error("测试超时")
                except Exception as e:
                    st.error(f"测试失败: {e}")

# ============================================================
# Page: 导出功能
# ============================================================
elif page == "📤 导出功能":
    st.title("📤 导出 Agent 到 Dify")
    st.markdown("---")

    agents_dir = Path("agents")
    if not agents_dir.exists():
        st.warning("agents 目录不存在")
        st.stop()

    agents = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

    if not agents:
        st.info("暂无 Agent 可导出")
        st.stop()

    # Select agent
    st.subheader("1️⃣ 选择 Agent")

    default_index = 0
    if 'selected_agent' in st.session_state:
        try:
            default_index = [a.name for a in agents].index(st.session_state.selected_agent)
        except ValueError:
            pass

    selected_agent = st.selectbox(
        "选择要导出的 Agent",
        agents,
        format_func=lambda x: x.name,
        index=default_index
    )

    if not selected_agent:
        st.stop()

    # Load graph
    graph_file = selected_agent / "graph.json"
    if not graph_file.exists():
        st.error(f"❌ 未找到 graph.json: {graph_file}")
        st.stop()

    st.success(f"✅ 已选择: {selected_agent.name}")

    # Load and validate
    st.subheader("2️⃣ 验证 Graph")

    try:
        from src.exporters import export_to_dify, validate_for_dify
        from src.utils.readme_generator import generate_readme
        from src.schemas.graph_structure import GraphStructure

        with open(graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        graph = GraphStructure.model_validate(graph_data)

        valid, warnings = validate_for_dify(graph)

        if valid:
            st.success("✅ Graph 验证通过")
        else:
            st.error("❌ Graph 验证失败")

        if warnings:
            st.warning("⚠️ 警告信息:")
            for warning in warnings:
                st.markdown(f"- {warning}")

        # Visualize graph
        with st.expander("📊 查看 Graph 结构"):
            from src.ui.components import visualize_graph
            visualize_graph(graph, height=400)

        # Export options
        st.markdown("---")
        st.subheader("3️⃣ 导出选项")

        col1, col2 = st.columns(2)

        with col1:
            export_yaml = st.checkbox("导出 Dify YAML", value=True)

        with col2:
            export_readme = st.checkbox("生成 README", value=True)

        if not export_yaml and not export_readme:
            st.warning("请至少选择一个导出选项")
            st.stop()

        # Export button
        st.markdown("---")

        if st.button("🚀 开始导出", type="primary", use_container_width=True):
            output_dir = Path("exports") / selected_agent.name
            output_dir.mkdir(parents=True, exist_ok=True)

            with st.spinner("正在导出..."):
                try:
                    if export_yaml:
                        dify_path = export_to_dify(
                            graph=graph,
                            agent_name=selected_agent.name,
                            output_path=output_dir / f"{selected_agent.name}_dify.yml"
                        )
                        st.success(f"✅ Dify YAML 已导出: {dify_path}")
                        st.info(f"文件大小: {dify_path.stat().st_size} 字节")

                        # Show download button
                        with open(dify_path, 'r', encoding='utf-8') as f:
                            yaml_content = f.read()

                        st.download_button(
                            label="⬇️ 下载 YAML",
                            data=yaml_content,
                            file_name=f"{selected_agent.name}_dify.yml",
                            mime="text/yaml",
                            use_container_width=True
                        )

                    if export_readme:
                        readme_path = generate_readme(
                            agent_name=selected_agent.name,
                            graph=graph,
                            output_path=output_dir / "README.md"
                        )
                        st.success(f"✅ README 已生成: {readme_path}")
                        st.info(f"文件大小: {readme_path.stat().st_size} 字节")

                        # Show download button
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            readme_content = f.read()

                        st.download_button(
                            label="⬇️ 下载 README",
                            data=readme_content,
                            file_name="README.md",
                            mime="text/markdown",
                            use_container_width=True
                        )

                    st.success(f"✅ 导出完成！文件保存在: {output_dir}")

                    # Show next steps
                    st.markdown("---")
                    st.subheader("💡 下一步")
                    st.markdown("""
                    1. 访问 [Dify Cloud](https://cloud.dify.ai)
                    2. 创建应用 → 选择 **Chatflow**
                    3. 点击 **导入 DSL** → 上传 YAML 文件
                    4. 配置 API Keys 和工具
                    5. 如果包含 RAG 节点，需要手动添加 Knowledge Retrieval 节点
                    6. 测试运行
                    """)

                except Exception as e:
                    st.error(f"❌ 导出失败: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    except Exception as e:
        st.error(f"❌ 加载 Graph 失败: {e}")
        import traceback
        st.code(traceback.format_exc())

# ============================================================
# Page: 设置
# ============================================================
elif page == "⚙️ 设置":
    st.title("⚙️ 系统设置")
    st.markdown("---")

    # API Configuration
    st.subheader("🔧 API 配置")

    env_file = Path(".env")
    if env_file.exists():
        st.success("✅ .env 文件存在")
        st.info(f"位置: {env_file.absolute()}")

        st.markdown("""
        ### 编辑 API 配置

        请直接编辑 `.env` 文件来配置 API 设置：

        ```bash
        # Builder API (用于构建 Agent)
        BUILDER_PROVIDER=openai
        BUILDER_MODEL=gpt-4o
        BUILDER_API_KEY=your_key_here

        # Runtime API (用于运行 Agent)
        RUNTIME_PROVIDER=openai
        RUNTIME_MODEL=gpt-3.5-turbo
        RUNTIME_API_KEY=your_key_here
        ```
        """)

        if st.button("📝 在编辑器中打开 .env"):
            import platform

            system = platform.system()
            try:
                if system == "Windows":
                    subprocess.run(["notepad", str(env_file)])
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", "-e", str(env_file)])
                else:  # Linux
                    subprocess.run(["xdg-open", str(env_file)])
                st.success("✅ 已在编辑器中打开")
            except Exception as e:
                st.error(f"❌ 打开失败: {e}")
    else:
        st.error("❌ .env 文件不存在")
        st.markdown("""
        ### 创建 .env 文件

        请从模板创建 .env 文件：

        ```bash
        cp .env.template .env
        ```

        然后编辑 .env 文件，添加您的 API Keys。
        """)

    st.markdown("---")

    # System info
    st.subheader("📊 系统信息")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Python 环境")
        st.info(f"Python 版本: {sys.version.split()[0]}")
        st.info(f"工作目录: {Path.cwd()}")

    with col2:
        st.markdown("#### 依赖状态")

        deps = {
            "streamlit": "Streamlit",
            "pydantic": "Pydantic",
            "yaml": "PyYAML",
            "jinja2": "Jinja2",
            "plotly": "Plotly"
        }

        for module, name in deps.items():
            try:
                mod = __import__(module.replace('-', '_'))
                version = getattr(mod, '__version__', 'unknown')
                st.success(f"✅ {name}: {version}")
            except ImportError:
                st.error(f"❌ {name}: 未安装")

    st.markdown("---")

    # About
    st.subheader("ℹ️ 关于")
    st.markdown("""
    **Agent Zero v8.0**

    智能 Agent 构建和管理平台

    - 🏗️ Agent 创建和优化
    - 📦 Agent 管理和运行
    - 🔄 测试和迭代优化
    - 📤 导出到 Dify 平台
    - ⚙️ 系统配置管理

    ---

    **Phase 5 功能**:
    - Dify 导出
    - README 生成
    - ZIP 打包
    - Streamlit UI

    ---

    Created: 2026-01-29
    """)

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🤖 Agent Zero v8.0 | Built with ❤️ using Streamlit"
    "</div>",
    unsafe_allow_html=True
)
