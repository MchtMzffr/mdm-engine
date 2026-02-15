# Chaos Boundary Scatter — aksiyon uzayı [0,1]^4, 2D projeksiyon

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go

from visualization.i18n import t


def plot_chaos_scatter(traces: List[Dict[str, Any]], lang: str = "tr") -> Optional[go.Figure]:
    if not traces:
        return None
    # Projeksiyon: severity (0) vs intervention (1)
    sev = []
    interv = []
    colors = []
    for e in traces:
        final = (e.get("final_action") or e.get("raw_action") or [0, 0, 0, 0])[:4]
        sev.append(final[0] if len(final) > 0 else 0)
        interv.append(final[1] if len(final) > 1 else 0)
        colors.append("red" if e.get("chaos") else "blue")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sev,
            y=interv,
            mode="markers",
            marker=dict(size=6, color=colors, opacity=0.7, line=dict(width=0.5, color="gray")),
            text=[f"S={s:.2f} I={i:.2f}" for s, i in zip(sev, interv)],
            hovertemplate="%{text}<extra></extra>",
            name=t("plot_chaos_name", lang),
        )
    )
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=1, y1=1,
        line=dict(color="green", width=1, dash="dot"),
        fillcolor="rgba(0,128,0,0.05)",
    )
    fig.update_layout(
        title=t("plot_chaos_title", lang),
        xaxis_title=t("plot_chaos_x", lang),
        yaxis_title=t("plot_chaos_y", lang),
        xaxis=dict(range=[-0.05, 1.05], scaleanchor="y"),
        yaxis=dict(range=[-0.05, 1.05]),
        height=280,
        margin=dict(l=50, r=30, t=40, b=40),
        showlegend=False,
    )
    return fig
