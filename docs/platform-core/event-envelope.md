# Platform Core — Event Envelope Standard

## 목적
모든 엔진이 공유하는 이벤트 봉투 표준.
45CM과 TAI 공통.

---

## Event Envelope

```json
{
  "event_id": "uuid",
  "event_type": "<namespace>.<action>",
  "version": "1.0",
  "timestamp": "ISO-8601",
  "source": {
    "engine": "watch | marketing | workflow | tai",
    "service": "tai-api | 45cm-api",
    "environment": "production | staging | mock"
  },
  "tenant": {
    "tenant_id": "string",
    "factory_id": "uuid | null"
  },
  "actor": {
    "actor_id": "string",
    "actor_type": "user | system | scheduler | synthetic"
  },
  "trace": {
    "trace_id": "string",
    "flow_key": "string",
    "step_key": "string | null",
    "step_order": "int | null"
  },
  "payload": {},
  "metadata": {
    "idempotency_key": "string | null",
    "retry_count": 0,
    "priority": "P1 | P2 | P3 | P4",
    "ttl_seconds": 3600
  }
}
```

## 필수 필드

| 필드 | 필수 | 설명 |
|------|:---:|------|
| event_id | ✅ | UUID v4 |
| event_type | ✅ | `<namespace>.<action>` |
| version | ✅ | SemVer |
| timestamp | ✅ | UTC ISO-8601 |
| source.engine | ✅ | 엔진 식별 |
| source.service | ✅ | 서비스 식별 |
| source.environment | ✅ | 환경 |
| tenant.tenant_id | ✅ | 테넌트 |
| trace.trace_id | ✅ | 추적 ID |
| trace.flow_key | ✅ | 워크플로우 |
| payload | ✅ | 엔진별 자유 구조 |

## Namespace 규칙

```
<engine>.<domain>_<action>
```

예시:
- `watch.integrity_detected`
- `watch.alert_fired`
- `marketing.conversion_detected`
- `workflow.step_completed`
- `tai.regulation_violation`

## 금지 사항

- Platform Core Event에 엔진 도메인 의미 포함 금지
- `integrity`, `governance`, `escalation` 등은 Engine Domain
- Core는 envelope + routing + retry만 정의
