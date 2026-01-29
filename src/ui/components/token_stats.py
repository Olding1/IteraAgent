"""
Token 消耗统计组件

显示 LLM API 调用的 Token 消耗和成本统计
"""

import streamlit as st
from typing import Dict, Optional


class TokenStatsDisplay:
    """Token 统计显示组件"""

    @staticmethod
    def display_metrics(stats: Dict, title: str = "📊 Token 消耗统计"):
        """
        显示 Token 统计指标

        Args:
            stats: 统计信息字典
            title: 标题
        """
        st.subheader(title)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="总调用次数",
                value=f"{stats.get('total_calls', 0):,}",
                help="LLM API 的总调用次数"
            )

        with col2:
            st.metric(
                label="输入 Tokens",
                value=f"{stats.get('total_input_tokens', 0):,}",
                help="发送给 LLM 的总 token 数量"
            )

        with col3:
            st.metric(
                label="输出 Tokens",
                value=f"{stats.get('total_output_tokens', 0):,}",
                help="LLM 生成的总 token 数量"
            )

        with col4:
            cost = stats.get('total_cost_usd', 0.0)
            st.metric(
                label="预估成本",
                value=f"${cost:.4f}",
                help="基于官方定价的预估成本（美元）"
            )

    @staticmethod
    def display_detailed(stats: Dict):
        """
        显示详细的 Token 统计信息

        Args:
            stats: 统计信息字典
        """
        st.subheader("📈 详细统计")

        # 计算总 tokens
        total_tokens = stats.get('total_input_tokens', 0) + stats.get('total_output_tokens', 0)

        # 创建数据表
        data = {
            "指标": [
                "总调用次数",
                "输入 Tokens",
                "输出 Tokens",
                "总 Tokens",
                "平均输入 Tokens/次",
                "平均输出 Tokens/次",
                "预估成本（美元）"
            ],
            "数值": [
                f"{stats.get('total_calls', 0):,}",
                f"{stats.get('total_input_tokens', 0):,}",
                f"{stats.get('total_output_tokens', 0):,}",
                f"{total_tokens:,}",
                f"{stats.get('total_input_tokens', 0) / max(stats.get('total_calls', 1), 1):.1f}",
                f"{stats.get('total_output_tokens', 0) / max(stats.get('total_calls', 1), 1):.1f}",
                f"${stats.get('total_cost_usd', 0.0):.4f}"
            ]
        }

        st.table(data)

    @staticmethod
    def display_chart(stats: Dict):
        """
        显示 Token 消耗图表

        Args:
            stats: 统计信息字典
        """
        import pandas as pd

        st.subheader("📊 Token 分布")

        input_tokens = stats.get('total_input_tokens', 0)
        output_tokens = stats.get('total_output_tokens', 0)

        if input_tokens == 0 and output_tokens == 0:
            st.info("暂无数据")
            return

        # 创建饼图数据
        chart_data = pd.DataFrame({
            "类型": ["输入 Tokens", "输出 Tokens"],
            "数量": [input_tokens, output_tokens]
        })

        st.bar_chart(chart_data.set_index("类型"))

    @staticmethod
    def display_compact(stats: Dict):
        """
        紧凑版显示（用于侧边栏）

        Args:
            stats: 统计信息字典
        """
        st.markdown("**📊 Token 统计**")

        total_tokens = stats.get('total_input_tokens', 0) + stats.get('total_output_tokens', 0)
        cost = stats.get('total_cost_usd', 0.0)

        st.caption(f"🔢 总调用: {stats.get('total_calls', 0):,}")
        st.caption(f"📥 输入: {stats.get('total_input_tokens', 0):,}")
        st.caption(f"📤 输出: {stats.get('total_output_tokens', 0):,}")
        st.caption(f"💰 成本: ${cost:.4f}")

    @staticmethod
    def display_full(stats: Dict):
        """
        完整显示（包含所有信息）

        Args:
            stats: 统计信息字典
        """
        # 指标卡片
        TokenStatsDisplay.display_metrics(stats)

        st.divider()

        # 详细表格和图表
        col1, col2 = st.columns(2)

        with col1:
            TokenStatsDisplay.display_detailed(stats)

        with col2:
            TokenStatsDisplay.display_chart(stats)


# 便捷函数
def show_token_stats(stats: Dict, mode: str = "metrics"):
    """
    显示 Token 统计

    Args:
        stats: 统计信息字典
        mode: 显示模式 (metrics/detailed/chart/compact/full)
    """
    if mode == "metrics":
        TokenStatsDisplay.display_metrics(stats)
    elif mode == "detailed":
        TokenStatsDisplay.display_detailed(stats)
    elif mode == "chart":
        TokenStatsDisplay.display_chart(stats)
    elif mode == "compact":
        TokenStatsDisplay.display_compact(stats)
    elif mode == "full":
        TokenStatsDisplay.display_full(stats)
    else:
        raise ValueError(f"Unknown mode: {mode}")


def create_token_stats_sidebar(stats: Dict):
    """
    在侧边栏创建 Token 统计

    Args:
        stats: 统计信息字典
    """
    with st.sidebar:
        st.divider()
        TokenStatsDisplay.display_compact(stats)
