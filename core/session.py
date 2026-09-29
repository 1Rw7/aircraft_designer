"""Session 状态管理：登录状态检查"""
import streamlit as st


def is_logged_in() -> bool:
    return st.session_state.get("user_id") is not None


def current_user() -> dict:
    if not is_logged_in():
        return None
    return {
        "id": st.session_state.get("user_id"),
        "name": st.session_state.get("username"),
    }


def require_login():
    """在页面开头调用。如果没登录，显示提示并 stop()"""
    if not is_logged_in():
        st.warning("🔒 请先在首页登录")
        st.info("👉 点击左侧导航栏的 **app**，登录或注册后再回来。")
        st.stop()