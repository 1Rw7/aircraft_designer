import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="计算结果", page_icon="📊", layout="wide")
from core.session import require_login
require_login()
st.title("📊 计算结果")
st.caption("飞机总体参数详细结果")

if "aircraft_result" not in st.session_state:
    st.warning("⚠️ 还没有设计数据")
    st.info("👉 请先去 **📥 设计输入** 页面输入参数")
    st.stop()

result = st.session_state["aircraft_result"]

st.markdown("### 🎯 关键总体参数")
col1, col2, col3, col4 = st.columns(4)
col1.metric("起飞重量", f"{result['W_TO_ton']:.2f} t")
col2.metric("翼面积", f"{result['S_wing_m2']:.2f} m²")
col3.metric("翼展", f"{result['wingspan_m']:.2f} m")
col4.metric("推力需求", f"{result['T_required_kN']:.1f} kN")

st.divider()
st.markdown("### 📋 完整参数表")

data = {
    "参数": [
        "乘客数", "航程", "巡航马赫数", "巡航高度", "发动机类型", "展弦比",
        "起飞重量 W_TO", "空重 W_empty", "燃油重量 W_fuel", "载荷重量 W_payload",
        "空重占比", "燃油占比", "载荷占比",
        "翼面积 S", "翼展 b", "平均弦长", "展弦比 AR",
        "推重比 T/W", "翼载荷 W/S", "升阻比 L/D", "巡航速度",
        "机身长度（估算）",
    ],
    "数值": [
        f"{result['n_passengers']} 人",
        f"{result['range_km']:.0f} km",
        f"{result['cruise_mach']:.3f}",
        f"{result['cruise_altitude_m']:.0f} m",
        "涡扇" if result["engine_type"] == "turbofan" else "涡桨",
        f"{result['aspect_ratio']:.2f}",
        f"{result['W_TO_ton']:.2f} t",
        f"{result['W_empty_ton']:.2f} t",
        f"{result['W_fuel_ton']:.2f} t",
        f"{result['W_payload_ton']:.2f} t",
        f"{result['empty_ratio']*100:.1f}%",
        f"{result['fuel_ratio']*100:.1f}%",
        f"{result['payload_ratio']*100:.1f}%",
        f"{result['S_wing_m2']:.2f} m²",
        f"{result['wingspan_m']:.2f} m",
        f"{result['mean_chord_m']:.2f} m",
        f"{result['aspect_ratio']:.2f}",
        f"{result['T_W_ratio']:.3f}",
        f"{result['W_S_Nm2']:.0f} N/m²",
        f"{result['L_D']:.2f}",
        f"{result['V_cruise_ms']:.1f} m/s",
        f"{result['L_fuselage_m']:.1f} m",
    ],
}
st.dataframe(pd.DataFrame(data), width='stretch', hide_index=True, height=800)

st.divider()
st.markdown("### ⚖️ 重量分解")

col_pie, col_info = st.columns([1, 1])
with col_pie:
    fig_pie = go.Figure(data=[go.Pie(
        labels=["空重", "燃油", "载荷"],
        values=[result["W_empty_ton"], result["W_fuel_ton"], result["W_payload_ton"]],
        hole=0.4,
        marker=dict(colors=["#1f77b4", "#ff7f0e", "#2ca02c"]),
        textinfo="label+percent",
        textfont=dict(size=14),
    )])
    fig_pie.update_layout(
        title=f"起飞重量 {result['W_TO_ton']:.1f} t 的构成",
        height=420, template="plotly_white",
    )
    st.plotly_chart(fig_pie, width='stretch')

with col_info:
    st.markdown("#### 📌 解读")
    st.markdown(f"""
- **空重**：{result['W_empty_ton']:.1f} t（{result['empty_ratio']*100:.1f}%）
- **燃油**：{result['W_fuel_ton']:.1f} t（{result['fuel_ratio']*100:.1f}%）
- **载荷**：{result['W_payload_ton']:.1f} t（{result['payload_ratio']*100:.1f}%）
    """)
    st.divider()
    st.markdown("#### 📊 与典型机型对比")
    st.markdown(f"""
| 指标 | 你的方案 | B737-800 | A320neo |
|------|----------|----------|---------|
| 乘客数 | {result['n_passengers']} | 162 | 180 |
| 起飞重量 | {result['W_TO_ton']:.1f} t | 79 t | 79 t |
| 翼展 | {result['wingspan_m']:.1f} m | 35.8 m | 35.8 m |
| 航程 | {result['range_km']:.0f} km | 5400 km | 6500 km |
    """)

st.divider()
st.info("👉 下一步：左侧导航栏点击 **📈 气动性能**。")