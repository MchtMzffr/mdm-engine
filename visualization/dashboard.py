# MDM — Canlı Akış Denetim Dashboard / Live Audit Dashboard
# Veriler canlı akar; grafikler karar dağılımı ve gecikmeyi gösterir. EN/TR.

import importlib.util
import json
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    from mdm_engine.audit_spec import get_level_spec, decision_packet_to_flat_row, decision_packet_to_csv_row
except ImportError:
    def get_level_spec(level: int) -> Dict:
        return {"label": f"L{level}", "short": "", "dashboard_badge": f"L{level}"}
    def decision_packet_to_flat_row(packet: Dict) -> Dict:
        inp = packet.get("input", {}); ext = packet.get("external", {}); mdm = packet.get("mdm", {})
        return {
            "time": packet.get("ts"), "title": inp.get("title", ""), "user": inp.get("user", ""),
            "revid": inp.get("revid", ""), "external_decision": ext.get("decision", ""),
            "p_damaging": ext.get("p_damaging"), "mdm_level": mdm.get("level", 0),
            "clamp": mdm.get("soft_clamp", False), "reason": mdm.get("reason", ""),
            "final_action": packet.get("final_action", ""), "mismatch": packet.get("mismatch", False),
            "run_id": packet.get("run_id", ""), "latency_ms": packet.get("latency_ms"),
        }
    def decision_packet_to_csv_row(packet: Dict) -> Dict:
        return decision_packet_to_flat_row(packet)

# Bilingual strings / Çift dilli metinler (tüm arayüz metinleri)
TEXTS = {
    "en": {
        "title": "MDM",
        "badge": "Live audit",
        "sidebar_data": "Data",
        "start_live": "Start live stream",
        "stop_live": "Stop live stream",
        "live_running": "Live stream running",
        "live_stopped": "Stopped",
        "upload_jsonl": "Or load JSONL file",
        "events": "Events",
        "external": "FLAG / ALLOW",
        "avg_latency": "Avg latency (ms)",
        "last_latency": "Last (ms)",
        "tab_monitor": "Live Monitor",
        "tab_detail": "Decision Detail",
        "tab_review": "Review Queue",
        "tab_search": "Search & Audit",
        "no_data": "No data yet. Click **Start live stream** to connect to Wikipedia EventStreams + ORES + MDM.",
        "chart_levels": "L0 / L1 / L2 distribution",
        "chart_events": "Decisions over time (last 50)",
        "chart_latency": "Latency (ms) — last 50",
        "chart_mismatch": "ORES vs AMI (mismatch matrix)",
        "chart_pdamage_level": "p_damaging vs AMI level",
        "chart_reason_breakdown": "Reason breakdown (L1/L2)",
        "chart_as_norm_histogram": "as_norm histogram (calibration)",
        "chart_drift_driver": "drift_driver distribution",
        "calibration_section": "Calibration (escalation_driver, as_norm, drift_driver)",
        "filter_mismatch": "Only mismatches (ORES≠AMI)",
        "detail_select": "Select a row in **Live Monitor** or **Search** to see details.",
        "review_pending": "Pending L2",
        "review_none": "No pending L2.",
        "filter_level": "Level",
        "filter_ext": "External decision",
        "filter_profile": "Config profile",
        "search_result": "Result",
        "search_sample_l0": "L0 sampling (1 per 100)",
        "download_csv": "Download CSV (full: ORES + AMI + clamp/model)",
        "language": "Language",
        "sample_every": "Sample every N events",
        "open_detail": "Open detail",
        "approve": "Approve",
        "reject": "Reject",
        "approve_tr": "Approve",
        "reject_tr": "Reject",
        "saved": "Saved",
        "category": "Category",
        "note": "Note",
        "see_detail_tab": "See **Decision Detail** for full view.",
        "packets_label": "packets",
        "detail_explain": "Explain",
        "detail_external": "External decision",
        "detail_signals": "Signals",
        "detail_content": "Content",
        "detail_actions": "Actions",
        "tab_quality": "Quality",
        "quality_override_rate": "L2 override rate (Reject %)",
        "quality_category_dist": "Category distribution",
        "quality_reason_heatmap": "Reason → Override (which mdm_reason leads to Reject)",
        "quality_no_reviews": "No review log yet. Resolve L2 items (Approve/Reject) to see metrics.",
        "theme": "Theme",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "core_signals": "Core / Quality signals",
        "core_missing_fields": "Missing fields",
        "core_valid_candidates": "Valid candidates",
        "core_invalid_reasons": "Invalid reason counts",
        "core_input_quality": "Input quality",
        "core_evidence_consistency": "Evidence consistency",
        "core_frontier_size": "Pareto frontier size",
        "core_pareto_gap": "Pareto gap",
        "core_drift_applied": "Drift applied",
        "core_selection_reason": "Selection reason",
        "core_state_hash": "State hash",
        "core_config_hash": "Config hash",
        "theme_caption": "Light / Dark — Dashboard compatible with both themes.",
        "engine_reason": "Engine reason",
        "evidence_status": "Evidence status",
        "compare_link": "Compare on Wikipedia",
    },
    "tr": {
        "title": "MDM",
        "badge": "Canlı denetim",
        "sidebar_data": "Veri",
        "start_live": "Canlı akışı başlat",
        "stop_live": "Canlı akışı durdur",
        "live_running": "Canlı akış açık",
        "live_stopped": "Durduruldu",
        "upload_jsonl": "Veya JSONL dosyası yükle",
        "events": "Olay",
        "external": "FLAG / ALLOW",
        "avg_latency": "Ort. gecikme (ms)",
        "last_latency": "Son (ms)",
        "tab_monitor": "Canlı İzleme",
        "tab_detail": "Karar Detayı",
        "tab_review": "İnceleme Kuyruğu",
        "tab_search": "Ara & Denetle",
        "no_data": "Henüz veri yok. **Canlı akışı başlat** ile Wikipedia EventStreams + ORES + MDM bağlanır.",
        "chart_levels": "L0 / L1 / L2 dağılımı",
        "chart_events": "Zamana göre kararlar (son 50)",
        "chart_latency": "Gecikme (ms) — son 50",
        "chart_mismatch": "ORES vs AMI (uyumsuzluk matrisi)",
        "chart_pdamage_level": "p_damaging vs AMI seviye",
        "chart_reason_breakdown": "Gerekçe dağılımı (L1/L2)",
        "chart_as_norm_histogram": "as_norm histogram (kalibrasyon)",
        "chart_drift_driver": "drift_driver dağılımı",
        "calibration_section": "Kalibrasyon (escalation_driver, as_norm, drift_driver)",
        "filter_mismatch": "Sadece uyumsuzlar (ORES≠AMI)",
        "detail_select": "Detay için **Canlı İzleme** veya **Ara** tablosunda bir satır seçin.",
        "review_pending": "Bekleyen L2",
        "review_none": "Bekleyen L2 yok.",
        "filter_level": "Seviye",
        "filter_ext": "Dış karar",
        "filter_profile": "Profil",
        "search_result": "Sonuç",
        "search_sample_l0": "L0 örnekleme (100'de 1)",
        "download_csv": "CSV indir (tam: ORES + AMI + frenleme/model)",
        "language": "Dil",
        "sample_every": "Her N olayda örnekle",
        "open_detail": "Detay aç",
        "approve": "Onayla",
        "reject": "Red",
        "approve_tr": "Onayla",
        "reject_tr": "Red",
        "saved": "Kaydedildi",
        "category": "Kategori",
        "note": "Not",
        "see_detail_tab": "Detay için **Karar Detayı** sekmesine geçin.",
        "packets_label": "paket",
        "detail_explain": "Açıklama",
        "detail_external": "Dış karar",
        "detail_signals": "Sinyaller",
        "detail_content": "İçerik",
        "detail_actions": "Aksiyonlar",
        "tab_quality": "Kalite",
        "quality_override_rate": "L2 override oranı (Red %)",
        "quality_category_dist": "Kategori dağılımı",
        "quality_reason_heatmap": "Gerekçe → Red (hangi mdm_reason Red üretiyor)",
        "quality_no_reviews": "Henüz inceleme kaydı yok. L2 kararlarını verin (Onayla/Red) metrikleri görmek için.",
        "theme": "Tema",
        "theme_light": "Açık",
        "theme_dark": "Koyu",
        "core_signals": "Çekirdek / Kalite sinyalleri",
        "core_missing_fields": "Eksik alanlar",
        "core_valid_candidates": "Geçerli aday sayısı",
        "core_invalid_reasons": "Geçersiz neden sayıları",
        "core_input_quality": "Giriş kalitesi",
        "core_evidence_consistency": "Kanıt tutarlılığı",
        "core_frontier_size": "Pareto frontier boyutu",
        "core_pareto_gap": "Pareto gap",
        "core_drift_applied": "Drift uygulandı",
        "core_selection_reason": "Seçim gerekçesi",
        "core_state_hash": "State hash",
        "core_config_hash": "Config hash",
        "theme_caption": "Açık / Koyu — Dashboard her iki temada uyumlu.",
        "engine_reason": "Motor gerekçesi",
        "evidence_status": "Kanıt durumu",
        "compare_link": "Wikipedia'da karşılaştır",
    },
}

st.set_page_config(
    page_title="MDM Live Audit",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Light theme (default) */
    .mdm-header { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 0 1.25rem 0; border-bottom: 1px solid rgba(0,0,0,.12); margin-bottom: 1rem; }
    .mdm-header h1 { margin: 0; font-size: 1.5rem; font-weight: 600; color: #0f172a; }
    .mdm-header .badge { font-size: 0.7rem; padding: 0.2rem 0.5rem; background: #0ea5e9; color: white; border-radius: 999px; font-weight: 500; }
    /* Dark theme: başlıklar okunur kalsın */
    [data-theme="dark"] .mdm-header h1 { color: #f1f5f9; }
    [data-theme="dark"] .mdm-header { border-bottom-color: rgba(255,255,255,.12); }
    /* Sidebar: hem light hem dark'ta okunaklı */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); }
    [data-testid="stSidebar"] .stMarkdown { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] label { color: #94a3b8 !important; }
    [data-testid="stSidebar"] .stCaptionContainer { color: #94a3b8 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.25rem; border-bottom: 1px solid rgba(0,0,0,.08); }
    [data-theme="dark"] .stTabs [data-baseweb="tab-list"] { border-bottom-color: rgba(255,255,255,.08); }
    [data-testid="stMetricValue"] { font-size: 1.2rem; }
    /* Tema uyumu: kullanıcı Koyu seçerse ana alan koyu (Streamlit tema ile uyumlu) */
    [data-theme="dark"] .stDataFrame { background: rgba(15,23,42,.4); }
    [data-theme="dark"] .stExpander { background: rgba(15,23,42,.3); }
</style>
""", unsafe_allow_html=True)


def _t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return TEXTS.get(lang, TEXTS["en"]).get(key, key)


def _parse_schema_version(s: Any) -> Optional[tuple]:
    """Parse schema_version to (major, minor) or None. E.g. '2.0' -> (2, 0)."""
    if s is None:
        return None
    parts = str(s).strip().split(".", 1)
    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        return (major, minor)
    except (ValueError, IndexError):
        return None


def _schema_v2_required(packets: List[Dict[str, Any]]) -> bool:
    """True if any packet is legacy: missing schema_version or schema_version < 2.0 (reject)."""
    min_ver = (2, 0)
    for p in packets:
        sv = _parse_schema_version(p.get("schema_version"))
        if sv is None or sv < min_ver:
            return True
    return False


def _append_review_log(packet: Dict, decision: str, category: str = "", note: str = "") -> None:
    """L2 review kararını kalıcı JSONL'e yazar (L2_override_rate / kategori / reason→override için)."""
    import os
    path = os.environ.get("MDM_REVIEW_LOG") or str(ROOT / "review_log.jsonl")
    entry = {
        "run_id": packet.get("run_id"),
        "ts": packet.get("ts"),
        "revid": packet.get("input", {}).get("revid"),
        "title": (packet.get("input", {}).get("title") or "")[:100],
        "user": packet.get("input", {}).get("user"),
        "mdm_level": packet.get("mdm", {}).get("level"),
        "mdm_reason": packet.get("final_action_reason") or packet.get("mdm", {}).get("escalation_driver") or packet.get("mdm", {}).get("reason", ""),
        "review_decision": decision,
        "review_category": category or "",
        "review_note": (note or "")[:500],
        "review_ts": time.time(),
    }
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _load_review_log() -> List[Dict[str, Any]]:
    """review_log.jsonl dosyasını okur (Kalite paneli için)."""
    import os
    path = os.environ.get("MDM_REVIEW_LOG") or str(ROOT / "review_log.jsonl")
    entries: List[Dict[str, Any]] = []
    try:
        if Path(path).exists():
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    return entries


def _render_quality_panel(packets: List[Dict], t: callable) -> None:
    """Kalite: L2 override rate, kategori dağılımı, reason → override heatmap; Research: policy override + Core→Policy matrix."""
    entries = _load_review_log()
    resolved = [e for e in (entries or []) if e.get("review_decision") in ("approve", "reject")]
    if not resolved:
        st.info(t("quality_no_reviews"))
    else:
        rejects = sum(1 for e in resolved if e.get("review_decision") == "reject")
        override_rate = (rejects / len(resolved)) * 100.0
        st.metric(t("quality_override_rate"), f"{override_rate:.1f}%")
        st.caption(f"Reject: {rejects} / Approve: {len(resolved) - rejects} (n={len(resolved)})")

        # Kategori dağılımı
        st.subheader(t("quality_category_dist"))
        from collections import Counter
        cats = Counter(e.get("review_category") or "" for e in resolved)
        cats = {k or "(empty)": v for k, v in cats.items()}
        if cats:
            fig_cat = go.Figure(data=[go.Bar(x=list(cats.keys()), y=list(cats.values()))])
            fig_cat.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=220)
            st.plotly_chart(fig_cat, width="stretch")
        else:
            st.caption("—")

        # Reason → Override heatmap: mdm_reason vs review_decision (approve/reject)
        st.subheader(t("quality_reason_heatmap"))
        reason_reject = Counter()
        reason_approve = Counter()
        for e in resolved:
            r = e.get("mdm_reason") or "(empty)"
            if e.get("review_decision") == "reject":
                reason_reject[r] += 1
            else:
                reason_approve[r] += 1
        all_reasons = sorted(set(reason_reject.keys()) | set(reason_approve.keys()))
        if all_reasons:
            fig_heat = go.Figure(data=[
                go.Bar(name="Approve", x=all_reasons, y=[reason_approve.get(r, 0) for r in all_reasons]),
                go.Bar(name="Reject", x=all_reasons, y=[reason_reject.get(r, 0) for r in all_reasons]),
            ])
            fig_heat.update_layout(barmode="group", margin=dict(l=20, r=20, t=30, b=120), height=280, xaxis_tickangle=-45)
            st.plotly_chart(fig_heat, width="stretch")
        else:
            st.caption("—")

    # Research (packet-based): policy override rate + Core→Policy transition matrix
    if packets:
        st.markdown("---")
        st.subheader("Research: Policy override & Core→Policy")
        overrides = [p for p in packets if p.get("mdm", {}).get("core_level") is not None and p.get("mdm", {}).get("core_level") != p.get("mdm", {}).get("level", 0)]
        n_packets = len(packets)
        override_rate_pct = (len(overrides) / n_packets * 100.0) if n_packets else 0
        st.metric("Policy override rate (core_level ≠ final level)", f"{override_rate_pct:.1f}%")
        if overrides:
            from collections import Counter
            override_reasons = Counter(p.get("final_action_reason") or "—" for p in overrides)
            st.caption("Override reason breakdown: " + ", ".join(f"{k}:{v}" for k, v in sorted(override_reasons.items(), key=lambda x: -x[1])))
        # Core→Policy transition matrix
        matrix: Dict[str, Dict[str, int]] = {}
        for p in packets:
            mdm = p.get("mdm", {})
            core = mdm.get("core_level")
            if core is None:
                core = mdm.get("level", 0)
            final = mdm.get("level", 0)
            row = f"L{core}"
            col = f"L{final}"
            if row not in matrix:
                matrix[row] = {}
            matrix[row][col] = matrix[row].get(col, 0) + 1
        if matrix:
            rows = sorted(matrix.keys(), key=lambda x: int(x[1]))
            cols = sorted(set(c for row in matrix.values() for c in row.keys()), key=lambda x: int(x[1]))
            st.caption("Core → Policy (rows=core, cols=final)")
            table_data = [{"Core": r, **{c: matrix.get(r, {}).get(c, 0) for c in cols}} for r in rows]
            st.dataframe(table_data, use_container_width=True, hide_index=True)


def _get_live_module():
    """tools.live_wiki_audit modülünü döndürür; önce package, yoksa dosyadan yükler."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from tools import live_wiki_audit
        return live_wiki_audit
    except ImportError:
        pass
    # tools paket değilse (örn. __init__.py yok) doğrudan dosyadan yükle
    path = ROOT / "tools" / "live_wiki_audit.py"
    if not path.exists():
        raise ImportError(f"Bulunamadı: {path}")
    spec = importlib.util.spec_from_file_location("live_wiki_audit", path, submodule_search_locations=[str(ROOT)])
    if spec is None or spec.loader is None:
        raise ImportError(f"Modül yüklenemedi: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["live_wiki_audit"] = mod
    spec.loader.exec_module(mod)
    return mod


def _sync_live_packets() -> None:
    """Copy from live_wiki_audit.LIVE_PACKETS into session_state."""
    try:
        mod = _get_live_module()
        st.session_state["audit_packets"] = list(mod.LIVE_PACKETS)
    except Exception:
        pass


def _audit_packets() -> List[Dict[str, Any]]:
    if st.session_state.get("live_running"):
        _sync_live_packets()
    return st.session_state.get("audit_packets", [])


def _start_live() -> None:
    # Hata olursa session_state'e yaz (on_click ile çağrıldığında st.error görünmeyebilir)
    if "live_start_error" in st.session_state:
        del st.session_state["live_start_error"]
    try:
        mod = _get_live_module()
        LIVE_PACKETS = mod.LIVE_PACKETS
        run_live_loop = mod.run_live_loop
    except Exception as e:
        import traceback
        st.session_state["live_start_error"] = f"{e}\n\n{traceback.format_exc()}"
        return
    if st.session_state.get("live_running"):
        return
    try:
        stop_ev = threading.Event()
        st.session_state["live_stop_event"] = stop_ev
        LIVE_PACKETS.clear()
        sample_n = 10
        if "sample_every" in st.session_state:
            try:
                sample_n = int(st.session_state["sample_every"])
            except (TypeError, ValueError):
                pass
        sample_n = max(5, min(100, sample_n))
        th = threading.Thread(
            target=run_live_loop,
            args=(LIVE_PACKETS.append, stop_ev),
            kwargs={"sample_every_n": sample_n},
            daemon=True,
        )
        th.start()
        st.session_state["live_thread"] = th
        st.session_state["live_running"] = True
        st.rerun()
    except Exception as e:
        import traceback
        st.session_state["live_start_error"] = f"{e}\n\n{traceback.format_exc()}"


def _stop_live() -> None:
    if not st.session_state.get("live_running"):
        return
    ev = st.session_state.get("live_stop_event")
    if ev:
        ev.set()
    st.session_state["live_running"] = False
    st.rerun()


def _charts(packets: List[Dict], t: callable) -> None:
    """Grafikler: L0/L1/L2 pasta, karar zaman serisi, gecikme zaman serisi."""
    last = packets[-50:] if len(packets) > 50 else packets
    if not last:
        return
    # 1) Level dağılımı (pasta)
    level_counts = [0, 0, 0]
    for p in last:
        lv = p.get("mdm", {}).get("level", 0)
        if 0 <= lv <= 2:
            level_counts[lv] += 1
    fig_pie = go.Figure(data=[go.Pie(
        labels=["L0", "L1", "L2"],
        values=level_counts,
        hole=0.45,
        marker_colors=["#10b981", "#f59e0b", "#ef4444"],
    )])
    fig_pie.update_layout(title=t("chart_levels"), height=280, margin=dict(t=40, b=20, l=20, r=20), showlegend=True)
    # 2) Karar indeksi (son 50)
    x = list(range(len(last)))
    levels = [p.get("mdm", {}).get("level", 0) for p in last]
    fig_lev = go.Figure()
    fig_lev.add_trace(go.Scatter(x=x, y=levels, mode="lines+markers", line=dict(color="#6366f1", width=2), marker=dict(size=6)))
    fig_lev.update_layout(title=t("chart_events"), xaxis_title="Index", yaxis_title="Level", height=260, margin=dict(t=40, b=20, l=20, r=20))
    fig_lev.update_yaxes(tickvals=[0, 1, 2])
    # 3) Gecikme (ms)
    latencies = [p.get("latency_ms") for p in last if p.get("latency_ms") is not None]
    if not latencies:
        latencies = [0] * len(last)
    fig_lat = go.Figure()
    fig_lat.add_trace(go.Scatter(x=list(range(len(latencies))), y=latencies, mode="lines+markers", line=dict(color="#ec4899", width=2), marker=dict(size=5)))
    fig_lat.update_layout(title=t("chart_latency"), xaxis_title="Index", yaxis_title="ms", height=260, margin=dict(t=40, b=20, l=20, r=20))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(fig_pie, width="stretch")
    with c2:
        st.plotly_chart(fig_lev, width="stretch")
    with c3:
        st.plotly_chart(fig_lat, width="stretch")


def _mismatch_matrix(packets: List[Dict], t: callable) -> None:
    """ORES (ALLOW/FLAG) x AMI (L0/L1/L2) matrisi."""
    if not packets:
        return
    matrix = {}
    for ores in ("ALLOW", "FLAG"):
        for lev in (0, 1, 2):
            matrix[(ores, lev)] = 0
    for p in packets:
        ores_d = (p.get("external") or {}).get("decision") or "ALLOW"
        mdm_level = p.get("mdm", {}).get("level", 0)
        if ores_d not in ("ALLOW", "FLAG"):
            ores_d = "ALLOW"
        matrix[(ores_d, mdm_level)] = matrix.get((ores_d, mdm_level), 0) + 1
    st.markdown(f"**{t('chart_mismatch')}**")
    cols = st.columns(4)
    with cols[0]:
        st.write("")
    with cols[1]:
        st.write("**L0**")
    with cols[2]:
        st.write("**L1**")
    with cols[3]:
        st.write("**L2**")
    for ores in ("ALLOW", "FLAG"):
        row = [f"**{ores}**", matrix.get((ores, 0), 0), matrix.get((ores, 1), 0), matrix.get((ores, 2), 0)]
        c0, c1, c2, c3 = st.columns(4)
        with c0:
            st.write(row[0])
        with c1:
            st.write(row[1])
        with c2:
            st.write(row[2])
        with c3:
            st.write(row[3])


def _reason_breakdown(packets: List[Dict], t: callable) -> None:
    """Escalation driver dağılımı (L1/L2) — teşhis: hangi sinyal L1/L2 tetikledi."""
    if not packets:
        return
    l1_l2 = [p for p in packets if p.get("mdm", {}).get("level") in (1, 2)]
    if not l1_l2:
        return
    from collections import Counter
    # final_action_reason (policy-facing); eski paketlerde escalation_driver / mdm.reason
    drivers = Counter(
        p.get("final_action_reason") or p.get("mdm", {}).get("escalation_driver") or p.get("mdm", {}).get("reason") or "—"
        for p in l1_l2
    )
    labels = list(drivers.keys())
    values = list(drivers.values())
    if not labels:
        return
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color="#6366f1")])
    fig.update_layout(
        title=t("chart_reason_breakdown") + " (escalation_driver)",
        xaxis_title="escalation_driver",
        yaxis_title="count",
        height=260,
        margin=dict(t=40, b=120, l=50, r=20),
    )
    st.plotly_chart(fig, width="stretch")


def _chart_as_norm_histogram(packets: List[Dict], t: callable) -> None:
    """as_norm histogram — kalibrasyon: AS_SOFT_THRESHOLD ile L1 kilidi teşhisi."""
    if not packets:
        return
    last = packets[-200:] if len(packets) > 200 else packets
    values = []
    for p in last:
        unc = (p.get("mdm") or {}).get("uncertainty") or {}
        an = unc.get("as_norm")
        if an is not None:
            values.append(float(an))
    if not values:
        return
    fig = go.Figure(data=[go.Histogram(x=values, nbinsx=24, marker_color="#0ea5e9")])
    fig.update_layout(
        title=t("chart_as_norm_histogram"),
        xaxis_title="as_norm",
        yaxis_title="count",
        height=260,
        margin=dict(t=40, b=50, l=50, r=20),
    )
    st.plotly_chart(fig, width="stretch")


def _chart_drift_driver(packets: List[Dict], t: callable) -> None:
    """drift_driver dağılımı — warmup vs mean/delta (erken drift tetiklemesi teşhisi)."""
    if not packets:
        return
    from collections import Counter
    drivers = Counter(
        ((p.get("mdm") or {}).get("temporal_drift") or {}).get("driver") or "—"
        for p in packets
    )
    labels = list(drivers.keys())
    values = list(drivers.values())
    if not labels:
        return
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color="#10b981")])
    fig.update_layout(
        title=t("chart_drift_driver"),
        xaxis_title="drift_driver",
        yaxis_title="count",
        height=260,
        margin=dict(t=40, b=100, l=50, r=20),
    )
    st.plotly_chart(fig, width="stretch")


def _chart_pdamage_vs_level(packets: List[Dict], t: callable) -> None:
    """p_damaging (ORES) vs AMI level dağılımı."""
    last = packets[-80:] if len(packets) > 80 else packets
    if not last:
        return
    p_dmg = []
    levels = []
    for p in last:
        ext = p.get("external") or {}
        pd = ext.get("p_damaging")
        if pd is not None:
            p_dmg.append(pd)
            levels.append(p.get("mdm", {}).get("level", 0))
    if not p_dmg:
        return
    fig = go.Figure()
    for lv in (0, 1, 2):
        xs = [p_dmg[i] for i in range(len(p_dmg)) if levels[i] == lv]
        ys = [lv] * len(xs)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", name=f"L{lv}", marker=dict(size=8, opacity=0.7)))
    fig.update_layout(
        title=t("chart_pdamage_level"),
        xaxis_title="ores_p_damaging",
        yaxis_title="AMI level",
        yaxis=dict(tickvals=[0, 1, 2]),
        height=260,
        margin=dict(t=40, b=40, l=50, r=20),
        showlegend=True,
    )
    st.plotly_chart(fig, width="stretch")


def _render_live_monitor(packets: List[Dict], t: callable) -> None:
    if not packets:
        if st.session_state.get("live_running"):
            try:
                mod = _get_live_module()
                status = getattr(mod, "LIVE_STATUS", {})
                err = status.get("error")
                events_seen = status.get("events_seen", 0)
                packets_sent = status.get("packets_sent", 0)
                sample_n = int(st.session_state.get("sample_every", 10))
                if err:
                    st.error(f"EventStreams bağlantı hatası: {err}")
                elif status.get("connected"):
                    if events_seen == 0:
                        st.warning(
                            "EventStreams bağlandı ama henüz olay gelmedi (ilk SSE mesajı bekleniyor). "
                            "Birkaç saniye bekleyin; olmazsa ağ/firewall/proxy kontrol edin (stream.wikimedia.org)."
                        )
                    else:
                        next_at = sample_n * (events_seen // sample_n + 1) if sample_n else 0
                        st.info(
                            f"EventStreams bağlı. Gelen olay: **{events_seen}**, işlenen paket: **{packets_sent}**. "
                            f"Her **{sample_n}** olayda bir paket üretilir (sonraki paket {next_at}. olayda). "
                            "Sidebar'dan N'i 5 yaparsanız ilk paket daha erken gelir."
                        )
                else:
                    st.info("EventStreams'e bağlanılıyor...")
            except Exception:
                st.info("Akış çalışıyor; ilk paket bekleniyor.")
        else:
            st.info(t("no_data"))
        return
    last_n = packets[-200:] if len(packets) > 200 else packets
    level_counts = {0: 0, 1: 0, 2: 0}
    ext_flag = ext_allow = 0
    latencies = []
    for p in last_n:
        level_counts[p.get("mdm", {}).get("level", 0)] = level_counts.get(p.get("mdm", {}).get("level", 0), 0) + 1
        if (p.get("external") or {}).get("decision") == "FLAG":
            ext_flag += 1
        else:
            ext_allow += 1
        if p.get("latency_ms") is not None:
            latencies.append(p["latency_ms"])
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric(t("events"), len(last_n))
    with c2:
        st.metric("L0", level_counts.get(0, 0))
    with c3:
        st.metric("L1", level_counts.get(1, 0))
    with c4:
        st.metric("L2", level_counts.get(2, 0))
    with c5:
        st.metric(t("external"), f"{ext_flag} / {ext_allow}")
    with c6:
        avg_lat = sum(latencies) / len(latencies) if latencies else 0
        last_lat = latencies[-1] if latencies else "—"
        st.metric(t("avg_latency"), f"{avg_lat:.0f}" if latencies else "—")
        st.caption(f"{t('last_latency')}: {last_lat}")
    _charts(packets, t)
    st.markdown("---")
    mcol1, mcol2, mcol3 = st.columns(3)
    with mcol1:
        _mismatch_matrix(packets, t)
    with mcol2:
        _chart_pdamage_vs_level(packets, t)
    with mcol3:
        _reason_breakdown(packets, t)
    st.markdown("---")
    st.markdown("**" + t("calibration_section") + "**")
    cal1, cal2 = st.columns(2)
    with cal1:
        _chart_as_norm_histogram(packets, t)
    with cal2:
        _chart_drift_driver(packets, t)
    st.markdown("---")
    level_filter = st.multiselect(t("filter_level"), [0, 1, 2], default=[0, 1, 2], format_func=lambda x: f"L{x}")
    ext_filter = st.multiselect(t("filter_ext"), ["FLAG", "ALLOW"], default=["FLAG", "ALLOW"])
    profile_options = sorted(set(p.get("config_profile") or "—" for p in last_n))
    profile_filter = st.multiselect(t("filter_profile"), profile_options, default=profile_options, key="filter_profile") if profile_options else []
    filter_mismatch = st.checkbox(t("filter_mismatch"), value=False, key="filter_mismatch")
    filtered = [
        p for p in last_n
        if p.get("mdm", {}).get("level") in level_filter
        and (p.get("external") or {}).get("decision") in ext_filter
        and ((p.get("config_profile") or "—") in profile_filter if profile_filter else True)
        and (not filter_mismatch or p.get("mismatch") is True)
    ]
    rows = [decision_packet_to_flat_row(p) for p in filtered]
    if not rows:
        return
    df_event = st.dataframe(
        rows,
        width="stretch",
        hide_index=True,
        column_config={
            "time": st.column_config.NumberColumn("time", format="%.1f"),
            "p_damaging": st.column_config.NumberColumn("p_damaging", format="%.3f"),
            "latency_ms": st.column_config.NumberColumn("latency_ms", format="%.0f"),
            "input_quality": st.column_config.NumberColumn("input_quality", format="%.2f"),
            "valid_candidate_count": st.column_config.NumberColumn("valid_candidate_count"),
            "frontier_size": st.column_config.NumberColumn("frontier_size"),
        },
        on_select="rerun",
        selection_mode="single-row",
        key="live_monitor_table",
    )
    sel = getattr(getattr(df_event, "selection", None), "rows", None) or []
    if sel and 0 <= sel[0] < len(filtered):
        st.session_state["selected_audit_packet"] = filtered[sel[0]]

    # CSV export: ORES + AMI + tüm frenleme/model alanları
    def _csv_cell(v):
        if v is None:
            return "—"
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, (list, tuple)):
            return ";".join(str(x) for x in v)
        return str(v)

    csv_rows = [decision_packet_to_csv_row(p) for p in filtered]
    if csv_rows:
        headers = list(csv_rows[0].keys())
        lines = [",".join(headers)]
        for row in csv_rows:
            line = ",".join(
                '"' + _csv_cell(row.get(h)).replace('"', '""') + '"' for h in headers
            )
            lines.append(line)
        csv_content = "\n".join(lines)
        st.download_button(
            "📥 " + t("download_csv"),
            csv_content,
            file_name=f"mdm_audit_{int(time.time())}.csv",
            mime="text/csv",
            key="download_csv_full",
        )


def _human_decision_summary(p: Dict, lang: str = "tr") -> str:
    """İnsanın anlayacağı tek cümle: Bu olay neden L0/L1/L2 aldı? (Sinyal adı değil, anlamı.)"""
    mdm = p.get("mdm", {})
    level = mdm.get("level", 0)
    ext = p.get("external", {})
    ores = (ext.get("decision") or "ALLOW").upper()
    reason = (p.get("final_action_reason") or mdm.get("escalation_driver") or mdm.get("reason") or "").lower()
    if lang == "tr":
        if level == 0:
            if "ores_flag" in reason:
                return "Uygulandı (L0): ORES şüpheli bulmuştu; politika gereği yine de insan incelemesine gönderildi (bu kart detay için)."
            return "Uygulandı (L0): Belirsizlik düşük, eşikler aşılmadı; dış karar (ORES) ile uyumlu. Düzenleme otomatik kabul edildi."
        if level == 1:
            if "confidence" in reason:
                return "Yumuşak fren (L1): Güven skoru düşüktü; sistem dikkatli davrandı. İnsan incelemesi zorunlu değil ama karar yumuşatıldı."
            if "constraint" in reason:
                return "Yumuşak fren (L1): Kısıt eşiği aşıldı. İnsan incelemesi zorunlu değil, ama aksiyon sınırlandı."
            if "drift" in reason:
                return "Yumuşak fren (L1): Zaman içi sapma (drift) tetiklendi. Sistem dikkatli davrandı."
            return "Yumuşak fren (L1): Bir güvenlik eşiği aşıldı; insan incelemesi zorunlu değil ama karar frenlendi."
        if level == 2:
            if "ores_flag" in reason or (ores == "FLAG" and "wiki" in reason):
                return "İnsan incelemesi (L2): ORES bu değişikliği şüpheli buldu (FLAG). Sizin onayınız veya reddiniz gerekiyor — diff'e bakıp karar verin."
            if "confidence" in reason:
                return "İnsan incelemesi (L2): Güven skoru çok düşüktü; sistem 'insan baksın' dedi."
            if "h_critical" in reason or "fail_safe" in reason:
                return "İnsan incelemesi (L2): Güvenlik eşiği (zarar/risk) aşıldı; fail-safe kuralı tetiklendi."
            if "drift" in reason:
                return "İnsan incelemesi (L2): Zaman içi sapma (drift) yüksek; insan onayı istendi."
            return "İnsan incelemesi (L2): Sistem bu düzenlemeyi insan onayına gönderdi. Diff'e bakıp Onayla veya Red deyin."
    else:
        if level == 0:
            return "Applied (L0): Low uncertainty, thresholds not exceeded; consistent with external decision (ORES)."
        if level == 1:
            return "Soft clamp (L1): A safety threshold was exceeded; human review not required but action was constrained."
        return "Human review (L2): This edit was sent for human approval. Check the diff and Approve or Reject."


def _render_decision_detail(packets: List[Dict], t: callable) -> None:
    selected = st.session_state.get("selected_audit_packet")
    if not selected:
        st.info(t("detail_select"))
        return
    p = selected
    mdm = p.get("mdm", {})
    level = mdm.get("level", 0)
    spec = get_level_spec(level)
    lang = st.session_state.get("lang", "en")
    st.subheader(f"{spec.get('dashboard_badge', f'L{level}')}")
    st.caption(spec.get("short", ""))
    # Core vs Policy (policy override varsa: Core Lx → Policy Ly)
    core_level = mdm.get("core_level")
    if core_level is not None and core_level != level:
        reason_display = p.get("final_action_reason") or mdm.get("escalation_driver") or mdm.get("reason") or "—"
        st.caption(f"**Core:** L{core_level} → **Policy:** L{level} ({reason_display})")
    # Engine reason (çekirdek teşhis; policy-facing reason üstte)
    engine_reason = mdm.get("engine_reason")
    if engine_reason:
        st.caption(f"**{t('engine_reason')}:** {engine_reason}")
    # İnsan için özet: Neden bu karar? (L0/L1/L2 hepsi için)
    st.markdown("**Neden bu karar? (İnsan için özet)**")
    st.info(_human_decision_summary(p, lang))
    # Gerçek veri kaynağı: her seviyede Wikipedia linki + diff (varsa)
    inp = p.get("input", {})
    has_wiki = inp.get("title") and (inp.get("revid") or (p.get("external") or {}).get("revid"))
    if has_wiki:
        st.markdown("**Gerçek veri kaynağı (inceleme için)**")
        wiki_url = _wiki_diff_url(p)
        if wiki_url:
            st.markdown(f"🔗 [{t('compare_link')}]({wiki_url})")
        # L2'de diff yoksa: evidence_status + compare link (retry backend'de; burada teşhis)
        evidence_status = p.get("evidence_status")
        if level == 2 and evidence_status:
            st.caption(f"**{t('evidence_status')}:** {evidence_status}")
            if p.get("evidence_error"):
                st.caption(f"Error: {str(p.get('evidence_error'))[:200]}")
        comment = (inp.get("comment") or "").strip()
        if comment:
            st.caption(f"Edit özeti (kullanıcı yazdığı): {comment[:400]}")
        evidence = inp.get("evidence") or {}
        diff_text = evidence.get("diff") or p.get("diff_excerpt") or ""
        if diff_text:
            st.caption("**(−) Eski sürüm | (+) Yeni sürüm**")
            diff_preview = (diff_text[:2500] + "…") if len(diff_text) > 2500 else diff_text
            st.text_area("Yapılan değişiklik (diff)", value=diff_preview, height=180, key="detail_diff", disabled=True)
        else:
            st.caption("Diff bu olay için yok (L0/L1'de bazen çekilmez). Linkten sayfayı açabilirsiniz.")
        st.markdown("---")
    st.markdown("**" + t("detail_explain") + "**")
    st.write(mdm.get("explain", "—"))
    if p.get("latency_ms") is not None:
        st.caption(f"{t('last_latency')}: **{p['latency_ms']}** ms")
    st.markdown("**" + t("detail_external") + "**")
    ext = p.get("external", {})
    st.write(f"decision={ext.get('decision')}, p_damaging={ext.get('p_damaging')}, p_goodfaith={ext.get('p_goodfaith')}")
    if p.get("mdm_input_risk") is not None:
        st.caption(f"mdm_input_risk (MDM'e giden): {p.get('mdm_input_risk')}")
    st.markdown("**Entity**")
    st.code(p.get("entity_id", ""))
    st.markdown("**" + t("detail_signals") + "**")
    st.json(mdm.get("signals", {}))
    # Core / Quality signals (Wiki + SSOT zenginleştirme)
    with st.expander("**" + t("core_signals") + "**", expanded=True):
        drift = mdm.get("temporal_drift") or {}
        def _cell(v):
            if v is None: return "—"
            if isinstance(v, bool): return "true" if v else "false"
            if isinstance(v, (list, tuple)): return ", ".join(str(x) for x in v) if v else "—"
            if isinstance(v, dict): return "; ".join(f"{k}:{v}" for k, v in sorted(v.items())) if v else "—"
            return str(v)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.caption(t("core_missing_fields"))
            st.write(_cell(mdm.get("missing_fields")))
            st.caption(t("core_valid_candidates"))
            st.write(_cell(mdm.get("valid_candidate_count")))
            st.caption(t("core_input_quality"))
            st.write(_cell(mdm.get("input_quality")))
            st.caption(t("core_frontier_size"))
            st.write(_cell(mdm.get("frontier_size")))
        with c2:
            st.caption(t("core_invalid_reasons"))
            st.write(_cell(mdm.get("invalid_reason_counts")))
            st.caption(t("core_evidence_consistency"))
            st.write(_cell(mdm.get("evidence_consistency")))
            st.caption(t("core_pareto_gap"))
            st.write(_cell(mdm.get("pareto_gap")))
            st.caption(t("core_drift_applied"))
            st.write(_cell(drift.get("applied")))
        with c3:
            st.caption(t("core_selection_reason"))
            st.write(_cell(mdm.get("selection_reason")))
            st.caption(t("core_state_hash"))
            st.code((mdm.get("state_hash") or "—")[:32] + "…" if mdm.get("state_hash") else "—")
            st.caption(t("core_config_hash"))
            st.code((mdm.get("config_hash") or "—")[:32] + "…" if mdm.get("config_hash") else "—")
    inp = p.get("input", {})
    st.markdown("**" + t("detail_content") + "**")
    st.write(f"title: {inp.get('title')}, user: {inp.get('user')}, revid: {inp.get('revid')}, comment: {(inp.get('comment') or '')[:200]}")
    evidence = inp.get("evidence") or {}
    if evidence and not has_wiki:
        st.text_area("Diff / evidence", evidence.get("diff", str(evidence)), height=120)
    review = p.get("review", {})
    if level == 2:
        st.markdown("---")
        st.markdown("**" + t("detail_actions") + "**")
        col_a, col_b = st.columns(2)
        category = st.selectbox(t("category"), ["", "false_positive", "irony", "needs_context", "true_positive", "spam", "other"], key="detail_category")
        note = st.text_input(t("note"), key="detail_note")
        if category:
            review["category"] = category
        if note:
            review["note"] = note
        with col_a:
            if st.button("✅ " + t("approve"), key="detail_approve"):
                review["status"] = "resolved"
                review["decision"] = "approve"
                _append_review_log(p, "approve", st.session_state.get("detail_category", ""), st.session_state.get("detail_note", ""))
                st.success(t("saved"))
        with col_b:
            if st.button("❌ " + t("reject"), key="detail_reject"):
                review["status"] = "resolved"
                review["decision"] = "reject"
                _append_review_log(p, "reject", st.session_state.get("detail_category", ""), st.session_state.get("detail_note", ""))
                st.success(t("saved"))


def _wiki_diff_url(p: Dict) -> str:
    """Wikipedia'da bu revizyonun diff sayfası linki (insan gözüyle inceleme için)."""
    inp = p.get("input", {})
    title = (inp.get("title") or "").strip()
    revid = inp.get("revid") or (p.get("external") or {}).get("revid")
    if not title or not revid:
        return ""
    # Önceki revizyon: evidence'dan veya revision.old (event'ten); yoksa sadece revid ile diff
    evidence = (inp.get("evidence") or {})
    from_revid = evidence.get("from_revid")
    to_revid = evidence.get("to_revid") or revid
    base = "https://en.wikipedia.org/wiki/Special:Compare"
    if from_revid and to_revid:
        return f"{base}?oldrev={from_revid}&newrev={to_revid}"
    # Tek revizyon: diff=revid ile o revizyona göre değişiklik görünür
    encoded_title = quote_plus(title.replace(" ", "_"))
    return f"https://en.wikipedia.org/w/index.php?title={encoded_title}&diff={revid}&oldid=prev"


def _render_review_queue(packets: List[Dict], t: callable) -> None:
    pending = [p for p in packets if p.get("mdm", {}).get("level") == 2 and (p.get("review") or {}).get("status") == "pending"]
    st.metric(t("review_pending"), len(pending))
    if not pending:
        st.info(t("review_none"))
        return
    for i, p in enumerate(pending):
        mdm = p.get("mdm", {})
        inp = p.get("input", {})
        with st.expander(f"L2 — {inp.get('title', '')[:40]} | {inp.get('user')} | reason={p.get('final_action_reason') or mdm.get('reason')}"):
            # Bu L2'yi kim tetikledi? (ORES mi yakaladı, AMI mi "insana sor" dedi?)
            ores_decision = (p.get("external") or {}).get("decision") or "—"
            reason_driver = p.get("final_action_reason") or mdm.get("escalation_driver") or mdm.get("reason") or "—"
            st.markdown("**Bu L2 nasıl anlaşılır?**")
            if ores_decision == "FLAG" and "ores_flag" in str(reason_driver).lower():
                st.info(
                    "**ORES yakaladı.** Dış sistem (Wikipedia ORES) bu değişikliği şüpheli buldu (FLAG). "
                    "AMI motoru L0 demiş olsa bile, 'sessiz geçme' politikası gereği L2'ye attık — yani **insan gözü baksın** diye. "
                    "Siz diff'e bakıp gerçekten vandalizm/hata mı (Red) yoksa yanlış alarm mı (Onayla) karar veriyorsunuz."
                )
            elif ores_decision == "FLAG":
                st.info(
                    "**ORES FLAG** dedi (dış sistem şüphelendi). L2 nedeni: " + str(reason_driver) + ". "
                    "Yine de insan incelemesiyle karar sizde."
                )
            else:
                st.info(
                    "**Bizim sistem (AMI) 'insana sor' dedi.** ORES bu edit'e ALLOW demiş; ama AMI motoru (confidence, eşik, drift vb.) "
                    "L2'ye yükseltti. Yani yakalayan ORES değil, sizin denetçi motorunuz — insan onayı istiyor."
                )
            st.caption(f"ORES kararı: **{ores_decision}** | Tetikleyici: **{reason_driver}**")
            st.write(mdm.get("explain", ""))
            if p.get("latency_ms") is not None:
                st.caption(f"Latency: {p['latency_ms']} ms")
            # Gerçek veri kaynağı: Wikipedia'da değişikliği aç + diff metni (insan gözüyle karar için)
            st.markdown("**Gerçek veri kaynağı (inceleme için)**")
            wiki_url = _wiki_diff_url(p)
            if wiki_url:
                st.markdown(f"🔗 [**Wikipedia'da bu değişikliği aç**]({wiki_url}) — Sayfayı açıp ne eklendi/silindi gördükten sonra Onayla/Red verebilirsiniz.")
            comment = (inp.get("comment") or "").strip()
            if comment:
                st.caption(f"Edit özeti (kullanıcı yazdığı): {comment[:300]}")
            evidence = inp.get("evidence") or {}
            diff_text = evidence.get("diff") or p.get("diff_excerpt") or ""
            if diff_text:
                st.caption(
                    "**Nasıl okunur?** "
                    "**(−) Eksi / sol/sarı** = Önceki sürüm (sayfada vardı, kaldırıldı veya değişti). "
                    "**(+) Artı / sağ/mavi** = Yeni sürüm (bu değişiklikle gelen metin). "
                    "Yani önce soldaki (eski), sonra sağdaki (yeni) okuyorsunuz."
                )
                diff_preview = (diff_text[:3000] + "…") if len(diff_text) > 3000 else diff_text
                st.text_area("Yapılan değişiklik (diff) — aşağıdaki metne bakarak karar verebilirsiniz", value=diff_preview, height=220, key=f"rq_diff_{i}", disabled=True)
            else:
                st.caption("Diff alınamadı (MISSING/ERROR). Yukarıdaki Wikipedia linkinden sayfayı açıp inceleyebilirsiniz.")
            st.markdown("---")
            if st.button(t("open_detail"), key=f"rq_detail_{i}"):
                st.session_state["selected_audit_packet"] = p
                st.rerun()
            if st.button("✅ " + t("approve"), key=f"rq_approve_{i}"):
                p.setdefault("review", {})["status"] = "resolved"
                p["review"]["decision"] = "approve"
                _append_review_log(p, "approve", p.get("review", {}).get("category", ""), p.get("review", {}).get("note", ""))
                st.rerun()
            if st.button("❌ " + t("reject"), key=f"rq_reject_{i}"):
                p.setdefault("review", {})["status"] = "resolved"
                p["review"]["decision"] = "reject"
                _append_review_log(p, "reject", p.get("review", {}).get("category", ""), p.get("review", {}).get("note", ""))
                st.rerun()


def _render_search_audit(packets: List[Dict], t: callable) -> None:
    if not packets:
        st.info(t("no_data"))
        return
    level_filter = st.multiselect(t("filter_level"), [0, 1, 2], default=[0, 1, 2], format_func=lambda x: f"L{x}", key="search_level")
    user_contains = st.text_input("User contains", key="search_user")
    title_contains = st.text_input("Title contains", key="search_title")
    filtered = [p for p in packets if p.get("mdm", {}).get("level") in level_filter]
    if user_contains:
        filtered = [p for p in filtered if user_contains.lower() in (p.get("input", {}).get("user") or "").lower()]
    if title_contains:
        filtered = [p for p in filtered if title_contains.lower() in (p.get("input", {}).get("title") or "").lower()]
    st.caption(f"{t('search_result')}: {len(filtered)}")
    sample_l0 = st.checkbox(t("search_sample_l0"), key="sample_l0")
    if sample_l0:
        l0_only = [p for p in filtered if p.get("mdm", {}).get("level") == 0]
        filtered = l0_only[:: max(1, len(l0_only) // 100)] if len(l0_only) > 100 else l0_only[:10]
    rows = [decision_packet_to_flat_row(p) for p in filtered[:200]]
    if rows:
        search_event = st.dataframe(rows, width="stretch", hide_index=True, key="search_table", on_select="rerun", selection_mode="single-row")
        sel = getattr(getattr(search_event, "selection", None), "rows", None) or []
        if sel and 0 <= sel[0] < len(filtered):
            st.session_state["selected_audit_packet"] = filtered[sel[0]]
            st.caption(t("see_detail_tab"))


def main():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    if "theme" not in st.session_state:
        st.session_state["theme"] = "Light"
    if "audit_packets" not in st.session_state:
        st.session_state["audit_packets"] = []
    if "live_running" not in st.session_state:
        st.session_state["live_running"] = False

    t = _t
    # Dil: 2 seçenek (canlı test için)
    lang = st.sidebar.radio(t("language"), ["en", "tr"], index=0 if st.session_state["lang"] == "en" else 1, horizontal=True, format_func=lambda x: "English" if x == "en" else "Türkçe")
    st.session_state["lang"] = lang
    # Tema: 2 seçenek (Light/Dark) — tercih kaydedilir; Streamlit koyu modu sağ üst ⋮ menüsünden açılabilir
    theme = st.sidebar.radio(t("theme"), ["Light", "Dark"], index=0 if st.session_state.get("theme") == "Light" else 1, horizontal=True, format_func=lambda x: t("theme_light") if x == "Light" else t("theme_dark"))
    st.session_state["theme"] = theme
    st.sidebar.caption(t("theme_caption"))

    packets = _audit_packets()
    pending_l2 = len([p for p in packets if p.get("mdm", {}).get("level") == 2 and (p.get("review") or {}).get("status") == "pending"])
    header_right = f'<span class="badge">{t("review_pending")}: {pending_l2}</span>' if pending_l2 else ""
    st.markdown(
        f'<div class="mdm-header"><h1>{t("title")}</h1><span class="badge">{t("badge")}</span>{header_right}</div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(f"### ◉ {t('sidebar_data')}")
        if st.session_state.get("live_start_error"):
            st.error("Canlı akış başlatılamadı")
            st.code(st.session_state["live_start_error"][:2000])
            if st.button("Hata kutusunu kapat", key="dismiss_start_error"):
                del st.session_state["live_start_error"]
                st.rerun()
        if st.session_state.get("live_running"):
            st.success(t("live_running"))
            if st.button(t("stop_live"), type="primary"):
                _stop_live()
        else:
            st.caption(t("live_stopped"))
            st.number_input(t("sample_every"), min_value=5, max_value=100, value=10, key="sample_every")
            st.button(t("start_live"), type="primary", key="btn_start_live", on_click=_start_live)
        st.markdown("---")
        st.caption("JSONL dosya yolundan yükle (CLI yazıyorsa)")
        jsonl_path = st.text_input("Dosya yolu", value=st.session_state.get("live_jsonl_path", "mdm_live.jsonl"), key="live_jsonl_path", label_visibility="collapsed", placeholder="mdm_live.jsonl")
        if st.button("Dosyadan yükle", key="load_jsonl_file"):
            if jsonl_path and jsonl_path.strip():
                p = Path(jsonl_path.strip())
                if not p.is_absolute():
                    p = ROOT / p
                if p.exists():
                    try:
                        packets = []
                        with open(p, "r", encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                if not line:
                                    continue
                                try:
                                    packets.append(json.loads(line))
                                except json.JSONDecodeError:
                                    continue
                        if _schema_v2_required(packets):
                            st.error("Eski şema veya schema_version yok / < 2.0. Yeni export alın: canlı koşu veya mdm ile üretilen JSONL (schema v2.0).")
                            st.session_state["audit_packets"] = []
                        else:
                            st.session_state["audit_packets"] = packets
                            st.success(f"{len(packets)} paket yüklendi: {p.name}")
                    except Exception as e:
                        st.error(f"Okuma hatası: {e}")
                else:
                    st.warning(f"Dosya yok: {p}")
        st.markdown("---")
        st.caption(t("upload_jsonl"))
        uploaded = st.file_uploader("JSONL", type=["jsonl", "json"], key="audit_jsonl", label_visibility="collapsed")
        if uploaded:
            lines = uploaded.read().decode("utf-8").strip().split("\n")
            packets = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    packets.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            if _schema_v2_required(packets):
                st.error("Eski şema veya schema_version yok / < 2.0. Yeni export alın: canlı koşu veya mdm ile üretilen JSONL (schema v2.0).")
                st.session_state["audit_packets"] = []
            else:
                st.session_state["audit_packets"] = packets
                st.success(f"{len(packets)} {t('packets_label')}")

    # Inbox-first: Review Queue ilk sekme (denetçi önceliği)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([t("tab_review"), t("tab_monitor"), t("tab_detail"), t("tab_search"), t("tab_quality")])
    with tab1:
        _render_review_queue(packets, t)
    with tab2:
        _render_live_monitor(packets, t)
    with tab3:
        _render_decision_detail(packets, t)
    with tab4:
        _render_search_audit(packets, t)
    with tab5:
        _render_quality_panel(packets, t)

    if st.session_state.get("live_running"):
        time.sleep(1.5)
        st.rerun()


if __name__ == "__main__":
    main()
