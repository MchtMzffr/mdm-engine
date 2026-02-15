# MDM — L0/L1/L2 proof state bulucu.
# Bir kez çalıştırın; tools/proof_states.json yazar. Dashboard ve test_phases_real_engine bu dosyayı kullanır.
# Repo root'tan: python tools/find_proof_states.py

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Giriş noktası engine olmalı (circular import önlemek için)
from engine import moral_decision_engine
from simulation.scenario_generator import generate_batch


def find_proof_states(
    max_iter: int = 1500,
    seed: int = 42,
    profiles: tuple = ("safe", "balanced", "chaos"),
    out_path: Path | None = None,
) -> dict:
    """L0, L1, L2 üreten ilk state'leri bulur; dict döner."""
    out_path = out_path or ROOT / "tools" / "proof_states.json"
    found = {0: None, 1: None, 2: None}
    context = {"cus_history": []}
    batch_size = 100
    attempted = 0

    while attempted < max_iter and (found[0] is None or found[1] is None or found[2] is None):
        for profile in profiles:
            if all(found[i] is not None for i in (0, 1, 2)):
                break
            try:
                states = generate_batch(batch_size, profile=profile, seed=seed + attempted)
            except Exception:
                states = generate_batch(batch_size, seed=seed + attempted)
            for state in states:
                if all(found[i] is not None for i in (0, 1, 2)):
                    break
                try:
                    result = moral_decision_engine(
                        state,
                        context=dict(context),
                        config_override="scenario_test",
                        deterministic=True,
                    )
                except Exception:
                    continue
                level = result.get("escalation", 0)
                if level in (0, 1, 2) and found[level] is None:
                    found[level] = state
        attempted += batch_size * len(profiles)

    payload = {
        "L0": found[0],
        "L1": found[1],
        "L2": found[2],
        "meta": {
            "seed": seed,
            "attempted": attempted,
            "profiles": list(profiles),
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return payload


def main():
    p = argparse.ArgumentParser(description="L0/L1/L2 proof state'lerini bulur, proof_states.json yazar.")
    p.add_argument("--max-iter", type=int, default=1500)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()
    payload = find_proof_states(max_iter=args.max_iter, seed=args.seed, out_path=args.out)
    print("L0:", "OK" if payload["L0"] else "YOK")
    print("L1:", "OK" if payload["L1"] else "YOK")
    print("L2:", "OK" if payload["L2"] else "YOK")
    print("Yazıldı:", args.out or (ROOT / "tools" / "proof_states.json"))


if __name__ == "__main__":
    main()
