# Runtime Binding Layer — 전체 작업 요약

**기간**: 2026-05-18 ~ 2026-05-19
**담당**: Claude (Product/SaaS/Runtime Ops Architect)

---

## 1. 작업 범위

독립적으로 존재하던 법령엔진 / 문서엔진 / 알림엔진 / Watch Runtime 사이를 연결하는 Runtime Binding Layer를 구축하고, 범용 플랫폼 엔진으로 정규화함.

## 2. 완료된 작업 목록

### 2-1. Runtime Projection Layer MVP (Phase 1)

| 항목 | 상태 |
|------|------|
| runtime_task 테이블 | ✅ |
| runtime_schedule 테이블 | ✅ |
| runtime_dependency 테이블 | ✅ |
| runtime_document_requirement 테이블 | ✅ |
| runtime_evidence_requirement 테이블 | ✅ |
| residual_log 테이블 | ✅ |
| runtime_event_log 테이블 | ✅ |
| EventEnvelope MVP | ✅ |
| Runtime Task CRUD API | ✅ |
| Runtime Schedule API | ✅ |
| Legal Adapter MVP | ✅ |
| Overdue Event + idempotency | ✅ |
| RLS 전 테이블 적용 | ✅ |

### 2-2. Cockpit 연결 (Phase 2)

| 항목 | 상태 |
|------|------|
| GET /runtime/cockpit/tasks (enriched) | ✅ |
| GET /runtime/cockpit/tasks/{id}/detail | ✅ |
| GET /runtime/cockpit/timeline | ✅ |
| Summary Cards UI | ✅ |
| Task List + Filter UI | ✅ |
| Detail Panel (doc/evidence/schedule/event) | ✅ |
| Activity Timeline UI | ✅ |
| Empty/Error/Loading State | ✅ |
| Notification Ready 배지 | ✅ |
| Mock 데이터 제거 + 실제 API 연결 | ✅ |

### 2-3. Binding Engine Engineization (Phase 3)

| 항목 | 상태 |
|------|------|
| RuntimeCandidateInput Contract | ✅ |
| RuntimeCandidateProjection Contract | ✅ |
| runtime_candidate 계열 6개 테이블 | ✅ |
| Binding Engine Core (candidate만 생성) | ✅ |
| Legal Adapter v2 (runtime_task 직접생성 제거) | ✅ |
| Activation Service (activate 시에만 task 생성) | ✅ |
| 점검항목관리 API (CRUD + activate) | ✅ |
| candidate → activation → runtime 분리 검증 | ✅ |

### 2-4. Contract Canonicalization (Phase 4)

| 항목 | 상태 |
|------|------|
| Runtime Taxonomy (15 categories) | ✅ |
| Canonical Payload Contract (4계층) | ✅ |
| Universal Activation Contract | ✅ |
| Governance Contract (4단계 preset) | ✅ |
| Capability Contract (3-tier) | ✅ |
| Event Taxonomy (20+ events) | ✅ |
| Engine Compatibility Matrix | ✅ |
| Boundary Audit (위반 0건) | ✅ |

## 3. 생성된 파일 전체 목록

### tai-api (백엔드)

| 파일 | 역할 |
|------|------|
| watch_engine/runtime_bus/event_envelope.py | EventEnvelope Pydantic + emit |
| models/__init__.py | 패키지 초기화 |
| models/runtime_candidate_contract.py | Input/Output/Activation Contract |
| models/runtime_payload_contract.py | Canonical Payload 4계층 |
| models/runtime_activation_contract.py | Universal Activation Contract |
| models/runtime_governance_contract.py | Governance 7영역 + 4 preset |
| models/runtime_capability_contract.py | Capability 13개 flag + 3 tier |
| services/runtime_task_service.py | Task CRUD + status transition |
| services/runtime_schedule_service.py | Schedule + Overdue detection |
| services/runtime_cockpit_service.py | Cockpit enriched views + detail + timeline |
| services/runtime_binding_engine.py | Binding Engine Core (candidate projection) |
| services/runtime_activation_service.py | candidate → runtime activation |
| services/legal_adapter.py | Legal Adapter v2 (candidate 기반) |
| routers/runtime_task_api.py | Task CRUD endpoints |
| routers/runtime_schedule_api.py | Schedule + check-overdue |
| routers/runtime_cockpit_api.py | Cockpit tasks/detail/timeline |
| routers/runtime_candidate_api.py | 점검항목관리 CRUD + activate |
| routers/legal_adapter_api.py | Legal Adapter endpoint |
| router_registry/runtime_bridge.py | 라우터 등록 (신규 5개 추가) |

### taieng (문서)

| 파일 | 내용 |
|------|------|
| docs/platform-core/runtime-taxonomy.md | 15개 category 정의 |
| docs/platform-core/runtime-payload-contract.md | Canonical Payload 규약 |
| docs/platform-core/runtime-activation-contract.md | Activation 규약 |
| docs/platform-core/runtime-governance-contract.md | Governance 규약 |
| docs/platform-core/runtime-capability-contract.md | Capability 규약 |
| docs/platform-core/runtime-event-taxonomy.md | Event 등록부 |
| docs/2026-05-18_runtime-projection-layer-mvp.md | MVP 구현 리포트 |
| docs/2026-05-18_runtime-e2e-verification.md | E2E 검증 리포트 |
| docs/2026-05-19_runtime-http-e2e-cockpit.md | HTTP E2E + Cockpit 리포트 |
| docs/2026-05-19_runtime-cockpit-implementation.md | Cockpit UI 구현 리포트 |
| docs/2026-05-19_binding-engine-engineization.md | 엔진화 리포트 |
| docs/2026-05-19_runtime-contract-canonicalization.md | Contract 정규화 리포트 |

### Supabase Migration

| Migration | 테이블 수 |
|-----------|--------|
| create_runtime_projection_layer | 6 + triggers |
| create_runtime_event_log | 1 |
| create_runtime_candidate_tables_v2 | 6 + trigger |

## 4. API 전체 목록

| Method | Path | 기능 |
|--------|------|------|
| POST | /runtime/tasks | Task 생성 |
| GET | /runtime/tasks | Task 목록 |
| GET | /runtime/tasks/{id} | Task 상세 |
| PATCH | /runtime/tasks/{id}/status | Status 전이 |
| POST | /runtime/schedules | Schedule 생성 |
| POST | /runtime/schedules/check-overdue | Overdue 감지 |
| POST | /runtime/legal-adapter/project | 법령결과 → Candidate Projection |
| GET | /runtime/cockpit/tasks | Cockpit 목록 (enriched) |
| GET | /runtime/cockpit/tasks/{id}/detail | Cockpit 상세 |
| GET | /runtime/cockpit/timeline | Cockpit 타임라인 |
| GET | /runtime/candidates | 점검항목 후보 목록 |
| GET | /runtime/candidates/{id} | 후보 상세 |
| PATCH | /runtime/candidates/{id} | 후보 수정/승인/거부 |
| POST | /runtime/candidates/{id}/activate | 운영 확정 |

## 5. DB 테이블 전체 목록 (13개)

### Runtime Projection (7개)
- runtime_task
- runtime_schedule
- runtime_dependency
- runtime_document_requirement
- runtime_evidence_requirement
- residual_log
- runtime_event_log

### Runtime Candidate (6개)
- runtime_candidate
- runtime_candidate_document_req
- runtime_candidate_evidence_req
- runtime_candidate_schedule
- runtime_candidate_dependency
- runtime_candidate_residual

전체 RLS 활성화 + tenant_id 기반.

## 6. 핵심 아키텍처 결정

### candidate → activation → runtime 분리

```
Engine Output
  → RuntimeCandidateInput (Normalized)
    → Binding Engine
      → runtime_candidate (projected)
        → 점검항목관리에서 안전관리자 승인/설정
          → POST /runtime/candidates/{id}/activate
            → runtime_task + runtime_schedule + doc/evidence
              → Cockpit 표시
```

법령결과가 바로 runtime_task가 되지 않음.
activation 시에만 runtime_task 생성.

### Payload 4계층

- core: Binding Engine이 읽는 영역
- domain: 엔진 전용 (해석 안 함)
- runtime: 런타임 행동 플래그
- governance: Watch Engine용

### 역할 분리

- 점검항목관리 = candidate 표시
- Cockpit = activated runtime_task만 표시
- Binding Engine = candidate projection만
- Activation Service = candidate → runtime 전환만
