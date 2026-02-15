# Level Timeline — index -> level (L0/L1/L2 renkli nokta)

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go

from visualization.i18n import t

LEVEL_COLORS = {0: "rgb(40,160,80)", 1: "rgb(230,140,40)", 2: "rgb(200,60,60)"}


def plot_level_timeline(
    traces: List[Dict[str, Any]],
    lang: str = "tr",
) -> Optional[go.Figure]:
    """Index -> level scatter; L0=yeşil, L1=turuncu, L2=kırmızı."""
    if not traces:
        return None
    levels = [e.get("level", 0) for e in traces]
    idx = list(range(len(traces)))
    fig = go.Figure()
    for lv in (0, 1, 2):
        mask = [i for i, L in enumerate(levels) if L == lv]
        if not mask:
            continue
        x = [idx[i] for i in mask]
        y = [levels[i] for i in mask]
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                name=f"L{lv}",
                marker=dict(size=6, color=LEVEL_COLORS.get(lv, "gray"), symbol="circle"),
            )
        )
    fig.update_layout(
        title=t("plot_level_timeline_title", lang),
        xaxis_title=t("plot_cus_x", lang),
        yaxis_title=t("plot_level_timeline_y", lang),
        yaxis=dict(tickmode="array", tickvals=[0, 1, 2], ticktext=["L0", "L1", "L2"]),
        hovermode="x unified",
        height=220,
        margin=dict(l=50, r=30, t=40, b=40),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig
