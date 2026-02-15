# MDM: Golden Example

**Purpose**: A complete, production-ready example demonstrating MDM's capabilities  
**Use Case**: Healthcare decision support with human escalation  
**Duration**: ~5 minutes to run

---

## Scenario: Patient Risk Assessment

### Domain Context

A healthcare AI system analyzes patient data and recommends treatment urgency levels. MDM acts as a governance layer, ensuring:
- Ethical boundaries are respected
- High-risk cases escalate to human clinicians
- All decisions are auditable

---

## Implementation

### Step 1: Domain Adapter

```python
# healthcare_adapter.py
"""
Healthcare domain adapter for MDM.

Converts patient data → raw_state → MDM → action → treatment recommendation
"""

from typing import Dict, Any
from mdm_engine import decide
from core.trace_collector import TraceCollector, build_decision_trace
import time


def patient_to_raw_state(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert patient data to MDM raw_state format.
    
    Args:
        patient_data: {
            "age": int,
            "symptoms": List[str],
            "vitals": {"bp": float, "heart_rate": int, "temp": float},
            "history": List[str],
            "medications": List[str]
        }
    
    Returns:
        raw_state dict for MDM
    """
    # Domain-specific risk calculation
    risk_score = calculate_patient_risk(patient_data)
    severity_score = calculate_severity(patient_data)
    
    return {
        "risk": risk_score,
        "severity": severity_score,
        "physical": patient_data.get("vitals", {}).get("bp", 0) / 200.0,  # Normalized
        "social": 0.5,  # Placeholder (would come from social determinants)
        "context": 0.6,  # Contextual factors
        "compassion": 0.7,  # Patient-centered care priority
        "justice": 0.9,  # Fairness in resource allocation
        "harm_sens": 0.8,  # Harm sensitivity (medical context)
        "responsibility": 0.9,  # Medical responsibility
        "empathy": 0.8,  # Empathy for patient
    }


def calculate_patient_risk(patient_data: Dict[str, Any]) -> float:
    """Calculate patient risk score (0-1)."""
    risk = 0.0
    
    # Age factor
    age = patient_data.get("age", 50)
    if age > 65:
        risk += 0.2
    elif age < 18:
        risk += 0.1
    
    # Vital signs
    vitals = patient_data.get("vitals", {})
    bp = vitals.get("bp", 120)
    if bp > 140 or bp < 90:
        risk += 0.3
    
    heart_rate = vitals.get("heart_rate", 70)
    if heart_rate > 100 or heart_rate < 60:
        risk += 0.2
    
    temp = vitals.get("temp", 98.6)
    if temp > 100.4:
        risk += 0.2
    
    # Medical history
    history = patient_data.get("history", [])
    if "diabetes" in history or "hypertension" in history:
        risk += 0.1
    
    return min(risk, 1.0)


def calculate_severity(patient_data: Dict[str, Any]) -> float:
    """Calculate symptom severity score (0-1)."""
    symptoms = patient_data.get("symptoms", [])
    severe_symptoms = ["chest pain", "difficulty breathing", "loss of consciousness"]
    
    severity = 0.0
    for symptom in symptoms:
        if any(severe in symptom.lower() for severe in severe_symptoms):
            severity += 0.3
        else:
            severity += 0.1
    
    return min(severity, 1.0)


def action_to_treatment_recommendation(action: list, level: int) -> Dict[str, Any]:
    """
    Convert MDM action to treatment recommendation.
    
    Args:
        action: [severity, intervention, compassion, delay]
        level: Escalation level (0, 1, or 2)
    
    Returns:
        Treatment recommendation dict
    """
    severity, intervention, compassion, delay = action
    
    recommendation = {
        "urgency_level": "low" if severity < 0.3 else "medium" if severity < 0.7 else "high",
        "intervention_type": "monitoring" if intervention < 0.3 else "treatment" if intervention < 0.7 else "immediate_care",
        "patient_centered": compassion > 0.5,
        "wait_time_hours": int(delay * 24),  # Convert to hours
        "escalation_level": level,
        "requires_human_review": level == 2,
    }
    
    return recommendation


def process_patient(patient_data: Dict[str, Any], collector: TraceCollector) -> Dict[str, Any]:
    """
    Process patient data through MDM.
    
    Returns:
        Complete result with treatment recommendation
    """
    # Convert to raw_state
    raw_state = patient_to_raw_state(patient_data)
    
    # Make decision with production-safe profile
    t_before = time.perf_counter()
    result = decide(raw_state, profile="production_safe", deterministic=True)
    t_after = time.perf_counter()
    latency_ms = (t_after - t_before) * 1000
    
    # Build trace
    trace = build_decision_trace(result, t=time.time(), latency_ms=latency_ms)
    collector.push(trace)
    
    # Convert action to recommendation
    recommendation = action_to_treatment_recommendation(
        result["action"],
        result["escalation"]
    )
    
    return {
        "patient_id": patient_data.get("id", "unknown"),
        "decision": result,
        "recommendation": recommendation,
        "trace": trace,
        "requires_human_review": result["human_escalation"],
    }


# Example usage
if __name__ == "__main__":
    collector = TraceCollector(jsonl_path="healthcare_traces.jsonl")
    
    # Example patient
    patient = {
        "id": "P001",
        "age": 72,
        "symptoms": ["chest pain", "shortness of breath"],
        "vitals": {"bp": 150, "heart_rate": 110, "temp": 99.8},
        "history": ["hypertension", "diabetes"],
        "medications": ["metformin", "lisinopril"],
    }
    
    result = process_patient(patient, collector)
    
    print("=" * 60)
    print("Patient Decision Result")
    print("=" * 60)
    print(f"Patient ID: {result['patient_id']}")
    print(f"Escalation Level: L{result['decision']['escalation']}")
    print(f"Human Review Required: {result['requires_human_review']}")
    print(f"\nRecommendation:")
    for key, value in result['recommendation'].items():
        print(f"  {key}: {value}")
    
    if result['requires_human_review']:
        print("\n⚠️  MANDATORY: Escalate to human clinician")
    
    collector.close()
    print(f"\n✅ Trace saved to: {collector.jsonl_path}")
```

---

## Step 2: Batch Processing Example

```python
# healthcare_batch.py
"""
Batch processing example for multiple patients.
"""

from healthcare_adapter import process_patient
from core.trace_collector import TraceCollector
import json

def process_patient_batch(patients: list, output_path: str = "healthcare_batch_results.json"):
    """Process multiple patients and generate report."""
    collector = TraceCollector(jsonl_path="healthcare_batch_traces.jsonl")
    
    results = []
    escalation_count = 0
    
    for patient in patients:
        result = process_patient(patient, collector)
        results.append(result)
        
        if result['requires_human_review']:
            escalation_count += 1
    
    collector.close()
    
    # Generate summary report
    report = {
        "total_patients": len(patients),
        "human_escalations": escalation_count,
        "escalation_rate": escalation_count / len(patients),
        "results": results,
    }
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Processed {len(patients)} patients")
    print(f"   Human escalations: {escalation_count} ({report['escalation_rate']*100:.1f}%)")
    print(f"   Results saved to: {output_path}")
    print(f"   Traces saved to: {collector.jsonl_path}")
    
    return report


# Example batch
if __name__ == "__main__":
    patients = [
        {
            "id": "P001",
            "age": 72,
            "symptoms": ["chest pain"],
            "vitals": {"bp": 150, "heart_rate": 110, "temp": 99.8},
            "history": ["hypertension"],
            "medications": [],
        },
        {
            "id": "P002",
            "age": 35,
            "symptoms": ["headache"],
            "vitals": {"bp": 120, "heart_rate": 75, "temp": 98.6},
            "history": [],
            "medications": [],
        },
        {
            "id": "P003",
            "age": 55,
            "symptoms": ["difficulty breathing"],
            "vitals": {"bp": 180, "heart_rate": 130, "temp": 101.2},
            "history": ["diabetes", "hypertension"],
            "medications": ["insulin"],
        },
    ]
    
    report = process_patient_batch(patients)
```

---

## Step 3: Dashboard Visualization

```bash
# After running healthcare_adapter.py
mdm dashboard

# Load healthcare_traces.jsonl in dashboard
# View:
# - CUS timeline
# - Level distribution (L0/L1/L2)
# - Escalation rate
# - Action drift
```

---

## Key Takeaways

### For Academics

1. **Complete Implementation**: Full adapter pattern example
2. **Traceability**: Every decision fully traced and replayable
3. **Validation**: Deterministic replay proves correctness
4. **Methodology**: Reusable pattern for other domains

### For Industry

1. **Production-Ready Pattern**: Adapter layer separates domain from governance
2. **Compliance**: Full audit trail for regulatory requirements
3. **Risk Mitigation**: Human escalation reduces liability
4. **Integration**: Clear integration points and responsibilities

---

## Running the Example

```bash
# Install
pip install mdm

# Run healthcare adapter
python healthcare_adapter.py

# View dashboard
mdm dashboard
# Load healthcare_traces.jsonl

# Batch processing
python healthcare_batch.py
```

---

## Expected Output

```
============================================================
Patient Decision Result
============================================================
Patient ID: P001
Escalation Level: L2
Human Review Required: True

Recommendation:
  urgency_level: high
  intervention_type: immediate_care
  patient_centered: True
  wait_time_hours: 0
  escalation_level: 2
  requires_human_review: True

⚠️  MANDATORY: Escalate to human clinician

✅ Trace saved to: healthcare_traces.jsonl
```

---

**This example demonstrates:**
- Domain adapter pattern
- Production-safe configuration
- Human escalation handling
- Complete trace generation
- Dashboard visualization

**Last Updated**: 2026-02-13
