"""
状态检查器组件

提供 Agent 运行时状态的查看和修改功能
"""

import streamlit as st
import json
from typing import Dict, Any, Optional


class StateInspector:
    """状态检查器"""

    @staticmethod
    def show(current_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        显示状态检查器

        Args:
            current_state: 当前状态字典

        Returns:
            修改后的状态（如果用户应用了修改），否则返回 None
        """
        st.subheader("🔍 当前状态")

        # 显示状态概览
        StateInspector._show_state_overview(current_state)

        st.divider()

        # 状态编辑器
        return StateInspector._show_state_editor(current_state)

    @staticmethod
    def _show_state_overview(state: Dict[str, Any]):
        """显示状态概览"""
        st.markdown("**状态概览**")

        # 统计信息
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("字段数量", len(state))

        with col2:
            # 计算嵌套深度
            def get_depth(obj, current_depth=0):
                if isinstance(obj, dict):
                    if not obj:
                        return current_depth
                    return max(get_depth(v, current_depth + 1) for v in obj.values())
                elif isinstance(obj, list):
                    if not obj:
                        return current_depth
                    return max(get_depth(item, current_depth + 1) for item in obj)
                return current_depth

            depth = get_depth(state)
            st.metric("嵌套深度", depth)

        with col3:
            # 计算总大小（字符数）
            json_str = json.dumps(state, ensure_ascii=False)
            st.metric("大小（字符）", len(json_str))

        # 字段列表
        st.markdown("**字段列表:**")
        for key, value in state.items():
            value_type = type(value).__name__
            value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            st.text(f"• {key} ({value_type}): {value_preview}")

    @staticmethod
    def _show_state_editor(state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        显示状态编辑器

        Args:
            state: 当前状态

        Returns:
            修改后的状态或 None
        """
        st.markdown("**编辑状态**")

        # 将状态转换为 JSON 字符串
        state_json = json.dumps(state, indent=2, ensure_ascii=False)

        # 文本编辑器
        edited_state_json = st.text_area(
            "状态 JSON（可编辑）",
            value=state_json,
            height=400,
            help="修改 JSON 格式的状态数据，点击下方按钮应用修改",
        )

        # 按钮区域
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            apply_btn = st.button("💾 应用修改", type="primary", use_container_width=True)

        with col2:
            reset_btn = st.button("🔄 重置", use_container_width=True)

        with col3:
            st.caption("⚠️ 修改状态可能影响 Agent 执行")

        # 处理按钮点击
        if apply_btn:
            try:
                new_state = json.loads(edited_state_json)
                st.success("✅ 状态已更新")
                return new_state
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON 格式错误: {e}")
                return None

        if reset_btn:
            st.info("🔄 状态已重置")
            st.rerun()

        return None

    @staticmethod
    def show_compact(state: Dict[str, Any]):
        """
        紧凑版状态显示（用于侧边栏）

        Args:
            state: 当前状态
        """
        st.markdown("**🔍 状态快照**")

        # 只显示关键字段
        key_fields = ["messages", "query", "result", "iteration"]

        for field in key_fields:
            if field in state:
                value = state[field]
                if isinstance(value, list):
                    st.caption(f"{field}: [{len(value)} items]")
                elif isinstance(value, dict):
                    st.caption(f"{field}: {{{len(value)} keys}}")
                else:
                    value_str = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                    st.caption(f"{field}: {value_str}")

    @staticmethod
    def show_field_editor(state: Dict[str, Any], field_name: str) -> Optional[Any]:
        """
        显示单个字段的编辑器

        Args:
            state: 当前状态
            field_name: 字段名

        Returns:
            修改后的字段值或 None
        """
        if field_name not in state:
            st.warning(f"字段 '{field_name}' 不存在")
            return None

        st.subheader(f"编辑字段: {field_name}")

        current_value = state[field_name]
        value_type = type(current_value).__name__

        st.caption(f"类型: {value_type}")

        # 根据类型选择编辑器
        if isinstance(current_value, str):
            new_value = st.text_area("值", current_value, height=150)
        elif isinstance(current_value, (int, float)):
            new_value = st.number_input("值", value=current_value)
        elif isinstance(current_value, bool):
            new_value = st.checkbox("值", value=current_value)
        elif isinstance(current_value, (list, dict)):
            # 使用 JSON 编辑器
            json_value = json.dumps(current_value, indent=2, ensure_ascii=False)
            edited_json = st.text_area("值（JSON）", json_value, height=200)
            try:
                new_value = json.loads(edited_json)
            except json.JSONDecodeError:
                st.error("JSON 格式错误")
                return None
        else:
            st.warning(f"不支持的类型: {value_type}")
            return None

        if st.button("💾 保存", type="primary"):
            return new_value

        return None

    @staticmethod
    def show_diff(old_state: Dict[str, Any], new_state: Dict[str, Any]):
        """
        显示状态差异

        Args:
            old_state: 旧状态
            new_state: 新状态
        """
        st.subheader("📊 状态差异")

        # 找出差异
        added_keys = set(new_state.keys()) - set(old_state.keys())
        removed_keys = set(old_state.keys()) - set(new_state.keys())
        common_keys = set(old_state.keys()) & set(new_state.keys())

        changed_keys = []
        for key in common_keys:
            if old_state[key] != new_state[key]:
                changed_keys.append(key)

        # 显示差异
        if added_keys:
            st.success(f"✅ 新增字段: {', '.join(added_keys)}")

        if removed_keys:
            st.error(f"❌ 删除字段: {', '.join(removed_keys)}")

        if changed_keys:
            st.warning(f"🔄 修改字段: {', '.join(changed_keys)}")

            # 显示详细差异
            for key in changed_keys:
                with st.expander(f"字段: {key}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**旧值:**")
                        st.json(old_state[key])

                    with col2:
                        st.markdown("**新值:**")
                        st.json(new_state[key])

        if not (added_keys or removed_keys or changed_keys):
            st.info("无差异")


# 便捷函数
def show_state_inspector(state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    显示状态检查器

    Args:
        state: 当前状态

    Returns:
        修改后的状态或 None
    """
    return StateInspector.show(state)


def show_state_compact(state: Dict[str, Any]):
    """
    显示紧凑版状态

    Args:
        state: 当前状态
    """
    StateInspector.show_compact(state)


def create_state_sidebar(state: Dict[str, Any]):
    """
    在侧边栏创建状态显示

    Args:
        state: 当前状态
    """
    with st.sidebar:
        st.divider()
        StateInspector.show_compact(state)
