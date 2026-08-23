# INSPECTION_DOCUMENT_BACKFILL_VALIDATION_PLAN_v1  (CANONICAL · WP-DATA-ARCH-03 PASS/CLOSED)

```
WP        = WP-DATA-ARCH-03 · CORR-02
STAGE     = CANONICAL DOCUMENT (post CORR-02 PASS · WP-DATA-ARCH-03 CLOSED)
MODE      = PLANNING ONLY · MUTATION 0
근거표기   = [실측]=DB · [설계]
공통규약   = 단일 TX · PRE/POST 대조 · 불일치 전량 롤백(부분성공 금지) · fail-closed(근거불명=NULL, 삭제/오설정 금지)
```

각 항목: CURRENT ROWS / NULL·BROKEN / SOURCE / DETERMINISTIC? / HUMAN REVIEW? / FAIL-CLOSED / PRE / POST.

---

## 1. safety_inspections.factory_id  (companion)
```
CURRENT      = si 2행 [실측]
NULL·BROKEN  = assignment_id NULL 1행 [실측 1/2]
SOURCE       = assignment_id → work_schedules.factory_id
DETERMINISTIC= YES (assignment_id 있는 행). assignment NULL 행은 불가
HUMAN REVIEW = NO
FAIL-CLOSED  = assignment NULL → factory_id NULL 유지(강제 채움 금지)
PRE  = SELECT count(*) FROM safety_inspections WHERE assignment_id IS NULL;   -- 기대 1
POST = 채워진 행.factory_id = 대응 ws.factory_id 100% 일치 · assignment NULL 행 factory_id NULL 유지
```

## 2. safety_inspections.submitted_by
```
CURRENT      = si 2행
NULL·BROKEN  = 전량(신규 컬럼)
SOURCE       = 없음(기존 행에 결정적 historical actor 부재)
DETERMINISTIC= NO
HUMAN REVIEW = NO
FAIL-CLOSED  = **backfill 하지 않음. 기존 행 NULL 유지(legacy row). future canonical write(CD5-1)부터 submitted_by 의미 보장**
PRE  = (없음 — 무backfill)
POST = 기존 2행 submitted_by NULL 유지 확인 · 이후 신규 write 행만 NOT NULL
```

## 3. safety_inspections.retention_until  (effective not-before-delete)
```
CURRENT      = si 2행
NULL·BROKEN  = 전량(신규 컬럼)
SOURCE       = P0-1 RETENTION POLICY RESOLUTION(inspection 유형/법령→기간) + runtime_evidence_retention_policy(reference/default, [실측 8행 deletion_allowed=false])
DETERMINISTIC= 유형/법령 매핑 확정분만
HUMAN REVIEW = 부분(법령 직독 P0-1)
FAIL-CLOSED  = 미해소 유형 → NULL 유지(삭제 금지). 숫자만으로 삭제 허용 금지
PRE  = P0-1 매핑표 법조문 대조 완료 여부 · 미해소 유형 목록화
POST = 해소 행 finite 값 · 미해소 행 NULL · 과거 오설정 0. (이 값 = 모든 DELETE/partition DROP eligibility 근거)
```

## 4. work_assignments.factory_id  (companion, WS-MIG 前 준비)
```
CURRENT      = work_assignments [실측 5,991행]
NULL·BROKEN  = 전량(신규 컬럼). 기존 3 INSERT creator 전부 factory_id 미기록
SOURCE       = schedule_id → work_schedules.factory_id
DETERMINISTIC= YES (schedule_id NOT NULL 전제 — schedule_id FK 존재)
HUMAN REVIEW = NO
FAIL-CLOSED  = schedule_id로 해소 불가 행(고아) → NULL 유지 + 목록화
PRE  = SELECT count(*) FROM work_assignments wa LEFT JOIN work_schedules ws ON wa.schedule_id=ws.id WHERE ws.id IS NULL;  -- 고아 기대 0
POST = wa.factory_id = ws.factory_id 100% 일치 · 고아 행만 NULL. (writer 3창도 factory_id 세팅하도록 patch = WA 전환 동반(ON CONFLICT + factory_id))
```

## 5. runtime_document_data.source_inspection_id
```
CURRENT      = runtime_document_data [실측 1행]
NULL·BROKEN  = 전량(신규 컬럼)
SOURCE       = 없음(기존 문서가 inspection 유래인지 결정적 근거 부재)
DETERMINISTIC= NO
HUMAN REVIEW = NO
FAIL-CLOSED  = **기존 non-inspection document에 임의 backfill 금지. NULL 유지. orchestration(CD5-2) 신규 생성분만 source 세팅**
PRE  = (없음 — 무backfill)
POST = 기존 행 source_inspection_id NULL 유지 · UNIQUE(source_inspection_id, form_schema_id)는 NULL 다중 허용
```

## 6. runtime_inspection_bridge.runtime_form_schema_id
```
CURRENT      = runtime_inspection_bridge [실측 324행]
NULL·BROKEN  = MAPPED인데 schema NULL 323행 [실측 323]
SOURCE       = curated 인간검수(P0-3A 결정 → P0-3B 승인 DML). 이름 유사도 auto-map 금지
DETERMINISTIC= NO
HUMAN REVIEW = **YES (P0-3A)**
FAIL-CLOSED  = P0-2로 323 MAPPED→NEEDS_HUMAN_REVIEW 되돌림(CHECK 선행). 검수 전 임의 schema 채움 금지
PRE  = SELECT count(*) WHERE mapping_status='MAPPED' AND runtime_form_schema_id IS NULL;  -- [실측 323] → P0-2 후 0
POST = P0-3B 승인분만 schema 채우고 MAPPED 승격 · 미검수는 NEEDS_HUMAN_REVIEW 유지
```

## 7. safety_inspection_results.checked_at / inspection_id  (backfill 아님 — gate 검증)
```
CURRENT      = results [실측 8행]
NULL·BROKEN  = inspection_id NULL 0 [실측] · checked_at NULL 0 [실측]
SOURCE       = 없음(이미 clean). 두 writer(worker_check·inspection_checklist) 항상 세팅[직독]
DETERMINISTIC= N/A (backfill 불요)
HUMAN REVIEW = NO
FAIL-CLOSED  = patch 전 신규 NULL 유입 시 C3-5/6 보류
PRE  = SELECT count(*) WHERE inspection_id IS NULL; = 0 · WHERE checked_at IS NULL; = 0
POST = 상동 0 재확인 직전 C3-5/C3-6 적용. checked_at = RANGE 파티션 키 자격 확인
```

## 8. safety_inspection_results.inspection_set_item_id
```
CURRENT      = results [실측 8행]
NULL·BROKEN  = 기존 NULL 5행 [실측] (worker_check 검증실패분·inspection_checklist 무검증분)
SOURCE       = 없음(항목 참조 결정적 복원 불가)
DETERMINISTIC= NO
HUMAN REVIEW = NO
FAIL-CLOSED  = **기존 NULL 5행 유지(NULL 허용). 임의 생성 금지. C3-7 FK RESTRICT는 nullable이라 NULL 허용**
PRE  = SELECT count(*) WHERE inspection_set_item_id IS NOT NULL AND inspection_set_item_id NOT IN (SELECT id FROM inspection_set_items);  -- 위반 기대 0 [실측 0]
POST = 위반 0 재확인 후 C3-7 FK 적용 · NULL 5행 유지
```

## 부속: bridge P0-2 revert (DML, backfill 아님·순서 hazard)
```
PRE  = SELECT count(*) WHERE mapping_status='MAPPED' AND runtime_form_schema_id IS NULL; = [실측 323]
실행  = UPDATE runtime_inspection_bridge SET mapping_status='NEEDS_HUMAN_REVIEW' WHERE mapping_status='MAPPED' AND runtime_form_schema_id IS NULL
POST = 위 count 0 → C3-4 CHECK 적용 가능
```
