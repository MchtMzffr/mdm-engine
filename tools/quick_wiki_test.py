#!/usr/bin/env python
"""Kısa wiki_calibrated testi: profil yükle, birkaç state ile decide(), sonuçları yaz."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdm_engine import decide
from mdm_engine.config_profiles import get_config

def main():
    co = get_config("wiki_calibrated")
    print("wiki_calibrated J_MIN:", co.get("J_MIN"), "| H_MAX:", co.get("H_MAX"),
          "| CUS_MEAN_THRESHOLD:", co.get("CUS_MEAN_THRESHOLD"))

    states = [
        {"risk": 0.01, "severity": 0.5, "physical": 0.2, "social": 0.2, "context": 0.1,
         "compassion": 0.5, "justice": 0.9, "harm_sens": 0.3, "responsibility": 0.6, "empathy": 0.7},
        {"risk": 0.45, "severity": 0.5, "physical": 0.4, "social": 0.4, "context": 0.3,
         "compassion": 0.5, "justice": 0.8, "harm_sens": 0.5, "responsibility": 0.7, "empathy": 0.6},
    ]
    for i, raw in enumerate(states):
        r = decide(raw, profile="wiki_calibrated", context={"external_confidence": 0.98})
        lev = r.get("escalation")
        drv = r.get("escalation_driver")
        margin = r.get("constraint_margin")
        worst_h = r.get("worst_H")
        print(f"  state{i}: level={lev} driver={drv!r} constraint_margin={margin} worst_H={worst_h}")
    print("Engine test OK.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
