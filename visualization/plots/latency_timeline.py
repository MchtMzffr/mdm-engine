# Latency Timeline — kayıt indeksi → latency_ms (trace'de varsa)

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go

from visualization.i18n import t


def plot_latency_timeline(
    traces: List[Dict[str, Any]],
    lang: str = "tr",
) -> Optional[go.Figure]:
    """Trace'lerde latency_ms varsa zaman serisi grafiği döndürür; yoksa None."""
    latencies = [e.get("latency_ms") for e in traces]
    if not any(l is not None for l in latencies):
        return None
    idx = list(range(len(traces)))
    # None olanları atlayarak çiz (veya 0 yapabiliriz; atlamak daha doğru)
    x_vals = [i for i, l in enumerate(latencies) if l is not None]
    y_vals = [l for l in latencies if l is not None]
    if not y_vals:
        return None
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=idx,
            y=[l if l is not None else None for l in latencies],
            mode="lines+markers",
            name=t("plot_latency_series", lang),
            line=dict(color="rgb(60,160,80)", width=2),
        )
    )
    fig.update_layout(
        title=t("plot_latency_title", lang),
        xaxis_title=t("plot_cus_x", lang),
        yaxis_title=t("plot_latency_y", lang),
        hovermode="x unified",
        height=280,
        margin=dict(l=50, r=30, t=40, b=40),
    )
    return fig
