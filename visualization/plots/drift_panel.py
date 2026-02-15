# Temporal Drift Panel — ΔCUS histogram, cus_mean zaman serisi

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from visualization.i18n import t


def plot_drift_panel(traces: List[Dict[str, Any]], lang: str = "tr") -> Optional[go.Figure]:
    if not traces:
        return None
    delta_cus_vals = [e.get("delta_cus") for e in traces if e.get("delta_cus") is not None]
    # X = kayıt indeksi (okunaklı)
    t_vals = list(range(len(traces)))
    cus_mean_vals = [e.get("cus_mean", e.get("cus", 0)) for e in traces]

    if not delta_cus_vals and not cus_mean_vals:
        return None

    subplot_1_title = t("plot_drift_hist_empty", lang) if not delta_cus_vals else t("plot_drift_hist", lang)
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(subplot_1_title, t("plot_drift_cus_mean", lang)),
        vertical_spacing=0.12,
        row_heights=[0.5, 0.5],
    )
    if delta_cus_vals:
        fig.add_trace(go.Histogram(x=delta_cus_vals, name="ΔCUS", marker_color="rgb(100,149,237)"), row=1, col=1)
    fig.add_trace(
        go.Scatter(
            x=t_vals,
            y=cus_mean_vals,
            mode="lines",
            name="CUS mean",
            line=dict(color="rgb(255,140,0)", width=2),
        ),
        row=2,
        col=1,
    )
    fig.update_layout(
        title=t("plot_drift_title", lang),
        height=320,
        margin=dict(l=50, r=30, t=50, b=40),
        showlegend=False,
    )
    fig.update_xaxes(title_text="ΔCUS", row=1, col=1)
    fig.update_xaxes(title_text=t("plot_drift_x_record", lang), row=2, col=1)
    fig.update_yaxes(title_text=t("plot_drift_y_cus", lang), row=2, col=1)
    return fig
