"""3D 飞机概念模型生成"""
import numpy as np
import plotly.graph_objects as go


def build_aircraft_mesh(
    L_fuselage: float,        # 机身长度 (m)
    wingspan: float,          # 翼展 (m)
    S_wing: float,            # 翼面积 (m²)
    sweep_deg: float = 25.0,  # 后掠角 (度)
    n_engines: int = 2,       # 发动机数量
):
    """
    生成简化的飞机 3D 模型。
    坐标系：
      X：翼展方向（左右）
      Y：机身长度方向（-Y 机头，+Y 机尾）
      Z：垂直方向（上下）
    """
    fig = go.Figure()

    # ============ 机身 ============
    fuselage_radius = L_fuselage / 20
    n_theta = 20
    n_y = 30
    theta = np.linspace(0, 2 * np.pi, n_theta)
    y_fus = np.linspace(-L_fuselage / 2, L_fuselage / 2, n_y)
    Theta, Y = np.meshgrid(theta, y_fus)

    radius_profile = fuselage_radius * (
        1 - 0.6 * (np.abs(Y) / (L_fuselage / 2)) ** 3
    )
    X_fus = radius_profile * np.cos(Theta)
    Z_fus = radius_profile * np.sin(Theta) + fuselage_radius

    fig.add_trace(go.Surface(
        x=X_fus, y=Y, z=Z_fus,
        colorscale=[[0, "#c9d9e8"], [1, "#c9d9e8"]],
        showscale=False, opacity=0.95,
        name="机身", hoverinfo="skip",
    ))

    # ============ 机翼（后掠） ============
    # 后掠：翼梢往 +Y（机尾）方向偏
    taper = 0.30
    chord_root = 2 * S_wing / wingspan / (1 + taper)
    chord_tip = chord_root * taper
    half_span = wingspan / 2
    sweep_rad = np.deg2rad(sweep_deg)
    x_shift_tip = half_span * np.tan(sweep_rad)  # 翼梢相对翼根的 y 偏移

    # 机翼在主翼位置（靠近重心，-Y 方向偏一点）
    y_wing_root = -L_fuselage * 0.10

    # 左右机翼（对称）
    for side in [-1, 1]:
        wing_x = [side * fuselage_radius, side * half_span,
                  side * half_span, side * fuselage_radius]
        # 翼梢往 +Y（机尾）偏 → 后掠
        wing_y = [
            y_wing_root + chord_root / 2,               # 翼根前缘
            y_wing_root + x_shift_tip + chord_tip / 2,  # 翼梢前缘
            y_wing_root + x_shift_tip - chord_tip / 2,  # 翼梢后缘
            y_wing_root - chord_root / 2,               # 翼根后缘
        ]
        wing_z = [fuselage_radius, fuselage_radius,
                  fuselage_radius, fuselage_radius]

        fig.add_trace(go.Mesh3d(
            x=wing_x, y=wing_y, z=wing_z,
            i=[0, 0], j=[1, 2], k=[2, 3],
            color="#5b8fc9", opacity=0.9,
            name="机翼", hoverinfo="skip", showlegend=False,
        ))

    # ============ 尾翼 ============
    tail_span = wingspan * 0.35
    tail_chord_root = chord_root * 0.5
    tail_chord_tip = tail_chord_root * 0.5
    tail_y = L_fuselage / 2 - chord_root * 0.5  # 机尾端

    for side in [-1, 1]:
        tx = [side * fuselage_radius * 0.5, side * tail_span / 2,
              side * tail_span / 2, side * fuselage_radius * 0.5]
        # 水平尾翼也后掠
        ty = [tail_y + tail_chord_root / 2,
              tail_y + tail_chord_root * 0.3 + tail_chord_tip / 2,
              tail_y + tail_chord_root * 0.3 - tail_chord_tip / 2,
              tail_y - tail_chord_root / 2]
        tz = [fuselage_radius, fuselage_radius,
              fuselage_radius, fuselage_radius]
        fig.add_trace(go.Mesh3d(
            x=tx, y=ty, z=tz,
            i=[0, 0], j=[1, 2], k=[2, 3],
            color="#5b8fc9", opacity=0.85,
            hoverinfo="skip", showlegend=False,
        ))

    # 垂直尾翼（在机尾上方）
    vtail_height = L_fuselage / 8
    vtail = go.Mesh3d(
        x=[0, 0, 0, 0],
        y=[tail_y + 0.3, tail_y - 0.5, tail_y - 0.3, tail_y + 0.5],
        z=[fuselage_radius, fuselage_radius,
           fuselage_radius + vtail_height, fuselage_radius + vtail_height],
        i=[0, 0], j=[1, 1], k=[2, 2],
        color="#4a7db8", opacity=0.9,
        hoverinfo="skip", showlegend=False,
    )
    fig.add_trace(vtail)

    # ============ 发动机 ============
    # 发动机挂在机翼下方，位置跟随机翼后掠
    if n_engines == 2:
        engine_positions = [
            (-half_span * 0.35, y_wing_root + x_shift_tip * 0.35),
            (half_span * 0.35, y_wing_root + x_shift_tip * 0.35),
        ]
    elif n_engines == 4:
        engine_positions = [
            (-half_span * 0.30, y_wing_root + x_shift_tip * 0.30),
            (-half_span * 0.65, y_wing_root + x_shift_tip * 0.65),
            (half_span * 0.30, y_wing_root + x_shift_tip * 0.30),
            (half_span * 0.65, y_wing_root + x_shift_tip * 0.65),
        ]
    else:
        engine_positions = [(0, 0)]

    engine_radius = fuselage_radius * 0.5
    engine_length = chord_root * 0.8

    for ex, ey in engine_positions:
        e_theta = np.linspace(0, 2 * np.pi, 16)
        e_y = np.linspace(ey - engine_length / 2, ey + engine_length / 2, 8)
        ETheta, EY = np.meshgrid(e_theta, e_y)
        EX = ex + engine_radius * np.cos(ETheta)
        # 发动机在机翼下方，z 略低于机身中心线
        EZ = engine_radius * np.sin(ETheta) + fuselage_radius * 0.3
        fig.add_trace(go.Surface(
            x=EX, y=EY, z=EZ,
            colorscale=[[0, "#888"], [1, "#888"]],
            showscale=False, opacity=1.0,
            hoverinfo="skip", showlegend=False,
        ))

    # ============ 造型 ============
    fig.update_layout(
        scene=dict(
            xaxis_title="X (m)  翼展方向",
            yaxis_title="Y (m)  机身方向",
            zaxis_title="Z (m)  垂直方向",
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.5, y=-1.5, z=0.8),
            ),
        ),
        height=650,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
    )
    return fig