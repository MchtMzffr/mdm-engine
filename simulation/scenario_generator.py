# Phase 6.2 — Scenario Generator: zorluk profilleri (safe, balanced, critical, chaos)

import random
from typing import Dict, List, Optional

STATE_KEYS = [
    "physical", "social", "context", "risk",
    "compassion", "justice", "harm_sens", "responsibility", "empathy",
]

# Profil bazlı (min, max) aralıkları — spec 17
PROFILE_BOUNDS: Dict[str, Dict[str, tuple]] = {
    "safe": {
        "compassion": (0.6, 0.95),
        "justice": (0.6, 0.95),
        "harm_sens": (0.05, 0.35),
        "risk": (0.1, 0.4),
        "physical": (0.3, 0.8),
        "social": (0.4, 0.9),
        "context": (0.3, 0.8),
        "responsibility": (0.5, 0.9),
        "empathy": (0.5, 0.95),
    },
    "balanced": {
        "compassion": (0.35, 0.85),
        "justice": (0.4, 0.85),
        "harm_sens": (0.15, 0.55),
        "risk": (0.25, 0.7),
        "physical": (0.2, 0.85),
        "social": (0.25, 0.8),
        "context": (0.2, 0.85),
        "responsibility": (0.3, 0.85),
        "empathy": (0.35, 0.85),
    },
    "critical": {
        "compassion": (0.2, 0.6),
        "justice": (0.15, 0.55),
        "harm_sens": (0.45, 0.9),
        "risk": (0.5, 0.95),
        "physical": (0.2, 0.9),
        "social": (0.2, 0.7),
        "context": (0.2, 0.85),
        "responsibility": (0.2, 0.7),
        "empathy": (0.2, 0.6),
    },
    "chaos": {
        k: (0.0, 1.0) for k in STATE_KEYS
    },
}

# Eksik key'ler chaos gibi [0,1]
for p in ("safe", "balanced", "critical"):
    for k in STATE_KEYS:
        if k not in PROFILE_BOUNDS[p]:
            PROFILE_BOUNDS[p][k] = (0.0, 1.0)

# Curriculum: önce kolay, sonra zor
CURRICULUM_ORDER = ("safe", "balanced", "critical", "chaos")

# Phase 6.3 — Öğrenme için 3 banda bölünmüş curriculum (J/H hedefli proxy)
# Easy: J 0.75–1.0, H 0.0–0.4 → L0/L1; Medium: J 0.55–0.85, H 0.2–0.7; Hard: J 0.30–0.70, H 0.6–1.0
CURRICULUM_BANDS = ("easy", "medium", "hard")
PROFILE_BOUNDS["easy"] = {
    "compassion": (0.75, 1.0),
    "justice": (0.75, 1.0),
    "harm_sens": (0.0, 0.25),
    "risk": (0.0, 0.35),
    "physical": (0.3, 0.7),
    "social": (0.4, 0.9),
    "context": (0.3, 0.8),
    "responsibility": (0.5, 0.95),
    "empathy": (0.6, 1.0),
}
PROFILE_BOUNDS["medium"] = {
    "compassion": (0.45, 0.85),
    "justice": (0.45, 0.85),
    "harm_sens": (0.2, 0.55),
    "risk": (0.25, 0.65),
    "physical": (0.2, 0.85),
    "social": (0.25, 0.8),
    "context": (0.2, 0.85),
    "responsibility": (0.35, 0.85),
    "empathy": (0.4, 0.85),
}
PROFILE_BOUNDS["hard"] = {
    "compassion": (0.15, 0.55),
    "justice": (0.15, 0.55),
    "harm_sens": (0.5, 0.95),
    "risk": (0.55, 0.95),
    "physical": (0.2, 0.95),
    "social": (0.15, 0.7),
    "context": (0.2, 0.9),
    "responsibility": (0.15, 0.6),
    "empathy": (0.15, 0.55),
}


def get_curriculum_profile_for_step(step: int, schedule: Optional[List[tuple]] = None) -> str:
    """
    Epoch/step indeksine göre curriculum band döndürür.
    schedule: [(max_step_exclusive, profile), ...] örn. [(5, "easy"), (10, "medium"), (None, "hard")].
    None = sınırsız. Boşsa varsayılan: 1–5 easy, 6–10 medium, 11+ hard.
    """
    schedule = schedule or [(5, "easy"), (10, "medium"), (None, "hard")]
    for max_step, profile in schedule:
        if max_step is None or step < max_step:
            return profile
    return schedule[-1][1] if schedule else "medium"


def generate_state(
    profile: str = "balanced",
    seed: Optional[int] = None,
    rng: Optional[random.Random] = None,
) -> Dict[str, float]:
    """
    Tek bir raw_state üretir; seçilen profil için tanımlı (min, max) aralığından uniform çekilir.
    profile: "safe" | "balanced" | "critical" | "chaos"
    """
    if rng is None:
        rng = random.Random(seed)
    bounds = PROFILE_BOUNDS.get(profile, PROFILE_BOUNDS["chaos"])
    return {
        k: rng.uniform(bounds[k][0], bounds[k][1])
        for k in STATE_KEYS
    }


def generate_batch(
    n: int,
    profile: str = "balanced",
    seed: Optional[int] = None,
) -> List[Dict[str, float]]:
    """
    n adet state üretir; hepsi aynı profilden.
    seed verilirse tekrarlanabilir.
    """
    rng = random.Random(seed)
    return [generate_state(profile=profile, rng=rng) for _ in range(n)]


def generate_curriculum_batch(
    n_per_stage: int = 25,
    stages: Optional[List[str]] = None,
    seed: Optional[int] = None,
) -> List[Dict[str, float]]:
    """
    Curriculum sırasıyla (safe → balanced → critical → chaos) state üretir.
    stages verilmezse CURRICULUM_ORDER kullanılır.
    Returns: safe'ten n_per_stage + balanced'tan n_per_stage + ... (birleşik liste).
    """
    stages = stages or list(CURRICULUM_ORDER)
    rng = random.Random(seed)
    out = []
    for i, profile in enumerate(stages):
        for _ in range(n_per_stage):
            out.append(generate_state(profile=profile, rng=rng))
    return out
