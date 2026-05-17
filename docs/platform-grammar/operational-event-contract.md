# Operational Event Contract

작성일: 2026-05-17
범위: 외부 Runtime → Notification Runtime 연결 표준

---

## 선언

**Notification Runtime은 Operational Event만 소비한다.**

---

## 필수 필드

| 필드 | 유형 | 필수 | 설명 |
|---|---|---|---|
| event_type | string | ✅ | 이벤트 유형 (e.g. `payment_failed`) |
| truth_source | string | ✅ | 발생 주체 Runtime (e.g. `billing`, `control`) |
| severity_snapshot | string | ✅ | CRITICAL / WARNING / INFO (Control 제공 또는 Policy default) |
| trace_id | string | ✅ | 추적 ID |
| occurred_at | datetime | ✅ | 이벤트 발생 시간 |
| payload | dict | ✅ | 이벤트 데이터 (title, body, company_id 등) |
| incident_ref | string? | ❌ | 연관 사고 ID (Control 제공) |
| audience_key | string? | ❌ | 수신 대상 힌트 (Wiring 기본값 사용) |
| requires_ack | boolean? | ❌ | ACK 필수 여부 |
| delivery_hint | dict? | ❌ | 채널/우선순위 힌트 |

---

## 현재 매핑

```python
await wire_and_emit(
    event_type="payment_failed",       # 필수
    payload={                           # 필수
        "title": "결제 실패",
        "body": "결제가 실패했습니다.",
        "company_id": "uuid",
        "truth_source": "billing",    # payload 내부
        "occurred_at": "2026-05-17T...",
    },
    override_severity="WARNING",        # severity_snapshot
)
```

---

## 규칙

1. **event_type은 Taxonomy 준수** — `{category}_{past_participle}`
2. **truth_source는 발생 주체** — billing/control/workflow/safety
3. **severity_snapshot은 읽기 전용** — Notification이 수정 금지
4. **payload.title + payload.body 필수** — 사용자 표시 메시지
