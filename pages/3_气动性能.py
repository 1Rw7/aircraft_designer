import streamlit as st
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.aerodynamics import (
    lift_curve_analysis, drag_polar, lift_to_drag_vs_speed, stall_speed,
)
from viz.aero_plot import plot_aero_dashboard, plot_ar_comparison

st.set_page_config(page_title="气动性能", page_icon="📈", layout="wide")
from core.session import require_login
require_login()
st.title("📈 气动性能分析")
st.caption("升力曲线、阻力极曲线、升阻比 vs 马赫数")

if "aircraft_result" not in st.session_state:
    st.warning("⚠️ 还没有设计数据")
    st.info("👉 请先去 **📥 设计输入** 页面输入参数")
    st.stop()

result = st.session_state["aircraft_result"]

st.markdown("### 🎯 当前方案参数")
col1, col2, col3, col4 = st.columns(4)
col1.metric("翼面积", f"{result['S_wing_m2']:.1f} m²")
col2.metric("展弦比", f"{result['aspect_ratio']:.2f}")
col3.metric("后掠角（典型值）", "25°")
col4.metric("巡航马赫数", f"{result['cruise_mach']:.3f}")

st.divider()

st.sidebar.header("📈 气动参数")
sweep_deg = st.sidebar.slider("后掠角 (°)", 0.0, 35.0, 25.0, 1.0)
mach_for_aero = st.sidebar.slider("分析马赫数", 0.4, 0.85, 0.78, 0.01)
ar_for_aero = st.sidebar.slider(
    "气动分析展弦比", 5.0, 14.0, float(result["aspect_ratio"]), 0.1,
)
st.sidebar.divider()
st.sidebar.caption("💡 拖动参数看曲线变化")

try:
    S_wing = result["S_wing_m2"]
    W_TO_N = result["W_TO_ton"] * 1000 * 9.80665
    altitude = result["cruise_altitude_m"]

    lift_data = lift_curve_analysis(
        S_wing=S_wing, AR=ar_for_aero, sweep_deg=sweep_deg,
        mach=mach_for_aero, altitude_m=altitude,
    )
    CL_range = np.linspace(0, lift_data["CL_max"], 100)
    polar_data = drag_polar(
        CL=CL_range, AR=ar_for_aero,
        sweep_deg=sweep_deg, mach=mach_for_aero,
    )
    ld_data = lift_to_drag_vs_speed(
        W_TO_N=W_TO_N, S_wing=S_wing, AR=ar_for_aero,
        altitude_m=altitude, sweep_deg=sweep_deg,
    )
    V_stall = stall_speed(
        W_TO_N=W_TO_N, S_wing=S_wing,
        CL_max=lift_data["CL_max"], altitude_m=0,
    )

    st.markdown("### 📊 气动性能总览")
    fig = plot_aero_dashboard(lift_data, polar_data, ld_data, V_stall)
    st.plotly_chart(fig, width='stretch')

    st.divider()
    st.markdown("### 📖 曲线解读")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
#### 📈 升力曲线 CL(α)
- **升力线斜率**：{lift_data['CL_alpha_per_deg']:.4f} /°
- **零升力迎角**：{lift_data['alpha_0']:.1f}°
- **最大升力系数**：{lift_data['CL_max']:.3f}
- **失速迎角**：{lift_data['alpha_stall']:.1f}°

迎角超过失速迎角，升力骤降。
        """)
        st.markdown(f"""
#### 📉 阻力极曲线 CD(CL)
- **零升阻力 CD0**：{polar_data['CD0']:.4f}
- **诱导阻力因子 k**：{polar_data['k']:.4f}
- **公式**：$C_D = C_{{D0}} + k C_L^2$

阻力 = 零升阻力 + 诱导阻力（与升力平方成正比）。
        """)

    with col_b:
        st.markdown(f"""
#### 📊 升阻比 vs 马赫数
- **最佳升阻比**：{ld_data['max_LD']:.1f}
- **最佳马赫数**：{ld_data['mach_at_max_LD']:.3f}

升阻比越大越省油，最佳点在跨音速前。
        """)
        st.markdown(f"""
#### ✈️ 失速速度
- **海平面失速速度**：{V_stall:.1f} m/s（{V_stall * 3.6:.0f} km/h）
- **安全起飞速度** ≈ 1.2 × V_stall = {V_stall * 1.2:.1f} m/s

低于失速速度，飞机将失控。
        """)

    st.divider()
    st.markdown("### 🔍 展弦比对升阻比的影响")
    st.caption("拖动左侧「气动分析展弦比」滑块观察主图变化；下图对比不同 AR")

    AR_range = [6, 8, 9.5, 11, 13]
    colors = ["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4", "#9467bd"]
    fig_compare = plot_ar_comparison(
        W_TO_N, S_wing, altitude, sweep_deg, AR_range, colors,
    )
    st.plotly_chart(fig_compare, width='stretch')

    st.info("""
💡 **工程含义**：展弦比越大，诱导阻力越小，升阻比越高，越省油。
但展弦比太大 → 机翼结构重、翼展大 → 机场适应性差。
实际设计在 8~11 之间权衡。
    """)
except Exception as e:
    st.error(f"气动计算错误：{type(e).__name__}: {e}")