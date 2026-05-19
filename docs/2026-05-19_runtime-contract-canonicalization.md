# Runtime Contract Canonicalization 리포트

**일자**: 2026-05-19

---

## 1. Runtime Taxonomy

15개 category 정의 완료.

| category | activation | schedule | escalation |
|----------|------------|----------|------------|
| inspection | required | periodic/one_time | ✅ |
| permit | required | deadline | ✅ |
| report | required | deadline | ✅ |
| training | required | periodic | ✅ |
| appointment | required | ❌ | ✅ |
| compliance_check | required | periodic | ✅ |
| notification_action | auto | ❌ | ❌ |
| marketing_action | optional | one_time | ❌ |
| governance_action | auto | ❌ | ✅ |
| recovery_action | auto | ❌ | ✅ |
| approval_action | required | deadline | ✅ |
| review_action | required | deadline | ❌ |
| evidence_collection | required | deadline | ✅ |
| document_submission | required | deadline | ✅ |
| workflow_action | optional | ❌ | ❌ |

문서: `docs/platform-core/runtime-taxonomy.md`

## 2. Canonical Payload Contract

4계층 분리:
- `core` — Binding Engine이 읽는 영역 (title, priority, confidence)
- `domain` — 엔진 전용 (Binding Engine이 해석 안 함)
- `runtime` — 런타임 행동 플래그
- `governance` — Watch Engine용 거버넌스 정책

문서: `docs/platform-core/runtime-payload-contract.md`
모델: `models/runtime_payload_contract.py`

## 3. Universal Activation Contract

- activation_mode: manual | automatic | conditional | delegated
- assignment_strategy: user | team | facility | auto_routing
- schedule_strategy: periodic | one_time | deadline | none
- escalation_policy: standard | strict | none
- governance_policy: passive | standard | strict | critical
- capability_scope: [required capabilities]

문서: `docs/platform-core/runtime-activation-contract.md`
모델: `models/runtime_activation_contract.py`

## 4. Governance Contract

7개 정책 영역:
- escalation (threshold_hours, target)
- retry (max_retries, backoff)
- digest (frequency, channel)
- throttling (max_per_hour)
- storm_protection (threshold, window)
- replay (retention_days)
- integrity (validation_mode, hash)

4단계 프리셋: passive / standard / strict / critical

문서: `docs/platform-core/runtime-governance-contract.md`
모델: `models/runtime_governance_contract.py`

## 5. Capability Contract

13개 capability flag 정의.
3개 tier 프리셋: Free / Standard / Premium.

문서: `docs/platform-core/runtime-capability-contract.md`
모델: `models/runtime_capability_contract.py`

## 6. Event Taxonomy

4개 영역, 20+ 이벤트 정의:
- candidate events (projected/approved/rejected/activated)
- runtime lifecycle (task/schedule CRUD + overdue)
- governance events (escalation/storm/digest/recovery)
- capability events (enabled/disabled)

문서: `docs/platform-core/runtime-event-taxonomy.md`

## 7. Engine Compatibility Matrix

| Engine | Input Contract | Output Contract | Activation | Governance |
|--------|---------------|----------------|------------|------------|
| Legal Engine | ✅ 호환 (Legal Adapter 경유) | ✅ RuntimeCandidateInput | ✅ manual | ✅ standard |
| Watch Engine | ✅ EventEnvelope | ✅ governance events | N/A (소비만) | ✅ 전체 |
| Notification Engine | ✅ EventEnvelope | ✅ notification_action | ❌ auto | ✅ passive |
| Marketing Engine (예상) | ✅ 호환 가능 | ✅ marketing_action candidate | ✅ optional | ✅ passive |
| Member Engine (예상) | ✅ 호환 가능 | ✅ appointment candidate | ✅ manual | ✅ standard |

모든 엔진이 동일한 RuntimeCandidateInput → Binding Engine → runtime_candidate 흐름 사용 가능.

## 8. Contract Boundary Audit

| 검증 항목 | 결과 |
|----------|------|
| Safe 전용 필드 top-level 존재 | ✅ 없음 |
| legal 전용 top-level field | ✅ 없음 (payload.domain.data 내부만) |
| runtime_task 직접 생성 우회 | ✅ 없음 (activation만) |
| EventEnvelope bypass | ✅ 없음 |
| cross-engine contract 위반 | ✅ 없음 |
| Binding Engine이 domain 해석 | ✅ 안 함 (core+runtime만) |

## 9. 남은 비정규화 영역

| 항목 | 상태 |
|------|------|
| Binding Engine에 CanonicalRuntimePayload 적용 | P1 — 현재 dict 기반 |
| Activation Service에 RuntimeActivationContract 적용 | P1 — 현재 단순 파라미터 |
| Capability 검사 로직 | P2 — 미구현 |
| Governance 정책 Watch Engine 전달 | P2 — 미구현 |

## 10. 다음 작업지시서

1. Binding Engine에 CanonicalRuntimePayload 4계층 구조 적용
2. Activation Service에 RuntimeActivationContract 적용
3. 점검항목관리 프론트엔드 UI
4. Legal Adapter v2 HTTP E2E curl 테스트
5. Capability 검사 로직 추가 (Binding Engine + Activation)
