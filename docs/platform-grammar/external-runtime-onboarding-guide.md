# External Runtime Onboarding Guide

작성일: 2026-05-17
범위: 외부 Runtime 연결 절차

---

## 7단계 연결 절차

### Step 1: Taxonomy 등록

`operational-event-taxonomy-v2.md`에 카테고리 + truth_source 확인.
없으면 신규 카테고리 등록.

### Step 2: event_type 등록

명명 규칙: `{noun}_{past_participle}` (snake_case)
예: `payment_failed`, `inspection_completed`

### Step 3: Audience Mapping

`default-audience-matrix.md`에 기본 audience + fallback 정의.

### Step 4: Policy 연결

`notification_policy_registry`에서 기존 policy 재사용 또는 신규 등록.
필수: channel, severity, cooldown, quiet_hour_bypass.

### Step 5: Wiring 연결

`notification_event_wiring_registry`에 INSERT:
```sql
INSERT INTO notification_event_wiring_registry
(wiring_key, event_type, source_engine, enabled,
 notification_policy_key, audience_key)
VALUES ('WIRE_YOUR_EVENT', 'your_event_type', 'your_runtime',
 true, 'POLICY_KEY', 'audience_key');
```

### Step 6: Emit Test

```python
from services.notification_engine.event_wiring import wire_and_emit

await wire_and_emit(
    event_type="your_event_type",
    payload={"title": "테스트", "body": "테스트 내용"}
)
```

또는 API: `POST /notification-engine/wirings/test`

### Step 7: Operational Validation

- Queue 생성 확인 (`/notification-engine/queue-status`)
- Timeline 확인 (`/notification-engine/timeline/{trace_id}`)
- Feed 확인 (IN_APP 채널인 경우)

---

## 필수 규칙

- Operational Event Contract 준수
- Legacy direct send 금지 (wire_and_emit 전용)
- try/except 감싸기 (실패 시 기존 로직 영향 없음)
