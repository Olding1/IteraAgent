"""
IteraAgent v8.0 - Chat 模式 Streamlit UI

使用 Chat 界面模拟 CLI 交互，实现完整的 Agent 创建流程
"""

import streamlit as st
import sys
from pathlib import Path
import asyncio
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Page config
st.set_page_config(page_title="IteraAgent v8.0 - Chat Mode", page_icon="🤖", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_step" not in st.session_state:
    st.session_state.current_step = "menu"
if "agent_data" not in st.session_state:
    st.session_state.agent_data = {}

# ============================================================
# Helper Functions
# ============================================================


def add_message(role, content):
    """Add message to chat history"""
    st.session_state.messages.append(
        {"role": role, "content": content, "timestamp": datetime.now()}
    )


def run_async(coro):
    """Run async function"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# ============================================================
# Main UI
# ============================================================

st.title("🤖 IteraAgent v8.0 - Chat 模式")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.subheader("💬 Chat 模式")
    st.markdown(
        """
    使用聊天界面与 IteraAgent 交互：

    - 🏗️ 创建 Agent
    - 📦 管理 Agent
    - 📤 导出到 Dify
    - ⚙️ 系统设置

    **提示**: 输入 `/help` 查看命令
    """
    )

    st.markdown("---")

    # Quick stats
    agents_dir = Path("agents")
    if agents_dir.exists():
        agents = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        st.metric("已生成 Agent", len(agents))
    else:
        st.metric("已生成 Agent", 0)

    st.markdown("---")

    if st.button("🔄 重置对话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_step = "menu"
        st.session_state.agent_data = {}
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Welcome message
if len(st.session_state.messages) == 0:
    welcome_msg = """
👋 欢迎使用 IteraAgent v8.0！

我可以帮你：
- 🏗️ 创建新的 Agent
- 📦 管理现有 Agent
- 📤 导出 Agent 到 Dify
- ⚙️ 配置系统设置

**快速命令**:
- `/create` - 创建新 Agent
- `/list` - 查看所有 Agent
- `/export` - 导出 Agent
- `/help` - 查看帮助

请输入命令或描述你的需求...
"""
    add_message("assistant", welcome_msg)
    st.rerun()

# Chat input
if prompt := st.chat_input("输入命令或消息..."):
    # Add user message
    add_message("user", prompt)

    # Process command
    response = ""

    # Command: /help
    if prompt.lower() in ["/help", "help", "帮助"]:
        response = """
📖 **可用命令**:

**Agent 管理**:
- `/create` - 创建新 Agent
- `/list` - 查看所有 Agent
- `/export` - 导出 Agent 到 Dify

**系统**:
- `/status` - 查看系统状态
- `/settings` - 系统设置
- `/clear` - 清空对话

**提示**: 你也可以直接描述需求，我会理解你的意图。
"""

    # Command: /create
    elif prompt.lower() in ["/create", "create", "创建", "新建"]:
        if st.session_state.current_step == "menu":
            st.session_state.current_step = "create_start"
            response = """
🏗️ **创建新 Agent**

让我们开始创建你的 Agent！

请描述你想要创建的 Agent：
- Agent 的用途是什么？
- 需要什么功能？
- 有什么特殊要求？

例如：
- "创建一个智能客服 Agent，可以回答用户问题"
- "创建一个新闻摘要 Agent，每天生成新闻摘要"
- "创建一个数据分析 Agent，可以分析 CSV 文件"

请描述你的需求...
"""

    # Command: /list
    elif prompt.lower() in ["/list", "list", "列表", "查看"]:
        agents_dir = Path("agents")
        if agents_dir.exists():
            agents = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
            if agents:
                response = f"📦 **已生成的 Agent ({len(agents)})**:\n\n"
                for i, agent in enumerate(agents, 1):
                    mtime = datetime.fromtimestamp(agent.stat().st_mtime)
                    response += f"{i}. **{agent.name}**\n"
                    response += f"   创建时间: {mtime.strftime('%Y-%m-%d %H:%M')}\n\n"
                response += "\n输入 `/export` 导出 Agent"
            else:
                response = "📦 暂无 Agent\n\n输入 `/create` 创建新 Agent"
        else:
            response = "📦 agents 目录不存在\n\n输入 `/create` 创建新 Agent"

    # Command: /export
    elif prompt.lower() in ["/export", "export", "导出"]:
        agents_dir = Path("agents")
        if agents_dir.exists():
            agents = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
            if agents:
                st.session_state.current_step = "export_select"
                response = f"📤 **导出 Agent 到 Dify**\n\n请选择要导出的 Agent:\n\n"
                for i, agent in enumerate(agents, 1):
                    response += f"{i}. {agent.name}\n"
                response += f"\n请输入序号 (1-{len(agents)}):"
            else:
                response = "📦 暂无 Agent 可导出\n\n输入 `/create` 创建新 Agent"
        else:
            response = "📦 agents 目录不存在"

    # Command: /status
    elif prompt.lower() in ["/status", "status", "状态"]:
        env_file = Path(".env")
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                import os

                load_dotenv()

                builder_key = os.getenv("BUILDER_API_KEY", "")
                runtime_key = os.getenv("RUNTIME_API_KEY", "")

                response = "📊 **系统状态**\n\n"
                response += f"✅ .env 文件: 存在\n"
                response += f"{'✅' if builder_key else '❌'} Builder API Key: {'已配置' if builder_key else '未配置'}\n"
                response += f"{'✅' if runtime_key else '❌'} Runtime API Key: {'已配置' if runtime_key else '未配置'}\n"
            except Exception as e:
                response = f"❌ 加载配置失败: {e}"
        else:
            response = "❌ .env 文件不存在\n\n请创建 .env 文件并配置 API Keys"

    # Command: /clear
    elif prompt.lower() in ["/clear", "clear", "清空"]:
        st.session_state.messages = []
        st.session_state.current_step = "menu"
        st.session_state.agent_data = {}
        st.rerun()

    # Handle current step
    elif st.session_state.current_step == "create_start":
        # User provided agent description
        st.session_state.agent_data["description"] = prompt
        st.session_state.current_step = "create_confirm"

        response = f"""
✅ **收到你的需求**:

"{prompt}"

**下一步**:

由于 Agent 创建涉及复杂的交互流程，我建议使用命令行工具完成创建：

```bash
python start.py
# 选择选项 1: 新建 Agent
```

**或者**，我可以帮你：
1. 生成一个简化的 Agent 配置
2. 提供详细的创建指南

请选择：
- 输入 `1` - 使用命令行工具（推荐）
- 输入 `2` - 生成简化配置
- 输入 `3` - 查看创建指南
"""

    elif st.session_state.current_step == "export_select":
        # User selected agent number
        try:
            idx = int(prompt)
            agents_dir = Path("agents")
            agents = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

            if 1 <= idx <= len(agents):
                selected_agent = agents[idx - 1]
                st.session_state.agent_data["selected_agent"] = selected_agent.name

                # Load and validate graph
                graph_file = selected_agent / "graph.json"
                if graph_file.exists():
                    try:
                        from src.exporters import export_to_dify, validate_for_dify
                        from src.schemas.graph_structure import GraphStructure

                        with open(graph_file, "r", encoding="utf-8") as f:
                            graph_data = json.load(f)
                        graph = GraphStructure.model_validate(graph_data)

                        valid, warnings = validate_for_dify(graph)

                        response = f"✅ **已选择**: {selected_agent.name}\n\n"
                        response += f"🔍 **验证结果**: {'✅ 通过' if valid else '❌ 失败'}\n\n"

                        if warnings:
                            response += "⚠️ **警告**:\n"
                            for warning in warnings:
                                response += f"- {warning}\n"
                            response += "\n"

                        # Export
                        output_dir = Path("exports") / selected_agent.name
                        output_dir.mkdir(parents=True, exist_ok=True)

                        dify_path = export_to_dify(
                            graph=graph,
                            agent_name=selected_agent.name,
                            output_path=output_dir / f"{selected_agent.name}_dify.yml",
                        )

                        response += f"✅ **导出成功**!\n\n"
                        response += f"📁 文件: `{dify_path}`\n"
                        response += f"📊 大小: {dify_path.stat().st_size} 字节\n\n"
                        response += "💡 **下一步**:\n"
                        response += "1. 访问 https://cloud.dify.ai\n"
                        response += "2. 创建应用 → Chatflow\n"
                        response += "3. 导入 DSL → 上传 YAML 文件\n"

                        if any(node.type == "rag" for node in graph.nodes):
                            response += "4. 手动添加 Knowledge Retrieval 节点\n"

                        st.session_state.current_step = "menu"

                    except Exception as e:
                        response = f"❌ 导出失败: {e}"
                        st.session_state.current_step = "menu"
                else:
                    response = f"❌ 未找到 graph.json: {graph_file}"
                    st.session_state.current_step = "menu"
            else:
                response = f"❌ 无效序号，请输入 1-{len(agents)}"
        except ValueError:
            response = "❌ 请输入有效的数字"

    # Default: try to understand intent
    else:
        if any(word in prompt.lower() for word in ["创建", "create", "新建", "new"]):
            response = "🏗️ 我理解你想创建 Agent\n\n输入 `/create` 开始创建流程"
        elif any(word in prompt.lower() for word in ["导出", "export", "输出"]):
            response = "📤 我理解你想导出 Agent\n\n输入 `/export` 开始导出流程"
        elif any(word in prompt.lower() for word in ["列表", "list", "查看", "显示"]):
            response = "📦 我理解你想查看 Agent 列表\n\n输入 `/list` 查看所有 Agent"
        else:
            response = f"""
🤔 我不太理解你的意思。

你可以：
- 输入 `/help` 查看可用命令
- 输入 `/create` 创建新 Agent
- 输入 `/list` 查看所有 Agent
- 输入 `/export` 导出 Agent

或者直接描述你的需求，我会尽力理解。
"""

    # Add assistant response
    add_message("assistant", response)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🤖 IteraAgent v8.0 Chat Mode | 输入 /help 查看帮助"
    "</div>",
    unsafe_allow_html=True,
)
