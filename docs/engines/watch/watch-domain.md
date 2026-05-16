# Watch Engine — Domain Definition

## 정의

**Watch Engine** = Business Workflow Integrity Engine

Platform Core 위에서 동작하는 운영 관제 엔진.
Platform Core 자체가 **아님**.

## Namespace

`watch.*`

## Domain 개념

| 개념 | Event Type | 설명 |
|------|-----------|------|
| Integrity | `watch.integrity_detected` | 워크플로우 무결성 이슈 |
| Incident | `watch.incident_created` | 운영 이슈 생성 |
| Governance | `watch.tenant_risk_changed` | 테넌트 위험도 변경 |
| Recovery | `watch.recovery_recommended` | 복구 추천 |
| Alert | `watch.alert_fired` | 알림 발송 |
| Escalation | `watch.escalation_triggered` | 위험 상향 |
| Synthetic | `watch.synthetic_completed` | 합성 테스트 완료 |
| Pattern | `watch.pattern_detected` | 패턴 탐지 |
| Stability | `watch.stability_changed` | 안정성 변경 |
| SLA | `watch.sla_violated` | SLA 위반 |

## Engine Interface 구현 현황

| 항목 | 상태 |
|------|:---:|
| Namespace | `watch` ✅ |
| Event Envelope | 부분 준수 (확장 필요) |
| Tenant Isolation | ✅ (environment 필터) |
| Idempotency | ✅ (trace+event_type dedupe) |
| Retry | ✅ (scheduler retry) |
| Health Check | ✅ (`/watch-engine/cockpit/health`) |
| Priority | ✅ (P1~P4 Priority Engine) |

## 현재 규모

| 항목 | 수량 |
|------|:---:|
| DB 테이블 | 24 |
| 라우터 | 13 |
| Scheduler Job | 9 |
| Cockpit 섹션 | 18 |
| Admin 페이지 | 6 |
| Semantic Adapter | 22 mappings |

## Platform Core 의존성

```
Watch Engine
  └── Platform Core
       ├── Event Envelope (trace_id, flow_key, tenant_id)
       ├── Tenant Isolation (environment filter)
       ├── Priority (P1~P4)
       ├── Retry (scheduler-based)
       └── Idempotency (trace+type dedupe)
```

Watch가 Core에 추가하는 것:
- integrity/incident/governance = **Watch Domain**
- escalation/recovery/pattern = **Watch Domain**
- alert/synthetic = **Watch Domain**

이들은 Core에 포함되지 않음.
