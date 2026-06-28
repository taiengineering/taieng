# WO-APPLICABILITY-INPUT-SOURCE-001 — Applicability 입력원천 최종 규명

**작성일:** 2026-06-28 | **성격:** 읽기 전용 규명(코드·DB 근거만, 추측·개선안 없음).
**Source of Truth 판정: A — `factories`.** facility_profiles는 Applicability에 미사용.

---

## TASK-001 — Call Graph (실제 호출 순서)
```
[Applicability 엔진 = 배치 스크립트. FastAPI 라우터 없음. 실행 railway run python3]
scripts/run_facility_applicability.py  main()
  → psycopg2.connect(DATABASE_URL)              # Railway 전용 (앱 라우터 아님)
  → CREATE TABLE IF NOT EXISTS facility_applicability(_detail/_issue)
  → TRUNCATE facility_applicability,_detail,_issue   # 재실행 시 전수 초기화
  [1] SELECT factories WHERE is_active=true
        (id, employee_count, electrical_capacity_kw, transformer_capacity_kva,
         building_area, gas_capacity_m3, gas_capacity_kg, construction_amount,
         site_type, ksic_code, name)
  [2] SELECT executable_draft ed JOIN draft_slot ds  (section=IF_NUMERIC: binding_field/operator/value)
      SELECT executable_draft ed JOIN draft_slot ds  (section=IF_SCOPE: binding_field)
  [3~11] for fac in factories:
           for draft in drafts:
             services.facility_applicability_eval.evaluate_draft_for_facility(fac, draft_id, numeric_slots, scope_slots)
               → evaluate_numeric_check() / evaluate_scope_check()
                   → FIELD_MAP[binding_field] → factories 컬럼 → facility.get(col)
                   → compare_numeric() / aggregate_applicability_status()
  → INSERT facility_applicability (factory_id, draft_id, part_id, applicability_status, match_details)
  → INSERT facility_applicability_detail
  [15] Validation: status/result/reason 집계 출력
```
※ 라우터·온디맨드 API 없음(코드 주석: "(future) on-demand API"). 순수 배치.

## TASK-002 — 실제 읽는 테이블 (전수)
```
READ : factories (is_active=true), executable_draft, draft_slot
WRITE: facility_applicability, facility_applicability_detail, facility_applicability_issue
읽지 않음(확인): facility_profiles, exists_input, building, equipment
  (FIELD_MAP equipment_type→None: EQUIPMENT_JOIN 미구현 — equipment 테이블 join 없음)
```

## TASK-003 — 입력 컬럼 사용처 1:1 (FIELD_MAP, 코드 직독)
```
binding_field        factories 컬럼              품질         판정식
employee_count    →  employee_count           DIRECT      compare_numeric(>=,<=,>,<)
area_size         →  building_area            DIRECT      compare_numeric
power_capacity    →  electrical_capacity_kw   DIRECT      compare_numeric
voltage_level     →  transformer_capacity_kva AMBIGUOUS   비교 안 함 → 항상 AMBIGUOUS
storage_capacity  →  gas_capacity_m3          AMBIGUOUS   항상 AMBIGUOUS
facility_type     →  site_type                AMBIGUOUS   항상 AMBIGUOUS
process_type      →  ksic_code                AMBIGUOUS   항상 AMBIGUOUS
monetary_value    →  construction_amount      AMBIGUOUS   항상 AMBIGUOUS
equipment_type    →  (없음)                    EQUIPMENT_JOIN  항상 MISSING_DATA(NO_FACILITY_COLUMN)
concentration_level→ (없음)                    MISSING     항상 MISSING_DATA
distance_value    →  (없음)                    MISSING     항상 MISSING_DATA
```
MISSING_DATA 트리거(코드): NO_FIELD_MAP / NO_FACILITY_COLUMN(fac_col=None) / FACILITY_VALUE_NULL(factories 값 NULL).

## TASK-004 — MISSING_DATA 발생 원인 (조항 수 = parts, DB 집계)
```
[구조적 — factories에 컬럼 자체 없음. 데이터로 해결 불가]
distance_value        219  NO_FACILITY_COLUMN
equipment_type        209  NO_FACILITY_COLUMN (EQUIPMENT_JOIN 미구현)
concentration_level    82  NO_FACILITY_COLUMN
  소계 510 parts

[데이터 결측 — 컬럼 존재하나 factories 값 NULL]
facility_type→site_type           133  (site_type 90% NULL, 또한 AMBIGUOUS 품질)
voltage_level→transformer_kva     110  (대부분 NULL, AMBIGUOUS)
storage_capacity→gas_capacity_m3   19  (대부분 NULL, AMBIGUOUS)
power_capacity→electrical_kw       10  (87.5% NULL, DIRECT)
area_size→building_area             7  (88% NULL, DIRECT)

[평가됨 — 데이터 있음]
employee_count                     37  (IF_NUMERIC 30 + IF_SCOPE 7, 100% present, DIRECT)
process_type→ksic_code             16  (93% present, 단 AMBIGUOUS 품질)
monetary_value→construction_amount  6  (92% present, AMBIGUOUS)
```

## TASK-005 — facility_profiles 사용 여부 (전 프로젝트 전수 검색)
참조 파일 5개뿐:
```
routers/facility_profile_api.py      (자체 CRUD: POST/GET/verify)
services/facility_profile_service.py (프로파일 build)
services/exists_input_service.py     (EXISTS 입력 기능)
routers/exists_input_api.py          (EXISTS 입력 API)
tests/test_exists_input.py           (테스트)
```
Applicability 엔진(run_facility_applicability.py / facility_applicability_eval.py)·diagnosis·legal_engine: **참조 0.**
**판정: Applicability 기준 미사용(Dead Code 경로).** 전역으로는 자체 CRUD API + exists_input 전용 → Applicability/진단 파이프라인에 미배선.

## TASK-006 — Source of Truth 최종 판정
```
판정: A — factories (단일 진실원천)
근거(코드):
  · run_facility_applicability.py: SELECT … FROM factories WHERE is_active=true
  · facility_applicability_eval.FIELD_MAP: 모든 매핑 대상이 factories 컬럼
  · evaluate_*_check: facility.get(fac_col) — facility = factories row dict
  · facility_profiles / exists_input 참조: 0
```

## TASK-007 — 입력 부족 원인 (binding_field 전수, 조항 수 우선)
```
순위  binding_field        parts  원인
 1   distance_value        219   컬럼 없음(구조적)
 2   equipment_type        209   컬럼 없음/EQUIPMENT_JOIN 미구현(구조적)
 3   facility_type         133   site_type 90% NULL + AMBIGUOUS
 4   voltage_level         110   transformer NULL + AMBIGUOUS
 5   concentration_level    82   컬럼 없음(구조적)
 6   employee_count         37   (충족 — 부족 아님)
 7   storage_capacity       19   gas NULL + AMBIGUOUS
 8   process_type           16   AMBIGUOUS(ksic 값은 있음)
 9   power_capacity         10   electrical 87.5% NULL
10   area_size               7   building_area 88% NULL
11   monetary_value          6   AMBIGUOUS(construction 값은 있음)
(binding_field 총 11종 전수 — TOP20 미만이므로 전부 제시)
```

## TASK-008 — 최종 결론 (사실만)
```
1. Applicability 입력 = factories. 11개 binding_field가 factories 컬럼(또는 무매핑)으로 평가됨.
   라우터 없는 배치 스크립트(railway run)로 전 시설 전수 재평가(TRUNCATE 후) 방식.
2. facility_profiles의 현재 역할 = Applicability에 미사용. 자체 CRUD API와 exists_input 기능에서만 참조.
   → 생성해도 Applicability 입력으로 진입하지 않음.
3. MISSING_DATA를 줄이려면 실제로 보강해야 하는 것(사실):
   · 구조적 510 parts(distance_value·equipment_type·concentration_level)는 factories에 대응 컬럼 자체가 없음
     → 데이터 채움으로 해결 불가(엔진 FIELD_MAP/스키마 한계).
   · 컬럼이 있는 결측 필드: building_area(88% NULL)·electrical_capacity_kw(87.5% NULL) — DIRECT라 값 채우면 평가 가능.
   · AMBIGUOUS 품질 필드(site_type·transformer·gas·ksic·construction_amount)는 값이 있어도 MATCH가 아닌 AMBIGUOUS 반환.
```

## Boundary 준수
```
읽기 전용. 코드/DB 수정·INSERT/UPDATE/DELETE 0. 엔진 미실행·미수정. 개선안 미작성(사실 규명만).
```

*WO-APPLICABILITY-INPUT-SOURCE-001 — Source of Truth = factories. facility_profiles는 Applicability 미사용. MISSING_DATA의 510 parts는 컬럼 부재(구조적), 나머지는 factories 컬럼 NULL/AMBIGUOUS 품질.*
