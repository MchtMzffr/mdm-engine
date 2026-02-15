# MDM Examples

This directory contains example scripts demonstrating how to use MDM.

## Quick Start

### 1. Hello World (`hello_world.py`)

The simplest example - make a single decision:

```bash
python examples/hello_world.py
```

### 2. Replay Example (`replay_example.py`)

Demonstrates trace replay for reproducibility:

```bash
python examples/replay_example.py
```

### 3. Trace Collection (`trace_collection.py`)

Shows how to collect multiple traces:

```bash
python examples/trace_collection.py
```

## Running Examples

### Option 1: Direct execution

```bash
# From project root
python examples/hello_world.py
```

### Option 2: After installation

```bash
# Install package
pip install -e .

# Run examples
python examples/hello_world.py
```

## Example Output

### Hello World

```
============================================================
MDM Hello World Example
============================================================

Input state:
  risk: 0.7
  severity: 0.8
  ...

Decision Result:
  Action: [0.0, 1.0, 0.58, 0.29]
  Escalation Level: L1
  Human Escalation: False
  Confidence: 0.12

✅ Decision completed successfully!
```

## Next Steps

1. **Explore Profiles**: Try different config profiles (`scenario_test`, `production_safe`, `high_critical`)
2. **Visualize**: Run `mdm dashboard` to see traces visually
3. **Collect Traces**: Use `TraceCollector` to build datasets
4. **Replay**: Verify determinism with `replay_trace()`

## Integration Examples

### Chat Moderation Adapter

```python
from mdm_engine import decide

def moderate_message(message_text):
    # Domain adapter: message → risk score
    risk_score = analyze_message_risk(message_text)
    
    raw_state = {
        "risk": risk_score,
        "severity": 0.7,
        # ... other fields
    }
    
    result = decide(raw_state, profile="scenario_test")
    
    if result["human_escalation"]:
        return "FLAG_FOR_REVIEW"
    elif result["escalation"] == 1:
        return "SOFT_WARNING"
    else:
        return "OK"
```

### Sensor/IoT Adapter

```python
from mdm_engine import decide

def analyze_sensor_data(temp, pressure, vibration):
    # Domain adapter: sensor data → physical risk
    physical_risk = calculate_risk(temp, pressure, vibration)
    
    raw_state = {
        "risk": physical_risk,
        "severity": 0.8,
        "physical": 0.9,
        # ... other fields
    }
    
    result = decide(raw_state, profile="production_safe")
    
    if result["human_escalation"]:
        alert_operator()
    elif result["escalation"] == 1:
        log_warning()
```

## See Also

- **README.md**: Main documentation
- **USAGE_POLICY.md**: Usage guidelines
- **AUDITABILITY.md**: Trace schema and replay
