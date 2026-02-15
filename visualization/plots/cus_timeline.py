# CUS Timeline — t → CUS (isteğe cus_mean overlay)

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go

from visualization.i18n import t


def plot_cus_timeline(
    traces: List[Dict[str, Any]],
    show_cus_mean: bool = True,
    lang: str = "tr",
) -> Optional[go.Figure]:
    if not traces:
        return None
    # X = kayıt indeksi (okunaklı; timestamp yerine)
    t_vals = list(range(len(traces)))
    cus_vals = [e.get("cus", 0) for e in traces]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=t_vals,
            y=cus_vals,
            mode="lines+markers",
            name="CUS",
            line=dict(color="rgb(70,130,180)", width=2),
        )
    )
    if show_cus_mean:
        cus_mean_vals = [e.get("cus_mean", e.get("cus", 0)) for e in traces]
        fig.add_trace(
            go.Scatter(
                x=t_vals,
                y=cus_mean_vals,
                mode="lines",
                name=t("plot_cus_mean_name", lang),
                line=dict(color="rgb(255,140,0)", width=1, dash="dash"),
            )
        )
    fig.update_layout(
        title=t("plot_cus_title", lang),
        xaxis_title=t("plot_cus_x", lang),
        yaxis_title=t("plot_cus_y", lang),
        yaxis=dict(range=[0, 1.05]),
        hovermode="x unified",
        height=280,
        margin=dict(l=50, r=30, t=40, b=40),
    )
    return fig
