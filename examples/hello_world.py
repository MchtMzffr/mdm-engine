#!/usr/bin/env python
"""
MDM Hello World Example

This is the simplest possible example of using MDM.
It demonstrates:
1. Creating a raw state
2. Making a decision
3. Inspecting the result
"""

from mdm_engine import decide


def main():
    # Create a raw state (domain adapter would provide this)
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
    print("MDM Hello World Example")
    print("=" * 60)
    print(f"\nInput state:")
    for key, value in raw_state.items():
        print(f"  {key}: {value}")

    # Make decision with scenario_test profile
    print(f"\nMaking decision with profile='scenario_test'...")
    result = decide(raw_state, profile="scenario_test")

    # Display results
    print(f"\nDecision Result:")
    print(f"  Action: {result['action']}")
    print(f"    [severity, intervention, compassion, delay]")
    print(f"  Escalation Level: L{result['escalation']}")
    print(f"    L0 = Automatic decision")
    print(f"    L1 = Soft clamp applied")
    print(f"    L2 = Human escalation required")
    print(f"  Human Escalation: {result['human_escalation']}")
    print(f"  Confidence: {result.get('confidence', 'N/A')}")

    if result.get("J") is not None:
        print(f"\nMoral Scores:")
        print(f"  Justice (J): {result.get('J', 'N/A')}")
        print(f"  Harm (H): {result.get('H', 'N/A')}")

    print(f"\n[OK] Decision completed successfully!")
    print(f"\nNext steps:")
    print(f"  1. Try different profiles: 'production_safe', 'high_critical'")
    print(f"  2. Check result['trace'] for full decision trace")
    print(f"  3. Use replay_trace() to reproduce the same decision")
    print(f"  4. Run 'mdm dashboard' to visualize traces")


if __name__ == "__main__":
    main()
