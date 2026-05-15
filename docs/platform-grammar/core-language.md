# TAI Platform Grammar — Core Language

플랫폼 공통 문법. 모든 엔진이 이 언어를 사용한다.

---

## Core Entities

| Entity | 정의 | 예시 |
|--------|------|------|
| **Event** | 업무 흐름의 단일 행위 기록 | 로그인 시도, 공정 저장 |
| **Workflow (Flow)** | 연속된 Step으로 구성된 업무 흐름 | login, process_registration |
| **Trace** | 하나의 Flow 실행 단위 (trace_id) | login_abc123 |
| **Step** | Flow 내 개별 행위 | input_email, click_submit |
| **Integrity** | Event/Flow의 정합성 판단 | field_mismatch, stuck_detected |
| **Incident** | 운영 대응이 필요한 이슈 | P1 sla_critical |
| **Alert** | 운영자에게 전달되는 알림 | Telegram 발송 |
| **Notification** | Alert의 실제 전달 (채널+대상) | Telegram → founder |
| **Audience** | 알림 수신 대상 그룹 | platform_admin, tenant_admin |
| **Governance** | 조직/Tenant 운영 영향 관리 | Tenant stability, escalation |
| **Identity** | 행위자 역할/권한/가시성 | platform_admin, tenant_user |
| **Visibility** | 행위자가 볼 수 있는 범위 | platform, tenant, self |
| **Recovery** | 이슈 대응/복구 추천 | CHECK_SELECTOR_MAPPING |
| **Knowledge** | 운영 경험 축적 (패턴/플레이북) | 반복 패턴, 해결 성공률 |
| **Stability** | 워크플로우/조직 안정성 | STABLE, WATCH, UNSTABLE, CRITICAL |
| **SLA** | 업무 완료 시간 기준 | login 3초 warning, 10초 critical |
| **Tenant Impact** | 고객사 영향도 | HEALTHY, WATCH, RISK, CRITICAL |

---

## Shared Naming Convention

| 범주 | 규칙 | 예시 |
|------|------|------|
| flow_key | snake_case | `login`, `process_registration_browser` |
| step_key | snake_case | `input_email`, `click_submit` |
| trace_id | flow + unique | `login_abc123` |
| event_type | snake_case | `field_mismatch`, `sla_critical` |
| role_key | snake_case | `platform_admin`, `tenant_user` |
| pattern_key | flow::event_type | `login::stuck_detected` |
| playbook_key | pb_ prefix | `pb_field_mismatch` |
| rule_key | alert_ prefix | `alert_stuck_critical` |

### Severity (심각도)
`INFO` → `WARNING` → `CRITICAL`

### Priority (우선순위)
`P1` (즉시) → `P2` (다음 점검) → `P3` (모니터링) → `P4` (무시 가능)

### Stability (안정성)
`STABLE` → `WATCH` → `UNSTABLE` → `CRITICAL`

### Tenant Status
`HEALTHY` → `WATCH` → `RISK` → `CRITICAL`

### Escalation Level
`L1` (단일 이슈) → `L2` (반복 SLA) → `L3` (복합 장애) → `L4` (다중 CRITICAL)

### Recovery Classification
`AUTO_RECOVERABLE` | `HUMAN_REQUIRED` | `INVESTIGATION_REQUIRED`

### Actor Types
`platform_admin` | `tenant_admin` | `tenant_user` | `partner_user` | `synthetic_user` | `system_actor`

### Connector Types
`api` | `browser` | `scheduler` | `system`

---

## Flow Status Lifecycle

```
running → completed (정상 완료)
       → failed (terminal failure step 도달)
       → stuck (stuck_threshold 초과, terminal 미도달)
       → abandoned (장기 방치)
```

## Issue Lifecycle

```
ACTIVE → ACKNOWLEDGED → RESOLVED
      → IGNORED
```
