#!/usr/bin/env python
"""
MDM Replay Example

Demonstrates how to replay a decision trace to reproduce the same decision.
"""

from mdm_engine import decide, replay_trace


def main():
    # Create a raw state
    raw_state = {
        "risk": 0.7,
        "severity": 0.8,
        "physical": 0.6,
        "social": 0.5,
        "context": 0.4,
        "compassion": 0.5,
        "justice": 0.9,
        "harm_sens": 0.5,
        "responsibility": 0.7,
        "empathy": 0.6,
    }

    print("=" * 60)
    print("MDM Replay Example")
    print("=" * 60)

    # Make initial decision
    print(f"\n1. Making initial decision...")
    result1 = decide(raw_state, profile="scenario_test", deterministic=True)
    print(f"   Action: {result1['action']}")
    print(f"   Level: L{result1['escalation']}")

    # Replay the trace
    print(f"\n2. Replaying trace...")
    result2 = replay_trace(result1["trace"], validate=True, verify_hash=False)
    print(f"   Action: {result2['action']}")
    print(f"   Level: L{result2['escalation']}")

    # Verify they match
    print(f"\n3. Verification:")
    if result1["action"] == result2["action"]:
        print(f"   ✅ Actions match - Determinism verified!")
    else:
        print(f"   ❌ Actions differ - This should not happen in deterministic mode")

    if result1["escalation"] == result2["escalation"]:
        print(f"   ✅ Escalation levels match")
    else:
        print(f"   ❌ Escalation levels differ")

    print(f"\n✅ Replay example completed!")


if __name__ == "__main__":
    main()
