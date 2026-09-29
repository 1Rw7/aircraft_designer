import streamlit as st
from core.database import init_db
from core.auth import login, register
from core.session import is_logged_in, current_user

st.set_page_config(
    page_title="飞机概念设计器",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

st.markdown("""
<style>
    .main-title {
        font-size: 3em; font-weight: 800;
        background: linear-gradient(135deg, #1a3a5c 0%, #2c7ba8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2em;
    }
    .subtitle { color: #666; font-size: 1.15em; margin-bottom: 1.5em; }
    .card {
        background: #f8f9fc; border-radius: 12px;
        padding: 1.3em 1.5em;
        border-left: 4px solid #2c7ba8;
        margin-bottom: 1em;
    }
    .card-title { font-size: 1.15em; font-weight: 700; color: #1a3a5c; margin-bottom: 0.3em; }
    .card-desc { color: #555; font-size: 0.95em; line-height: 1.6; }
    .flow-box {
        display: inline-block; background: #e8f2f9;
        border-radius: 8px; padding: 0.8em 1.2em;
        margin: 0.3em; font-weight: 600; color: #1a3a5c;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 侧边栏登录状态 ----------
if is_logged_in():
    user = current_user()
    st.sidebar.success(f"👤 已登录：**{user['name']}**")
    if st.sidebar.button("退出登录"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
else:
    st.sidebar.warning("🔒 未登录")

# ---------- 未登录：显示登录/注册表单 ----------
if not is_logged_in():
    st.markdown('<div class="main-title">✈️ 飞机概念设计器</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">从设计指标到总体参数 —— 一个交互式的飞机初步设计工具</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔐 请登录或注册以使用")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔑 登录")
        with st.form("login_form"):
            login_user = st.text_input("用户名", key="login_user")
            login_pwd = st.text_input("密码", type="password", key="login_pwd")
            submitted = st.form_submit_button("登录", type="primary")
            if submitted:
                ok, msg, uname = login(login_user, login_pwd)
                if ok:
                    st.session_state.user_id = msg
                    st.session_state.username = uname
                    st.success(f"欢迎回来，{uname}！")
                    st.rerun()
                else:
                    st.error(msg)

    with col2:
        st.subheader("✨ 注册新账号")
        with st.form("register_form"):
            reg_user = st.text_input("用户名（≥2 字符）", key="reg_user")
            reg_pwd = st.text_input("密码（≥4 字符）", type="password", key="reg_pwd")
            reg_pwd2 = st.text_input("确认密码", type="password", key="reg_pwd2")
            submitted = st.form_submit_button("注册", type="primary")
            if submitted:
                if reg_pwd != reg_pwd2:
                    st.error("两次密码不一致")
                else:
                    ok, msg = register(reg_user, reg_pwd)
                    if ok:
                        st.success("注册成功！请到左侧登录。")
                    else:
                        st.error(msg)

    st.divider()
    st.info("💡 **提示**：每个账号的**设计方案独立存档**，你保存的方案只有自己能看见。")
    st.stop()

# ---------- 已登录：显示首页 ----------
user = current_user()
st.markdown(f'<div class="main-title">✈️ 欢迎，{user["name"]}！</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">从设计指标到总体参数 —— 一个交互式的飞机初步设计工具</div>', unsafe_allow_html=True)

st.markdown("### 🚀 功能导航")

features = [
    ("📥", "设计输入", "输入乘客数、航程、巡航速度等设计指标"),
    ("📊", "计算结果", "起飞重量、翼面积、推力需求等总体参数"),
    ("📈", "气动性能", "升力曲线、阻力极曲线、升阻比分析"),
    ("✈️", "3D 概念模型", "参数化生成 3D 飞机模型"),
    ("🔍", "敏感性分析", "看哪个参数对起飞重量影响最大"),
    ("📚", "知识库", "公式和术语解释"),
    ("💾", "方案管理", "保存和对比多个设计方案（仅显示你自己的）"),
]

col1, col2 = st.columns(2)
for i, (icon, title, desc) in enumerate(features):
    target = col1 if i % 2 == 0 else col2
    with target:
        st.markdown(
            f'<div class="card"><div class="card-title">{icon} {title}</div>'
            f'<div class="card-desc">{desc}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("### 🎯 设计流程")
st.markdown("""
<div style="text-align: center; margin: 1.5em 0;">
    <span class="flow-box">📥 输入指标</span>
    <span style="font-size: 1.5em; color: #999;">→</span>
    <span class="flow-box">🔢 迭代计算</span>
    <span style="font-size: 1.5em; color: #999;">→</span>
    <span class="flow-box">📊 输出参数</span>
    <span style="font-size: 1.5em; color: #999;">→</span>
    <span class="flow-box">📈 气动分析</span>
    <span style="font-size: 1.5em; color: #999;">→</span>
    <span class="flow-box">✈️ 3D 可视化</span>
</div>
""", unsafe_allow_html=True)

st.divider()
st.info("💡 **快速开始**：左侧导航栏点击 **📥 设计输入**，输入你的设计指标。")
st.caption("✈️ 飞机概念设计器 · 基于 Python + Streamlit · 版本 1.0")