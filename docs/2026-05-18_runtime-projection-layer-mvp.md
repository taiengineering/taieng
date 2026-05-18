# Runtime Projection Layer MVP — 구현 완료 리포트

**일자**: 2026-05-18  
**담당**: Claude (Product/SaaS/Runtime Ops Architect)

---

## 1. 생성된 Migration 목록

| # | Migration | 내용 |
|---|-----------|------|
| 1 | `create_runtime_projection_layer` | 6 테이블 + residual_log + RLS + triggers |
| 2 | `create_runtime_event_log` | EventEnvelope 저장 테이블 |

## 2. 생성된 Runtime Table 목록

| 테이블 | 용도 | RLS |
|--------|------|-----|
| runtime_task | Task Projection (candidate→assigned→in_progress→completed/overdue) | ✅ |
| runtime_schedule | Schedule Projection (periodic/one_time/deadline) | ✅ |
| runtime_dependency | 객체간 의존관계 (requires/produces/blocks) | ✅ |
| runtime_evidence_requirement | 증빙 요구사항 (photo/signature/file 등) | ✅ |
| runtime_document_requirement | 문서 요구사항 (document_forms 연결) | ✅ |
| residual_log | 변환 불가 rule 기록 | ✅ |
| runtime_event_log | EventEnvelope 저장소 | ✅ |

## 3. 생성된 API 목록

| Method | Path | 기능 |
|--------|------|------|
| POST | `/runtime/tasks` | Task 생성 (candidate) |
| GET | `/runtime/tasks` | Task 목록 (tenant_id 필수) |
| GET | `/runtime/tasks/{id}` | Task 상세 |
| PATCH | `/runtime/tasks/{id}/status` | Status 전이 (validation 포함) |
| POST | `/runtime/schedules` | Schedule 생성 |
| POST | `/runtime/schedules/check-overdue` | Overdue 감지 + 이벤트 발생 |
| POST | `/runtime/legal-adapter/project` | 법령결과 → Runtime Projection |

## 4. EventEnvelope 구현 상태

- 파일: `watch_engine/runtime_bus/event_envelope.py`
- Pydantic BaseModel 기반
- 필수 필드: event_id, event_type, tenant_id, trace_id, source, timestamp, payload
- 선택 필드: idempotency_key
- emit_envelope(): runtime_event_log에 INSERT (Phase-1 direct, Phase-2 event_bus 통합)
- 기존 event_bus.py 수정 없음 (Wrapper 방식)

## 5. Legal Adapter 구현 상태

- 파일: `services/legal_adapter.py` + `routers/legal_adapter_api.py`
- rule_kind → task_type 매핑 완료
  - INSPECTION → inspection
  - PERMIT → permit
  - REPORT → report
  - TRAINING → training
  - APPOINTMENT → appointment
  - PROHIBITION → compliance_check
- PENALTY/STANDARD → residual_log 기록만 (Runtime Task 변환 금지)
- 자동 Document/Evidence Binding 포함

## 6. Document/Evidence Binding 구현 상태

- Legal Adapter가 task 생성 시 자동으로:
  - runtime_document_requirement 생성 (task_type별 기본 서식)
  - runtime_evidence_requirement 생성 (task_type별 기본 증빙)
- document_forms 직접 수정 없음 (document_form_id 연결만)
- GPT-exclusive 파일(document_runtime.py 등) 수정 없음

## 7. Overdue Event 구현 상태

- `services/runtime_schedule_service.py` → `check_overdue_schedules()`
- next_due_date < today인 active 스케줄 탐색
- task status를 overdue로 전이
- EventEnvelope(event_type="runtime.schedule_overdue") 생성 및 emit
- 알림엔진은 이벤트 소비만 가능 (task state 변경 금지)

## 8. Runtime Contract 위반 여부

**위반 없음.**
- 모든 이벤트에 tenant_id + trace_id 포함
- source_engine + source_ref_id 보존
- EventEnvelope 래퍼 방식 (기존 event_bus.py 미수정)

## 9. Boundary 침범 여부

**침범 없음.**
- 법령 truth 변경 없음 (Legal Adapter는 read-only translation)
- document_forms 수정 없음 (document_form_id 참조만)
- GPT-exclusive 파일 수정 없음
- 알림엔진이 task state 변경하는 구조 없음

## 10. 생성 파일 목록

| 파일 | 위치 | 라인수 |
|------|------|--------|
| event_envelope.py | watch_engine/runtime_bus/ | ~75 |
| runtime_task_service.py | services/ | ~90 |
| runtime_task_api.py | routers/ | ~80 |
| legal_adapter.py | services/ | ~170 |
| legal_adapter_api.py | routers/ | ~35 |
| runtime_schedule_service.py | services/ | ~85 |
| runtime_schedule_api.py | routers/ | ~45 |
| runtime_bridge.py (수정) | router_registry/ | +3 lines |

## 11. 다음 작업지시서

1. **Railway 배포 확인** — main push 자동배포 후 /health 200 확인
2. **E2E curl 테스트** — CASE 1(건설) / CASE 2(제조) 시나리오 실행
3. **Overdue cron 등록** — POST /runtime/schedules/check-overdue를 scheduler에 등록
4. **알림엔진 연결** — runtime.schedule_overdue 이벤트 소비 → notification dispatch
5. **Frontend Cockpit 연결** — runtime_task 목록을 SaaS UI에 표시
6. **EventEnvelope Phase-2** — runtime_event_log → event_bus 구독 연결
