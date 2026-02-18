# Release Notes — mdm-engine 0.2.1

**Release Date:** 2026-02-17  
**Type:** Patch Release (backward-compatible)

---

## Summary

This patch release adds batch flush support to `TraceLogger` for improved IO performance in high-throughput scenarios, while maintaining backward-compatible default behavior.

---

## Changes

### ✅ F5 — TraceLogger Batch Flush

**Problem:** `TraceLogger.write()` performed `flush()` on every write, creating an IO bottleneck for high-throughput scenarios.

**Solution:** Added configurable batch flush:
- `flush_every_n` parameter (default: 1, backward-compatible)
- Context manager pattern (`__enter__`/`__exit__`)
- Explicit `flush()` method
- Automatic flush on `close()`

**Files Changed:**
- `mdm_engine/trace/trace_logger.py`: Added batch flush support

**Performance:** For high-throughput scenarios, set `flush_every_n=100` or higher to reduce IO operations.

**Example:**
```python
from mdm_engine.trace.trace_logger import TraceLogger
from pathlib import Path

# Default: flush every write (backward-compatible)
logger = TraceLogger(Path("./runs/test"))

# High-throughput: flush every 100 writes
logger = TraceLogger(Path("./runs/test"), flush_every_n=100)

# Context manager ensures flush on exit
with TraceLogger(Path("./runs/test"), flush_every_n=100) as logger:
    logger.write(packet)
    # Automatic flush on exit
```

---

## Backward Compatibility

✅ **Fully backward-compatible:**
- Default `flush_every_n=1` maintains existing behavior
- No API changes (only new optional parameter)
- Existing code continues to work without modification

---

## Migration Guide

**No migration needed.** Existing code continues to work.

**Optional:** For high-throughput scenarios, enable batch flushing:
```python
# Before (still works)
logger = TraceLogger(run_dir)

# After (optional optimization)
logger = TraceLogger(run_dir, flush_every_n=100)
```

---

## Testing

- ✅ All existing tests pass
- ✅ Backward compatibility verified
- ✅ Context manager pattern tested

---

## References

- **Issue:** F5 from static analysis report
- **Performance:** IO throughput improvement for batch scenarios

---

**Upgrade Path:** `pip install "mdm-engine>=0.2.1,<0.3"`
