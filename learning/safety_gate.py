# Phase 6.4 — Safety gate: optimizasyon çıktısının güvenli bölgede kalması

from typing import Dict, Tuple


def safety_gate(metrics: Dict[str, float]) -> Tuple[bool, str]:
    """
    Önerilen config'in metrikleri güvenli aralıkta mı kontrol eder.
    fail_safe_rate çok düşükse veya mean_cus çok yüksekse BLOCKED.
    Returns: (passed: bool, reason: str)
    """
    fail_safe_rate = metrics.get("fail_safe_rate", 0.0)
    mean_cus = metrics.get("mean_cus", 0.0)
    if fail_safe_rate < 0.15:
        return False, "fail_safe too low"
    if mean_cus > 0.85:
        return False, "cus too high"
    return True, "ok"
