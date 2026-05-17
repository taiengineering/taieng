# Control Output Gateway

## \ubaa9\uc801

Control Runtime\uc774 \uc0dd\uc131\ud55c Operational Truth\ub97c \uc678\ubd80\uc5d0 \ud45c\uc900 \ubc29\uc2dd\uc73c\ub85c \ucd9c\ub825\ud558\ub294 \uacf5\uc2dd \ucd9c\uad6c.

---

## Output Stream

| Stream | \ub370\uc774\ud130 | Endpoint |
|--------|--------|----------|
| Incident | \uc0dd\uc131/\ud574\uacb0/\uc885\ub8cc | `GET /control-runtime/incidents` |
| Severity | \uc774\uc288 \uc2ec\uac01\ub3c4 | `GET /control-runtime/severity` |
| Escalation | \uc704\ud5d8 \uc0c1\ud5a5 | `GET /control-runtime/escalations` |
| Recovery | \ubcf5\uad6c \ucd94\ucc9c | `GET /control-runtime/recovery` |
| Status | \uc6b4\uc601 \uc0c1\ud0dc | `GET /control-runtime/status` |
| Stability | \uc548\uc815\uc131 | `GET /control-runtime/stability` |

## Output \ud615\uc2dd

```json
{
  "truth_source": "control_runtime",
  "output_type": "incident_stream",
  "tenant_id": "tenant_001",
  "timestamp": "2026-05-16T12:00:00Z",
  "data": [
    {
      "incident_id": "uuid",
      "event_type": "field_mismatch",
      "severity": "WARNING",
      "flow_key": "process_registration",
      "status": "CREATED",
      "requires_ack": true,
      "created_at": "..."
    }
  ]
}
```

## Output \uaddc\uce59

1. **Truth\ub9cc \ucd9c\ub825** \u2014 Projection/Formatting \ud3ec\ud568 \uae08\uc9c0
2. **truth_source: control_runtime** \ud56d\uc0c1 \ud3ec\ud568
3. **Tenant Boundary** \u2014 \uc694\uccad\ud55c tenant\uc758 \ub370\uc774\ud130\ub9cc \ubc18\ud658
4. **Pagination** \u2014 limit/offset \uc9c0\uc6d0
5. **Environment \ud544\ud130** \u2014 mock \uc81c\uc678 \uae30\ubcf8

## Output\uc5d0\uc11c \uae08\uc9c0\ub41c \uac83

| \uae08\uc9c0 | \uc774\uc720 |
|------|------|
| UI projection | Surface Runtime \uc5ed\ud560 |
| Notification formatting | Notification Runtime \uc5ed\ud560 |
| Digest aggregation | Notification Runtime \uc5ed\ud560 |
| Template rendering | Notification Runtime \uc5ed\ud560 |
| Delivery execution | Delivery Runtime \uc5ed\ud560 |

Output Gateway\ub294 \uc21c\uc218 Truth \ubc18\ud658\ub9cc. \uc18c\ube44\uc790\uac00 Projection\uc744 \uc218\ud589.

## \ud5a5\ud6c4 \ud655\uc7a5

| Phase | \ubc29\uc2dd | \uc124\uba85 |
|:---:|------|------|
| 1 | REST Pull | \uc678\ubd80\uac00 \uc8fc\uae30\uc801 \uc870\ud68c \u2705 |
| 2 | Webhook Push | \uc774\ubca4\ud2b8 \ubc1c\uc0dd \uc2dc \uc678\ubd80\uc5d0 \uc804\ub2ec |
| 3 | Streaming (SSE/WS) | \uc2e4\uc2dc\uac04 \uc2a4\ud2b8\ub9bc |
