"""敏感性分析可视化"""
import plotly.graph_objects as go


def plot_sensitivity_curve(sens_data, param_label, base_value):
    """单参数敏感性曲线：参数变化 vs 起飞重量"""
    fig = go.Figure()

    x = [d["param_value"] for d in sens_data]
    y = [d["W_TO_ton"] for d in sens_data if d["W_TO_ton"] is not None]

    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers",
        line=dict(color="#2c7ba8", width=3),
        marker=dict(size=10, color="#2c7ba8"),
        name="起飞重量",
    ))

    # 基准点
    base_y = next((d["W_TO_ton"] for d in sens_data
                   if abs(d["variation"]) < 1e-6), None)
    if base_y is not None:
        fig.add_trace(go.Scatter(
            x=[base_value], y=[base_y], mode="markers",
            marker=dict(size=16, color="red", symbol="star"),
            name="基准方案",
        ))

    fig.update_layout(
        title=f"{param_label} 对起飞重量的影响",
        xaxis_title=param_label,
        yaxis_title="起飞重量 (t)",
        height=450, template="plotly_white", hovermode="x unified",
    )
    return fig


def plot_tornado_chart(sens_results):
    """
    龙卷风图：所有参数的敏感性对比
    sens_results: {参数名: 相对变化率}
    """
    items = sorted(sens_results.items(), key=lambda x: abs(x[1]), reverse=True)
    labels = [x[0] for x in items]
    values = [x[1] for x in items]

    colors = ["#d62728" if v > 0 else "#1f77b4" for v in values]

    fig = go.Figure(go.Bar(
        x=values, y=labels,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{v:+.2f}%" for v in values],
        textposition="outside",
    ))

    fig.update_layout(
        title="起飞重量敏感性（+20% 输入参数的影响）",
        xaxis_title="起飞重量变化 (%)",
        yaxis_title="",
        height=450, template="plotly_white",
        xaxis=dict(zeroline=True, zerolinecolor="black", zerolinewidth=2),
    )
    return fig