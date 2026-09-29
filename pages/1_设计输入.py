import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.calculator import calculate_aircraft

st.set_page_config(page_title="设计输入", page_icon="📥", layout="wide")
from core.session import require_login
require_login()
st.title("📥 设计输入")
st.caption("输入飞机设计指标，实时预览总体参数")

st.sidebar.header("🛠️ 设计参数")

engine_type_label = st.sidebar.radio(
    "发动机类型", ["涡扇（干线客机）", "涡桨（支线机）"], index=0,
)
engine_type = "turbofan" if "涡扇" in engine_type_label else "turboprop"

n_passengers = st.sidebar.slider("乘客数", 20, 400, 150, 5)
range_km = st.sidebar.slider("航程 (km)", 500, 12000, 3000, 100)
cruise_mach = st.sidebar.slider("巡航马赫数", 0.5, 0.85, 0.78, 0.01)
cruise_altitude = st.sidebar.slider("巡航高度 (m)", 5000, 12500, 11000, 250)

st.sidebar.divider()
use_custom_AR = st.sidebar.checkbox("自定义展弦比", value=False)
aspect_ratio = None
if use_custom_AR:
    aspect_ratio = st.sidebar.slider("展弦比", 5.0, 14.0, 9.5, 0.1)

st.sidebar.divider()
st.sidebar.caption("💡 拖动滑块，右侧实时更新结果")

try:
    result = calculate_aircraft(
        n_passengers=n_passengers, range_km=range_km,
        cruise_mach=cruise_mach, cruise_altitude_m=cruise_altitude,
        engine_type=engine_type, aspect_ratio=aspect_ratio,
    )
    st.session_state["aircraft_result"] = result
    st.session_state["aircraft_input"] = {
        "n_passengers": n_passengers, "range_km": range_km,
        "cruise_mach": cruise_mach, "cruise_altitude_m": cruise_altitude,
        "engine_type": engine_type,
    }

    st.success("✅ 参数已计算，可到「📊 计算结果」查看详细数据")
    st.markdown("### 📊 实时预估")
    st.caption("拖动左侧滑块，这里的数字会实时更新")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("起飞重量", f"{result['W_TO_ton']:.1f} t")
    col2.metric("空重", f"{result['W_empty_ton']:.1f} t")
    col3.metric("燃油重量", f"{result['W_fuel_ton']:.1f} t")
    col4.metric("载荷重量", f"{result['W_payload_ton']:.1f} t")

    st.divider()
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("翼面积", f"{result['S_wing_m2']:.1f} m²")
    col6.metric("翼展", f"{result['wingspan_m']:.1f} m")
    col7.metric("推力需求", f"{result['T_required_kN']:.1f} kN")
    col8.metric("升阻比", f"{result['L_D']:.1f}")

    st.divider()
    st.info("👉 下一步：左侧导航栏点击 **📊 计算结果**，查看完整参数和图表。")
except Exception as e:
    st.error(f"计算错误：{type(e).__name__}: {e}")