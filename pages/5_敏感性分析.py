import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.calculator import calculate_aircraft
from viz.sensitivity_plot import plot_sensitivity_curve, plot_tornado_chart

st.set_page_config(page_title="敏感性分析", page_icon="🔍", layout="wide")
from core.session import require_login
require_login()
st.title("🔍 敏感性分析")
st.caption("看哪个参数对起飞重量影响最大")

if "aircraft_input" not in st.session_state:
    st.warning("⚠️ 还没有设计输入")
    st.info("👉 请先去 **📥 设计输入** 页面输入参数")
    st.stop()

base = st.session_state["aircraft_input"]

# ---------- 单参数敏感性 ----------
st.markdown("### 📊 单参数敏感性")

param_choice = st.selectbox(
    "选择要分析的参数",
    options=[
        ("n_passengers", "乘客数"),
        ("range_km", "航程 (km)"),
        ("cruise_mach", "巡航马赫数"),
        ("cruise_altitude_m", "巡航高度 (m)"),
    ],
    format_func=lambda x: x[1],
)
param_key, param_label = param_choice

variations = [-0.2, -0.1, 0, 0.1, 0.2]
base_value = base[param_key]

sens_data = []
for var in variations:
    params = base.copy()
    params[param_key] = base_value * (1 + var)
    try:
        r = calculate_aircraft(**params)
        sens_data.append({
            "variation": var,
            "param_value": params[param_key],
            "W_TO_ton": r["W_TO_ton"],
        })
    except Exception:
        sens_data.append({
            "variation": var,
            "param_value": params[param_key],
            "W_TO_ton": None,
        })

fig = plot_sensitivity_curve(sens_data, param_label, base_value)
st.plotly_chart(fig, width='stretch')

# 数值展示
st.markdown("#### 📋 数据表")
import pandas as pd
df = pd.DataFrame([{
    f"{param_label}": f"{d['param_value']:.2f}",
    "变化": f"{d['variation']*100:+.0f}%",
    "起飞重量 (t)": f"{d['W_TO_ton']:.2f}" if d["W_TO_ton"] else "—",
} for d in sens_data])
st.dataframe(df, width='stretch', hide_index=True)

st.divider()

# ---------- 多参数对比（龙卷风图） ----------
st.markdown("### 🌪️ 多参数敏感性对比")
st.caption("每个参数 +20%，对起飞重量的影响（越大越敏感）")

if st.button("运行多参数分析", type="primary"):
    with st.spinner("计算中..."):
        base_result = calculate_aircraft(**base)
        base_W = base_result["W_TO_ton"]

        sens_results = {}
        for key, label in [
            ("n_passengers", "乘客数"),
            ("range_km", "航程"),
            ("cruise_mach", "巡航马赫数"),
            ("cruise_altitude_m", "巡航高度"),
        ]:
            params = base.copy()
            params[key] = base[key] * 1.2
            try:
                r = calculate_aircraft(**params)
                delta_pct = (r["W_TO_ton"] - base_W) / base_W * 100
                sens_results[label] = delta_pct
            except Exception:
                sens_results[label] = 0.0

        fig_tornado = plot_tornado_chart(sens_results)
        st.plotly_chart(fig_tornado, width='stretch')

        st.markdown("#### 📖 解读")
        sorted_items = sorted(sens_results.items(),
                              key=lambda x: abs(x[1]), reverse=True)
        top = sorted_items[0]
        st.success(f"**最敏感的参数**：{top[0]}（+20% 导致起飞重量变化 {top[1]:+.2f}%）")

        st.markdown(f"""
**起飞重量对以下参数最敏感**（按影响排序）：
""" + "\n".join([
            f"{i+1}. **{k}**：{v:+.2f}%"
            for i, (k, v) in enumerate(sorted_items)
        ]))

st.divider()
st.info("""
💡 **工程含义**：
- 敏感性分析帮助判断"哪个参数最关键"
- 例如：如果航程最敏感，改航程需要重新设计大部分结构
- 设计中应优先锁定高敏感性参数
""")