# Event Wiring Boundary

작성일: 2026-05-17
범위: Notification Engine · Wiring Layer

---

## 정의

Wiring은 **연결**이다.

이벤트를 정책에 연결하고, 정책을 전달에 연결하는 것.

---

## 허용

- event_type → policy_key 매핑
- audience_key 결정
- cooldown 오버라이드
- escalation 활성화 여부
- digest 활성화 여부
- channel/severity 오버라이드 (wire_and_emit 파람)

---

## 금지

| 항목 | 이유 |
|---|---|
| Event 의미 해석 | Wiring은 routing만 담당 |
| Incident 생성 | Incident은 별도 시스템 |
| Governance 판단 | 위험 평가는 Watch Engine 영역 |
| Workflow 상태 변경 | Wiring은 read-only |
| Severity 계산 | severity는 Event source에서 결정 |

---

## 흐름

```
Event Source (Watch/Workflow/SLA)
  → event_type 발생
  → Event Wiring Service
  → wiring registry lookup
  → policy resolve
  → wire_and_emit()
  → Notification Pipeline
  → Queue → Worker → Adapter → Feed
```
