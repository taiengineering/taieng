# External Runtime Contract & Tenant Boundary

## \uc678\ubd80 Runtime\uc774 \uc54c\uc544\uc57c \ud558\ub294 \uac83

| \ud544\uc694 | \ubd88\ud544\uc694 |
|------|--------|
| Event Envelope \ud615\uc2dd | DB schema |
| Workflow Event Type | governance logic |
| API Key \uc778\uc99d | recovery internals |
| Tenant Boundary | notification internals |
| Severity \ub808\ubca8 (INFO/WARNING/CRITICAL) | alert rule \uc124\uc815 |

## Tenant Boundary

\ubaa8\ub4e0 \uc678\ubd80 \uc694\uccad\uc5d0 \ud544\uc218:

```json
{
  "tenant_id": "tenant_001",
  "environment": "production"
}
```

\uaddc\uce59:
- API Key\ub294 tenant\uc5d0 \ubc14\uc778\ub529
- \uc694\uccad tenant \u2260 \uc778\uc99d tenant \uc2dc **403 Forbidden**
- cross-tenant \uc870\ud68c **\uae08\uc9c0**
- mock tenant\ub294 production \uae30\ub85d **\uae08\uc9c0**

## SDK \ubc29\ud5a5 (\ud5a5\ud6c4)

| Phase | SDK | \uc124\uba85 |
|:---:|------|------|
| 1 | REST API | \ud604\uc7ac \u2705 |
| 2 | JS SDK | `controlRuntime.emit({...})` |
| 3 | Python SDK | `control.emit(event_type=..., tenant_id=...)` |
| 4 | Go SDK | `control.Emit(ctx, event)` |

\ubaa9\ud45c: **\uc2a4\ud06c\ub9bd\ud2b8 1\uac1c \ub610\ub294 SDK 3\uc904**\ub85c \uad00\uc81c\uc5d4\uc9c4 \uc5f0\uacb0 \uac00\ub2a5.

## \ub0b4\ubd80 \ub178\ucd9c \uae08\uc9c0

\uc678\ubd80\uc5d0 \uc808\ub300 \ub178\ucd9c\ud558\uc9c0 \uc54a\ub294 \uac83:

| \uae08\uc9c0 | \uc774\uc720 |
|------|------|
| DB schema / table \uad6c\uc870 | \ub0b4\ubd80 \uad6c\ud604 |
| governance \ub85c\uc9c1 | Runtime Sovereignty |
| recovery \ub0b4\ubd80 | Runtime Sovereignty |
| notification \ub0b4\ubd80 | Runtime Sovereignty |
| scheduler \ub0b4\ubd80 | Runtime Sovereignty |
| RLS \uc815\ucc45 | \ubcf4\uc548 |
| service_role key | \ubcf4\uc548 |
| \ub0b4\ubd80 trace \uad6c\uc870 | \ub0b4\ubd80 \uad6c\ud604 |

## \uc5f0\ub3d9 \ud750\ub984 \uc694\uc57d

```
\uc678\ubd80 SaaS
  \u2502
  \u251c\u2500\u2500 Event Push \u2192 POST /control-runtime/events
  \u251c\u2500\u2500 Heartbeat  \u2192 POST /control-runtime/heartbeat
  \u2502
  \u2502         Control Runtime (\ub0b4\ubd80)
  \u2502         \u251c\u2500 Evaluate \u2192 Integrity \u2192 Incident \u2192 Alert
  \u2502         \u2514\u2500 Governance \u2192 Stability \u2192 Recovery
  \u2502
  \u251c\u2500\u2500 Incident Read \u2192 GET /control-runtime/incidents
  \u2514\u2500\u2500 Status Read  \u2192 GET /control-runtime/status
```
