<div align="center">

# 🤖 Agent Zero

**Define Logic, Generate Graph, Auto-Deploy**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Powered-green.svg)](https://github.com/langchain-ai/langgraph)

*An intelligent platform for building, testing, optimizing, and deploying production-ready AI agents*

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [Examples](#-examples) • [中文文档](README_CN.md)

</div>

---

## 🎯 What is Agent Zero?

Agent Zero is a **complete AI agent lifecycle management platform** that transforms your ideas into production-ready agents through an automated, AI-driven workflow.

```
Your Idea → AI Design → Auto-Generate → Test & Optimize → Deploy to Dify
```

**Key Differentiators:**
- 🧠 **AI-Powered Design** - Intelligent graph structure generation using proven design patterns
- 🔄 **Self-Optimizing** - Automatic testing and iterative improvement with LLM-driven analysis
- 📦 **One-Click Export** - Deploy to Dify and other platforms instantly
- 🎨 **Multiple Interfaces** - CLI, Web UI, Chat UI, and Python API
- 🛡️ **Production-Ready** - Built-in validation, error handling, and subprocess isolation

---

## ✨ Features

### 🏗️ Intelligent Agent Creation

- **Three-Step Design Method**: Pattern Selection → State Definition → Graph Construction
- **5 Proven Design Patterns**: Sequential, Reflection, Supervisor, Plan-Execute, Custom
- **16+ Curated Tools**: DuckDuckGo, Tavily, Arxiv, Wikipedia, Google Scholar, PubMed, and more
- **RAG Integration**: Automatic document processing and vector database setup

### 🔬 Automated Testing & Optimization

- **DeepEval Integration**: Comprehensive test generation and execution
- **Multi-Target Optimization**:
  - RAG parameters (chunk size, overlap, retrieval count)
  - Tool selection and configuration
  - Graph structure refinement
  - Dependency optimization
- **LLM-Powered Analysis**: Intelligent root cause analysis and automated fixes
- **Iteration History**: Complete audit trail of all optimization cycles

### 🚀 Deployment & Export

- **Dify Export**: Convert agents to Dify-compatible YAML format
- **Auto-Documentation**: Generate comprehensive README files
- **ZIP Packaging**: Bundle agents with all dependencies
- **Validation**: Pre-export compatibility checking

### 🎨 Flexible Interfaces

| Interface | Best For | Launch Command |
|-----------|----------|----------------|
| **CLI** | Full features & automation | `python start.py` |
| **Web UI** | Visual management & monitoring | `python scripts/start_ui.bat` |
| **Chat UI** | Beginners & quick tasks | `python scripts/start_chat_ui.bat` |
| **Python API** | Programmatic integration | `from src.exporters import export_to_dify` |

### 🛡️ Advanced Features (v8.0)

- **Interface Guard**: Pydantic-based parameter validation with LLM auto-repair
- **Tool Discovery Engine**: Intelligent tool indexing and search
- **Graph as Code**: JSON intermediate layer decoupling logic from implementation
- **Subprocess Isolation**: Safe agent execution in isolated Python environments
- **API Dual-Track**: Separate models for building (GPT-4o) vs runtime (GPT-3.5)
- **HITL Support**: Human-in-the-loop pause/resume/stop controls

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- OpenAI API key (or Anthropic/Azure)

### Installation

**Option 1: One-Click Installation (Recommended)**

```bash
# Clone the repository
git clone https://github.com/Olding1/Agent_Zero.git
cd Agent_Zero

# Windows users
setup.bat

# Linux/Mac users
chmod +x setup.sh
./setup.sh

# Or run Python script directly
python setup.py
```

The one-click installation script will automatically:
- ✅ Check Python version
- ✅ Upgrade pip to the latest version
- ✅ Install all dependencies (requirements.txt)
- ✅ Optionally install development dependencies (requirements-dev.txt)
- ✅ Create and configure .env file (interactive API key setup)
- ✅ Create necessary project directories
- ✅ Verify installation success

**Option 2: Manual Installation**

```bash
# Install core dependencies
pip install -r requirements.txt

# (Optional) Install development dependencies (for testing, type checking, documentation)
pip install -r requirements-dev.txt

# Configure environment
cp .env.template .env
# Edit .env file and add your API keys
```

### Create Your First Agent

**Option 1: CLI (Recommended)**

```bash
python start.py
# Select: 1. 🏗️ Create New Agent
# Follow the interactive prompts
```

**Option 2: Chat UI (Easiest)**

```bash
python scripts/start_chat_ui.bat  # Windows
./scripts/start_chat_ui.sh        # Linux/Mac

# In the chat interface:
# "Create a customer service agent that can search documentation and answer questions"
```

**Option 3: Python API**

```python
from src.core.agent_factory import AgentFactory
from src.llm.builder_client import BuilderClient

# Initialize
client = BuilderClient()
factory = AgentFactory(client)

# Create agent
result = factory.create_agent(
    requirement="Create a research assistant that can search papers and summarize findings",
    agent_name="ResearchAssistant"
)

print(f"Agent created at: {result.output_dir}")
```

---

## 📖 Documentation

### Core Concepts

**Graph as Code**: Agent Zero uses a JSON-based intermediate representation that decouples business logic from implementation:

```
User Requirement → JSON Graph → Python Code → Executable Agent
```

**Design Patterns**: Choose from proven architectural patterns:

- **Sequential**: Linear workflow (A → B → C)
- **Reflection**: Self-improving loops (Generate ↔ Critique)
- **Supervisor**: Manager-worker delegation
- **Plan-Execute**: Planning with dynamic re-planning
- **Custom**: Define your own topology

**Optimization Loop**: Continuous improvement through testing:

```
Generate → Test → Analyze → Fix → Repeat
```

### Project Structure

```
Agent_Zero/
├── src/
│   ├── core/              # Core engine (18+ modules)
│   │   ├── agent_factory.py      # Main orchestrator
│   │   ├── graph_designer.py     # Graph structure design
│   │   ├── compiler.py           # Code generation
│   │   ├── runner.py             # Test execution
│   │   ├── judge.py              # Result analysis
│   │   ├── interface_guard.py    # Parameter validation
│   │   └── tool_discovery.py     # Tool indexing
│   ├── llm/               # LLM integration
│   ├── exporters/         # Platform exporters (Dify, etc.)
│   ├── ui/                # Streamlit UI components
│   ├── schemas/           # Pydantic data models
│   ├── templates/         # Jinja2 code templates
│   ├── tools/             # Tool definitions (16+)
│   └── utils/             # Utilities
├── scripts/               # Installation & startup scripts
├── agents/                # Generated agents
├── exports/               # Export outputs
├── start.py               # CLI entry point
├── app.py                 # Web UI (full)
└── app_chat.py            # Web UI (chat)
```

### CLI Menu

```bash
python start.py
```

1. 🏗️ **Create New Agent** - AI-driven agent generation
2. 📦 **View Agents** - Browse generated agents
3. 🔄 **Re-test Agent** - Iterative optimization
4. 🔧 **Configure API** - Set up LLM providers
5. 🧪 **Run Tests** - Execute test suites
6. 📖 **View Docs** - Access documentation
7. 📤 **Export to Dify** - One-click deployment
8. 🎨 **Launch Web UI** - Start Streamlit interface
9. 🚪 **Exit**

---

## 💡 Examples

### Example 1: Customer Service Agent

```bash
python start.py
# Select: 1. Create New Agent

# Input requirement:
"Create a customer service agent that can:
- Search our documentation using RAG
- Answer common questions
- Escalate complex issues to human agents"

# Agent Zero will:
# 1. Design a Supervisor pattern graph
# 2. Configure RAG with your documents
# 3. Select appropriate tools (search, QA)
# 4. Generate Python code
# 5. Run tests and optimize
# 6. Export to Dify
```

### Example 2: Research Assistant

```python
from src.core.agent_factory import AgentFactory
from src.llm.builder_client import BuilderClient

client = BuilderClient()
factory = AgentFactory(client)

# Create research agent
result = factory.create_agent(
    requirement="""
    Create a research assistant that:
    - Searches academic papers (Arxiv, PubMed, Google Scholar)
    - Summarizes key findings
    - Generates literature reviews
    """,
    agent_name="ResearchAssistant",
    pattern="plan_execute"  # Use Plan-Execute pattern
)

# Agent is ready at: agents/ResearchAssistant/
```

### Example 3: Export Existing Agent

```bash
# Using Chat UI
python scripts/start_chat_ui.bat

# Commands:
/list      # View all agents
/export    # Export agent
1          # Select agent number

# Output: exports/ResearchAssistant_dify.zip
```

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| **AI Framework** | LangGraph, LangChain |
| **LLM Providers** | OpenAI, Anthropic, Azure |
| **Vector DB** | Chroma |
| **Web UI** | Streamlit |
| **Testing** | DeepEval, pytest |
| **Validation** | Pydantic v2 |
| **Templates** | Jinja2 |
| **Document Processing** | Unstructured, PyMuPDF |

---

## 🎓 Advanced Usage

### Custom Design Patterns

Create your own agent patterns:

```python
from src.schemas.pattern import PatternConfig

custom_pattern = PatternConfig(
    name="custom_workflow",
    description="My custom agent pattern",
    states=["start", "process", "validate", "end"],
    edges=[
        {"from": "start", "to": "process"},
        {"from": "process", "to": "validate"},
        {"from": "validate", "to": "end", "condition": "is_valid"},
        {"from": "validate", "to": "process", "condition": "needs_retry"}
    ]
)
```

### Multi-Agent Orchestration

```python
# Create supervisor agent
supervisor = factory.create_agent(
    requirement="Supervisor that coordinates research and writing agents",
    pattern="supervisor"
)

# Create worker agents
researcher = factory.create_agent(
    requirement="Research papers and extract insights",
    pattern="sequential"
)

writer = factory.create_agent(
    requirement="Write reports based on research",
    pattern="reflection"
)
```

### Custom Tool Integration

```python
from src.tools.registry import ToolRegistry

# Register custom tool
@ToolRegistry.register("my_custom_tool")
def my_tool(query: str) -> str:
    """Custom tool implementation"""
    return f"Processed: {query}"
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Code formatting
black src/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent framework
- [Dify](https://dify.ai) - AI application platform
- [Streamlit](https://streamlit.io) - Web UI framework
- [DeepEval](https://github.com/confident-ai/deepeval) - Testing framework

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Agent_Zero/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Agent_Zero/discussions)
- **Documentation**: [docs/](docs/)

---

<div align="center">

**Built with ❤️ by the Agent Zero Team**

If this project helps you, please give us a ⭐️

</div>
