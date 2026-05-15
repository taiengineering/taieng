# TAI Platform Grammar — Watch Engine / Notification Engine Boundary

작성일: 2026-05-15
프로젝트: 45cm / TAI Platform
목적: 관제엔진과 알림엔진 사이의 중복 언어를 정리하고, 플랫폼 공통 문법을 고정한다.

---

# 1. 정리 배경

Watch Engine과 Notification Engine을 각각 진행하면서 다음 개념들이 양쪽에서 중복 사용되기 시작했다.

- Event
- Workflow
- Incident
- Alert
- Notification
- Audience
- Visibility
- Governance
- Identity

이는 플랫폼이 커지며 자연스럽게 발생하는 현상이다. 하지만 소유권과 경계를 정리하지 않으면 같은 단어를 다른 의미로 쓰게 되고, 엔진 간 책임 충돌이 발생한다.

따라서 본 문서는 아래 원칙을 확정한다.

```text
Notification Engine은 판단하지 않는다.
Watch Engine은 전달하지 않는다.
Identity Core는 대상/가시성 기준을 제공한다.
```

---

# 2. Canonical Flow

플랫폼의 표준 흐름은 아래 순서를 따른다.

```text
Event
→ Workflow
→ Integrity
→ Incident
→ Alert
→ Notification
→ Audience
```

각 단계는 이전 단계의 결과를 소비하며, 자기 책임 범위 밖의 판단을 하지 않는다.

---

# 3. Core Ownership

| 개념 | 정의 | 소유 레이어 | 금지 영역 |
|---|---|---|---|
| Event | 발생 사실 | Core Event Layer | 정상/비정상 판단 금지 |
| Workflow | 의미 있는 Event Sequence | Workflow / Watch | 전달 대상 판단 금지 |
| Integrity | Workflow 정상성 판단 | Watch Engine | 메시지 발송 금지 |
| Incident | 운영 개입이 필요한 상태 | Watch Engine | 권한 정책 구현 금지 |
| Alert | Incident의 운영 승격 | Watch / Alert Rule | 채널 발송 직접 수행 금지 |
| Notification | 대상에게 전달하는 행위 | Notification Engine | Incident 생성/Severity 판단 금지 |
| Audience | 받을 대상 계산 | Identity Core / Notification 소비 | 운영 위험도 계산 금지 |
| Visibility | 볼 수 있는 범위 | Identity Core | Incident 우선순위 판단 금지 |
| Governance | 고객사/조직 운영 영향 | Watch Governance | 권한 정책 엔진 구현 금지 |

---

# 4. Watch Engine 책임

Watch Engine의 책임은 다음이다.

```text
업무 흐름이 정상인가?
운영 개입이 필요한가?
무엇을 먼저 봐야 하는가?
어떤 고객사가 영향을 받는가?
```

Watch Engine이 소유하는 영역:

- business_event 수집 규약
- workflow reconstruction
- integrity evaluation
- incident 생성
- priority/risk/stability 계산
- SLA 판단
- tenant impact/governance 계산
- recovery recommendation
- operational memory

Watch Engine이 하면 안 되는 것:

- Telegram/Email/SMS 직접 발송 정책 소유
- 수신자 채널 preference 관리
- read status 관리
- user inbox 운영
- role-based delivery policy 소유

---

# 5. Notification Engine 책임

Notification Engine의 책임은 다음이다.

```text
이미 판단된 Alert/Incident를
누구에게, 어떤 채널로, 언제, 어떻게 전달할 것인가?
```

Notification Engine이 소유하는 영역:

- channel routing
- delivery policy
- notification history
- delivery status
- retry / fallback
- quiet hour
- digest
- read status
- inbox
- escalation delivery

Notification Engine이 하면 안 되는 것:

- Incident 생성
- Severity 판단
- Workflow 정상성 판단
- SLA 계산
- Governance risk 계산
- Tenant impact 계산
- Stability score 계산
- 권한 정책 엔진 구현
- AI root cause 판단

---

# 6. Alert vs Notification Boundary

## Alert

Alert는 운영 중요도로 승격된 Incident/Event이다.

예:

```text
process_registration field_mismatch repeated 5회
login_browser sla_critical
workflow_instability P1
```

Alert의 본질:

```text
운영적으로 중요한가?
```

소유:

- Watch Engine / Alert Rule Layer

---

## Notification

Notification은 Alert를 실제 대상에게 전달하는 행위다.

예:

```text
platform_admin에게 Telegram 발송
tenant_admin에게 in-app 알림 생성
협력사 담당자에게 제한된 workflow 알림 발송
```

Notification의 본질:

```text
누구에게 어떻게 전달할 것인가?
```

소유:

- Notification Engine

---

# 7. Audience vs Visibility Boundary

## Audience

Audience는 “누가 받아야 하는가”이다.

예:

- platform_admin
- tenant_admin
- workflow_owner
- approver
- partner_user

Notification Engine은 Audience Resolution 결과를 소비한다.

---

## Visibility

Visibility는 “누가 볼 수 있는가”이다.

예:

- platform_admin: 전체 tenant visibility
- tenant_admin: 자기 tenant visibility
- tenant_user: 자기 workflow visibility
- synthetic_user: 일반 사용자 비노출

Visibility는 Identity Core가 소유한다.

---

# 8. Governance vs Identity Boundary

## Governance

Governance는 고객사/조직의 운영 영향도 판단이다.

예:

- tenant A = CRITICAL
- browser failure + SLA violation 동시 발생
- multi-workflow impact

소유:

- Watch Governance Layer

---

## Identity

Identity는 actor/role/scope/visibility 기준이다.

예:

- actor_type
- role_key
- tenant_id
- scope_type
- visible_tenants
- visible_incidents

소유:

- Identity Core Interface

Governance는 Identity를 사용하지만 직접 권한 정책을 구현하지 않는다.

---

# 9. Engine Interaction Standard

```text
1. Service emits Event
2. Workflow Layer reconstructs flow
3. Integrity Layer judges normality
4. Incident Layer creates operational issue
5. Alert Rule Layer decides escalation eligibility
6. Identity Core resolves audience/visibility
7. Notification Engine delivers message
8. Recovery/Knowledge layers record response/outcome
```

---

# 10. Naming Convention

## 공통 키

| 이름 | 용도 |
|---|---|
| event_type | 발생 사건 유형 |
| flow_key | 업무 흐름 식별자 |
| step_key | workflow step 식별자 |
| trace_id | 단일 flow 추적 ID |
| incident_id | 운영 이슈 ID |
| alert_rule_key | Alert 판단 규칙 |
| notification_id | 실제 전달 이력 |
| audience_key | 전달 대상 그룹 |
| actor_id | 행위자 ID |
| role_key | 역할 키 |
| tenant_id | 고객사/조직 범위 |

## 상태 값

- severity: INFO / WARNING / CRITICAL / FATAL
- priority: P1 / P2 / P3 / P4
- stability: STABLE / WATCH / UNSTABLE / CRITICAL
- tenant_status: HEALTHY / WATCH / RISK / CRITICAL
- recovery_classification: AUTO_RECOVERABLE / HUMAN_REQUIRED / INVESTIGATION_REQUIRED

---

# 11. 발견된 개념 충돌과 정리

## 충돌 1: Alert와 Notification 혼용

정리:

```text
Alert = 운영 중요도 승격
Notification = 실제 전달
```

## 충돌 2: Notification이 Severity를 판단하려는 경향

정리:

```text
Severity는 Watch/Incident 계층에서 판단한다.
Notification은 severity를 소비한다.
```

## 충돌 3: Governance와 Identity의 경계

정리:

```text
Governance = 고객 영향도
Identity = 볼 수 있는 범위/받을 수 있는 대상
```

## 충돌 4: Audience와 Visibility 혼용

정리:

```text
Audience = 받을 대상
Visibility = 볼 수 있는 범위
```

## 충돌 5: Recovery와 Notification의 혼용

정리:

```text
Recovery = 대응/조치
Notification = 대응 필요 사실 전달
```

---

# 12. 금지 규칙

## Notification Engine 금지

- Incident 생성 금지
- Severity 계산 금지
- SLA 판단 금지
- Tenant risk 계산 금지
- Workflow stability 계산 금지
- 권한 정책 직접 구현 금지

## Watch Engine 금지

- 사용자별 채널 preference 소유 금지
- Inbox/read status 소유 금지
- SMS/Email/Telegram delivery retry 정책 소유 금지

## Governance Layer 금지

- Identity policy 직접 구현 금지
- Notification channel routing 소유 금지

## Identity Layer 금지

- Incident priority 판단 금지
- SLA/Integrity 판단 금지

---

# 13. 최종 확정 문장

```text
Watch Engine decides what matters.
Identity Core decides who can see or receive it.
Notification Engine delivers it.
Recovery/Knowledge records what happened after.
```

한국어 기준:

```text
관제엔진은 무엇이 중요한지 판단한다.
아이덴티티 코어는 누가 볼 수 있고 받을 수 있는지 결정한다.
알림엔진은 그것을 전달한다.
복구/지식 레이어는 이후 대응과 결과를 기록한다.
```

이 문장을 플랫폼 문법의 기준으로 사용한다.
