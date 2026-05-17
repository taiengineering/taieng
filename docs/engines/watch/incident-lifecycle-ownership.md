# Incident Lifecycle Ownership

## 선언

Incident의 전체 생명주기는 **Control Runtime**이 독점 소유한다.

---

## Lifecycle

```
DETECTED → CREATED → ACKNOWLEDGED → INVESTIGATING → RESOLVED → CLOSED
                                          │
                                          ├─→ ESCALATED
                                          └─→ IGNORED
```

## 단계별 Ownership

| 단계 | Owner | 트리거 | 저장 위치 |
|------|:---:|--------|----------|
| DETECTED | Control | evaluator → integrity_event | engine_integrity_event |
| CREATED | Control | evaluator / repeated | engine_integrity_event |
| ACKNOWLEDGED | Control | UI → Control API | incident_action_log |
| INVESTIGATING | Control | operator action | incident_action_log |
| ESCALATED | Control | governance engine | tenant_operational_registry |
| RESOLVED | Control | UI → Control API | incident_action_log |
| IGNORED | Control | UI → Control API | incident_action_log |
| CLOSED | Control | auto (30일) / manual | incident_action_log |

## 핵심 규칙

1. **Incident 생성**: Control Runtime만 (evaluator.py, repeated.py)
2. **Severity 판정**: Control Runtime만 (rule-based)
3. **Escalation 판단**: Control Runtime만 (governance engine)
4. **ACK 요구**: Control Runtime이 `requires_ack=true` 설정
5. **ACK 완료**: UI가 Control API에 요청 → Control이 기록
6. **Resolution**: UI가 Control API에 요청 → Control이 기록
7. **Recovery 추천**: Control이 recovery_registry 기반으로 추천

## Notification의 역할 (Incident 관련)

| 허용 | 금지 |
|------|------|
| incident 생성 알림 발송 | incident 생성 |
| escalation 알림 발송 | escalation 판단 |
| ACK 요청 알림 | ACK 완료 판정 |
| resolution 알림 | resolution 판정 |
| 수신자 매핑 | severity 계산 |

## 현재 구현 현황

| 항목 | 구현 | 위치 |
|------|:---:|------|
| Incident 생성 | ✅ | evaluator.py, repeated.py |
| Severity 판정 | ✅ | rule-based (flow_integrity_rule_registry) |
| Escalation | ✅ | governance/__init__.py |
| ACK | ✅ | incident_action_log (watch_engine_api.py) |
| Resolution | ✅ | incident_action_log |
| Recovery 추천 | ✅ | recovery_registry (watch_engine_recovery_api.py) |
| Auto-close | ❌ | 미구현 (30일 규칙) |
| Notification projection | ✅ | alert_rule_registry → Telegram |

## 데이터 저장소

| 데이터 | 테이블 | Owner |
|--------|--------|:---:|
| Incident 원본 | engine_integrity_event | Control |
| 조치 이력 | incident_action_log | Control |
| 패턴 | incident_pattern_registry | Control |
| 복구 매핑 | workflow_recovery_registry | Control |
| 플레이북 | operational_playbook_registry | Control |
| 테넌트 위험도 | tenant_operational_registry | Control |
| 알림 이력 | alert_history | Notification (projection) |
