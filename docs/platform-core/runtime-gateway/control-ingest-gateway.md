# Control Ingest Gateway

## 목적

외부 SaaS / 외부 시스템이 Control Runtime에 표준 방식으로 이벤트를 전달하는 공식 입구.

---

## Endpoint

| Method | Path | 설명 |
|--------|------|------|
| POST | `/control-runtime/events` | 표준 Event 전달 |
| POST | `/control-runtime/workflows` | Workflow 상태 전달 |
| POST | `/control-runtime/heartbeat` | 서비스 생존 신호 |
| GET | `/control-runtime/health` | 관제엔진 상태 확인 |

## Event Push (\ud45c\uc900 \uc785\ub825)

```json
POST /control-runtime/events
{
  "event_type": "workflow.step_failed",
  "version": "1.0",
  "tenant_id": "tenant_001",
  "trace_id": "trace_abc",
  "flow_key": "signup",
  "step_key": "payment",
  "severity": "WARNING",
  "timestamp": "2026-05-16T12:00:00Z",
  "source": {
    "engine": "external",
    "service": "partner-saas",
    "environment": "production"
  },
  "payload": {
    "error_code": "TIMEOUT",
    "duration_ms": 30500
  }
}
```

\uc751\ub2f5:
```json
{"status": "accepted", "event_id": "uuid", "trace_id": "trace_abc"}
```

## Input \ubc29\uc2dd 3\uac00\uc9c0

| \ubc29\uc2dd | \uc124\uba85 | Phase |
|------|------|:---:|
| **Event Push** | \uc678\ubd80 SaaS \u2192 REST API \u2192 Control | Phase 1 \u2705 |
| **Pull Observation** | Control \u2192 \uc678\ubd80 API \uc870\ud68c \u2192 \uc774\ubca4\ud2b8 \uc0dd\uc131 | Phase 2 |
| **Synthetic Observation** | Control \u2192 Browser/API \uc9c1\uc811 \uad00\ucc30 | Phase 1 \u2705 |

\ud604\uc7ac TAI\ub294 Phase 1 (Synthetic + \ub0b4\ubd80 Event Push) \uc6b4\uc601 \uc911.

## \ud544\uc218 \ud544\ub4dc

| \ud544\ub4dc | \ud544\uc218 | \uac80\uc99d |
|------|:---:|------|
| event_type | \u2705 | `<namespace>.<action>` \ud615\uc2dd |
| tenant_id | \u2705 | \ube44\uc5b4\uc788\uc73c\uba74 \uac70\ubd80 |
| trace_id | \u2705 | \ube44\uc5b4\uc788\uc73c\uba74 \uc790\ub3d9 \uc0dd\uc131 |
| flow_key | \u2705 | Workflow \uc2dd\ubcc4 |
| severity | \u2705 | INFO / WARNING / CRITICAL |
| timestamp | \u2705 | UTC ISO-8601 |
| source.service | \u2705 | \ucd9c\ucc98 \uc2dd\ubcc4 |

## \ubcf4\uc548

- API Key \uc778\uc99d (\ud5e4\ub354: `X-Control-API-Key`)
- Tenant Boundary \uac80\uc99d (\uc694\uccad tenant \u2260 \uc778\uc99d tenant \uc2dc \uac70\ubd80)
- Rate limit: 100 events/\ubd84/tenant
- \ud658\uacbd \uac80\uc99d: mock event\ub294 production\uc5d0 \uae30\ub85d \uae08\uc9c0

## Idempotency

- `idempotency_key` \ud544\ub4dc \uc120\ud0dd
- \uc5c6\uc73c\uba74 `trace_id + event_type + step_key` \uc870\ud569\uc73c\ub85c \uc790\ub3d9 \uc0dd\uc131
- 24\uc2dc\uac04 \ub0b4 \ub3d9\uc77c key \uc911\ubcf5 \uc774\ubca4\ud2b8 \ubb34\uc2dc
