"""
流式日志查看器组件

提供实时日志显示功能，支持自动滚动和日志级别过滤
"""

import streamlit as st
from typing import List, Optional
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class LogViewer:
    """流式日志查看器"""

    # 日志级别对应的 emoji 和颜色
    LEVEL_CONFIG = {
        LogLevel.DEBUG: {"emoji": "🔍", "color": "#808080"},
        LogLevel.INFO: {"emoji": "ℹ️", "color": "#0066cc"},
        LogLevel.WARNING: {"emoji": "⚠️", "color": "#ff9900"},
        LogLevel.ERROR: {"emoji": "❌", "color": "#cc0000"},
        LogLevel.SUCCESS: {"emoji": "✅", "color": "#00cc00"},
    }

    def __init__(self, max_logs: int = 1000):
        """
        初始化日志查看器

        Args:
            max_logs: 最大保存的日志条数
        """
        self.max_logs = max_logs

        # 初始化 session_state
        if 'log_history' not in st.session_state:
            st.session_state.log_history = []
        if 'log_filter' not in st.session_state:
            st.session_state.log_filter = None

    def append_log(self, message: str, level: LogLevel = LogLevel.INFO):
        """
        追加日志消息

        Args:
            message: 日志内容
            level: 日志级别
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }

        # 添加到历史记录
        st.session_state.log_history.append(log_entry)

        # 限制日志数量
        if len(st.session_state.log_history) > self.max_logs:
            st.session_state.log_history = st.session_state.log_history[-self.max_logs:]

    def clear_logs(self):
        """清空日志"""
        st.session_state.log_history = []

    def _format_log_entry(self, log_entry: dict) -> str:
        """
        格式化单条日志

        Args:
            log_entry: 日志条目

        Returns:
            格式化后的 HTML 字符串
        """
        level = log_entry["level"]
        config = self.LEVEL_CONFIG.get(level, {"emoji": "📝", "color": "#000000"})

        return f"""
        <div style="margin-bottom: 8px; padding: 8px; border-left: 3px solid {config['color']}; background-color: rgba(0,0,0,0.02);">
            <span style="color: {config['color']}; font-weight: bold;">
                {config['emoji']} [{log_entry['timestamp']}] {level.value}
            </span>
            <span style="margin-left: 10px; color: #333;">
                {log_entry['message']}
            </span>
        </div>
        """

    def render(self, height: int = 400, enable_filter: bool = True, auto_scroll: bool = True):
        """
        渲染日志查看器

        Args:
            height: 日志容器高度（像素）
            enable_filter: 是否启用日志级别过滤
            auto_scroll: 是否自动滚动到底部
        """
        # 过滤器
        if enable_filter:
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                filter_options = ["全部"] + [level.value for level in LogLevel]
                selected_filter = st.selectbox(
                    "日志级别过滤",
                    filter_options,
                    key="log_level_filter"
                )
                st.session_state.log_filter = None if selected_filter == "全部" else selected_filter

            with col2:
                if st.button("🗑️ 清空日志", key="clear_logs_btn"):
                    self.clear_logs()
                    st.rerun()

            with col3:
                st.metric("日志条数", len(st.session_state.log_history))

        # 过滤日志
        filtered_logs = st.session_state.log_history
        if st.session_state.log_filter:
            filtered_logs = [
                log for log in st.session_state.log_history
                if log["level"].value == st.session_state.log_filter
            ]

        # 渲染日志容器
        if not filtered_logs:
            st.info("📝 暂无日志")
        else:
            # 生成 HTML
            logs_html = "".join([self._format_log_entry(log) for log in filtered_logs])

            # 容器样式
            container_style = f"""
            <div id="log-container" style="
                max-height: {height}px;
                overflow-y: auto;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
                font-family: monospace;
                font-size: 13px;
            ">
                {logs_html}
            </div>
            """

            # 自动滚动脚本
            scroll_script = """
            <script>
                // 等待 DOM 加载完成
                setTimeout(function() {
                    var logContainer = document.getElementById('log-container');
                    if (logContainer) {
                        logContainer.scrollTop = logContainer.scrollHeight;
                    }
                }, 100);
            </script>
            """ if auto_scroll else ""

            st.markdown(container_style + scroll_script, unsafe_allow_html=True)

    def render_compact(self, max_display: int = 10):
        """
        渲染紧凑版日志查看器（用于侧边栏或小空间）

        Args:
            max_display: 最多显示的日志条数
        """
        st.subheader("📋 最近日志")

        recent_logs = st.session_state.log_history[-max_display:]

        if not recent_logs:
            st.caption("暂无日志")
        else:
            for log in reversed(recent_logs):  # 最新的在上面
                config = self.LEVEL_CONFIG.get(log["level"], {"emoji": "📝", "color": "#000000"})
                st.caption(f"{config['emoji']} `{log['timestamp']}` {log['message']}")


# 便捷函数
def create_log_viewer(max_logs: int = 1000) -> LogViewer:
    """
    创建日志查看器实例

    Args:
        max_logs: 最大保存的日志条数

    Returns:
        LogViewer 实例
    """
    return LogViewer(max_logs=max_logs)


def log_info(message: str):
    """记录 INFO 级别日志"""
    if 'log_viewer' not in st.session_state:
        st.session_state.log_viewer = LogViewer()
    st.session_state.log_viewer.append_log(message, LogLevel.INFO)


def log_warning(message: str):
    """记录 WARNING 级别日志"""
    if 'log_viewer' not in st.session_state:
        st.session_state.log_viewer = LogViewer()
    st.session_state.log_viewer.append_log(message, LogLevel.WARNING)


def log_error(message: str):
    """记录 ERROR 级别日志"""
    if 'log_viewer' not in st.session_state:
        st.session_state.log_viewer = LogViewer()
    st.session_state.log_viewer.append_log(message, LogLevel.ERROR)


def log_success(message: str):
    """记录 SUCCESS 级别日志"""
    if 'log_viewer' not in st.session_state:
        st.session_state.log_viewer = LogViewer()
    st.session_state.log_viewer.append_log(message, LogLevel.SUCCESS)


def log_debug(message: str):
    """记录 DEBUG 级别日志"""
    if 'log_viewer' not in st.session_state:
        st.session_state.log_viewer = LogViewer()
    st.session_state.log_viewer.append_log(message, LogLevel.DEBUG)
