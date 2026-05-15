# Platform Entity Map — Engine Interaction

## 엔진 계층 (아래로 흐름)

```
[Service Layer]
  emit_event() → business_event
       │
[Event Layer]
  business_event 축적
       │
[Integrity Layer]
  Evaluator → 4 rules + SLA check
  → engine_integrity_event
       │
[Incident Layer]
  Priority Engine (P1~P4)
  Repeated Failure Detection
  Workflow Risk Score
       │
[Alert Layer]
  Alert Rule → Cooldown/Dedupe → Telegram
  → alert_history
       │
[Recovery Layer]
  Recovery Recommendation
  Action Log
       │
[Knowledge Layer]
  Pattern Updater (자동)
  Playbook Registry
  Recovery Effectiveness
       │
[Governance Layer]
  Tenant Impact
  Escalation (L1~L4)
       │
[Identity Layer]
  Actor Context
  Visibility Scope
  Audience Resolution
       │
[Cockpit]
  Founder Operations Control Surface
  18개 섹션 UI
```

## DB 테이블 (16개)

| 테이블 | 레이어 |
|--------|--------|
| business_event | Event |
| engine_integrity_event | Integrity |
| flow_registry | Workflow |
| flow_step_registry | Workflow |
| flow_integrity_rule_registry | Integrity |
| flow_scenario_binding | Workflow |
| alert_rule_registry | Alert |
| alert_history | Alert |
| browser_synthetic_registry | Synthetic |
| workflow_sla_registry | SLA |
| workflow_risk_registry | Incident |
| workflow_recovery_registry | Recovery |
| incident_action_log | Recovery |
| incident_pattern_registry | Knowledge |
| operational_playbook_registry | Knowledge |
| tenant_operational_registry | Governance |
| identity_role_registry | Identity |

## Scheduler (9개 direct job)

| Job | 주기 | 레이어 |
|-----|------|--------|
| INTEGRITY_EVALUATE | 5분 | Integrity |
| ALERT_EVALUATE | 5분 | Alert |
| SYNTHETIC_LOGIN | 5분 | Synthetic |
| SYNTHETIC_PROCESS_REG | 15분 | Synthetic |
| SYNTHETIC_BROWSER_LOGIN | 15분 | Browser |
| SYNTHETIC_BROWSER_PROCESS | 15분 | Browser |
| INCIDENT_REPEATED | 5분 | Incident |
| SYNTHETIC_CLEANUP | 매일 3시 | Synthetic |
| PATTERN_SYNC | 6시간 | Knowledge |

## Router (11개 Watch Engine)

| Router | 레이어 |
|--------|--------|
| watch_engine_api | Core + Cockpit |
| watch_engine_alert_api | Alert |
| watch_engine_browser_api | Browser Synthetic |
| watch_engine_sla_api | SLA |
| watch_engine_incident_api | Incident |
| watch_engine_recovery_api | Recovery |
| watch_engine_knowledge_api | Knowledge |
| watch_engine_memory_api | Knowledge (자동화) |
| watch_engine_governance_api | Governance |
| watch_engine_identity_api | Identity |

## Cockpit 섹션 (18개)

| # | 섹션 | 레이어 |
|---|------|--------|
| S1 | 건강 요약 | Core |
| S2 | 스케줄러 | Core |
| S3 | Synthetic Heartbeat | Synthetic |
| S4 | 실패 Top 플로우 | Integrity |
| S5 | 운영 이슈 (ACK/해결/무시) | Integrity |
| S6 | 알림 규칙 | Alert |
| S7 | 알림 이력 | Alert |
| S8 | Telegram 테스트 | Alert |
| S9 | 브라우저 감시 | Browser |
| S10 | 업무 SLA & 사용자 영향 | SLA |
| S11 | 인시던트 우선순위 | Incident |
| S12 | 워크플로우 위험도 | Incident |
| S13 | 인시던트 복구 대응 | Recovery |
| S14 | 반복 패턴 Top | Knowledge |
| S15 | 운영 플레이북 | Knowledge |
| S16 | 운영 메모리 & 안정성 | Knowledge |
| S17 | Tenant 거버넌스 | Governance |
| S18 | Identity & Visibility | Identity |
