# Plotly fig builder'lar (pure).
from __future__ import annotations

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go


def plot_timeline(traces: List[Dict[str, Any]], metric: str, title: str, color: str = "#667eea") -> Optional[go.Figure]:
    if not traces:
        return None
    x = list(range(len(traces)))
    y = [t.get(metric, 0) for t in traces]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name=metric, line=dict(color=color, width=2), marker=dict(size=4)))
    fig.update_layout(title=title, xaxis_title="Step", yaxis_title=metric, height=250, margin=dict(l=40, r=40, t=40, b=40), showlegend=False)
    return fig


def plot_level_pie(traces: List[Dict[str, Any]], title: str = "Escalation levels") -> Optional[go.Figure]:
    if not traces:
        return None
    counts = {0: 0, 1: 0, 2: 0}
    for t in traces:
        if "error" in t:
            continue
        lv = t.get("level", 0)
        counts[lv] = counts.get(lv, 0) + 1
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["L0", "L1", "L2"],
                values=[counts.get(0, 0), counts.get(1, 0), counts.get(2, 0)],
                hole=0.4,
                marker_colors=["#10b981", "#f59e0b", "#ef4444"],
            )
        ]
    )
    fig.update_layout(
        title=title,
        height=300,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5),
    )
    return fig
