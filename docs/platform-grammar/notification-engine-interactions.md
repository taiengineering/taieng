# Notification Engine Interactions

작성일: 2026-05-16

---

## 엔진간 관계

```
Watch Engine
  → Integrity Event 발생
  → Alert Rule 평가 (alert_rule_registry_v2)
  → Alert Event 생성 (workflow_alert_event)

Alert Layer
  → Notification Runtime으로 Event 전달

Workflow Engine
  → Workflow Event Contract
  → workflow_event_log INSERT
  → Notification Runtime으로 Event 전달

Identity Core
  → Audience/Visibility 계산
  → Recipient Resolution에 사용

Notification Engine
  → Event Intake
  → Recipient Resolution
  → Queue
  → Worker
  → Adapter
  → Audit

Recovery Layer (미구현)
  → Alert 해결 후 대응 기록

Knowledge Layer (미구현)
  → 장기 분석 기록
```

## Boundary 원칙

| 영역 | 책임 | Notification과의 관계 |
|---|---|---|
| Watch Engine | 무결성 감지 | Event 생성자 |
| Alert Layer | 운영 중요도 판단 | Event 생성자 |
| Workflow Engine | 상태 흐름 | Event 생성자 |
| Identity Core | 수신자 결정 | Recipient 공급자 |
| Notification Engine | 전달 | Delivery 전담 |

## 금지사항 (Notification Engine 내부)

- Incident 생성 금지
- Severity 계산 금지
- Governance 계산 금지
- Workflow 판단 금지
- SLA 계산 금지
- AI 판단 금지
