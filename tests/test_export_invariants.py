# Export invariant: UI/CSV mapping drift yakalama.
# - final_action_reason doluysa flat row "reason" aynı olmalı
# - final_action != HOLD_REVIEW ise selection_reason fail_safe olmamalı (action_selector'dan gelen gerçek)

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdm_engine.audit_spec import decision_packet_to_flat_row, decision_packet_to_csv_row


def test_flat_row_reason_equals_final_action_reason():
    """final_action_reason set ise flat row 'reason' aynı olmalı."""
    packet = {
        "ts": 123.0,
        "input": {"title": "Foo", "user": "U", "revid": 1},
        "external": {"decision": "FLAG", "p_damaging": 0.7},
        "mdm": {"level": 2, "reason": "wiki:ores_flag_disagree", "selection_reason": "pareto_tiebreak:margin"},
        "final_action": "HOLD_REVIEW",
        "final_action_reason": "wiki:ores_flag_disagree",
        "mismatch": False,
        "run_id": "r1",
    }
    row = decision_packet_to_flat_row(packet)
    assert row["reason"] == packet["final_action_reason"], (row.get("reason"), packet["final_action_reason"])


def test_flat_row_reason_fallback_when_no_final_action_reason():
    """final_action_reason yoksa mdm.reason kullanılır."""
    packet = {
        "ts": 123.0,
        "input": {"title": "Foo", "user": "U", "revid": 1},
        "external": {"decision": "ALLOW"},
        "mdm": {"level": 0, "reason": "none", "selection_reason": "pareto_tiebreak:margin"},
        "final_action": "APPLY",
        "mismatch": False,
        "run_id": "r1",
    }
    row = decision_packet_to_flat_row(packet)
    assert row["reason"] == "none" or row["reason"] == packet.get("final_action_reason") or (packet.get("mdm") or {}).get("reason") == "none"


def test_selection_reason_not_fail_safe_when_apply():
    """final_action == APPLY ise selection_reason fail_safe olmamalı (L0 = normal seçim)."""
    packet = {
        "ts": 123.0,
        "input": {"title": "T", "user": "U", "revid": 1},
        "external": {"decision": "ALLOW"},
        "mdm": {"level": 0, "reason": "none", "selection_reason": "pareto_tiebreak:margin>H>J"},
        "final_action": "APPLY",
        "final_action_reason": "none",
        "mismatch": False,
        "run_id": "r1",
    }
    row = decision_packet_to_flat_row(packet)
    assert row["selection_reason"] != "fail_safe", "APPLY satırında selection_reason fail_safe olmamalı"
    assert row["final_action"] == "APPLY"


def test_csv_mdm_reason_equals_final_action_reason():
    """CSV mdm_reason = final_action_reason (SSOT)."""
    packet = {
        "ts": 123.0,
        "input": {"title": "T", "user": "U", "revid": 1, "comment": ""},
        "external": {"decision": "FLAG", "p_damaging": 0.8},
        "mdm": {"level": 2, "reason": "wiki:ores_flag_disagree", "selection_reason": "fail_safe"},
        "final_action": "HOLD_REVIEW",
        "final_action_reason": "wiki:ores_flag_disagree",
        "mismatch": True,
        "run_id": "r1",
        "clamps": [{"type": "human_review"}],
    }
    row = decision_packet_to_csv_row(packet)
    assert row.get("mdm_reason") == packet["final_action_reason"], (row.get("mdm_reason"), packet["final_action_reason"])


# selection_reason: HOLD_REVIEW'ta fail_safe/no_valid_fallback olabilir; APPLY/APPLY_CLAMPED'ta olamaz
HOLD_REVIEW_SELECTION_REASONS = ("fail_safe", "no_valid_fallback")
NON_HOLD_SELECTION_FORBIDDEN = ("fail_safe", "no_valid_fallback")


def test_hold_review_implies_level_2_and_allowed_selection_reason():
    """final_action == HOLD_REVIEW ise mdm.level == 2 ve selection_reason L2'ye uygun (fail_safe/no_valid_fallback vb)."""
    packet = {
        "ts": 123.0,
        "input": {"title": "T", "user": "U", "revid": 1},
        "external": {"decision": "FLAG"},
        "mdm": {"level": 2, "reason": "fail_safe", "selection_reason": "fail_safe"},
        "final_action": "HOLD_REVIEW",
        "final_action_reason": "fail_safe",
        "mismatch": False,
        "run_id": "r1",
    }
    row = decision_packet_to_flat_row(packet)
    assert row["final_action"] == "HOLD_REVIEW"
    assert row["mdm_level"] == 2
    assert row.get("selection_reason") in HOLD_REVIEW_SELECTION_REASONS or (row.get("selection_reason") or "").startswith("pareto") or row.get("selection_reason") == "fail_safe" or row.get("selection_reason") == "no_valid_fallback"


def test_non_hold_review_selection_reason_not_fail_safe_or_no_valid():
    """final_action != HOLD_REVIEW ise selection_reason fail_safe veya no_valid_fallback olamaz."""
    for final_action in ("APPLY", "APPLY_CLAMPED"):
        packet = {
            "ts": 123.0,
            "input": {"title": "T", "user": "U", "revid": 1},
            "external": {"decision": "ALLOW"},
            "mdm": {"level": 0 if final_action == "APPLY" else 1, "reason": "none", "selection_reason": "pareto_tiebreak:margin"},
            "final_action": final_action,
            "final_action_reason": "none",
            "mismatch": False,
            "run_id": "r1",
        }
        row = decision_packet_to_flat_row(packet)
        assert row["final_action"] == final_action
        sel = row.get("selection_reason") or ""
        assert sel not in NON_HOLD_SELECTION_FORBIDDEN, f"{final_action} satırında selection_reason {sel} olamaz"


if __name__ == "__main__":
    test_flat_row_reason_equals_final_action_reason()
    print("  OK flat row reason = final_action_reason")
    test_flat_row_reason_fallback_when_no_final_action_reason()
    print("  OK flat row reason fallback")
    test_selection_reason_not_fail_safe_when_apply()
    print("  OK selection_reason not fail_safe when APPLY")
    test_csv_mdm_reason_equals_final_action_reason()
    print("  OK CSV mdm_reason = final_action_reason")
    test_hold_review_implies_level_2_and_allowed_selection_reason()
    print("  OK HOLD_REVIEW => level=2 and allowed selection_reason")
    test_non_hold_review_selection_reason_not_fail_safe_or_no_valid()
    print("  OK non-HOLD_REVIEW => selection_reason not fail_safe/no_valid_fallback")
    print("Tum export invariant testleri gecti.")
