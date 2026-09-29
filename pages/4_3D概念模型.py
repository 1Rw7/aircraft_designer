import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.aircraft_3d import build_aircraft_mesh

st.set_page_config(page_title="3D 概念模型", page_icon="✈️", layout="wide")
from core.session import require_login
require_login()
st.title("✈️ 3D 概念模型")
st.caption("根据参数生成的飞机概念图（拖动左侧参数实时更新）")

if "aircraft_result" not in st.session_state:
    st.warning("⚠️ 还没有设计数据")
    st.info("👉 请先去 **📥 设计输入** 页面输入参数")
    st.stop()

result = st.session_state["aircraft_result"]

# ---------- 侧边栏：控制参数 ----------
st.sidebar.header("✈️ 3D 模型参数")

# 默认从结果里取
default_sweep = 25.0
sweep_deg = st.sidebar.slider("后掠角 (°)", 0.0, 35.0, default_sweep, 1.0)

n_engines = st.sidebar.radio("发动机数量", [2, 4], index=0)

# 允许用户临时覆盖几何参数（只影响显示）
override = st.sidebar.checkbox("覆盖几何参数（仅影响显示）", value=False)

if override:
    L_fuselage = st.sidebar.slider(
        "机身长度 (m)", 20.0, 80.0, float(result["L_fuselage_m"]), 1.0,
    )
    wingspan = st.sidebar.slider(
        "翼展 (m)", 15.0, 70.0, float(result["wingspan_m"]), 0.5,
    )
    S_wing = st.sidebar.slider(
        "翼面积 (m²)", 30.0, 300.0, float(result["S_wing_m2"]), 5.0,
    )
else:
    L_fuselage = result["L_fuselage_m"]
    wingspan = result["wingspan_m"]
    S_wing = result["S_wing_m2"]

st.sidebar.divider()
st.sidebar.caption("💡 鼠标拖动旋转、滚轮缩放")

# ---------- 主区域：3D 模型 ----------
col_info, col_3d = st.columns([1, 3])

with col_info:
    st.markdown("### 📐 几何参数")
    st.metric("机身长度", f"{L_fuselage:.1f} m")
    st.metric("翼展", f"{wingspan:.1f} m")
    st.metric("翼面积", f"{S_wing:.1f} m²")
    st.metric("后掠角", f"{sweep_deg:.1f}°")
    st.metric("发动机数", f"{n_engines} 台")

    st.divider()
    st.markdown("### 📊 比例参考")
    st.markdown(f"""
    - 翼展 / 机身长 = {wingspan/L_fuselage:.2f}
    - 展弦比 = {result['aspect_ratio']:.2f}
    - 与 B737-800 对比：
      - 翼展 35.8 m
      - 机身长 39.5 m
    """)

with col_3d:
    try:
        fig = build_aircraft_mesh(
            L_fuselage=L_fuselage,
            wingspan=wingspan,
            S_wing=S_wing,
            sweep_deg=sweep_deg,
            n_engines=n_engines,
        )
        st.plotly_chart(fig, width='stretch')
    except Exception as e:
        st.error(f"3D 生成错误：{type(e).__name__}: {e}")

st.divider()
st.markdown("""
### 🔍 观察要点

- **机身**：圆柱形，两端略收窄
- **机翼**：梯形，带后掠角，从机身两侧伸出
- **尾翼**：水平尾翼 + 垂直尾翼
- **发动机**：吊挂在机翼下方

**拖动左侧滑块**，观察飞机形状如何随参数变化：

- 后掠角越大 → 机翼越向后倾斜（适合高速）
- 翼展越大 → 展弦比越大（省油但结构重）
- 发动机数量 → 2 发（主流）或 4 发（大型）
""")