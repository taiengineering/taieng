# WO-INPUT-TO-FACILITY-PROFILE-RESTORE-001 — 입력→facility_profiles 원래 경로 복원(규명·계획)

**작성일:** 2026-06-28 | **성격:** 읽기 전용 규명 + 1시설 실증계획. 데이터 변경 0. 새 엔진/Adapter/FieldMap/입력표준 생성 없음.
**판정: B — 기존 facility_profiles 계약을 채우는 "얇은 입력 정규화"만 필요(build_facility_profile 본체·저장계약 그대로 재사용).**

---

## TASK-001 — 소비자 입력 현재 저장 지점 (실측)
```
anonymous_diagnosis_results.input_data  171행 / factory_id 153
   {sector, ksic_code, factory_id, floor_area, worker_count}  has_* 없음   ← 주 경로
public_diagnosis_requests.facility_data  14행
   {has_elevator, has_gas, has_hazardous, floor_area, worker_count}  has_* 일부, factory_id 없음(biz_no)
factory_diagnosis_results.input_data  7행 (input_data 보유 7)  has_* 없음
─ facility_profiles 104행 / 102시설  ← 현재 factories(목업)에서 build (진단입력과 factory_id 공유 0)
```
→ 세 진단 저장소 중 어느 것도 facility_profiles로 흐르지 않음(WO-RESTORE-ORIGINAL-PATH-001 끊김-1 재확인).

## TASK-002 — diagnosis_input_fields 입력 목록 (입력표준)
```
섹터: BUILDING / INDUSTRIAL / CONSTRUCTION (COMMON 없음 — 3-섹터 체계)
키 컬럼: field_code, field_name, field_type, sector, tier, is_required, auto_source
핵심 입력: worker_count·total_floor_area·ksic_major·project_amount·electric_capacity·building_use_type·construction_type
has_*: has_crane·has_confined_space·has_excavation·has_welding·has_boiler·has_chemical_substance·has_high_pressure_gas·has_gas·has_chemical … (다수 is_active=false)
auto_source=building_register: total_floor_area/floor_count/building_use_type/built_year/main_structure
```

## TASK-003 — facility_profiles 저장 계약 (build_facility_profile / profile_to_db_row, 코드 직독)
```
평탄화 컬럼(11차원): sector, ksic_code,
  regular_workers_{state,value,provenance}, subcontract_workers_*, total_workers_*,
  use_code_*, floor_area_*, floor_count_*, construction_amount_*, electrical_kw_*, gas_capacity_*
provenance 목록: input_fields[], inferred_fields[], default_fields[]
profile_snapshot(JSON 전체): workforce/building/metrics + facility_physical/facility_hazard/
  construction/process/equipment/construction_process/construction_work  (has_* 보존)
profile_version (버전)
규칙(docstring): "수집→전달만. 값 변환/판정/조건 추가 금지." 새 컬럼 추가 없음.
```

## TASK-004 — 입력값 → facility_profiles 매핑 (기존 입력표준↔계약 사이만)
```
diagnosis_input_fields        build_facility_profile 기대 키(=factories 컬럼명)   facility_profiles
worker_count              →   employee_count                →   regular_workers_value        [키 이름 다름]
total_floor_area         →   building_area                 →   floor_area_value             [다름]
ksic_major               →   ksic_code                     →   ksic_code                    [동일]
project_amount           →   construction_amount           →   construction_amount_value    [다름]
electric_capacity        →   electrical_capacity_kw        →   electrical_kw_value          [다름]
building_use_type        →   building_use_code             →   use_code_value               [다름]
construction_type        →   construction_type             →   profile_snapshot.construction
has_confined_space       →   has_confined_space            →   profile_snapshot.construction.has_confined_space [동일]
has_crane                →   has_tower_crane               →   profile_snapshot / input_fields  [이름 다름]
has_excavation           →   has_excavation_work           →   profile_snapshot.construction_work [다름]
has_welding              →   has_welding_work              →   profile_snapshot.construction_work [다름]
```
→ 일부 항목은 입력 field_code와 build 기대 키의 **이름이 다름**(worker_count↔employee_count, has_crane↔has_tower_crane, has_excavation↔has_excavation_work). 이 차이를 흡수하는 정규화가 필요(=판정 B). 단 이는 **기존 입력표준↔facility_profiles 계약 사이의 키 정규화**이지 새 FieldMap이 아님.

## TASK-005 — build_facility_profile 재사용 판정
```
입력: build_facility_profile(row: dict) — row.get("employee_count")/("building_area")/("has_tower_crane") …
      = factories 컬럼명 키를 기대. 현재 POST /facility-profiles/{factory_id}가 factories row를 공급.
진단 입력 JSON을 직접 투입 시: 키 이름 불일치(worker_count≠employee_count 등) → 대부분 UNKNOWN.
판정: B — 함수 본체·저장계약(profile_to_db_row)·컬럼은 그대로 재사용 가능.
      단 진단 입력 field_code를 build 기대 키로 맞추는 "얇은 입력 정규화"가 선행 필요.
      (새 엔진/Adapter 아님 — 기존 facility_profiles 저장 계약을 채우는 입력 정규화로 한정)
```

## TASK-006 — 저장 시점 (판정 기준만, 실행 안 함)
```
factory_id 존재: step1부터 존재(진단 폼이 factory 선택). 입력 완성도: FREE(sector/worker/area/ksic) → PAID(has_*/process).
profile_version 중복 위험: 단계마다 저장하면 version 누적.
→ 권장 후보 = "최종 진단 실행 직전 1회" (입력 완성도 최대 + version 1회 생성).
  대안 = step1 저장 직후 1차 적재 후, 후속 단계는 동일 factory 최신 version 갱신.
  (정책 결정만 — 실행은 별도)
```

## TASK-007 — profile_version 정책 (기존 정책 확인, 새 정책 없음)
```
기존 API(facility_profile_api): 동일 factory_id 기존 존재 → profile_version = max+1 insert.
build 기본값 2. 최신 판단 = max(profile_version). 재진단 → 새 version 생성.
중복 방지 = factory_id별 최신 version 사용(읽기 시 max). → 기존 정책 그대로 따름.
```

## TASK-008 — 1시설 실증 계획 (대량 금지)
```
대상: 진단 입력 JSON 1건 보유 시설 1개(예: factory_diagnosis_results.input_data 보유분 중 1).
절차: 입력 JSON → (얇은 정규화: field_code→build 기대 키) → build_facility_profile → profile_to_db_row → facility_profiles 1행.
성공 기준(전수 글읽기): profile 생성 / sector 보존 / ksic 보존 / worker_count 보존 /
  has_* 보존(profile_snapshot) / input_fields 보존 / profile_snapshot 보존.
실행: 본 WO는 계획 확정까지. 실제 적재는 승인 후 별도(1건).
```

## TASK-009 — 기존 파이프라인 훼손 여부
```
이번 WO: 읽기 전용 — Applicability/obligation_generator/obligation_instance/Adapter/Persist/
  diagnosis_transform/front route/legal_engine step1 전부 미접촉.
복원 작업 시에도 facility_profiles 적재(쓰기)만 → 위 컴포넌트 불변
  (facility_profiles는 generator 소스이지 Applicability/step1 입력 아님 → step1 계약·라우팅 무영향).
```

## TASK-010 — 최종 판정
```
B. 기존 facility_profiles 계약을 채우는 "얇은 입력 정규화"만 필요.
   - 재사용: build_facility_profile + profile_to_db_row + 11차원 컬럼 + profile_snapshot 계약 그대로.
   - 추가: 진단 입력 field_code → build 기대 키 정규화(이름 흡수)뿐. 새 엔진/Adapter/FieldMap/입력표준 아님.
   - C 아님(저장 구조는 facility_profiles 계약과 호환). A 아님(키 이름 차이로 직접 투입 시 UNKNOWN).
```

## Boundary 준수
```
새 Engine/Adapter/FieldMap/Data Contract/입력표준 생성: 0.
run_facility_applicability/mock factories 기준 판단: 사용 안 함. from-instances 우회·step1 라우팅 변경: 없음.
obligation_instance 생성·대량 profile 생성: 없음. 읽기 전용 + 1시설 실증계획만.
```

*WO-INPUT-TO-FACILITY-PROFILE-RESTORE-001 — 판정 B. build_facility_profile·저장계약 재사용, 진단 field_code→build 기대 키 "얇은 정규화"만 선행. 저장시점=최종 실행 직전 1회 권장, version=기존 max+1 정책. 1시설 실증계획 확정. 기존 파이프라인 무접촉.*
