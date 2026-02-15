# MDM — State Encoder (Phase 2 spec §1.1)
# Ham durumu standart state vektörüne dönüştürür; deterministik, [0,1] clamp.
# Input quality / evidence consistency: Tavsiye §1 — mask + quality vector.

from dataclasses import dataclass
from typing import Any, Dict, Tuple

# Import from repo root config (backward compat) or mdm_engine.config
try:
    from mdm_engine.config import DEFAULT_UNKNOWN
except ImportError:
    from config import DEFAULT_UNKNOWN

# State alanları (eksiklik hesabı için)
STATE_KEYS_EXT = ("physical", "social", "context", "risk")
STATE_KEYS_MORAL = ("compassion", "justice", "harm_sens", "responsibility", "empathy")
STATE_KEYS = STATE_KEYS_EXT + STATE_KEYS_MORAL


@dataclass(frozen=True)
class State:
    """Kodlanmış state: x_ext (dış), x_moral (iç)."""
    x_ext: tuple
    x_moral: tuple

    def __post_init__(self):
        assert len(self.x_ext) == 4 and len(self.x_moral) == 5


@dataclass
class InputQualityResult:
    """Giriş kalitesi ve kanıt tutarlılığı (Tavsiye §1)."""
    missing_mask: Tuple[bool, ...]  # True = alan mevcut ve geçerli
    missing_ratio: float  # 0=hepsi var, 1=hepsi eksik
    input_quality: float   # [0,1]; adapter verirse o, yoksa 1 - missing_ratio
    evidence_consistency: float  # [0,1]; 1=tutarlı, 0=çelişkili; adapter verirse o, yoksa 1.0


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _get_float(data: Dict[str, Any], key: str, default: float = DEFAULT_UNKNOWN) -> float:
    v = data.get(key)
    if v is None:
        return default
    try:
        return _clamp(float(v))
    except (TypeError, ValueError):
        return default


def _is_present_and_valid(data: Dict[str, Any], key: str) -> bool:
    v = data.get(key)
    if v is None:
        return False
    try:
        f = float(v)
        return 0 <= f <= 1
    except (TypeError, ValueError):
        return False


def compute_input_quality(raw_state: Dict[str, Any]) -> InputQualityResult:
    """
    Eksik alan oranı ve (varsa) adapter'dan gelen input_quality / evidence_consistency.
    Core tek başına: missing_mask + missing_ratio; input_quality/evidence_consistency
    raw_state veya context'ten gelmezse türetilir (1 - missing_ratio, 1.0).
    """
    mask = tuple(_is_present_and_valid(raw_state, k) for k in STATE_KEYS)
    n = len(mask)
    missing_ratio = 1.0 - (sum(mask) / n) if n else 0.0
    # Adapter raw_state'e koyabilir
    iq = raw_state.get("input_quality")
    if iq is not None:
        try:
            input_quality = max(0.0, min(1.0, float(iq)))
        except (TypeError, ValueError):
            input_quality = 1.0 - missing_ratio
    else:
        input_quality = 1.0 - missing_ratio
    ec = raw_state.get("evidence_consistency")
    if ec is not None:
        try:
            evidence_consistency = max(0.0, min(1.0, float(ec)))
        except (TypeError, ValueError):
            evidence_consistency = 1.0
    else:
        evidence_consistency = 1.0
    return InputQualityResult(
        missing_mask=mask,
        missing_ratio=missing_ratio,
        input_quality=input_quality,
        evidence_consistency=evidence_consistency,
    )


def encode_state(raw_state: Dict[str, Any]) -> State:
    """
    Ham durum sözlüğünü Phase 1 state vektörüne çevirir.
    Eksik/geçersiz alanlar DEFAULT_UNKNOWN (0.5) ile doldurulur.
    """
    x_ext = (
        _get_float(raw_state, "physical"),
        _get_float(raw_state, "social"),
        _get_float(raw_state, "context"),
        _get_float(raw_state, "risk"),
    )
    x_moral = (
        _get_float(raw_state, "compassion"),
        _get_float(raw_state, "justice"),
        _get_float(raw_state, "harm_sens"),
        _get_float(raw_state, "responsibility"),
        _get_float(raw_state, "empathy"),
    )
    return State(x_ext=x_ext, x_moral=x_moral)
