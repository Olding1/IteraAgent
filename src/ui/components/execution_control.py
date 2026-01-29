"""
执行控制组件

提供 HITL (Human-in-the-Loop) 执行控制界面
支持暂停、继续、停止等操作
"""

import streamlit as st
import time
from typing import Optional
from ...core.runner import Runner, ExecutionControl


class ExecutionControlPanel:
    """执行控制面板"""

    @staticmethod
    def show_controls(runner: Optional[Runner] = None):
        """
        显示执行控制按钮

        Args:
            runner: Runner 实例（可选，从 session_state 获取）
        """
        # 从 session_state 获取 runner
        if runner is None:
            runner = st.session_state.get('runner')

        if not runner:
            st.warning("⚠️ 没有正在运行的任务")
            return

        st.subheader("🎮 执行控制")

        # 显示当前状态
        status = runner.get_status()
        status_emoji = {
            "running": "▶️",
            "paused": "⏸️",
            "stopped": "⏹️"
        }
        status_color = {
            "running": "🟢",
            "paused": "🟡",
            "stopped": "🔴"
        }

        st.markdown(f"**当前状态:** {status_color.get(status, '⚪')} {status_emoji.get(status, '❓')} {status.upper()}")

        # 控制按钮
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("⏸️ 暂停", disabled=(status != "running"), use_container_width=True):
                runner.pause()
                st.success("已暂停")
                st.rerun()

        with col2:
            if st.button("▶️ 继续", disabled=(status != "paused"), use_container_width=True):
                runner.resume()
                st.success("已继续")
                st.rerun()

        with col3:
            if st.button("⏹️ 停止", disabled=(status == "stopped"), type="secondary", use_container_width=True):
                runner.stop()
                st.error("已停止")
                st.rerun()

    @staticmethod
    def show_status_monitor(runner: Optional[Runner] = None, auto_refresh: bool = True):
        """
        显示状态监控器（轮询状态和日志）

        Args:
            runner: Runner 实例
            auto_refresh: 是否自动刷新
        """
        # 从 session_state 获取 runner
        if runner is None:
            runner = st.session_state.get('runner')

        if not runner:
            return

        # 状态显示区域
        status_placeholder = st.empty()
        log_placeholder = st.empty()

        # 轮询状态队列
        try:
            while not runner.status_queue.empty():
                status_msg = runner.status_queue.get_nowait()
                status_placeholder.info(f"📊 状态: {status_msg.get('message', 'Unknown')}")
        except:
            pass

        # 轮询日志队列
        try:
            logs = []
            while not runner.log_queue.empty():
                log_msg = runner.log_queue.get_nowait()
                level = log_msg.get('level', 'INFO')
                message = log_msg.get('message', '')

                level_emoji = {
                    "INFO": "ℹ️",
                    "WARNING": "⚠️",
                    "ERROR": "❌",
                    "SUCCESS": "✅"
                }
                emoji = level_emoji.get(level, "📝")
                logs.append(f"{emoji} {message}")

            if logs:
                log_placeholder.text_area("最近日志", "\n".join(logs[-10:]), height=150)
        except:
            pass

        # 自动刷新
        if auto_refresh and runner.get_status() == "running":
            time.sleep(0.5)
            st.rerun()

    @staticmethod
    def show_compact_controls():
        """紧凑版控制面板（用于侧边栏）"""
        runner = st.session_state.get('runner')

        if not runner:
            st.caption("⚪ 无运行任务")
            return

        status = runner.get_status()
        status_emoji = {
            "running": "▶️",
            "paused": "⏸️",
            "stopped": "⏹️"
        }

        st.markdown(f"**状态:** {status_emoji.get(status, '❓')} {status}")

        # 按钮行
        col1, col2 = st.columns(2)

        with col1:
            if status == "running":
                if st.button("⏸️", key="compact_pause"):
                    runner.pause()
                    st.rerun()
            elif status == "paused":
                if st.button("▶️", key="compact_resume"):
                    runner.resume()
                    st.rerun()

        with col2:
            if status != "stopped":
                if st.button("⏹️", key="compact_stop"):
                    runner.stop()
                    st.rerun()


class ExecutionMonitor:
    """执行监控器"""

    @staticmethod
    def show_progress(runner: Optional[Runner] = None):
        """
        显示执行进度

        Args:
            runner: Runner 实例
        """
        runner = runner or st.session_state.get('runner')

        if not runner:
            st.info("暂无执行任务")
            return

        st.subheader("📈 执行进度")

        # 这里可以添加更详细的进度信息
        # 例如：当前测试用例、已完成数量等
        status = runner.get_status()

        if status == "running":
            st.progress(0.5, text="执行中...")
        elif status == "paused":
            st.warning("⏸️ 执行已暂停")
        elif status == "stopped":
            st.error("⏹️ 执行已停止")


# 便捷函数
def show_execution_controls(runner: Optional[Runner] = None):
    """
    显示执行控制面板

    Args:
        runner: Runner 实例
    """
    ExecutionControlPanel.show_controls(runner)


def show_execution_monitor(runner: Optional[Runner] = None, auto_refresh: bool = True):
    """
    显示执行监控器

    Args:
        runner: Runner 实例
        auto_refresh: 是否自动刷新
    """
    ExecutionControlPanel.show_status_monitor(runner, auto_refresh)


def create_execution_sidebar(runner: Optional[Runner] = None):
    """
    在侧边栏创建执行控制

    Args:
        runner: Runner 实例
    """
    with st.sidebar:
        st.divider()
        st.markdown("### 🎮 执行控制")
        ExecutionControlPanel.show_compact_controls()
