# TAI Runtime Engineization Progress Report

작성일: 2026-05-19
상태: Runtime Candidate Projection Engineization 진행중

---

# 1. 목적

초기 TAI Safe Runtime 구조는:

```text
법령진단
→ runtime_task 즉시 생성
→ Cockpit 표시
```

구조였다.

하지만 실제 산업 운영 흐름에서는:

- 안전관리자의 검토
- 반복주기 지정
- 담당자 지정
- 점검항목 수정
- 제외 처리

단계가 존재한다.

따라서 Runtime Projection Layer를:

```text
Engine Result
→ Candidate Projection
→ Activation
→ Runtime
```

구조로 재설계하였다.

---

# 2. 핵심 구조 변화

## BEFORE

```text
Legal Engine
→ runtime_task 생성
→ runtime_schedule 생성
→ Cockpit 표시
```

문제:

- 사람 승인 없음
- 운영 기준 확정 없음
- 엔진과 Runtime 결합
- Safe 전용 구조
- 법령 결과가 곧 운영 Runtime이 되는 구조

---

## AFTER

```text
Legal Engine
→ RuntimeCandidateInput
→ Binding Engine
→ runtime_candidate 생성
→ 점검항목관리
→ Activation
→ runtime_task/runtime_schedule 생성
→ Cockpit 표시
```

핵심:

- Candidate Layer 분리
- Activation Layer 분리
- Runtime Layer 분리
- Cockpit 역할 분리
- Binding Engine 독립화

---

# 3. Runtime Layer 구조

## Engine Layer

- legal
- document
- notification
- marketing
- watch
- member

↓

## Runtime Contract Layer

- EventEnvelope
- RuntimeCandidateInput
- RuntimeCandidateProjection
- RuntimeActivationContract
- RuntimeGovernanceContract
- RuntimeCapabilityContract

↓

## Binding Engine

역할:

```text
Engine Output
→ Operational Candidate Projection
```

중요:

runtime_task 직접 생성 금지.

---

## Candidate Layer

테이블:

- runtime_candidate
- runtime_candidate_document_requirement
- runtime_candidate_evidence_requirement
- runtime_candidate_schedule
- runtime_candidate_dependency
- runtime_candidate_residual

상태:

- projected
- pending_review
- approved
- rejected
- activated

---

## Activation Layer

안전관리자/운영자가:

- 담당자 지정
- 반복주기 지정
- 점검항목 수정
- 우선순위 수정
- 사용 여부 결정

수행 후:

```text
candidate
→ runtime_task
→ runtime_schedule
```

생성.

---

## Runtime Layer

운영 중 Runtime:

- runtime_task
- runtime_schedule
- runtime_dependency
- runtime_document_requirement
- runtime_evidence_requirement
- runtime_event_log

---

## Cockpit

Cockpit은:

```text
Activated Runtime Viewer
```

역할만 수행.

Candidate 표시 금지.

---

# 4. Candidate / Runtime 역할 분리

## 점검항목관리

역할:

- candidate 검토
- 반복주기 지정
- 담당자 지정
- activation

즉:

```text
운영 확정 전 단계
```

---

## Cockpit

역할:

- overdue
- completeness
- timeline
- 운영 상태

즉:

```text
운영 중 Runtime 상태 표시
```

---

# 5. Canonical Runtime Contract

## RuntimeCandidateInput

핵심 필드:

- candidate_id
- candidate_type
- title
- description
- source_engine
- source_event_id
- source_ref_id
- tenant_id
- facility_id
- trace_id
- payload
- source_trace

---

## CanonicalRuntimePayload

4계층 구조:

```json
{
  "core": {},
  "domain": {},
  "runtime": {},
  "governance": {}
}
```

목적:

- domain 자유도 유지
- runtime/governance 공통화
- cross-engine interoperability 확보

---

## RuntimeActivationContract

activation_mode:

- manual
- automatic
- delegated
- conditional

assignment_strategy:

- user
- team
- facility
- auto-routing

---

## RuntimeGovernanceContract

governance_level:

- passive
- standard
- strict
- critical

기능:

- escalation
- retry
- digest
- throttling
- storm protection
- replay
- integrity validation

---

## RuntimeCapabilityContract

예:

```json
{
  "runtime_overdue": true,
  "advanced_governance": false,
  "digest": true
}
```

목적:

- 인앱 과금
- capability enablement
- tenant runtime isolation

---

# 6. Runtime Taxonomy

정의 완료 category:

- inspection
- permit
- report
- training
- appointment
- compliance_check
- notification_action
- marketing_action
- governance_action
- recovery_action
- approval_action
- review_action
- evidence_collection
- document_submission
- workflow_action

목적:

TAI 전체 엔진의 Runtime 공통 언어 정의.

---

# 7. Event Taxonomy

정의 완료:

- runtime.candidate_projected
- runtime.candidate_approved
- runtime.candidate_activated
- runtime.task_created
- runtime.schedule_created
- runtime.schedule_overdue
- watch.escalation_triggered
- watch.runtime_recovered
- watch.storm_detected
- runtime.capability_enabled

모든 이벤트:

- EventEnvelope 기반
- tenant_id 필수
- trace_id 필수

---

# 8. 현재 완료 상태

| 영역 | 상태 |
|---|---|
| Runtime Candidate Layer | 완료 |
| Activation Layer | 완료 |
| Cockpit 분리 | 완료 |
| Runtime 분리 | 완료 |
| Binding Engine 분리 | 완료 |
| Safe coupling 감소 | 완료 |
| 법령 coupling 감소 | 완료 |
| Canonical Contract 정의 | 완료 |
| Taxonomy 정의 | 완료 |
| Event Taxonomy 정의 | 완료 |
| Capability Contract 정의 | 완료 |
| Governance Contract 정의 | 완료 |

---

# 9. 현재 남은 이슈

## 1. Hard Contract Enforcement 미적용

현재 Runtime 일부는:

```python
payload: dict
```

기반.

CanonicalRuntimePayload 강제 적용 시:

- legacy payload
- old event replay
- hidden coupling
- UI payload mismatch

문제 가능.

현재 전략:

```text
Loose Contract
+ Strong Boundary
```

유지.

---

## 2. Activation Contract 실적용 미완료

현재 activation 일부는 단순 파라미터 기반.

향후:

RuntimeActivationContract 적용 필요.

---

## 3. Capability Enforcement 미적용

현재 capability는 정의 수준.

실 Runtime enforcement 미적용.

---

## 4. Governance Runtime 미연결

현재:

- escalation
- digest
- retry
- storm protection

은 contract/document 수준.

실 Runtime 연결은 후속.

---

# 10. 현재 전략적 판단

현재 단계에서:

```text
Hard Contract Enforcement
```

를 즉시 적용하면:

사실상 Runtime 재개발 수준 위험 존재.

따라서 현재 우선순위:

1. Binding Engine 분리 완료
2. Candidate/Activation Runtime 안정화
3. Cockpit 운영 흐름 안정화
4. Progressive Enforcement

전략 유지.

---

# 11. 현재 구조의 의미

현재 TAI는:

```text
기능 중심 SaaS
```

단계를 지나,

```text
Contract 기반 Runtime Platform
```

단계로 진입 중.

핵심:

- Engine Independence
- Runtime Projection
- Candidate Activation Lifecycle
- Governance Layer
- Capability Layer
- Cross-engine Runtime Protocol

구조 확보.
