# WP-PERSISTENCE-02 — INSPECTION WRITER TRACE

- 작성일: 2026-08-25
- 모드: READ-ONLY DESIGN / EVIDENCE FIRST (mutation 0)
- ANALYSIS BASELINE: tai-api@`2b10e3a6` / REVIEW-TIME MAIN: tai-api@`2780acf8`
  (DRIFT +1 commit = routers/building_register.py only, relevant-code diff 0, 재분석 불필요)
- DB: `vwlahtguyggrhvslabax`
- 목적: safety_inspection.id 를 만드는 live writer 를 직독으로 확정 (Q1–Q4)

---

## 0. 결론 요약

safety_inspection.id 를 생성하는 live writer 는 **2곳**이며, 둘 다
explicit inspection.id 를 생성·반환한다. 단 완료 시점의 explicit id 확보는
**경로별로 다르다**: result / worker-submit 경로에서는 확보 가능하나,
manual complete(/inspection/complete/{work_schedule_id}) 경로에서는 단일
inspection.id 가 보장되지 않는다(B3). → INSPECTION ID AVAILABILITY = PARTIAL.

또한 이 writer 들 어디에도 "이 점검이 어떤 form_schema 로 문서를 만들지"를
정하는 로직이 없다 (→ FORM_SCHEMA_MAPPING_AUDIT 에서 B1 판정).

---

## 1. WRITER A — 안전관리자 웹 흐름 (inspection_checklist.py)

파일: `routers/inspection_checklist.py` (blob 8f7f0479), prefix `/inspection`

### CREATE 지점 — `POST /inspection/start/{work_schedule_id}`
```python
# parent work_schedules 에서 factory_id companion 먼저 확보 (fail-closed)
_ws = ...select("factory_id").eq("id", work_schedule_id)...
_parent_factory_id = _ws.data[0]["factory_id"]   # 없으면 409

insp_res = supabase.table("safety_inspections").insert({
    "assignment_id": work_schedule_id,     # FK → work_schedules(id)
    "inspection_date": started_at,
    "status_code": "in_progress",          # 소문자
    "factory_id": _parent_factory_id,      # WP-04D parent companion
}).execute()
# 반환: insp_res.data[0]["id"]   ← inspection.id 생성+반환 지점
```

### RESULT/COMPLETE 전이 — `POST /inspection/result/{inspection_id}/items`
```python
# inspection_id 를 path 로 직접 받음 → explicit id 확보 100%
...safety_inspection_results insert...
# 전 항목 통과(FAIL/NA 없음) 시:
work_schedules.update(status_code="completed", completed_at=...)
safety_inspections.update(status_code="completed").eq("id", inspection_id)
```

### COMPLETE 지점 — `POST /inspection/complete/{work_schedule_id}`
```python
work_schedules.update(status_code="completed", ...)
# rolling: 다음 회차 work_schedules 1건 자동 생성
safety_inspections.update(status_code="completed").eq("assignment_id", work_schedule_id)
```

## 2. WRITER B — 작업자 앱 흐름 (worker_check.py)

파일: `routers/worker_check.py` (blob 5ec91b03), prefix `/worker-check`

### CREATE = COMPLETE (한 번에) — `POST /worker-check/submit`
```python
# 결과에 따라 즉시 최종 상태 결정
status_code = "ISSUE" if has_issue else ("HOLD" if has_hold else "COMPLETED")   # 대문자

# schedule 참조 확보 (assignment_id → work_assignments.schedule_id 변환), 없으면 409
# parent work_schedules 에서 factory_id 확보 (body.factory_id 신뢰 안 함), 없으면 409

ins_res = supabase.table("safety_inspections").insert({
    "inspector_id": inspector_id,
    "inspection_date": now,
    "status_code": status_code,            # COMPLETED/ISSUE/HOLD
    "assignment_id": schedule_ref,         # work_schedules(id)
    "factory_id": _parent_factory_id,
}).execute()
inspection_id = ins_res.data[0]["id"]      # ← 생성+반환
# 이어서 safety_inspection_results insert (참조검증 + item_name 서버 마스터 덮어쓰기)
```

작업자 앱은 제출 순간 결과까지 확정한다. 단 **CREATE(safety_inspections INSERT)와
결과 저장(safety_inspection_results INSERT)은 동일 request/function flow 에서 연속
수행될 뿐, 명시적 DB atomic transaction 은 없다**(supabase .execute() 가 각각 별도 호출).

---

## 3. Q1–Q4 답변 (확정)

**Q1. inspection 생성/완료 writer 의 정확한 위치?**
→ 생성: `inspection_checklist.start_inspection` (웹) / `worker_check.submit_check` (앱).
  완료전이: `inspection_checklist.record_inspection_results` (전항목 통과 시)
  및 `inspection_checklist.complete_inspection`. 앱은 submit 이 곧 완료.

**Q2. inspection.id 최초 생성 지점?**
→ 두 writer 의 `safety_inspections.insert(...)` 반환값 `.data[0]["id"]`.
  둘 다 id 를 응답으로 돌려준다 (start → inspection_id, submit → inspection_id).

**Q3. 완료 action 시 이미 존재하는 inspection.id 확보 가능? — 경로별로 다름**
```
/inspection/result/{inspection_id}/items   = EXPLICIT INSPECTION ID AVAILABLE
    (inspection_id 를 path 로 직접 받음. 전항목 통과 시 그 id 만 completed 전이)
/worker-check/submit                        = EXPLICIT INSPECTION ID AVAILABLE
    (submit 응답에 inspection_id 포함. 단일 id 확정)
/inspection/complete/{work_schedule_id}     = SINGLE EXPLICIT INSPECTION ID NOT GUARANTEED
    (input=work_schedule_id. UPDATE ... WHERE assignment_id=work_schedule_id 로
     복수 inspection 을 한꺼번에 completed 로 바꿈. response 에 inspection_id 없음.
     safety_inspections.assignment_id 에 UNIQUE 없음 → 단일 id 보장 안 됨)
```
→ result 경로와 worker submit 경로에서는 explicit id 확보 가능(YES).
  manual complete 경로에서는 단일 inspection.id 가 보장되지 않음 → **B3**.

**Q4. source anchor writer 의 trigger 는? — 경로별 분리**
```
WEB result completion  /inspection/result/{inspection_id}/items
    = candidate trigger / explicit id available
WORKER submit          /worker-check/submit
    = candidate trigger / explicit id available
WEB manual complete    /inspection/complete/{work_schedule_id}
    = anchor trigger unsuitable in current contract
      (single inspection.id not guaranteed → B3)
```
- CREATE(start, in_progress)는 결과 전 → 빈 문서 조기 생성 위험, trigger 부적합.
- 따라서 anchor trigger 후보 = result-completion / worker-submit 두 경로.
  manual-complete 는 현 계약에서 부적합.
- trigger 최종 확정은 form_schema 매핑(B1) 해제 후에야 유효.

---

## 4. 부수 관찰 (기록만, 이번 WP 수정 대상 아님)

- **status_code 어휘 혼재의 근원**: 웹 writer 는 소문자(in_progress/completed),
  앱 writer 는 대문자(COMPLETED/ISSUE/HOLD). WP-PERSISTENCE-01 DB_EVIDENCE 의
  COMPLETED/completed 혼재가 이 두 경로에서 비롯됨. → 별도 정합화 WP (CD 계열).
- **assignment_id 명명 불일치**: 컬럼명은 assignment_id 이나 FK 는 work_schedules(id).
  worker_check v1.4.1 주석이 명시. 이번 WP 는 이를 건드리지 않는다.
- 두 writer 모두 factory_id 를 parent work_schedules 에서 서버 확정(client 미신뢰)
  → Q11 tenant companion 정본 패턴이 이미 확립되어 있음(재사용 가능).
