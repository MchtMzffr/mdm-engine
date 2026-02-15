#!/usr/bin/env python3
"""mdm_live.jsonl özeti: level, escalation_driver, drift_driver dağılımı."""
import json
import sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "mdm_live.jsonl"
levels = []
drivers = []
drift_drivers = []
configs = []

with open(path, encoding="utf-8") as f:
    for line in f:
        p = json.loads(line)
        mdm = p.get("mdm") or {}
        levels.append(mdm.get("level"))
        drivers.append(mdm.get("escalation_driver") or "—")
        td = mdm.get("temporal_drift") or {}
        drift_drivers.append(td.get("driver") or "—")
        configs.append(p.get("config_profile", "—"))

print("Level:", Counter(levels))
print("config_profile:", Counter(configs))
print("escalation_driver:", Counter(drivers))
print("drift_driver:", Counter(drift_drivers))

new_schema = [p for p in (json.loads(l) for l in open(path, encoding="utf-8")) if (p.get("mdm") or {}).get("escalation_driver") is not None]
print("--- Yeni schema (escalation_driver dolu) paket sayısı:", len(new_schema))
if new_schema:
    print("  Level:", Counter(p["mdm"]["level"] for p in new_schema))
    print("  escalation_driver:", Counter(p["mdm"]["escalation_driver"] for p in new_schema))
