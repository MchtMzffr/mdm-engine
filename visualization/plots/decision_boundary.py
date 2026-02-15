# Phase 7 — Decision Boundary Heatmap: J × H → L0/L1/L2

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go

from visualization.i18n import t


def plot_decision_boundary_heatmap(traces: List[Dict[str, Any]], lang: str = "tr") -> Optional[go.Figure]:
    """
    X: J (justice), Y: H (harm). Renk: escalation level (L0=yeşil, L1=turuncu, L2=kırmızı).
    Trace'lerde J ve H yoksa None döner (engine Phase 7 ile J/H döndürüyorsa dolar).
    """
    points = [(e.get("J"), e.get("H"), e.get("level", 2)) for e in traces]
    points = [(j, h, lv) for j, h, lv in points if j is not None and h is not None]
    if not points:
        return None
    j_vals = [p[0] for p in points]
    h_vals = [p[1] for p in points]
    levels = [p[2] for p in points]
    colors = ["#2ecc71", "#f39c12", "#e74c3c"]  # L0 green, L1 orange, L2 red
    color_map = [colors[min(int(lv), 2)] for lv in levels]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=j_vals,
            y=h_vals,
            mode="markers",
            marker=dict(size=8, color=color_map, opacity=0.8, line=dict(width=0.5, color="gray")),
            text=[f"J={j:.2f} H={h:.2f} L{lv}" for j, h, lv in points],
            hovertemplate="%{text}<extra></extra>",
            name=t("plot_boundary_name", lang),
        )
    )
    fig.update_layout(
        title=t("plot_boundary_title", lang),
        xaxis_title=t("plot_boundary_x", lang),
        yaxis_title=t("plot_boundary_y", lang),
        xaxis=dict(range=[-0.05, 1.05]),
        yaxis=dict(range=[-0.05, 1.05], scaleanchor="x"),
        height=320,
        margin=dict(l=50, r=30, t=40, b=40),
        showlegend=False,
    )
    return fig
