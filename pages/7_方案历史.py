import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import (
    list_designs, get_design, save_design, delete_design, clear_all
)
from core.session import require_login, current_user

st.set_page_config(page_title="方案历史", page_icon="💾", layout="wide")

require_login()
user = current_user()

st.title("💾 方案管理")
st.caption(f"当前用户：{user['name']} —— 只显示你自己的方案")

# ---------- 保存当前方案 ----------
st.markdown("### 💾 保存当前方案")

if "aircraft_input" not in st.session_state:
    st.info("👉 请先去 **📥 设计输入** 页面输入参数，再回来保存")
else:
    base = st.session_state["aircraft_input"]
    result = st.session_state["aircraft_result"]

    col1, col2 = st.columns([2, 1])
    with col1:
        default_name = f"方案_{base['n_passengers']}座_{int(base['range_km'])}km"
        design_name = st.text_input("方案名称", value=default_name)
    with col2:
        st.write("")
        st.write("")
        if st.button("💾 保存", type="primary"):
            if design_name.strip():
                did = save_design(user["id"], design_name, base, result)
                st.success(f"✅ 已保存：{design_name}（ID={did}）")
            else:
                st.warning("请输入方案名称")

st.divider()

# ---------- 方案列表 ----------
st.markdown("### 📋 我的方案")

designs = list_designs(user["id"])

if not designs:
    st.info("暂无保存的方案。去设计输入页，调好参数后保存一个吧！")
else:
    df = pd.DataFrame(designs, columns=["ID", "方案名称", "创建时间"])
    st.dataframe(df, width='stretch', hide_index=True)

    st.markdown("### 🔍 查看详情")
    selected_id = st.selectbox(
        "选择方案",
        options=[d[0] for d in designs],
        format_func=lambda x: next(
            f"{d[1]}（ID={d[0]}）" for d in designs if d[0] == x
        ),
    )

    if selected_id:
        design = get_design(selected_id, user["id"])
        if design:
            r = design["result_data"]
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("起飞重量", f"{r['W_TO_ton']:.2f} t")
            col2.metric("翼面积", f"{r['S_wing_m2']:.2f} m²")
            col3.metric("翼展", f"{r['wingspan_m']:.2f} m")
            col4.metric("推力需求", f"{r['T_required_kN']:.1f} kN")

            with st.expander("📋 完整参数"):
                st.json(r)

    st.divider()
    st.markdown("### 🗑️ 管理")
    col1, col2 = st.columns(2)
    with col1:
        del_id = st.number_input("删除某条（输入 ID）", min_value=0, step=1)
        if st.button("删除"):
            if del_id > 0:
                delete_design(del_id, user["id"])
                st.success(f"已删除 ID={del_id}")
                st.rerun()
    with col2:
        if st.button("⚠️ 清空全部"):
            clear_all(user["id"])
            st.success("已清空你的方案")
            st.rerun()