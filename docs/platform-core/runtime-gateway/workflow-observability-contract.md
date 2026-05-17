# Workflow Observability Contract

## \ubaa9\uc801

\uc678\ubd80 SaaS\uac00 Workflow \uc0c1\ud0dc\ub97c Control Runtime\uc5d0 \uc804\ub2ec\ud558\ub294 \ud45c\uc900.
\uad00\uc81c\uc5d4\uc9c4\uc758 \ud575\uc2ec\uc740 **\ud750\ub984(Flow)\uc744 \uc774\ud574\ud558\ub294 \ub2a5\ub825**.

---

## Workflow Event Type

| Event Type | \uc124\uba85 | Severity |
|-----------|------|:---:|
| `workflow.started` | \uc6cc\ud06c\ud50c\ub85c\uc6b0 \uc2dc\uc791 | INFO |
| `workflow.step_started` | \ub2e8\uacc4 \uc2dc\uc791 | INFO |
| `workflow.step_completed` | \ub2e8\uacc4 \uc644\ub8cc | INFO |
| `workflow.step_failed` | \ub2e8\uacc4 \uc2e4\ud328 | WARNING |
| `workflow.blocked` | \ub2e8\uacc4 \ucc28\ub2e8/\ub300\uae30 | WARNING |
| `workflow.timeout` | \uc2dc\uac04 \ucd08\uacfc | WARNING |
| `workflow.completed` | \uc6cc\ud06c\ud50c\ub85c\uc6b0 \uc644\ub8cc | INFO |
| `workflow.failed` | \uc6cc\ud06c\ud50c\ub85c\uc6b0 \uc2e4\ud328 | CRITICAL |

## Event \uad6c\uc870

```json
{
  "event_type": "workflow.step_failed",
  "tenant_id": "tenant_001",
  "trace_id": "trace_signup_123",
  "flow_key": "signup",
  "step_key": "payment",
  "step_order": 3,
  "severity": "WARNING",
  "timestamp": "2026-05-16T12:00:00Z",
  "source": {
    "service": "partner-saas",
    "environment": "production"
  },
  "payload": {
    "error": "payment_timeout",
    "duration_ms": 30000,
    "retry_count": 2
  }
}
```

## \ud544\uc218 \ud544\ub4dc

| \ud544\ub4dc | \ud544\uc218 | \uc124\uba85 |
|------|:---:|------|
| flow_key | \u2705 | \uc6cc\ud06c\ud50c\ub85c\uc6b0 \uc2dd\ubcc4 |
| trace_id | \u2705 | \uc2e4\ud589 \ucd94\uc801 ID (\ub3d9\uc77c flow\uc758 \ub3d9\uc77c \uc2e4\ud589) |
| step_key | \uc120\ud0dd | \ub2e8\uacc4 \uc2dd\ubcc4 |
| step_order | \uc120\ud0dd | \ub2e8\uacc4 \uc21c\uc11c |

## Control Runtime\uc774 \ud558\ub294 \uc77c

\uc678\ubd80 Workflow Event \uc218\uc2e0 \uc2dc:

1. **Event \uae30\ub85d** \u2192 business_event
2. **Integrity \ud3c9\uac00** \u2192 \uaddc\uce59 \uae30\ubc18 \ubb34\uacb0\uc131 \uac80\uc99d
3. **Anomaly \ud0d0\uc9c0** \u2192 timeout, stuck, mismatch
4. **Incident \uc0dd\uc131** \u2192 \uc784\uacc4\uac12 \ucd08\uacfc \uc2dc
5. **Alert \ubc1c\uc1a1** \u2192 \uaddc\uce59 \ub9e4\uce6d \uc2dc
6. **Governance \ubc18\uc601** \u2192 tenant impact \uc7ac\uacc4\uc0b0

\uc678\ubd80 SaaS\ub294 \uc774 \uacfc\uc815\uc744 \uc54c \ud544\uc694 \uc5c6\uc74c. Event\ub9cc \uc804\ub2ec\ud558\uba74 \ub428.

## \ucd5c\uc18c \uc5f0\ub3d9 \uc608\uc2dc (\uc2a4\ud06c\ub9bd\ud2b8 3\uc904)

```javascript
// \ucd5c\uc18c \uc5f0\ub3d9: workflow step \uc2e4\ud328 \uc2dc \uad00\uc81c\uc5d0 \uc804\ub2ec
await fetch('https://api.taieng.co.kr/control-runtime/events', {
  method: 'POST',
  headers: {'Content-Type': 'application/json', 'X-Control-API-Key': API_KEY},
  body: JSON.stringify({
    event_type: 'workflow.step_failed',
    tenant_id: 'my_tenant',
    trace_id: `trace_${Date.now()}`,
    flow_key: 'checkout',
    step_key: 'payment',
    severity: 'WARNING',
    timestamp: new Date().toISOString(),
    source: {service: 'my-saas', environment: 'production'},
    payload: {error: 'timeout'}
  })
});
```
