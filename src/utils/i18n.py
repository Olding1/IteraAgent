"""
i18n - Internationalization module for IteraAgent

Provides translation support for Chinese and English.
"""

# Global language setting
_CURRENT_LANG = "zh"  # Default to Chinese

# Translation dictionary
TRANSLATIONS = {
    "zh": {
        # Banner and startup
        "banner": "🚀 IteraAgent v8.0 - 智能 Agent 构建工厂",
        "banner_subtitle": "   🆕 Interface Guard | 🔍 Tool Discovery | 📚 114+ Tools",
        "select_language": "Select Language / 选择语言",
        "language_chinese": "1. 中文 (Chinese)",
        "language_english": "2. English",
        "language_prompt": "\nPlease select / 请选择 (1/2): ",
        # System health check
        "health_check": "📊 系统健康检查",
        "health_check_title": "📊 系统健康检查",
        "checking_builder_api": "🔍 正在检查 Builder API...",
        "checking_runtime_api": "🔍 正在检查 Runtime API...",
        "provider": "提供商",
        "model": "模型",
        "api_key": "API Key",
        "api_key_configured": "✓ 已配置",
        "api_key_missing": "✗ 缺失",
        "testing_connectivity": "⏳ 正在测试连接性...",
        "response_time": "响应时间",
        "all_systems_ok": "✅ 所有系统运行正常！",
        "partial_systems_down": "⚠️  部分系统运行异常",
        "system_issues": "⚠️  部分系统运行异常",
        "check_suggestions": "请检查:",
        "check_env_file": "1. .env 文件中是否配置了正确 API Key",
        "check_network": "2. 网络连接状态",
        "check_api_status": "3. API 服务状态",
        "check_instructions": "\n请检查:\n1. .env 文件中是否配置了正确 API Key\n2. 网络连接状态\n3. API 服务状态",
        "health_check_failed": "❌ 健康检查失败",
        "health_warning": "⚠️  系统健康检查未通过。您可以继续，但\n   部分功能可能无法正常工作。",
        "continue_anyway": "仍要继续吗? (y/n)",
        "exiting": "正在退出...",
        # Main menu
        "main_menu": "📋 主菜单",
        "main_menu_title": "📋 主菜单",
        "menu_create": "🏗️  新建 Agent",
        "menu_view": "📦 查看已生成 Agent",
        "menu_retest": "🔄 重新测试现有 Agent (迭代优化)",
        "menu_config": "🔧 配置 API 设置",
        "menu_tests": "🧪 运行测试",
        "menu_run_tests": "🧪 运行测试",
        "menu_docs": "📖 查看文档",
        "menu_export": "📤 导出 Agent 到 Dify",
        "menu_webui": "🎨 启动 Web UI",
        "menu_exit": "🚪 退出",
        "menu_prompt": "请选择 (1-9): ",
        "select_option": "请选择 (1-9)",
        # Factory
        "factory_title": "🏭 Agent 工厂 - 交互模式",
        "factory_describe": "请输入您想构建的 Agent 描述:\n> ",
        "factory_files": "\n是否有参考文件/文档? (逗号分隔路径，或留空):\n> ",
        "building": "开始构建... (这可能需要几分钟)",
        # Progress steps
        "step_pm": "PM Agent",
        "step_resource": "Resource Config",
        "step_design": "Design & Simulation",
        "step_build": "Build & Evolve",
        "step_complete": "完成",
        # Results
        "agent_created": "🎉 Agent 构建成功!",
        "agent_location": "📂 位置",
        "time_elapsed": "⏱️  耗时",
        "iterations": "🔄 迭代次数",
        "modules_updated": "✅ 核心模块已更新",
        "press_enter": "\n按回车键继续...",
        # Errors
        "error": "❌ 错误",
        "interrupted": "👋 Interrupted by user. Goodbye!",
        "invalid_option": "❌ 无效选项，请选择 1-9。",
        "no_env_file": "⚠️  未找到 .env 文件!",
        "env_instructions": "\n请从模板创建 .env 文件:\n   cp .env.template .env\n\n然后编辑 .env 并添加您的 API Keys。",
        # Agent management
        "generated_agents": "📦 已生成的 Agent",
        "no_agents": "   (空) 尚未生成任何 Agent",
        "agents_dir_missing": "   (空) agents 目录不存在",
        "select_agent": "请输入序号选择要运行的 Agent (或输入 0 返回):",
        "starting_agent": "🚀 正在启动",
        "select_action": "请选择操作:",
        "action_run": "1. 💬 交互式运行 (python agent.py)",
        "action_test": "2. 🧪 运行测试 (pytest)",
        # Export
        "export_title": "📤 导出 Agent 到 Dify",
        "available_agents": "\n可用的 Agent:",
        "select_agent_number": "\n请选择 Agent 编号 (0=取消): ",
        "graph_not_found": "❌ 未找到 graph.json",
        "validating_graph": "\n🔍 验证 Graph...",
        "graph_valid": "✅ Graph 验证通过",
        "graph_invalid": "❌ Graph 验证失败",
        "warnings": "\n⚠️  警告信息:",
        "export_options": "\n请选择导出选项:",
        "export_dify": "  1. 导出 Dify YAML",
        "export_readme": "  2. 生成 README",
        "export_both": "  3. 两者都导出",
        "export_cancel": "  0. 取消",
        "export_success": "✅ Dify YAML 已导出",
        "readme_generated": "✅ README 已生成",
        "file_size": "   文件大小",
        "export_dir": "\n📁 导出目录",
        "next_steps": "\n💡 下一步:",
        "dify_instructions": "   1. 访问 https://cloud.dify.ai\n   2. 创建应用 → Chatflow\n   3. 导入 DSL → 上传 YAML 文件",
        "rag_note": "   4. 手动添加 Knowledge Retrieval 节点（RAG 节点已跳过）",
        "cancelled": "已取消",
        "invalid_number": "无效序号",
        # Goodbye
        "goodbye": "\n👋 再见!",
    },
    "en": {
        # Banner and startup
        "banner": "🚀 IteraAgent v8.0 - Intelligent Agent Factory",
        "banner_subtitle": "   🆕 Interface Guard | 🔍 Tool Discovery | 📚 114+ Tools",
        "select_language": "Select Language / 选择语言",
        "language_chinese": "1. 中文 (Chinese)",
        "language_english": "2. English",
        "language_prompt": "\nPlease select / 请选择 (1/2): ",
        # System health check
        "health_check": "📊 System Health Check",
        "health_check_title": "📊 System Health Check",
        "checking_builder_api": "🔍 Checking Builder API...",
        "checking_runtime_api": "🔍 Checking Runtime API...",
        "provider": "Provider",
        "model": "Model",
        "api_key": "API Key",
        "api_key_configured": "✓ Configured",
        "api_key_missing": "✗ Missing",
        "testing_connectivity": "⏳ Testing connectivity...",
        "response_time": "Response time",
        "all_systems_ok": "✅ All systems operational!",
        "partial_systems_down": "⚠️  Some systems have issues",
        "system_issues": "⚠️  Some systems have issues",
        "check_suggestions": "Please check:",
        "check_env_file": "1. API Keys in .env file",
        "check_network": "2. Network connection",
        "check_api_status": "3. API service status",
        "check_instructions": "\nPlease check:\n1. API Keys in .env file\n2. Network connection\n3. API service status",
        "health_check_failed": "❌ Health check failed",
        "health_warning": "⚠️  System health check failed. You can continue, but\n   some features may not work properly.",
        "continue_anyway": "Continue anyway? (y/n)",
        "exiting": "Exiting...",
        # Main menu
        "main_menu": "📋 Main Menu",
        "main_menu_title": "📋 Main Menu",
        "menu_create": "🏗️  Create New Agent",
        "menu_view": "📦 View Generated Agents",
        "menu_retest": "🔄 Re-test & Optimize Agent",
        "menu_config": "🔧 Configure API Settings",
        "menu_tests": "🧪 Run Tests",
        "menu_run_tests": "🧪 Run Tests",
        "menu_docs": "📖 View Documentation",
        "menu_export": "📤 Export Agent to Dify",
        "menu_webui": "🎨 Launch Web UI",
        "menu_exit": "🚪 Exit",
        "menu_prompt": "Please select (1-9): ",
        "select_option": "Please select (1-9)",
        # Factory
        "factory_title": "🏭 Agent Factory - Interactive Mode",
        "factory_describe": "Please describe the Agent you want to build:\n> ",
        "factory_files": "\nAny reference files/documents? (comma-separated paths, or leave empty):\n> ",
        "building": "Starting build... (this may take a few minutes)",
        # Progress steps
        "step_pm": "PM Agent",
        "step_resource": "Resource Config",
        "step_design": "Design & Simulation",
        "step_build": "Build & Evolve",
        "step_complete": "Complete",
        # Results
        "agent_created": "🎉 Agent created successfully!",
        "agent_location": "📂 Location",
        "time_elapsed": "⏱️  Time elapsed",
        "iterations": "🔄 Iterations",
        "modules_updated": "✅ Core modules updated",
        "press_enter": "\nPress Enter to continue...",
        # Errors
        "error": "❌ Error",
        "interrupted": "👋 Interrupted by user. Goodbye!",
        "invalid_option": "❌ Invalid option, please select 1-9.",
        "no_env_file": "⚠️  .env file not found!",
        "env_instructions": "\nPlease create .env file from template:\n   cp .env.template .env\n\nThen edit .env and add your API Keys.",
        # Agent management
        "generated_agents": "📦 Generated Agents",
        "no_agents": "   (empty) No agents generated yet",
        "agents_dir_missing": "   (empty) agents directory does not exist",
        "select_agent": "Enter number to select agent (or 0 to return):",
        "starting_agent": "🚀 Starting",
        "select_action": "Select action:",
        "action_run": "1. 💬 Interactive run (python agent.py)",
        "action_test": "2. 🧪 Run tests (pytest)",
        # Export
        "export_title": "📤 Export Agent to Dify",
        "available_agents": "\nAvailable Agents:",
        "select_agent_number": "\nSelect agent number (0=cancel): ",
        "graph_not_found": "❌ graph.json not found",
        "validating_graph": "\n🔍 Validating Graph...",
        "graph_valid": "✅ Graph validation passed",
        "graph_invalid": "❌ Graph validation failed",
        "warnings": "\n⚠️  Warnings:",
        "export_options": "\nSelect export options:",
        "export_dify": "  1. Export Dify YAML",
        "export_readme": "  2. Generate README",
        "export_both": "  3. Export both",
        "export_cancel": "  0. Cancel",
        "export_success": "✅ Dify YAML exported",
        "readme_generated": "✅ README generated",
        "file_size": "   File size",
        "export_dir": "\n📁 Export directory",
        "next_steps": "\n💡 Next steps:",
        "dify_instructions": "   1. Visit https://cloud.dify.ai\n   2. Create App → Chatflow\n   3. Import DSL → Upload YAML file",
        "rag_note": "   4. Manually add Knowledge Retrieval node (RAG nodes skipped)",
        "cancelled": "Cancelled",
        "invalid_number": "Invalid number",
        # Goodbye
        "goodbye": "\n👋 Goodbye!",
    },
}


def set_language(lang: str):
    """Set current language."""
    global _CURRENT_LANG
    if lang in TRANSLATIONS:
        _CURRENT_LANG = lang
    else:
        _CURRENT_LANG = "zh"  # Default fallback


def get_language() -> str:
    """Get current language."""
    return _CURRENT_LANG


def t(key: str, **kwargs) -> str:
    """
    Translate key to current language.

    Args:
        key: Translation key
        **kwargs: Format arguments for string formatting

    Returns:
        Translated string
    """
    translation = TRANSLATIONS.get(_CURRENT_LANG, {}).get(key, key)

    # Support string formatting
    if kwargs:
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError):
            return translation

    return translation
