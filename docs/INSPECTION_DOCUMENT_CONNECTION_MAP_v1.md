# INSPECTION_DOCUMENT_CONNECTION_MAP_v1

```
WP        = WP-DATA-ARCH-01
STAGE     = CANONICAL DOCUMENT (post CORR-01 PASS / CLOSED)
SOURCE REPO      = taiengineering/tai-api
SOURCE MAIN SHA  = e1506aa45d3b35bf4d99d3c123600e9f19ab6996
CANONICAL REPO   = taiengineering/taieng
CANONICAL PATH   = docs/
DATE      = 2026-08-23
MODE      = READ ONLY (문서화 전용)
MUTATION  = 0
근거표기   = [실측]=DB 직독 / [코드근거]=repo 직독 / [판정]=아키텍처 판정
```

모든 화살표는 파일 또는 테이블 근거를 가진다. 가정한 연결 없음.

---

## 1. CONNECTED

```
law rule ─(inspection_sets.legal_rule_id, 논리참조)→ inspection_sets(327)
  [코드근거 queries.py: master 테이블 JOIN 제거, inspection_sets 자체 LEG컬럼 서빙]

inspection_sets ─(generate_items, legal_rule_id 보유 세트)→ inspection_set_items(5,184)

inspection_sets(anchor_confirmed, is_active)
  ─(schedules._build_next_schedule_row)→ work_schedules(66, inspection_set_id FK)

work_assignments.id
  ─(items.resolve_set_id_for_assignment · 3홉:
     schedule_id → work_schedules.inspection_set_id → inspection_set_items)→ 점검항목
  [set_id 미연결 시 빈 배열 반환 — FAIL-SOFT]

safety_inspections ─(inspection_id FK)→ safety_inspection_results

runtime_document_data(1)
  ─(document_confirm_svc 원자 TX)→ runtime_document_archive(0)
  [실측 UNIQUE uq_rdarch_doc_version(runtime_document_id, document_version)]

runtime_document_archive ─(generated_document.snapshot_id FK → runtime_document_archive.id)→ generated_document(1,544)
  = STRUCTURAL LINK AVAILABLE · LIVE SNAPSHOT LINK = 0  [실측: snapshot_id linked 0 / 1,544]
  [참고: generated_document.runtime_document_id FK → runtime_document_data · live linked = 2 / 1,544]

generated_document ─(submission_bridge)→ runtime_submission (정부제출)
  = OPTIONAL LOGICAL REFERENCE
  · runtime_submission.generated_document_id 컬럼 존재, DB FK = NONE  [실측: FK는 filing_registry_id 하나뿐]
  · LIVE LINK = 0  [실측: runtime_submission 50 / generated_document_id linked 0]
  → 현재 E2E CONNECTED 판정 금지.
```

---

## 2. Worker Write Path (교정: users-resolved worker)

worker_check의 저장 경로는 두 개의 별개 질문으로 분해한다.

```
질문 A. users.id로 해소되는가?
질문 B. 그 사람이 실제 인증된 현재 사용자임이 강제되는가?
```

```
users-resolved worker ─→ safety_inspections
  = FK-compatible write path
  [코드근거 worker_check: phone → users 매칭 성공 시 users.id를 inspector_id로 사용]
  [실측 safety_inspections.inspector_id FK → users.id]

authenticated actor binding
  = NOT ENFORCED by worker_check
  [코드근거 worker_check Authorization = optional. 토큰 없이도 phone으로 inspector 특정 후 제출 가능]
```

[판정]
- A(해소)는 일부 성립 — users에 존재하는 작업자만.
- B(인증 강제)는 현재 worker_check에서 강제되지 않음.
- 이 차이는 향후 Inspection→Document에서 submitted_by / confirmed_by identity를
  연결할 때 결정적이다.

---

## 3. PARTIAL

```
PLAN → EXEC (전체) = PARTIAL
  · users-resolved worker 경로 = FK-compatible (CONNECTED)
  · users-unresolved roster 경로 = BROKEN (§4)
  → 단일 CONNECTED 아님.
```

---

## 4. BROKEN / FK MISMATCH  →  [IDENTITY BREAK]

```
users-unresolved roster worker (phone → users 해소 실패) ──X── safety_inspections write

[코드근거 worker_check]
  phone → users 해소 성공 → users.id를 inspector_id로 사용
  phone → users 해소 실패 → worker_registry.id를 inspector_id로 사용
  (phone 매칭 = clean phone + 하이픈 형식 exact match)

[실측] safety_inspections.inspector_id FK → users.id

따라서 users에 해소되지 않는 roster worker는 worker_registry.id가
users.id FK를 만족하지 못해 저장 실패 가능.

[IDENTITY BREAK]
  worker_registry total              = 28  [실측]
  worker_registry.user_id linked     = 1   [실측]
  phone → users match                = 3   [실측: clean-full exact]
  phone → auth-linked users match    = 1   [실측: users.auth_id NOT NULL]
  roster → authenticated principal   = 1   [실측]
  principal-unlinked roster          = 27  [실측: 28 − 1]
  users-unresolved roster (FK break) = 25  [실측: 28 − 3]

주의: worker_registry.user_id NULL 27명 전체가 FK break 대상은 아니다.
  · FK break cohort         = 25 (users-unresolved)
  · principal-unlinked cohort = 27
  · 그중 2명(=3−1)은 phone→users로 해소되어 FK-compatible 저장은 가능하나
    authenticated principal은 아니다. (두 cohort를 섞지 않는다.)

유일 연결 경로 = auth/verify-otp 내부 _link_worker_registry (OTP 로그인 완료 시점만) [코드근거]
```

---

## 5. DORMANT PARALLEL

```
runtime_operational_work_order
  → runtime_inspection_session(0)
  → runtime_checklist_execution(0)
  → runtime_inspection_evidence(0)
  → runtime_inspection_submission

CODE      = IMPLEMENTED  (FK+UNIQUE 정교: 1 work_order=1 session, item/evidence 중복차단) [실측]
LIVE DATA = 0  [실측]
STATUS    = DORMANT PARALLEL IMPLEMENTATION
SoT       = NO  (현재 Operational Execution SoT = safety_inspections/results)
```

---

## 6. CRITICAL DISCONNECT  →  MISSING ORCHESTRATION BRIDGE

```
safety_inspections / safety_inspection_results ──X── runtime_document_data
  [코드근거 document_engine_svc.create_document(form_schema_id, ...):
    inspection 계열 테이블 일절 미참조, 빈 DRAFT 생성]
  공유 키 부재: results에 document_id/form_schema_id 없음 · doc_data에 inspection_id/session_id 없음

runtime_inspection_bridge
  STRUCTURE = EXISTS · mapping_status='MAPPED' 323 [실측]
  runtime_form_schema_id populated = 0 [실측]
  → INSUFFICIENT / STALE MAPPING STATE. CONNECTED 금지.
```

[판정] MISSING ORCHESTRATION BRIDGE
- Inspection fetcher(점검 데이터 reader)와 Runtime document lifecycle 양쪽 자산은 이미 존재한다.
- 없는 것은 데이터 reader가 아니라, 두 자산을 **호출 순서 + identity/source contract**로 잇는
  orchestration이다.

---

## 7. DATA MODEL INCONSISTENCY (유지, 미수정)

```
safety_inspections.assignment_id (컬럼명) → FK 대상 = work_schedules.id  [실측]
  [코드근거 worker_check: body.assignment_id(=work_assignments.id)
    → work_assignments.schedule_id → work_schedules.id 변환 후 저장]
판정: assignment_id name ≠ physical referenced entity. 기록만, 이번 단계 미수정.
```

---

## 8. 요약도

```
LEG ──✅──> DEF ──✅──> PLAN(schedule) ──✅──> PLAN(assignment)
                                                    │
                                          ┌─── users-resolved ──✅──> EXEC(safety_inspections/results)
                                          └─── users-unresolved ─❌──> [IDENTITY BREAK]

EXEC(safety_*) ──❌ MISSING ORCHESTRATION BRIDGE──> DOC(runtime_document_data)
DOC(working) ──✅──> DOC(archive, immutable)
DOC(archive) ──[STRUCTURAL / LIVE UNVERIFIED, snapshot 0]──> generated_document
generated_document ──[OPTIONAL LOGICAL REF / DB FK 없음 / LIVE 0]──> runtime_submission

[병렬·DORMANT] operational_work_order → runtime_inspection_session/checklist/evidence (데이터 0)
```
