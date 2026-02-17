# MDM Engine

**MDM Engine** is a runtime system for **Model Decision Models** (MDM). It provides event loop orchestration, feature extraction, reference MDM implementation, and trace/audit capabilities.

## Domain-Agnostic Guarantee

MDM Engine is designed to work across **any domain** that requires proposal generation:

- ✅ **No domain-specific logic**: Feature extraction and proposal generation are generic
- ✅ **Generic interfaces**: Adapters (`DataSource`, `Broker`) work for any domain
- ✅ **Flexible features**: Feature builder accepts generic event dictionaries
- ✅ **Contract-first**: Uses `decision-schema` for type contracts (domain-agnostic)
- ✅ **Private hook pattern**: Domain-specific models go in `_private/` (gitignored)
- ✅ **Trace/audit**: PacketV2 tracing works for any decision pipeline

## What MDM Engine Does

MDM Engine provides:
- **Event Loop**: Orchestrates proposal generation → (optional DMC modulation) → execution flow
- **Feature Extraction**: Builds features from event data (generic event dictionaries)
- **Reference MDM**: Simple explainable scoring model (logistic/linear) for demonstration
- **Adapters**: Generic interfaces for data sources and executors
- **Trace/Audit**: Logging and security utilities (redaction)

## What MDM Engine Is NOT

- **Not DMC**: MDM Engine generates proposals; DMC modulates them (see `decision-modulation-core`)
- **Not domain-specific**: No domain-specific adapters or implementations
- **Not an execution engine**: No order management, position management, or execution logic beyond interfaces
- **Not a strategy**: Reference MDM is for demonstration; use private hook for production models

## Use Cases

MDM Engine enables proposal generation in various domains:

### 1. Content Moderation Pipeline
- **Event**: Content submission (text, image, video)
- **Features**: ML model scores, metadata, user history
- **Proposal**: Moderate/flag/approve with confidence
- **Execution**: Apply moderation action or queue for review

### 2. Robotics Control System
- **Event**: Sensor readings (camera, lidar, IMU)
- **Features**: Obstacle distance, battery level, velocity
- **Proposal**: Move/stop/rotate with confidence
- **Execution**: Send command to robot actuators

### 3. Resource Allocation System
- **Event**: Resource request (compute, storage, bandwidth)
- **Features**: Current utilization, demand patterns, priority
- **Proposal**: Allocate/reject with confidence
- **Execution**: Allocate resources or queue request

### 4. API Rate Limiting & Quota Management
- **Event**: API request (endpoint, user, timestamp)
- **Features**: Request rate, quota usage, error rate
- **Proposal**: Allow/throttle/deny with confidence
- **Execution**: Process request or return rate-limit response

### 5. Trading/Financial Markets (Optional)
- **Event**: Market data (prices, order book, trades)
- **Features**: Microstructure features (spread, depth, imbalance)
- **Proposal**: Execute trade with confidence
- **Execution**: Submit order to exchange

See `docs/examples/` for domain-specific examples.

## Core Components

### 1. Event Loop (`ami_engine/loop/run_loop.py`)

Main orchestration: event → features → MDM proposal → DMC modulation → execution → trace.

### 2. Feature Extraction (`ami_engine/features/feature_builder.py`)

Builds features from generic event dictionaries:
- Basic: numeric values, timestamps, counts
- Advanced: aggregations, rolling statistics, derived metrics

### 3. Reference MDM (`ami_engine/mdm/`)

- `reference_model.py`: Simple logistic scoring (demonstration)
- `decision_engine.py`: Glues features → proposal (uses private hook if available)
- `position_manager.py`: Reference exit policy (TP/SL/time stops) - **reference only, not production-ready**

### 4. Adapters (`ami_engine/adapters/`)

Generic interfaces:
- `DataSource`: Abstract interface for event streams
- `Broker`: Abstract interface for action execution

No domain-specific implementations (external adapters removed; use your own).

### 5. Trace/Audit (`ami_engine/trace/`, `ami_engine/security/`)

- `TraceLogger`: Writes PacketV2 to JSONL
- `AuditLogger`: Security audit logs
- `redaction`: Secret redaction utilities

## Private MDM Hook

MDM Engine supports a private model hook:

1. Create `ami_engine/mdm/_private/model.py` (gitignored)
2. Implement `compute_proposal_private(features: dict, **kwargs) -> Proposal`
3. `DecisionEngine` will use it if present; otherwise falls back to reference

This allows proprietary MDM models without exposing them in public code.

## Quick Start

```python
from ami_engine.mdm.decision_engine import DecisionEngine
from ami_engine.features.feature_builder import build_features
from decision_schema.types import Action

# Build features from generic event
event = {
    "value": 0.5,
    "timestamp_ms": 1000,
    "metadata": {"source": "sensor_1"},
}
features = build_features(event, history=[], ...)

# MDM proposal
mdm = DecisionEngine(confidence_threshold=0.5)
proposal = mdm.propose(features)

print(f"Action: {proposal.action}, Confidence: {proposal.confidence}")
```

## Integration with Decision Schema

MDM Engine outputs `Proposal` (from `decision-schema` package). This is the **single source of truth** for type contracts.

**Schema Dependency**: MDM Engine depends **only** on `decision-schema>=0.1,<0.2` for type contracts. This ensures compatibility across the multi-core ecosystem.

**Optional DMC Integration**: For risk-aware decision modulation, you can integrate `decision-modulation-core` (DMC) as an optional layer:

```python
from decision_schema.types import Proposal, Action, FinalDecision
from decision_modulation_core.dmc.modulator import modulate
from decision_modulation_core.dmc.risk_policy import RiskPolicy

proposal = mdm.propose(features)

# Optional: Apply risk guards via DMC
final_action, mismatch = modulate(proposal, RiskPolicy(), context)

if mismatch.flags:
    # Guards triggered - do not execute
    return

# Execute final_action
```

**Without DMC**: Proposals can be executed directly (no risk guards). This is suitable for testing or when risk management is handled elsewhere.

See `decision-modulation-core` repository for DMC documentation.

## Documentation

- `docs/ARCHITECTURE.md`: System architecture and data flow
- `docs/TERMINOLOGY.md`: Key terms and concepts
- `docs/SAFETY_LIMITATIONS.md`: What MDM Engine does NOT guarantee
- `docs/PUBLIC_RELEASE_GUIDE.md`: Public release checklist
- `docs/examples/`: Domain-specific examples (content moderation, robotics, trading)

## Installation

```bash
pip install -e .
```

Or from git:
```bash
pip install git+https://github.com/MeetlyTR/mdm-engine.git
```

## Tests

```bash
pytest tests/
```

## License

[Add your license]
