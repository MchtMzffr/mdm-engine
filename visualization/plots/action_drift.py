# Action Drift — raw vs final aksiyon (bileşen bazlı fark)

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go

from visualization.i18n import t


LABELS = ["Severity", "Intervention", "Delay", "Compassion"]


def plot_action_drift(traces: List[Dict[str, Any]], lang: str = "tr") -> Optional[go.Figure]:
    if not traces:
        return None
    indices = list(range(len(traces)))
    fig = go.Figure()
    for idx, label in enumerate(LABELS):
        raw_vals = []
        final_vals = []
        for e in traces:
            raw = (e.get("raw_action") or [0, 0, 0, 0])[:4]
            final = (e.get("final_action") or e.get("raw_action") or [0, 0, 0, 0])[:4]
            raw_vals.append(raw[idx] if idx < len(raw) else 0)
            final_vals.append(final[idx] if idx < len(final) else 0)
        fig.add_trace(
            go.Scatter(x=indices, y=raw_vals, mode="lines", name=f"{label} (raw)", line=dict(width=1.5, dash="dot"))
        )
        fig.add_trace(
            go.Scatter(x=indices, y=final_vals, mode="lines", name=f"{label} (final)", line=dict(width=2))
        )
    fig.update_layout(
        title=t("plot_action_drift_title", lang),
        xaxis_title=t("plot_action_drift_x", lang),
        yaxis_title=t("plot_action_drift_y", lang),
        yaxis=dict(range=[0, 1.05]),
        hovermode="x unified",
        height=280,
        margin=dict(l=50, r=30, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig
