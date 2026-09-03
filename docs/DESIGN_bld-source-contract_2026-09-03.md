# BUILDING SOURCE CONTRACT (2026-09-03)

> WO-BLD-SOURCE-DESIGN. A1~A6 설계 GATE 동결본 취합(정본). authority = 이 계약.
> 실제 값/매핑/컬럼/구현 = 후속 WO. 이 문서는 SOURCE CONTRACT(정책)이며 구현 아님.
> 선행 AUDIT: taieng/docs/AUDIT_bld-safe-wiring_2026-09-03.md (LEG consumed 48, ownership 5-class).

## PRE-LOCK (격리사실, CONFIRMED)
- PRE-1 BUILDING PAID marketing denominator = 67 (diagnosis_input_fields).
- PRE-2 build_facility N1 sector-gate 실재(_BUILDING_N1_FIELDS 32, FIX-001 test-lock).
- PRE-3 유료진단 precondition = auth_token(diagnosis_auth_log UUID) + payment_ref + disclaimer.
- PRE-4 factories 대장 컬럼 8 실재(main_purpose_name/code, building_area, arch_area, building_height,
  occupant_capacity, underground_floor_count, building_structure_name).

## GATE-A1 — PRIMARY 48 (FROZEN)
LEG ACTUAL CONSUMED = 48 = DIRECT_MAPPED 12 + INDIRECT_LEAF 36.
INDIRECT 36 = N1 33 + safety composite 2(has_truck_loading_unloading, has_manual_heavy_handling) + worker_count.
DUPLICATES 0 · DIRECT∩INDIRECT 0 · UNIQUE 48.
48 밖: has_building_elevator(SIDE-CAR derived, mapped 7 atom), elevator_count(NOT_CONSUMED),
  has_chemical(special, LEG mapped 부재).

## GATE-A2 — 8 SEMANTIC FAMILY (MECE, FROZEN)
- F1 BUILDING_REGISTER_CORE (7): floor_count, building_use_type, building_height_m, total_floor_area, occupancy_capacity, building_use_category, building_activity_type
- F2 HIGH_RISE_FLOOR_AGGREGATE (4): floor_area_sum_at_or_above_11f, performance_use_floor_area_sum, has_performance_assembly_use, is_target_facility_in_basement
- F3 SPECIAL_STRUCTURE_DESIGN (6): cantilever_projection_m, column_span_m, flat_plate_column_section_ratio, has_flat_plate_structure, authority_designated_special_structure, article32_3_alternative_confirmation_subject
- F4 UNDERGROUND_CONNECTION (8): underground_connection_entrance_distance_m, connection_open_space_floor_area_m2, connection_open_space_open_area_ratio, stair_or_ramp_effective_width_m, has_wall_between_connection_entrances, wall_between_connection_entrances_is_fire_resistant, has_stair_or_ramp_in_open_space, is_connected_to_subway_or_underground_mall
- F5 LAND_GROUND_CONDITION (6): is_collapse_risk_land, has_land_preparation, has_building_construction_activity, has_wet_land, has_water_seepage_risk, has_landfill_or_similar_ground
- F6 FACILITY_UTILITY_HAZMAT (11): has_boiler, has_gas, has_water_tank, has_hazmat_storage, has_emergency_gen, has_emergency_broadcast, is_energy_intensive, is_multi_use, has_gas_boiler_heating_system, has_centralized_gas_supply, has_hazardous_material_in_out_event
- F7 WORK_HANDLING_SAFETY (5): work_height_m, truck_loading_height_m, manual_handling_weight_kg, has_truck_loading_unloading, has_manual_heavy_handling
- F8 ORG_SCALE (1): worker_count
MECE: dup 0 / missing 0 / extra 0 / SUM 7+4+6+8+6+11+5+1 = 48.

## GATE-A3 — 8 FAMILY × 6 CONTRACT DIMENSION (FROZEN, +5 correction)
DIMENSION: D1 acquisition / D2 persistence / D3 override / D4 semantic / D5 unit / D6 readiness.
- F1: REGISTER_CANDIDATE / SAFE_ASSET_COLUMN / precedence-후증명 / SEMANTIC_UNVERIFIED / UNIT_UNVERIFIED / NEEDS_PROOF (floor_count 예외 = EXISTING_SAFE/OK/READY)
- F2: REGISTER_CANDIDATE(파생) / DIAGNOSIS_SNAPSHOT / UNRESOLVED / SEMANTIC_UNVERIFIED / UNIT_UNVERIFIED / NEEDS_PROOF
- F3: NEW_SAFE_UI / SAFE_ASSET_COLUMN / USER_FIRST / SEMANTIC_DECLARED / UNIT_UNVERIFIED / NEEDS_DEF_MAP
- F4: NEW_SAFE_UI / SAFE_ASSET_COLUMN / USER_FIRST / SEMANTIC_DECLARED / UNIT_UNVERIFIED / NEEDS_UI
- F5: RUNTIME_USER_INPUT / RUNTIME_ONLY / USER_FIRST / SEMANTIC_OK / UNIT_NA / NEEDS_UI
- F6A EXISTING_SAFE(has_boiler,is_multi_use): EXISTING_SAFE_COLUMN / SAFE_ASSET / SAFE_FIRST / SEMANTIC_OK / READY_NOW
- F6B SPECIAL(has_gas + chemical): GATE-A5 격리 (SEMANTIC_SPLIT_REQUIRED)
- F6C ABSENT_RUNTIME(나머지): RUNTIME_USER_INPUT / RUNTIME_ONLY / USER_FIRST / SEMANTIC_OK / NEEDS_UI
- F7: RUNTIME_USER_INPUT / RUNTIME_ONLY / USER_FIRST / SEMANTIC_OK / UNIT_OK / READY_NOW
- F8 worker_count: EXISTING_SAFE_COLUMN(후보) / SAFE_ASSET / OVERRIDE_UNRESOLVED / SEMANTIC_UNVERIFIED / NEEDS_PROOF
correction: C1 REGISTER_CANDIDATE(확정금지) · C2 F6 3-way split · C3 chemical/gas→A5 · C4 SEMANTIC_DECLARED(≠매핑증명) · C5 worker_count OVERRIDE UNRESOLVED.

## GATE-A4 — SEMANTIC PROOF PROTOCOL (FROZEN, +4 correction; proof 수행 0)
REGISTER_CANDIDATE = 9 (CLASS-R 5 + CLASS-D 2 + CLASS-E enum 2). 증명 전 전부 PRESENT_UNVERIFIED.

CLASS-R (대장 직접 5): worker_count↔employee_count, total_floor_area↔building_area/arch_area,
  building_use_type↔main_purpose_name, building_height_m↔building_height, occupancy_capacity↔occupant_capacity.
  명제 PR-1 semantic equivalence / PR-2 value domain / PR-3 unit equivalence / PR-4 null-default / PR-5 provenance.
  ⚠️ building_use_type PR-2 enum 매핑 = SEMANTIC-CRITICAL (chemical/gas급).

CLASS-D (층별개요 집계 2): floor_area_sum_at_or_above_11f, performance_use_floor_area_sum.
  명제 PD-1 source completeness / PD-2 floor discriminator / PD-3 area semantics / PD-4 performance-use taxonomy /
  PD-5 dedup-grouping / PD-6 determinism.
  ⚠️ HIGHEST DERIVATION RISK — fail 시 silent wrong aggregation. PROOF_FAIL → runtime fallback 강제.

CLASS-E (enum 2, C1 추가): building_use_category, building_activity_type ↔ LEG taxonomy(N1 tree leaf) 대조.

RESULT: PROOF_PASS → OWNED_SEMANTIC_VERIFIED(R/E) or OWNED_DERIVABLE(D). PROOF_FAIL → PRESENT_UNVERIFIED 유지 → runtime/UI fallback.
OVERRIDE = 증명 종속(verified→REGISTER_FIRST 후보, fail→USER_FIRST). 현재 UNRESOLVED.
PROOF 수행 = 별도 WO(BUILDING-SEMANTIC-PROOF), building-leg(WP-3) 전 선행 필수.

## GATE-A5 — CHEMICAL/GAS SEMANTIC SPLIT (FROZEN, +3 correction; auto alias 0)
LEG-side mapped_field 정본(leg-prod 실측):
  has_chemical_substance = 화관법 제31조 · 1 atom
  has_hazardous_material = 산안기준규칙 · 45 atom
  has_gas = 도시가스사업법 · 6 atom
  has_high_pressure_gas = 고압가스법 · 3 atom
  (has_chemical = LEG mapped 부재 0)

CHEMICAL: TAI has_chemical ↔ {has_chemical_substance, has_hazardous_material} = SEMANTIC_UNRESOLVED.
  판정명제 Q1(화관법 외연), Q2(산안 외연), Q3(1→2 fan-out or input split). 현재 OPT-C3(미전달)=임시(정답 아님).
  옵션: C1 input_split / C2 fan_out_verified / C3 keep_unmapped.
GAS: TAI has_gas ↔ {has_gas(도시가스), has_high_pressure_gas(고압가스)} = SEMANTIC_UNRESOLVED.
  판정명제 Q4(도시가스 외연), Q5(고압가스 포함), Q6(분리질문).
  옵션: G1 input_split / G2 도시가스만 / G3 fan_out_verified.
  ⚠️ WP3-BLOCKER-GAS-OVERCLAIM: 현재 has_high_pressure_gas=body.has_gas = ACTIVE DEFECT.
    "가스 사용"(도시가스 가능)→"고압가스" 과잉전달. building-leg(WP-3) 진입 전 Q4~Q6 판정 + OPT-G로 해소 필수.
Q1~Q6 = LEG SEMANTIC AUTHORITY(GPT/법령) 판정. Claude 판정 불가. AUTO ALIAS = 0.

## GATE-A6 — RUNTIME/UI INPUT ACQUISITION CONTRACT (FROZEN, +4 correction; UI 구현 0)
RUNTIME/UI = 35 (48 - OWNED_EXACT 3 - SEMANTIC_PROOF 9 - SPECIAL 1[has_gas]).
INPUT TYPE:
  numeric 10 (undefined|value, 0보존): work_height_m, truck_loading_height_m, manual_handling_weight_kg,
    cantilever_projection_m, column_span_m, flat_plate_column_section_ratio,
    underground_connection_entrance_distance_m, connection_open_space_floor_area_m2,
    connection_open_space_open_area_ratio, stair_or_ramp_effective_width_m
  boolean 25 (3-state undefined/true/false)
  (enum 2 building_use_category/building_activity_type = CLASS-E로 이동 → SEMANTIC_PROOF)

PARENT-CHILD (건설 RUNTIME20 패턴):
  F4 지하연계 3-depth: is_connected_to_subway_or_underground_mall → distance/open_space/wall/stair
    → wall_between_connection_entrances_is_fire_resistant(grandchild) / stair_or_ramp_effective_width_m(grandchild)
  F3 평판구조 2-depth: has_flat_plate_structure → flat_plate_column_section_ratio (+column_span_m 연관)
  F7 건설검증 2-depth: has_truck_loading_unloading→truck_loading_height_m, has_manual_heavy_handling→manual_handling_weight_kg
  계약: parent !== true → child undefined.

PERSISTENCE: RUNTIME_ONLY(P3) F5토지·F7산안·운영이벤트 / STABLE_USER_FACT 후보(P1) F3·F4·F6C고정설비.
  ⚠️ P1 vs P3 = UNRESOLVED (자산화 판정, 신규 SAFE 컬럼 S6 수반).
OVERRIDE: USER_INPUT_FIRST (자산화 시 SAFE_FIRST + 진단 override).
3-STATE: WP-1 UI_UNKNOWN sentinel + 건설 normalizeNum 재사용.
⚠️ C3 F3/F4 전문 numeric(cantilever/column_span/connection_ratio) = EXPERT_INPUT_RISK.
  일반 사용자 입력 불가 수준 → UI 단계 재검토(전문가 입력 / 대장·설계도서 파생 / 조건부 노출).

## 48 최종 분류 (SOURCE CONTRACT)
- OWNED_EXACT 3: floor_count, has_boiler, is_multi_use (EXISTING_SAFE_COLUMN, READY_NOW)
- SEMANTIC_PROOF 9: CLASS-R 5(worker_count/total_floor_area/building_use_type/building_height_m/occupancy_capacity)
  + CLASS-D 2(floor_area_sum/performance_use) + CLASS-E 2(building_use_category/building_activity_type) — proof 전 PRESENT_UNVERIFIED
- SPECIAL 1: has_gas (semantic split, WP3-BLOCKER)
- RUNTIME/UI 35: numeric 10 + boolean 25
검산 = 3+9+1+35 = 48.
48 밖: has_chemical(special, GATE-A5), has_building_elevator(SIDE-CAR derived), elevator_count(NOT_CONSUMED).

## 선행 WO (building-leg WP-3 진입 전 필수)
1. BUILDING-SEMANTIC-PROOF (CLASS-R 5 + CLASS-D 2 + CLASS-E 2 = 9축 증명, PR/PD/enum 명제)
2. GAS OVER-CLAIM 해소 (WP3-BLOCKER, Q4~Q6 판정 + OPT-G)
3. CHEMICAL/GAS LEG SEMANTIC AUTHORITY 판정 (Q1~Q6, GPT/법령)
4. P1 vs P3 자산화 판정
5. F3/F4 EXPERT_INPUT_RISK UI 재검토

## STATUS
BUILDING SOURCE DESIGN 설계 GATE A1~A6 = FROZEN. 이 문서 = SOURCE CONTRACT 정본(계약).
값/매핑/컬럼/UI/route/구현 = 0 (후속 WO). CODE/DB/LEG write = 0. nexas = 0. prj = 0.
Frozen 순서: DOC CLOSE ✅ → SOURCE DESIGN(이 문서) → SEMANTIC-PROOF → BUILDING-LEG(WP-3) → UI → 3-SECTOR CANARY(WP-2).
