# Runtime Binding Engine — Engineization 리포트

**일자**: 2026-05-19

## 1. Coupling Audit

| 결합 유형 | 위치 | 상태 |
|----------|------|------|
| legal matched_rules → runtime_task 직접 생성 | legal_adapter.py | ✅ 제거 (v2로 변경) |
| runtime_document/evidence 자동 바인딩 | legal_adapter.py | ✅ candidate sub-object로 이동 |
| candidate 단계 부재 | 전체 | ✅ runtime_candidate 테이블 생성 |
| activation 단계 부재 | 전체 | ✅ activate API 구현 |
| EventEnvelope 우회 | legal_adapter.py | ✅ binding_engine에서 emit |

## 2. Input Contract: RuntimeCandidateInput

- candidate_type (engine-agnostic)
- source_engine / source_ref_id / source_event_id
- tenant_id / facility_id / trace_id
- priority / confidence
- payload / source_trace (법령 전용 필드는 여기에만)
- document_suggestions / evidence_suggestions / schedule_suggestion
- requires_activation: true

## 3. Output Contract: RuntimeCandidateProjection

- projection_id / candidate_id / projection_type
- status: projected → pending_review → approved → activated

## 4. Candidate DB Schema (6 테이블)

| 테이블 | RLS | 용도 |
|--------|-----|------|
| runtime_candidate | ✅ | 후보 저장 |
| runtime_candidate_document_req | ✅ | 문서 요구 후보 |
| runtime_candidate_evidence_req | ✅ | 증빙 요구 후보 |
| runtime_candidate_schedule | ✅ | 스케줄 후보 |
| runtime_candidate_dependency | ✅ | 의존 후보 |
| runtime_candidate_residual | ✅ | 변환불가 기록 |

## 5. Binding Engine Core

- `services/runtime_binding_engine.py`
- project_candidate(): RuntimeCandidateInput → runtime_candidate + sub-objects
- runtime_task 생성 금지 (candidate만)
- EventEnvelope `runtime.candidate_projected` 발행

## 6. Legal Adapter v2

- `services/legal_adapter.py` 전면 개편
- matched_rules → RuntimeCandidateInput → Binding Engine → runtime_candidate
- runtime_task 직접 생성 제거
- PENALTY/STANDARD → runtime_candidate_residual

## 7. Activation API

- `services/runtime_activation_service.py`
- `POST /runtime/candidates/{id}/activate`
- candidate → runtime_task + runtime_schedule + doc/evidence
- 이때만 runtime_task 생성

## 8. 점검항목관리 API

| Method | Path | 기능 |
|--------|------|------|
| GET | /runtime/candidates | 후보 목록 |
| GET | /runtime/candidates/{id} | 후보 상세 |
| PATCH | /runtime/candidates/{id} | 수정/승인/거부 |
| POST | /runtime/candidates/{id}/activate | 운영 확정 |

## 9. Cockpit 역할 분리

- 점검항목관리 = candidate 표시 (projected/pending_review/approved)
- Cockpit = activated runtime_task만 표시

## 10. EventEnvelope

- `runtime.candidate_projected` — 후보 생성 시
- `runtime.candidate_activated` — 활성화 시

## 11. 검증 시나리오 결과

| 단계 | 예상 | 실제 |
|------|------|------|
| 법령진단 후 | candidates=3, tasks=0 | ✅ 3, 0 |
| 활성화 후 | activated=1, pending=2, tasks=1 | ✅ 1, 2, 1 |
| residual | 1건 | ✅ |

## 12. Railway 배포

✅ SUCCESS + Healthcheck 통과 + Import 에러 0건

## 13. 다음 작업

1. 점검항목관리 프론트엔드 UI
2. Cockpit에서 candidate 제외 확인
3. Legal Adapter v2 HTTP E2E curl 테스트
4. 알림엔진 연결
