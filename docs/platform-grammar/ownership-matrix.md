# Canonical Ownership Matrix

플랫폼 전체 개념의 소유 엔진 정의.
"누가 무엇을 소유하는가."

---

## Entity Ownership

| 개념 | 소유 엔진 | 소유 테이블 | 금지 |
|------|----------|------------|------|
| Business Event | Event Layer | `business_event` | 판단 금지 (기록만) |
| Flow Definition | Workflow Layer | `flow_registry`, `flow_step_registry` | 실행 금지 (기준만) |
| Integrity Rule | Integrity Layer | `flow_integrity_rule_registry` | 수동 생성 금지 (Evaluator만) |
| Integrity Event | Integrity Layer | `engine_integrity_event` | Notification에서 생성 금지 |
| Alert Rule | Alert Layer | `alert_rule_registry` | Notification에서 변경 금지 |
| Alert History | Alert Layer | `alert_history` | 발송 결과만 기록 |
| SLA Definition | SLA Layer | `workflow_sla_registry` | Notification에서 계산 금지 |
| Incident Priority | Incident Layer | (runtime 계산) | Notification에서 계산 금지 |
| Repeated Failure | Incident Layer | (runtime 탐지) | Notification에서 생성 금지 |
| Workflow Risk | Incident Layer | `workflow_risk_registry` | Notification에서 점수 계산 금지 |
| Recovery Recommendation | Recovery Layer | `workflow_recovery_registry` | 자동 실행 금지 |
| Action Log | Recovery Layer | `incident_action_log` | Notification에서 생성 가능 (delivery 조치만) |
| Pattern | Knowledge Layer | `incident_pattern_registry` | Notification에서 갱신 금지 |
| Playbook | Knowledge Layer | `operational_playbook_registry` | Notification에서 수정 금지 |
| Tenant Impact | Governance Layer | `tenant_operational_registry` | Notification에서 계산 금지 |
| Escalation | Governance Layer | (runtime 계산) | Notification에서 판단 금지 |
| Actor Context | Identity Layer | `identity_role_registry` | Notification에서 변경 금지 |
| Visibility | Identity Layer | (runtime 해석) | Notification에서 정책 구현 금지 |
| Audience | Identity Layer | `resolve_notification_audience()` | Notification은 **소비만** |
| Delivery | Notification Layer | `alert_history` (현재) | 판단 금지, 전달만 |

---

## Cross-Engine 규칙

1. **단방향 의존**: 상위 → 하위만 참조 (Event → Integrity → Incident → Alert → Notification)
2. **역참조 금지**: Notification → Incident 생성 금지
3. **Audience 소비**: Identity가 계산, Notification이 소비
4. **Governance 소비**: Governance가 계산, Cockpit이 표시
5. **Recovery 소비**: Recovery가 추천, 운영자가 실행, Notification이 알림
