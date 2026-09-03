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

## TRACK A — TAI TRANSPORT (BUILDING 소비자 입력 → facility)
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
- INDIRECT_LEAF_CONSUMED = 35 (N1 33 + safety composite 2: has_truck_loading_unloading, has_manual_heavy_handling)
- NOT_CONSUMED = 20
TOTAL = 67
N1 33: INDIRECT_LEAF_CONSUMED = 33/33 (조건트리 Leaf로 전량 실제 소비). NOT_CONSUMED = 0.

BLOCKER (TRACK A defect ∩ LEG 실제 소비):
- B1 building_use_type: DRIFT('사무실') + LEG 소비(atom 30afe158 enum_eq '오피스텔'). 오피스텔 가스보일러 조항 오판정.
- B2 floor_count: DRIFT(5) + LEG 소비(>=11/30/50 고층·초고층 atom). 고층 조항 오판정.
- B3 total_floor_area: DRIFT(400) + LEG 소비(atom 0ce68131 산안19조 연면적>=400). 300㎡ 사업장도 400 threshold 충족 오판정.
- B4 has_chemical NAME_MISMATCH_TRANSPORT: BUILDING facility=has_chemical, LEG=has_hazardous_material/has_chemical_substance.
  LEG conditions에 has_chemical 키 부재 → UNKNOWN → 유해물질 조항 미적용. (semantic 동의 여부=GPT 판정, 자동 alias 금지)
- B5 elevator DERIVATION GAP: LEG has_building_elevator(7 atom 승강기법) 소비 but paid path elevator_count top-level 미전송 → 파생 미실행 → 조항 미적용.

## TRACK C — SAFE OWNERSHIP (LEG 소비 47축 ↔ SAFE 자산)
SAFE BUILDING ASSET = factories(sector=BUILDING) + building_register(건축물대장 API 적재). buildings=식별용(진단자산 아님).
REGISTER-MATERIALIZATION AUTHORITY: legal_context._factory_to_context(레거시), safe_industrial_canonical_assembler(산업),
  building_register.py(대장→factories 적재). ⚠️ BUILDING paid(run-leg) 경로는 어느 authority도 미호출 = 배선 미완.
LEG 소비 47축 4-tier:
- TIER-1 EXACT_COLUMN (factories 동일이름, CONSUMED) = 3 : floor_count, has_boiler, is_multi_use
- TIER-2 REGISTER_MATERIALIZED (대장 원천+변환 authority 존재, exact-name 아님) = 6 :
  building_use_type←main_purpose_name, total_floor_area←building_area/arch_area, basement_count←underground_floor_count,
  main_structure←building_structure_name, building_height_m←building_height, occupancy_capacity←occupant_capacity
- TIER-4 GENUINELY_ABSENT (대장·factories 원천 없음) = 38 :
  N1 특수판정축 (floor_area_sum_at_or_above_11f, performance_use_floor_area_sum, has_performance_assembly_use,
  is_target_facility_in_basement, cantilever_projection_m, column_span_m, flat_plate_column_section_ratio,
  has_flat_plate_structure, authority_designated_special_structure, building_activity_type, building_use_category,
  article32_3_alternative_confirmation_subject, has_gas_boiler_heating_system, has_centralized_gas_supply,
  is_collapse_risk_land, has_land_preparation, has_building_construction_activity, has_wet_land, has_water_seepage_risk,
  has_landfill_or_similar_ground, underground_connection_entrance_distance_m, has_wall_between_connection_entrances,
  wall_between_connection_entrances_is_fire_resistant, connection_open_space_floor_area_m2,
  connection_open_space_open_area_ratio, has_stair_or_ramp_in_open_space, stair_or_ramp_effective_width_m,
  is_connected_to_subway_or_underground_mall, has_hazardous_material_in_out_event)
  + 산업계열 소비축 (has_gas, has_water_tank, work_height_m, truck_loading_height_m, manual_handling_weight_kg,
  has_emergency_gen, has_emergency_broadcast, has_hazmat_storage, has_truck_loading_unloading, has_manual_heavy_handling)
47축 SUMMARY: EXACT 3 + REGISTER_MAT 6 + ABSENT 38 = 47.

## 종합 (3 TRACK)
- N1 33 = LEG 실제 소비(조건트리). SAFE 원천: floor_count(EXACT) + building_use_type/total_floor_area(REGISTER_MAT). 나머지 N1 30 = GENUINELY_ABSENT.
- 즉시 배선 가능(SAFE 원천 존재) = 9축 (EXACT 3 + REGISTER_MAT 6).
- 신규 수집 필요(GENUINELY_ABSENT) = 38축.
- BLOCKER 5: B1/B2/B3/B5 = SAFE 원천 존재 → wiring으로 해소 가능. B4 = NAME_MISMATCH(GPT semantic 판정).
- BUILDING SAFE wiring 실체: N1 특수 30축은 SAFE 수집 자체가 없어 LEG 소비하나 SAFE가 값 보유 못함(신규 입력/대장확장 필요).

## STATUS
AUDIT A/B/C = CLOSED (read-only). 구현/컬럼/매핑/파생/building-leg route/N1 승격 = NOT AUTHORIZED (별도 WO).
CODE/DB/LEG WRITE = 0. nexas = 0. prj = 0.
