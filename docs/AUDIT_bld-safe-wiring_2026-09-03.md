# BUILDING SAFE WIRING AUDIT (2026-09-03)

> WO-BLD-SAFE-WIRING-AUDIT-001. read-only 조사. authority 아님(index/handoff).
> CODE SoT = 각 repo current code · LEGAL SoT = leg · DB evidence = 실측 production.
> 구현/컬럼/매핑/파생/route/N1승격 = 이 문서로 승인되지 않음(별도 WO).

## 0. AUTHORITY / BOUNDARY
- Current Definition = 45cminc/leg .../DEFINITION_consumer-pipeline_v1.md (hyphen, sha f08cb1c5). Legacy(underscore) 미사용.
- TAI last stage = build_facility → facility. LEG first = POST /rtm/evaluate.
- BUILDING paid 정본 경로 = tai-www free-diagnosis.astro handlePaidEntry→loadPaidFlow→runPaidDiagnosis
  → form_data:formValues['paid'] → POST /diagnosis/run-leg → run_diagnosis → build_facility.
  (paid-diagnosis-detail = CONSTRUCTION handoff, BUILDING 미사용. nexas 격리 0.)
- LEG SoT DB = leg-prod wrfcedzgdrfupenzqhur. TAI DB(vwlahtguyggrhvslabax)=SAFE 자산(LEG SoT 아님). prj law 0.

## TRACK A — TAI TRANSPORT (PRE-WP1 AUDIT SNAPSHOT; BUILDING 소비자 입력 → facility)
BUILDING CONSUMER DENOMINATOR = 67 (diagnosis_input_fields BUILDING/PAID/active)
전송: form_data=formValues['paid'](setVal 평탄+facility 중첩, false/0 보존). body.input은 raw_structured_input 저장만(canonical 미경유).
build_facility 분류 (L4 최종 facility값 기준):
- FACILITY_EXACT = 50 (form_data→canonical(_LEG_INPUT_FIELDS exact-name)→facility 사용자값; N1 sector-gate 31 + sector무관 19)
- DRIFT = 3 : building_use_type→'사무실', floor_count→5, total_floor_area→400
  (BUILDING Step1 top-level default가 build_facility precedence(top-level>input)로 사용자값을 덮어씀. CAN_USER_OVERRIDE=NO, 항상 실행)
- TAI_DROPPED = 14 : electric_capacity, elevator_count, address, basement_count, built_year, main_structure,
  has_smoke_control, water_tank_ton, multi_use_type, gas_capacity_m3, boiler_capacity_kw,
  transformer_capacity_kva, annual_energy_toe, building_grade (_LEG_INPUT_FIELDS 아님 → canonical 미통과)
- TRANSFORM = 0 (elevator_count→has_building_elevator 파생은 top-level 미전송으로 미실행)
TOTAL = 50+3+14 = 67
N1 33: facility user-value exact 31, drift 2 (floor_count, building_use_type). canonical reach 33/33.

## TRACK B — LEG CONSUMPTION (facility → RTM 실제 소비)
LEG SoT = leg-prod public.production_semantic_repository (348 HARDENED, freeze 15cd17e8).
소비 모델 = mapped_field(direct) ∪ ConditionExtractor.extract leaf(indirect, iter_leaf_fields).
  (mapped_field DISTINCT-only 아님. 조건트리 Leaf가 실제 소비 vocabulary.)
N1 +9 atom (건축법 계열) → _bld_n1_tree (applicable.py) → N1 33 primitive Leaf.
  identity (atom_id, semantic_clause_id) exact pair = 9/9 production 존재 확인. tree leaf ∪ = N1 33 정확.
BUILDING 67 정본 분류:
- DIRECT_MAPPED_AND_CONSUMED = 12 (has_gas, has_boiler, is_multi_use, is_energy_intensive, has_water_tank,
  work_height_m, truck_loading_height_m, total_floor_area, manual_handling_weight_kg,
  has_emergency_gen, has_emergency_broadcast, has_hazmat_storage)
- INDIRECT_LEAF_CONSUMED = 36 (N1 33 + safety composite 2[has_truck_loading_unloading, has_manual_heavy_handling] + worker_count)
  · worker_count: mapped_field 0 이나 산안19조 atom(0ce68131) 조건트리 Leaf(total_floor_area>=400 OR worker_count>=50)로 실제 소비.
- NOT_CONSUMED = 19 (elevator_count 포함)
TOTAL = 67 · LEG ACTUAL CONSUMED = 48 (R2 CORRECTION: 구버전 47 → worker_count 계상 정정)
DERIVED LEG TARGET(67 denominator 밖): has_building_elevator (production mapped 7 atom, 승강기법).
  SAFE elevator_count → TAI lossless derivation(WP-1: 0→False/>0→True) → LEG has_building_elevator.
  ※ elevator_count 자체는 LEG condition Leaf 아님 → NOT_CONSUMED 유지(INDIRECT 아님).
N1 33: INDIRECT_LEAF_CONSUMED = 33/33 (조건트리 Leaf로 전량 실제 소비). NOT_CONSUMED = 0.

BLOCKER (TRACK A defect ∩ LEG 실제 소비):
- B1 building_use_type: DRIFT('사무실') + LEG 소비(atom 30afe158 enum_eq '오피스텔'). 오피스텔 가스보일러 조항 오판정.
- B2 floor_count: DRIFT(5) + LEG 소비(>=11/30/50 고층·초고층 atom). 고층 조항 오판정.
- B3 total_floor_area: DRIFT(400) + LEG 소비(atom 0ce68131 산안19조 연면적>=400). 300㎡ 사업장도 400 threshold 충족 오판정.
- B4 has_chemical NAME_MISMATCH_TRANSPORT: BUILDING facility=has_chemical, LEG=has_hazardous_material/has_chemical_substance.
  LEG conditions에 has_chemical 키 부재 → UNKNOWN → 유해물질 조항 미적용. (semantic 동의 여부=GPT 판정, 자동 alias 금지)
- B5 elevator DERIVATION GAP: LEG has_building_elevator(7 atom 승강기법) 소비 but paid path elevator_count top-level 미전송 → 파생 미실행 → 조항 미적용.

## TRACK C — SAFE OWNERSHIP (LEG 소비 48축 ↔ SAFE 자산, ownership 5-class)
SAFE BUILDING ASSET = factories(sector=BUILDING) + building_register(건축물대장 API 적재). buildings=식별용(진단자산 아님).
REGISTER-MATERIALIZATION AUTHORITY: legal_context._factory_to_context(레거시), safe_industrial_canonical_assembler(산업),
  building_register.py(대장→factories 적재). ⚠️ BUILDING paid(run-leg) 경로는 어느 authority도 미호출 = 배선 미완.
LEG 소비 48축 ownership 5-class (factories DB + 대장 실측; semantic 미증명은 PRESENT_UNVERIFIED):
- OWNED_EXACT = 3 : floor_count, has_boiler, is_multi_use (factories exact-name + semantic 자명)
- OWNED_SEMANTIC_VERIFIED = 0 (semantic/unit/provenance 증명 완료 축 없음)
- OWNED_DERIVABLE = 0 (lossless deterministic derivation 증명 완료 축 없음)
- PRESENT_UNVERIFIED = 7 : worker_count, total_floor_area, building_use_type, building_height_m,
  occupancy_capacity, floor_area_sum_at_or_above_11f, performance_use_floor_area_sum
  · SAFE 후보 컬럼 존재하나 semantic equivalence/단위/provenance 미증명:
    worker_count↔factories.employee_count, total_floor_area↔building_area/arch_area,
    building_use_type↔main_purpose_name, building_height_m↔building_height,
    occupancy_capacity↔occupant_capacity (컬럼 존재 ≠ 의미 동일 증명)
  · floor_area_sum/performance_use ↔ 층별개요(getBrFlrOulnInfo) 집계 후보이나 floor discriminator/
    area 의미·단위/중복/동호 grouping/지하옥탑/pagination/performance-use taxonomy 미증명.
- ABSENT_SOURCE = 38 : N1 특수판정축(cantilever/column_span/flat_plate/연결공지/토지지반/설계·운영) +
  산업계열 안전축(has_gas, has_water_tank, work_height_m, truck_loading_height_m, manual_handling_weight_kg,
  has_emergency_gen, has_emergency_broadcast, has_hazmat_storage, has_truck_loading_unloading,
  has_manual_heavy_handling, is_energy_intensive) — SAFE asset/API/대장/derivation 후보 부재.
48축 SUMMARY: OWNED_EXACT 3 + SEMANTIC_VERIFIED 0 + DERIVABLE 0 + PRESENT_UNVERIFIED 7 + ABSENT_SOURCE 38 = 48. (overlap 0, missing 0)

## 종합 (3 TRACK)
- N1 33 = LEG 실제 소비(조건트리). SAFE 원천: floor_count(OWNED_EXACT) + building_use_type/building_height_m/
  occupancy_capacity/floor_area_sum/performance_use(PRESENT_UNVERIFIED — 후보 존재, semantic 미증명). 나머지 N1 특수축 = ABSENT_SOURCE.
- ownership: OWNED_EXACT 3 · SEMANTIC_VERIFIED 0 · DERIVABLE 0 · PRESENT_UNVERIFIED 7 · ABSENT_SOURCE 38 = 48.
- BLOCKER 5(POST-WP1): B1/B2/B3/B5 = WP-1 해소·배포 완료. B4 = NO ALIAS/SEMANTIC SPLIT(GPT 판정, OPEN).
- 수집방식(existing/register/derivation/stable user fact/runtime/new UI) 선정은 AUDIT 범위 밖 → BUILDING SOURCE DESIGN.
  AUDIT은 ownership(OWNED/UNVERIFIED/ABSENT)까지만. (구버전 "즉시 배선 9축/신규 38축" 확정 표기 폐기.)

## POST-WP1 STATUS (2026-09-03)
TRACK A DRIFT/DROPPED 은 PRE-WP1 SNAPSHOT. WP-1(tai-api b3e8c3b0/배포 SUCCESS)로 해소:
- B1 building_use_type / B2 floor_count / B3 total_floor_area default overwrite = FIXED
- B5 elevator 0 loss = FIXED (0→False/>0→True) · form_data persistence = FIXED · RAW→CANONICAL fallback = FIXED
- WP-1 = FULL CLOSED (baseline b3e8c3b08c079c6f7e368f2698e63839c1373279)
- B4 chemical = NO ALIAS / SEMANTIC SPLIT / OPEN (BUILDING SOURCE DESIGN 단계)

## STATUS
AUDIT A/B/C = R2 (TRACK B 48 consumed / TRACK C ownership 5-class). read-only.
구현/컬럼/매핑/파생/building-leg route/N1 승격 = NOT AUTHORIZED (별도 WO).
CODE/DB/LEG WRITE = 0. nexas = 0. prj = 0.
