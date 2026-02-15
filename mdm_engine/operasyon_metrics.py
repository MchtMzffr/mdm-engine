# MDM — Operasyon metrikleri (kalibrasyon sayısallaştırma)
# Dashboard/CSV'den tek bakışta "sistem düzgün mü?" için 6 metrik.

from collections import Counter
from typing import Any, Dict, List, Optional


def compute_operasyon_metrics(
    packets: List[Dict[str, Any]],
    replay_check_fn: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    packets: Decision packet listesi (veya ami çıktıları).
    replay_check_fn: opsiyonel; (packet) -> bool (replay aynı hash döndü mü).
    Döner: L0_rate, L2_backlog_rate, driver_distribution, override_rate, mismatch_rate, replay_pass_rate.
    """
    if not packets:
        return {
            "L0_rate": None,
            "L2_backlog_rate": None,
            "driver_distribution": {},
            "driver_max_pct": None,
            "degenerate_driver_alarm": False,
            "override_rate": None,
            "mismatch_rate": None,
            "replay_pass_rate": None,
            "n": 0,
        }

    n = len(packets)
    levels = []
    drivers_all: List[str] = []
    l2_backlog = 0
    mismatches = 0
    overrides = 0
    override_denom = 0
    replay_ok = 0
    replay_total = 0

    for p in packets:
        mdm = p.get("mdm", p)
        level = mdm.get("level", mdm.get("escalation", 0))
        levels.append(level)
        # Primary driver: packet'te birleşik "A|B" için tek ana neden (degenerate/research tutarlı)
        dr = p.get("final_action_reason_primary") or mdm.get("escalation_driver") or mdm.get("reason") or "none"
        if isinstance(dr, str) and "|" in dr:
            dr = dr.split("|")[0].strip()
        drivers_all.append(dr or "none")
        if level == 2:
            vc = mdm.get("valid_candidate_count")
            if vc == 0 or dr == "fail_safe" or dr == "no_valid_candidates":
                l2_backlog += 1
        if p.get("mismatch") is True:
            mismatches += 1
        review = p.get("review") or {}
        if level == 2:
            override_denom += 1
            if review.get("review_decision") == "reject":
                overrides += 1
        if replay_check_fn and callable(replay_check_fn):
            replay_total += 1
            if replay_check_fn(p):
                replay_ok += 1

    driver_counts = Counter(drivers_all)
    driver_distribution = dict(driver_counts)
    # none hariç tek driver %80+ ise alarm; sağlıklı koşuda "none" çoğunluk olmasın diye
    counts_without_none = {k: v for k, v in driver_counts.items() if (k or "").lower() != "none"}
    n_for_max = sum(counts_without_none.values()) or 1
    driver_max_pct = max((c / n_for_max * 100.0 for c in counts_without_none.values()), default=0.0)
    degenerate_alarm = driver_max_pct >= 80.0

    return {
        "L0_rate": (levels.count(0) / n * 100.0) if n else None,
        "L2_backlog_rate": (l2_backlog / n * 100.0) if n else None,
        "driver_distribution": driver_distribution,
        "driver_max_pct": round(driver_max_pct, 2),
        "degenerate_driver_alarm": degenerate_alarm,
        "override_rate": (overrides / override_denom * 100.0) if override_denom else None,
        "mismatch_rate": (mismatches / n * 100.0) if n else None,
        "replay_pass_rate": (replay_ok / replay_total * 100.0) if replay_total else None,
        "n": n,
    }
