<div align="center">

# 🤖 Agent Zero

**定义逻辑，生成图谱，自动部署**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Powered-green.svg)](https://github.com/langchain-ai/langgraph)

*一个用于构建、测试、优化和部署生产级 AI Agent 的智能平台*

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [文档](#-文档) • [示例](#-示例) • [English](README.md)

</div>

---

## 🎯 什么是 Agent Zero？

Agent Zero 是一个**完整的 AI Agent 生命周期管理平台**，通过自动化、AI 驱动的工作流，将你的想法转化为生产就绪的 Agent。

```
你的想法 → AI 设计 → 自动生成 → 测试优化 → 部署到 Dify
```

**核心优势：**
- 🧠 **AI 驱动设计** - 使用经过验证的设计模式智能生成图谱结构
- 🔄 **自我优化** - 通过 LLM 驱动的分析自动测试和迭代改进
- 📦 **一键导出** - 即时部署到 Dify 和其他平台
- 🎨 **多种界面** - CLI、Web UI、Chat UI 和 Python API
- 🛡️ **生产就绪** - 内置验证、错误处理和子进程隔离

---

## ✨ 功能特性

### 🏗️ 智能 Agent 创建

- **三步设计法**：模式选择 → 状态定义 → 图谱构建
- **5 种经典设计模式**：顺序、反思、监督者、计划执行、自定义
- **16+ 精选工具**：DuckDuckGo、Tavily、Arxiv、Wikipedia、Google Scholar、PubMed 等
- **RAG 集成**：自动文档处理和向量数据库设置

### 🔬 自动化测试与优化

- **DeepEval 集成**：全面的测试生成和执行
- **多目标优化**：
  - RAG 参数（分块大小、重叠、检索数量）
  - 工具选择和配置
  - 图谱结构优化
  - 依赖优化
- **LLM 驱动分析**：智能根因分析和自动修复
- **迭代历史**：完整的优化周期审计跟踪

### 🚀 部署与导出

- **Dify 导出**：将 Agent 转换为 Dify 兼容的 YAML 格式
- **自动文档**：生成全面的 README 文件
- **ZIP 打包**：打包 Agent 及所有依赖
- **验证检查**：导出前的兼容性检查

### 🎨 灵活的界面

| 界面 | 适用场景 | 启动命令 |
|------|---------|---------|
| **CLI** | 完整功能和自动化 | `python start.py` |
| **Web UI** | 可视化管理和监控 | `python scripts/start_ui.bat` |
| **Chat UI** | 新手和快速任务 | `python scripts/start_chat_ui.bat` |
| **Python API** | 程序化集成 | `from src.exporters import export_to_dify` |

### 🛡️ 高级特性 (v8.0)

- **接口守卫**：基于 Pydantic 的参数验证和 LLM 自动修复
- **工具发现引擎**：智能工具索引和搜索
- **图谱即代码**：JSON 中间层解耦逻辑与实现
- **子进程隔离**：在隔离的 Python 环境中安全执行 Agent
- **API 双轨制**：构建（GPT-4o）和运行时（GPT-3.5）使用不同模型
- **HITL 支持**：人机协同的暂停/恢复/停止控制

---

## 🚀 快速开始

### 前置要求

- Python 3.8 或更高版本
- Git
- OpenAI API 密钥（或 Anthropic/Azure）

### 安装

**方式 1: 一键安装（推荐）**

```bash
# 克隆仓库
git clone https://github.com/Olding1/Agent_Zero.git
cd Agent_Zero

# Windows 用户
setup.bat

# Linux/Mac 用户
chmod +x setup.sh
./setup.sh

# 或直接运行 Python 脚本
python setup.py
```

一键安装脚本会自动完成：
- ✅ 检查 Python 版本
- ✅ 升级 pip 到最新版本
- ✅ 安装所有依赖（requirements.txt）
- ✅ 可选安装开发依赖（requirements-dev.txt）
- ✅ 创建并配置 .env 文件（交互式配置 API 密钥）
- ✅ 创建必要的项目目录
- ✅ 验证安装是否成功

**方式 2: 手动安装**

```bash
# 安装核心依赖
pip install -r requirements.txt

# (可选) 安装开发依赖（用于测试、类型检查、文档生成）
pip install -r requirements-dev.txt

# 配置环境
cp .env.template .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 创建你的第一个 Agent

**方式 1: CLI（推荐）**

```bash
python start.py
# 选择：1. 🏗️ 创建新 Agent
# 按照交互式提示操作
```

**方式 2: Chat UI（最简单）**

```bash
python scripts/start_chat_ui.bat  # Windows
./scripts/start_chat_ui.sh        # Linux/Mac

# 在聊天界面中输入：
# "创建一个客服 Agent，可以搜索文档并回答问题"
```

**方式 3: Python API**

```python
from src.core.agent_factory import AgentFactory
from src.llm.builder_client import BuilderClient

# 初始化
client = BuilderClient()
factory = AgentFactory(client)

# 创建 Agent
result = factory.create_agent(
    requirement="创建一个研究助手，可以搜索论文并总结发现",
    agent_name="ResearchAssistant"
)

print(f"Agent 已创建于: {result.output_dir}")
```

---

## 📖 文档

### 核心概念

**图谱即代码**：Agent Zero 使用基于 JSON 的中间表示，将业务逻辑与实现解耦：

```
用户需求 → JSON 图谱 → Python 代码 → 可执行 Agent
```

**设计模式**：从经过验证的架构模式中选择：

- **顺序（Sequential）**：线性工作流（A → B → C）
- **反思（Reflection）**：自我改进循环（生成 ↔ 批评）
- **监督者（Supervisor）**：管理者-工作者委派
- **计划执行（Plan-Execute）**：带动态重新规划的计划
- **自定义（Custom）**：定义你自己的拓扑

**优化循环**：通过测试持续改进：

```
生成 → 测试 → 分析 → 修复 → 重复
```

### 项目结构

```
Agent_Zero/
├── src/
│   ├── core/              # 核心引擎（18+ 模块）
│   │   ├── agent_factory.py      # 主编排器
│   │   ├── graph_designer.py     # 图谱结构设计
│   │   ├── compiler.py           # 代码生成
│   │   ├── runner.py             # 测试执行
│   │   ├── judge.py              # 结果分析
│   │   ├── interface_guard.py    # 参数验证
│   │   └── tool_discovery.py     # 工具索引
│   ├── llm/               # LLM 集成
│   ├── exporters/         # 平台导出器（Dify 等）
│   ├── ui/                # Streamlit UI 组件
│   ├── schemas/           # Pydantic 数据模型
│   ├── templates/         # Jinja2 代码模板
│   ├── tools/             # 工具定义（16+）
│   └── utils/             # 工具函数
├── scripts/               # 安装和启动脚本
├── agents/                # 生成的 Agent
├── exports/               # 导出输出
├── start.py               # CLI 入口
├── app.py                 # Web UI（完整版）
└── app_chat.py            # Web UI（聊天版）
```

### CLI 菜单

```bash
python start.py
```

1. 🏗️ **创建新 Agent** - AI 驱动的 Agent 生成
2. 📦 **查看 Agent** - 浏览已生成的 Agent
3. 🔄 **重新测试 Agent** - 迭代优化
4. 🔧 **配置 API** - 设置 LLM 提供商
5. 🧪 **运行测试** - 执行测试套件
6. 📖 **查看文档** - 访问文档
7. 📤 **导出到 Dify** - 一键部署
8. 🎨 **启动 Web UI** - 启动 Streamlit 界面
9. 🚪 **退出**

---

## 💡 示例

### 示例 1：客服 Agent

```bash
python start.py
# 选择：1. 创建新 Agent

# 输入需求：
"创建一个客服 Agent，可以：
- 使用 RAG 搜索我们的文档
- 回答常见问题
- 将复杂问题升级给人工客服"

# Agent Zero 将会：
# 1. 设计一个监督者模式图谱
# 2. 使用你的文档配置 RAG
# 3. 选择合适的工具（搜索、问答）
# 4. 生成 Python 代码
# 5. 运行测试并优化
# 6. 导出到 Dify
```

### 示例 2：研究助手

```python
from src.core.agent_factory import AgentFactory
from src.llm.builder_client import BuilderClient

client = BuilderClient()
factory = AgentFactory(client)

# 创建研究 Agent
result = factory.create_agent(
    requirement="""
    创建一个研究助手，可以：
    - 搜索学术论文（Arxiv、PubMed、Google Scholar）
    - 总结关键发现
    - 生成文献综述
    """,
    agent_name="ResearchAssistant",
    pattern="plan_execute"  # 使用计划执行模式
)

# Agent 已准备好：agents/ResearchAssistant/
```

### 示例 3：导出现有 Agent

```bash
# 使用 Chat UI
python scripts/start_chat_ui.bat

# 命令：
/list      # 查看所有 Agent
/export    # 导出 Agent
1          # 选择 Agent 编号

# 输出：exports/ResearchAssistant_dify.zip
```

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **AI 框架** | LangGraph、LangChain |
| **LLM 提供商** | OpenAI、Anthropic、Azure |
| **向量数据库** | Chroma |
| **Web UI** | Streamlit |
| **测试** | DeepEval、pytest |
| **验证** | Pydantic v2 |
| **模板** | Jinja2 |
| **文档处理** | Unstructured、PyMuPDF |

---

## 🎓 高级用法

### 自定义设计模式

创建你自己的 Agent 模式：

```python
from src.schemas.pattern import PatternConfig

custom_pattern = PatternConfig(
    name="custom_workflow",
    description="我的自定义 Agent 模式",
    states=["start", "process", "validate", "end"],
    edges=[
        {"from": "start", "to": "process"},
        {"from": "process", "to": "validate"},
        {"from": "validate", "to": "end", "condition": "is_valid"},
        {"from": "validate", "to": "process", "condition": "needs_retry"}
    ]
)
```

### 多 Agent 编排

```python
# 创建监督者 Agent
supervisor = factory.create_agent(
    requirement="监督者协调研究和写作 Agent",
    pattern="supervisor"
)

# 创建工作者 Agent
researcher = factory.create_agent(
    requirement="研究论文并提取见解",
    pattern="sequential"
)

writer = factory.create_agent(
    requirement="基于研究撰写报告",
    pattern="reflection"
)
```

### 自定义工具集成

```python
from src.tools.registry import ToolRegistry

# 注册自定义工具
@ToolRegistry.register("my_custom_tool")
def my_tool(query: str) -> str:
    """自定义工具实现"""
    return f"已处理: {query}"
```

---

## 🤝 贡献

我们欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

### 开发设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/ -v

# 代码格式化
black src/
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent 框架
- [Dify](https://dify.ai) - AI 应用平台
- [Streamlit](https://streamlit.io) - Web UI 框架
- [DeepEval](https://github.com/confident-ai/deepeval) - 测试框架

---

## 📞 支持

- **问题反馈**：[GitHub Issues](https://github.com/Olding1/Agent_Zero/issues)
- **讨论交流**：[GitHub Discussions](https://github.com/Olding1/Agent_Zero/discussions)
- **文档**：[docs/](docs/)

---

<div align="center">

**由 Agent Zero 团队用 ❤️ 构建**

如果这个项目对你有帮助，请给我们一个 ⭐️

</div>
