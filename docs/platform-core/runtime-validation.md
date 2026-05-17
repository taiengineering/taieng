# Runtime Validation Layer

## \ubaa9\uc801

Canonical Event\ub97c \uc2e4\uc81c Runtime \uc218\uc900\uc5d0\uc11c \uac80\uc99d. \ubbf8\ub4f1\ub85d Event / \uc798\ubabb\ub41c Severity / Forbidden Mutation \ucc28\ub2e8.

## \uad6c\uc870

```
watch_engine/runtime_validation/
\u251c\u2500\u2500 __init__.py              # \ud328\ud0a4\uc9c0 export
\u251c\u2500\u2500 canonical_registry.py   # 39\uac1c Canonical Event + Ownership + Severity \uad8c\ud55c
\u251c\u2500\u2500 event_validator.py       # \ud1b5\ud569 \uac80\uc99d (6\ub2e8\uacc4)
\u2514\u2500\u2500 validation_errors.py     # 6\uac1c Error \ud074\ub798\uc2a4
```

## \uac80\uc99d 6\ub2e8\uacc4

| # | \uac80\uc99d | \uc2e4\ud328 \uc2dc |
|---|------|--------|
| 1 | \ud544\uc218 \ud544\ub4dc (event_type, tenant_id) | error |
| 2 | Naming (`<domain>.<action>` \uc18c\ubb38\uc790) | error |
| 3 | Canonical Registry \ub4f1\ub85d \uc5ec\ubd80 | warning |
| 4 | Severity \uc720\ud6a8\uc131 + Runtime \uad8c\ud55c | error |
| 5 | Runtime Event Ownership | error |
| 6 | Tenant Boundary (mock\u2192production \uae08\uc9c0) | error |

## \uc0ac\uc6a9\ubc95

```python
from watch_engine.runtime_validation import validate_event

# \uac80\uc99d \ud1b5\uacfc
result = validate_event(
    event={"event_type": "workflow.failed", "tenant_id": "tai", "severity": "CRITICAL"},
    runtime="control"
)
# {"valid": True, "errors": [], "warnings": ["trace_id is missing"]}

# \uac80\uc99d \uc2e4\ud328 \u2192 InvalidRuntimeEvent
result = validate_event(
    event={"event_type": "incident.created", "tenant_id": "tai", "severity": "CRITICAL"},
    runtime="notification"  # notification\uc740 incident \uc0dd\uc131 \ubd88\uac00
)
# \u2192 InvalidRuntimeEvent: notification cannot emit incident.created
```

## Error \ud074\ub798\uc2a4

| Error | \uc124\uba85 |
|-------|------|
| `InvalidRuntimeEvent` | \uae30\ubcf8 \uac80\uc99d \uc2e4\ud328 |
| `UnregisteredEventType` | \ubbf8\ub4f1\ub85d Event |
| `ForbiddenSeverityMutation` | Severity \uad8c\ud55c \uc704\ubc18 |
| `ForbiddenRuntimeMutation` | Runtime Event \uc0dd\uc131 \uad8c\ud55c \uc704\ubc18 |
| `InvalidTenantBoundary` | Tenant \uacbd\uacc4 \uc704\ubc18 |
| `InvalidTraceIntegrity` | Trace \ubb34\uacb0\uc131 \uc704\ubc18 |

## Violation \ub85c\uae45

\uac80\uc99d \uc2e4\ud328 \uc2dc:
1. `logger.warning` \ucd9c\ub825
2. `engine_integrity_event`\uc5d0 `watch.sovereignty_violation` \uc774\ubca4\ud2b8 \uae30\ub85d

## Gateway \uc5f0\uacb0 \ubc29\ud5a5

```
\uc678\ubd80 SaaS \u2192 Gateway \u2192 Validation Layer \u2192 Control Runtime
                         \u2502
                    \uc2e4\ud328 \uc2dc \uac70\ubd80 + violation \ub85c\uae45
```

\ud5a5\ud6c4 \ubaa8\ub4e0 Gateway \uc785\ub825\uc740 Validation \ud1b5\uacfc \ud544\uc218.
