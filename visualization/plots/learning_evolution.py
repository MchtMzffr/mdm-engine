# Phase 6.1 — Learning / Optimization evrim grafikleri

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from visualization.i18n import t

PARAM_KEYS = ["J_MIN", "H_MAX", "SOFT_CLAMP_ALPHA", "SOFT_CLAMP_BETA", "SOFT_CLAMP_GAMMA"]
PARAM_LABELS = {"J_MIN": "J_MIN", "H_MAX": "H_MAX", "SOFT_CLAMP_ALPHA": "α", "SOFT_CLAMP_BETA": "β", "SOFT_CLAMP_GAMMA": "γ"}


def plot_loss_evolution(history: List[Dict[str, Any]], lang: str = "tr") -> Optional[go.Figure]:
    """Loss (L) zaman serisi: step → L."""
    if not history:
        return None
    steps = [h["step"] for h in history]
    L_vals = [h["L"] for h in history]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=L_vals,
            mode="lines+markers",
            name="L",
            line=dict(color="rgb(180,60,60)", width=2),
        )
    )
    fig.update_layout(
        title=t("plot_loss_title", lang),
        xaxis_title=t("plot_loss_x", lang),
        yaxis_title=t("plot_loss_y", lang),
        height=260,
        margin=dict(l=50, r=30, t=40, b=40),
    )
    return fig


def plot_metrics_evolution(history: List[Dict[str, Any]], lang: str = "tr") -> Optional[go.Figure]:
    """Fail-safe oranı, mean_cus, clamp_distortion, (non_fail_reward) → step."""
    if not history:
        return None
    steps = [h["step"] for h in history]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=steps, y=[h["fail_safe_rate"] for h in history], mode="lines+markers", name=t("plot_metrics_fail_safe", lang), line=dict(width=2))
    )
    fig.add_trace(
        go.Scatter(x=steps, y=[h["mean_cus"] for h in history], mode="lines+markers", name=t("plot_metrics_mean_cus", lang), line=dict(width=2))
    )
    fig.add_trace(
        go.Scatter(x=steps, y=[h["clamp_distortion"] for h in history], mode="lines+markers", name=t("plot_metrics_clamp_dist", lang), line=dict(width=2))
    )
    if history[0].get("non_fail_reward") is not None:
        fig.add_trace(
            go.Scatter(x=steps, y=[h.get("non_fail_reward", 0) for h in history], mode="lines+markers", name=t("plot_metrics_non_fail", lang), line=dict(width=2))
        )
    fig.update_layout(
        title=t("plot_metrics_title", lang),
        xaxis_title=t("plot_metrics_x", lang),
        yaxis_title=t("plot_metrics_y", lang),
        yaxis=dict(range=[0, 1.05]),
        height=260,
        margin=dict(l=50, r=30, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def plot_param_evolution(history: List[Dict[str, Any]], lang: str = "tr") -> Optional[go.Figure]:
    """J_MIN, H_MAX, α, β, γ evrimi."""
    if not history:
        return None
    steps = [h["step"] for h in history]
    fig = go.Figure()
    for key in PARAM_KEYS:
        if key not in history[0]:
            continue
        label = PARAM_LABELS.get(key, key)
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=[h[key] for h in history],
                mode="lines+markers",
                name=label,
                line=dict(width=1.5),
            )
        )
    fig.update_layout(
        title=t("plot_param_evol_title", lang),
        xaxis_title=t("plot_param_evol_x", lang),
        yaxis_title=t("plot_param_evol_y", lang),
        yaxis=dict(range=[0, 1.05]),
        height=280,
        margin=dict(l=50, r=30, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def _corr(x: List[float], y: List[float]) -> float:
    """Pearson correlation; listeler aynı uzunlukta."""
    n = len(x)
    if n < 2:
        return 0.0
    mx, my = sum(x) / n, sum(y) / n
    vx = sum((a - mx) ** 2 for a in x) ** 0.5
    vy = sum((b - my) ** 2 for b in y) ** 0.5
    if vx == 0 or vy == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (vx * vy)


def plot_param_sensitivity(history: List[Dict[str, Any]], lang: str = "tr") -> Optional[go.Figure]:
    """
    Phase 7 — Parametre duyarlılığı: her param için fail_safe_rate ve mean_cus ile korelasyon.
    Bu parametre gerçekten metrikleri etkili mi? (adım bazlı korelasyon)
    """
    if not history or len(history) < 2:
        return None
    steps_vals = [h["step"] for h in history]
    fsr = [h.get("fail_safe_rate", 0) for h in history]
    mc = [h.get("mean_cus", 0) for h in history]
    param_keys = [k for k in PARAM_KEYS if k in history[0]]
    if not param_keys:
        return None
    corr_fsr = [_corr([h.get(k, 0) for h in history], fsr) for k in param_keys]
    corr_mc = [_corr([h.get(k, 0) for h in history], mc) for k in param_keys]
    labels = [PARAM_LABELS.get(k, k) for k in param_keys]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=labels,
            y=corr_fsr,
            name=t("plot_sensitivity_fail_safe", lang),
            marker_color="rgb(200,80,80)",
        )
    )
    fig.add_trace(
        go.Bar(
            x=labels,
            y=corr_mc,
            name=t("plot_sensitivity_mean_cus", lang),
            marker_color="rgb(80,80,200)",
        )
    )
    fig.update_layout(
        title=t("plot_sensitivity_title", lang),
        xaxis_title=t("plot_sensitivity_x", lang),
        yaxis_title=t("plot_sensitivity_y", lang),
        barmode="group",
        yaxis=dict(range=[-1.05, 1.05]),
        height=280,
        margin=dict(l=50, r=30, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig
