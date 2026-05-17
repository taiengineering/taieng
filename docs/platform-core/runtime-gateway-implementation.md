# Runtime Gateway Implementation

## \uad6c\uc870

```
\uc678\ubd80 SaaS / \ub0b4\ubd80 Runtime
  \u2502
  \u251c\u2500 POST /control-runtime/events      \u2500\u2500\u2510
  \u251c\u2500 POST /control-runtime/workflows   \u2500\u2500\u2524
  \u251c\u2500 POST /control-runtime/heartbeat   \u2500\u2500\u2524
  \u2502                                        \u2502
  \u2502              \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
  \u2502              \u2502
  \u2502     API Key \uc778\uc99d (X-Control-API-Key)
  \u2502              \u2502
  \u2502     RuntimeContext \uc0dd\uc131
  \u2502              \u2502
  \u2502     emit_runtime_event(ctx, event)
  \u2502       \u251c\u2500 Validation (6\ub2e8\uacc4)
  \u2502       \u251c\u2500 Sovereignty
  \u2502       \u251c\u2500 Event Store
  \u2502       \u2514\u2500 EventResult
  \u2502
  \u2514\u2500 GET /control-runtime/health
```

## API

| Method | Path | \uc778\uc99d | \uc124\uba85 |
|--------|------|:---:|------|
| POST | `/control-runtime/events` | \u2705 | \ud45c\uc900 Event Push |
| POST | `/control-runtime/workflows` | \u2705 | Workflow \uc0c1\ud0dc Push |
| POST | `/control-runtime/heartbeat` | \u2705 | \uc0dd\uc874 \uc2e0\ud638 |
| GET | `/control-runtime/health` | \u274c | Gateway \uc0c1\ud0dc |

## \uc678\ubd80 \uc5f0\ub3d9 curl \uc608\uc2dc

```bash
# Event Push
curl -X POST https://api.taieng.co.kr/control-runtime/events \
  -H 'Content-Type: application/json' \
  -H 'X-Control-API-Key: dev_test_key' \
  -d '{
    "event_type": "workflow.completed",
    "flow_key": "signup",
    "trace_id": "test_001",
    "severity": "INFO"
  }'

# Workflow Push
curl -X POST https://api.taieng.co.kr/control-runtime/workflows \
  -H 'Content-Type: application/json' \
  -H 'X-Control-API-Key: dev_test_key' \
  -d '{"flow_key": "checkout", "event_type": "workflow.failed", "severity": "WARNING"}'

# Health
curl https://api.taieng.co.kr/control-runtime/health
```

## emit_event Wrapper

\uae30\uc874 \ucf54\ub4dc\uc5d0\uc11c Runtime Bus\ub85c \uc810\uc9c4 \uc5f0\uacb0:

```python
# Before (\uae30\uc874)
emit_event(step_key="save_db", result="success", ...)

# After (Bus \uacbd\uc720)
from watch_engine.runtime_bus.emit_wrapper import emit_event_via_bus
emit_event_via_bus(step_key="save_db", result="success", flow_key="process_registration", tenant_id="tai")
```

\uae30\uc874 interface \uc720\uc9c0. \ub0b4\ubd80\uc5d0\uc11c Canonical event_type \uc790\ub3d9 \ub9e4\ud551:
- `result="success"` \u2192 `step.completed` or `workflow.completed`
- `result="failure"` \u2192 `step.failed` or `workflow.failed`
- `result="timeout"` \u2192 `workflow.timeout`

## \uc810\uc9c4 \uc801\uc6a9 \uacc4\ud68d

| Phase | \ub300\uc0c1 | \uc0c1\ud0dc |
|:---:|------|:---:|
| 1 | Gateway API | \u2705 \uad6c\ud604 |
| 2 | emit_event_via_bus wrapper | \u2705 \uad6c\ud604 |
| 3 | factory_process_v3 \ub0b4\ubd80 emit_event \u2192 wrapper \uad50\uccb4 | \ud83d\udea7 |
| 4 | \uc804\uccb4 emit_event \u2192 Bus \uad50\uccb4 | \ud83d\udea7 |
