"""气动性能可视化"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_aero_dashboard(lift_data, polar_data, ld_data, stall_V, title=""):
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "升力曲线 CL(α)",
            "阻力极曲线 CD(CL)",
            "升阻比 vs 马赫数",
            f"关键参数（失速速度 = {stall_V:.1f} m/s）",
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "table"}],
        ],
    )

    fig.add_trace(
        go.Scatter(x=lift_data["alpha_deg"], y=lift_data["CL"],
                   mode="lines", name="CL",
                   line=dict(color="#1f77b4", width=2.5)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=[lift_data["alpha_stall"]], y=[lift_data["CL_max"]],
                   mode="markers", name="失速",
                   marker=dict(size=12, color="red", symbol="x")),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(x=polar_data["CD"], y=polar_data["CL"],
                   mode="lines", name="极曲线",
                   line=dict(color="#d62728", width=2.5)),
        row=1, col=2,
    )

    fig.add_trace(
        go.Scatter(x=ld_data["mach"], y=ld_data["LD"],
                   mode="lines", name="L/D",
                   line=dict(color="#2ca02c", width=2.5)),
        row=2, col=1,
    )
    fig.add_trace(
        go.Scatter(x=[ld_data["mach_at_max_LD"]],
                   y=[ld_data["max_LD"]],
                   mode="markers", name="最佳点",
                   marker=dict(size=12, color="red", symbol="star")),
        row=2, col=1,
    )

    fig.add_trace(
        go.Table(
            header=dict(values=["参数", "数值"],
                        fill_color="#1a3a5c",
                        font=dict(color="white", size=13),
                        align="left"),
            cells=dict(values=[
                ["最大升力系数 CL_max", "失速迎角 α_stall",
                 "零升力迎角 α_0", "升力线斜率 CL_α",
                 "零升阻力 CD0", "诱导阻力因子 k",
                 "最佳升阻比 L/D_max", "失速速度 V_stall"],
                [f"{lift_data['CL_max']:.3f}",
                 f"{lift_data['alpha_stall']:.2f}°",
                 f"{lift_data['alpha_0']:.2f}°",
                 f"{lift_data['CL_alpha_per_deg']:.4f} /°",
                 f"{polar_data['CD0']:.4f}",
                 f"{polar_data['k']:.4f}",
                 f"{ld_data['max_LD']:.2f}",
                 f"{stall_V:.2f} m/s"],
            ], fill_color="#f8f9fc", align="left",
            font=dict(size=12)),
        ),
        row=2, col=2,
    )

    fig.update_layout(height=750, template="plotly_white",
                      showlegend=False, title=title)
    return fig


def plot_ar_comparison(W_TO_N, S_wing, altitude_m, sweep_deg, AR_range, colors):
    fig = go.Figure()
    from core.aerodynamics import lift_to_drag_vs_speed
    for i, ar in enumerate(AR_range):
        data = lift_to_drag_vs_speed(
            W_TO_N=W_TO_N, S_wing=S_wing, AR=ar,
            altitude_m=altitude_m, sweep_deg=sweep_deg,
        )
        fig.add_trace(go.Scatter(
            x=data["mach"], y=data["LD"], mode="lines",
            name=f"AR = {ar}", line=dict(color=colors[i], width=2.5),
        ))
    fig.update_layout(
        xaxis_title="马赫数", yaxis_title="升阻比 L/D",
        height=450, template="plotly_white", hovermode="x unified",
    )
    return fig