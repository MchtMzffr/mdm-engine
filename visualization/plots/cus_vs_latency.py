# CUS vs Latency — belirsiz durumlar daha mı yavaş? (scatter)

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go

from visualization.i18n import t


def plot_cus_vs_latency(
    traces: List[Dict[str, Any]],
    lang: str = "tr",
) -> Optional[go.Figure]:
    """CUS (x) vs latency_ms (y). Sadece her ikisi de olan kayıtlar. Renk = level (L0/L1/L2)."""
    points = [
        (e.get("cus"), e.get("latency_ms"), e.get("level", 0))
        for e in traces
        if e.get("cus") is not None and e.get("latency_ms") is not None
    ]
    if not points:
        return None
    cus_vals = [p[0] for p in points]
    lat_vals = [p[1] for p in points]
    levels = [p[2] for p in points]
    # Renk: L0 yeşil, L1 turuncu, L2 kırmızı
    color_map = {0: "rgb(60,160,80)", 1: "rgb(255,140,0)", 2: "rgb(200,80,80)"}
    colors = [color_map.get(lv, "gray") for lv in levels]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=cus_vals,
            y=lat_vals,
            mode="markers",
            marker=dict(size=6, color=colors, opacity=0.7, line=dict(width=0.5, color="gray")),
            text=[f"CUS={c:.3f} L{lv} {lat:.2f} ms" for c, lat, lv in points],
            hovertemplate="%{text}<extra></extra>",
            name=t("plot_cus_vs_latency_y", lang),
        )
    )
    fig.update_layout(
        title=t("plot_cus_vs_latency_title", lang),
        xaxis_title=t("plot_cus_vs_latency_x", lang),
        yaxis_title=t("plot_cus_vs_latency_y", lang),
        xaxis=dict(range=[0, 1.02]),
        hovermode="closest",
        height=280,
        margin=dict(l=50, r=30, t=40, b=40),
    )
    return fig
