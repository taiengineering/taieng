# Runtime Event Bus

## \ubaa9\uc801

\ubaa8\ub4e0 Runtime Event\uac00 \ud558\ub098\uc758 \uc911\uc559 Bus\ub97c \ud1b5\uacfc\ud558\ub3c4\ub85d \uac15\uc81c.
Validation + Sovereignty + Tenant Boundary + Event Store \uc790\ub3d9 \uc801\uc6a9.

## \uad6c\uc870

```
watch_engine/runtime_bus/
\u251c\u2500\u2500 __init__.py          # emit_runtime_event, EventResult, RuntimeContext
\u251c\u2500\u2500 event_bus.py         # \uc911\uc559 emit \ud568\uc218 (5\ub2e8\uacc4 \ud30c\uc774\ud504\ub77c\uc778)
\u251c\u2500\u2500 runtime_context.py   # RuntimeContext (\ubc1c\uc2e0\uc790 \uc2dd\ubcc4)
\u251c\u2500\u2500 event_result.py      # EventResult (\uacb0\uacfc \ud45c\uc900)
\u2514\u2500\u2500 event_store.py       # DB \uc800\uc7a5 (business_event / integrity_event)
```

## \ud750\ub984

```
Runtime (workflow, notification, ui, ...)
  \u2502
  \u25bc
emit_runtime_event(ctx, event)
  \u2502
  \u251c\u2500 0. \uae30\ubcf8\uac12 \ubcf4\uc815 (trace_id, timestamp, source)
  \u251c\u2500 1. Validation (6\ub2e8\uacc4: naming, registry, severity, ownership, tenant, trace)
  \u251c\u2500 2. Sovereignty (truth_enforcer)
  \u251c\u2500 3. Event Store (business_event or integrity_event)
  \u2514\u2500 4. EventResult \ubc18\ud658
```

## \uc0ac\uc6a9\ubc95

```python
from watch_engine.runtime_bus import emit_runtime_event, make_context

ctx = make_context("workflow", tenant_id="tai", actor_id="user_001")

result = emit_runtime_event(ctx, {
    "event_type": "workflow.completed",
    "flow_key": "process_registration",
    "trace_id": "procreg_123",
    "severity": "INFO",
})

print(result.status)    # "accepted"
print(result.event_id)  # "uuid"
print(result.accepted)  # True
```

## \ucc28\ub2e8 \uc608\uc2dc

```python
# Notification\uc774 incident \uc0dd\uc131 \uc2dc\ub3c4 \u2192 blocked
ctx = make_context("notification")
result = emit_runtime_event(ctx, {
    "event_type": "incident.created",
    "severity": "CRITICAL",
    "tenant_id": "tai",
})
print(result.status)          # "blocked"
print(result.blocked_reason)  # "notification cannot emit incident.created"
```

## EventResult

| status | \uc758\ubbf8 |
|--------|------|
| `accepted` | \uc815\uc0c1 \uc800\uc7a5 |
| `accepted_with_warning` | \uc800\uc7a5\ub418\uc5c8\uc9c0\ub9cc warning \uc874\uc7ac |
| `blocked` | \uac80\uc99d \uc2e4\ud328\ub85c \uc800\uc7a5 \uac70\ubd80 |
| `failed` | \uc2dc\uc2a4\ud15c \uc624\ub958 |

## \uc6b0\ud68c \ubc29\uc9c0

| \uae08\uc9c0 | \ud5c8\uc6a9 |
|------|------|
| Runtime\uc774 \uc9c1\uc811 `business_event` INSERT | `emit_runtime_event()` \uacbd\uc720 |
| Runtime\uc774 \uc9c1\uc811 `integrity_event` INSERT | `emit_runtime_event()` \uacbd\uc720 |
| Notification\uc774 incident \uc0dd\uc131 | Control API \uacbd\uc720 |
| UI\uac00 severity \uc218\uc815 | Control API \uacbd\uc720 |

## Gateway \uc5f0\uacb0

```
POST /control-runtime/events
  \u2192 emit_runtime_event(gateway_ctx, event_payload)
  \u2192 EventResult \ubc18\ud658
```

## \uc810\uc9c4\uc801 \uc801\uc6a9 \ubc29\ud5a5

| Phase | \ub300\uc0c1 |
|:---:|------|
| 1 | \uc2e0\uaddc \ucf54\ub4dc\uc5d0\uc11c `emit_runtime_event` \uc0ac\uc6a9 |
| 2 | Gateway endpoint\uc5d0\uc11c \uc0ac\uc6a9 |
| 3 | \uae30\uc874 `emit_event` \ub0b4\ubd80\uc5d0\uc11c Bus \ud638\ucd9c |
| 4 | \uc9c1\uc811 INSERT \uc804\uba74 \uad50\uccb4 |
