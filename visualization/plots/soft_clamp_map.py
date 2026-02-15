# Soft Clamp Aktivite — CUS × severity, clamp vurgusu

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go

from visualization.i18n import t


def plot_soft_clamp_map(traces: List[Dict[str, Any]], lang: str = "tr") -> Optional[go.Figure]:
    if not traces:
        return None
    cus_vals = []
    severity_vals = []
    clamp_intensity = []  # |final - raw| for severity
    colors = []
    for e in traces:
        raw = e.get("raw_action") or [0, 0, 0, 0]
        final = e.get("final_action") or e.get("raw_action") or [0, 0, 0, 0]
        raw = list(raw)[:4]
        final = list(final)[:4]
        cus = e.get("cus", 0)
        sev_raw = raw[0] if len(raw) > 0 else 0
        diff = abs((final[0] if len(final) > 0 else 0) - sev_raw)
        cus_vals.append(cus)
        severity_vals.append(sev_raw)
        clamp_intensity.append(diff)
        colors.append("red" if e.get("soft_clamp") else "lightblue")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=cus_vals,
            y=severity_vals,
            mode="markers",
            marker=dict(
                size=8,
                color=colors,
                line=dict(width=1, color="gray"),
            ),
            text=[f"CUS={c:.2f} S={s:.2f} Δ={d:.2f}" for c, s, d in zip(cus_vals, severity_vals, clamp_intensity)],
            hovertemplate="%{text}<extra></extra>",
            name=t("plot_soft_clamp_name", lang),
        )
    )
    fig.update_layout(
        title=t("plot_soft_clamp_title", lang),
        xaxis_title=t("plot_soft_clamp_x", lang),
        yaxis_title=t("plot_soft_clamp_y", lang),
        xaxis=dict(range=[0, 1.05]),
        yaxis=dict(range=[0, 1.05]),
        height=280,
        margin=dict(l=50, r=30, t=40, b=40),
        showlegend=False,
    )
    return fig
