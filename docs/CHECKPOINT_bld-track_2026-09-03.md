# BUILDING TRACK — SESSION CHECKPOINT (2026-09-03)

> 세션 종료 시점 BUILDING TRACK 전체 상태 동결. 기존 동결값 취합(신규 설계/수치변경 0).
> authority = 각 원본 문서/PR. 이 문서는 index/handoff.

## REPO ANCHORS
- tai-api main = 9dac9bb01fd0bbe2fa5c0f3f1539bf99fe12b805 (WP-1 + WP3-BLOCKER-FIX, 배포 SUCCESS)
- taieng main = f359861e (설계·판정 문서 5종 merged)
- LEG SoT = leg-prod wrfcedzgdrfupenzqhur (production_semantic_repository 348)

## 완료 단계 (CLOSED)
1. WP-1 (현존 오판정 결함) = FULL CLOSED / 배포
   - B1/B2/B3 default overwrite 제거 · B5 elevator 0→False · form_data round-trip · RAW→CANONICAL firewall
   - tai-api b3e8c3b0. PR #248/#249/#250/#251.
2. AUDIT A/B/C R2 = taieng #24 merged
   - TRACK A(TAI transport, PRE-WP1): EXACT 50/DRIFT 3/DROPPED 14
   - TRACK B(LEG consumption): DIRECT 12 + INDIRECT 36 = LEG ACTUAL CONSUMED 48
   - TRACK C(SAFE ownership 5-class): OWNED_EXACT 3/SEMANTIC_VERIFIED 0/DERIVABLE 0/PRESENT_UNVERIFIED 7/ABSENT_SOURCE 38
3. SOURCE DESIGN A1~A7 = taieng #25 merged (SOURCE CONTRACT 정본)
4. SEMANTIC-PROOF = taieng #26 merged (9축 PROOF_FAIL → runtime/UI, REGISTER 폐기)
5. GAS-CHEM DECISION = taieng #27 merged (G1/C1 input_split + WP3-BLOCKER 2건)
6. WP3-BLOCKER-FIX = tai-api 9dac9bb0 merged/배포 (GAS/CHEM OVER-CLAIM 제거, WP3-BLOCKER COUNT 0)
7. SAFE-FRONT-PRESTATE = FROZEN (SAFE bForm 7, LEG48 기준 U1~U4)

## 48 CONTRACT (동결값)
LEG ACTUAL CONSUMED = 48 (audit R2, 정상계약 기준 FROZEN)
- DIRECT_MAPPED 12: total_floor_area, has_emergency_gen, has_emergency_broadcast, has_gas, has_hazmat_storage,
  has_water_tank, is_multi_use, is_energy_intensive, has_boiler, work_height_m, truck_loading_height_m, manual_handling_weight_kg
- INDIRECT_LEAF 36: N1 33 + safety composite 2(has_truck_loading_unloading, has_manual_heavy_handling) + worker_count
- 48 밖: has_building_elevator(SIDE-CAR derived, mapped 7 atom), elevator_count(NOT_CONSUMED), has_chemical(special)

## OWNERSHIP 5-class (48, SEMANTIC-PROOF 반영)
- OWNED_EXACT 3: floor_count, has_boiler, is_multi_use (즉시 SAFE)
- SEMANTIC_PROOF 9 → 전부 PROOF_FAIL → RUNTIME/UI fallback (REGISTER 폐기):
  worker_count, total_floor_area, building_use_type, building_height_m, occupancy_capacity,
  floor_area_sum_at_or_above_11f, performance_use_floor_area_sum, building_use_category, building_activity_type
- SPECIAL 1: has_gas (G1 split)
- RUNTIME/UI 35
실질 acquisition: OWNED_EXACT 3 + RUNTIME/UI 44 + SPECIAL 1 = 48.

## GAS/CHEM DECISION (RESOLVED)
- D-GAS G1 INPUT_SPLIT: 도시가스(has_gas/도시가스법) + 고압가스(has_high_pressure_gas/고압가스법) 분리
- D-CHEM C1 INPUT_SPLIT: 화관법 도급(has_chemical_substance) + 산안 유해물질(has_hazardous_material) 분리
- OVER-CLAIM 2건 = REMOVED/DEPLOYED (WP3-BLOCKER COUNT 0)

## SAFE-FRONT-PRESTATE (FROZEN)
SAFE frontend = tai-admin diagnosis-step1 bForm 7 (건물진단 입력면; tai-www 마케팅 별개 제품 제외)
- bForm 7: building_use, area, floors, workers, kw, gas, haz
- BUILDING endpoint = v510 /diagnose/step1 (building-leg 미구현)
U1~U4 (LEG48 기준):
- U1 REUSE(UI_SHELL) 4: total_floor_area, floor_count, building_use_type, worker_count (값은 runtime, SAFE 데이터 아님)
- U2 PLACEMENT 0
- U3 MODIFY 2: has_gas/has_chemical split (+ 도시가스 SAFE 입력 신규 필요)
- U4 NEW 44: N1 31 + 시설상세 (building-leg 신규 수집)

## 미결 / 다음 (building-leg WP-3 본선)
building-leg 신규 route (industrial-leg/construction-leg 대칭):
- backend: safe_building_canonical_assembler + safe_building_leg_runtime + /legal-engine/diagnose/building-leg
- SAFE UI: bForm 7 → LEG48 커버 확대 (U4 NEW 44 신규 + U3 split 2 + U1 UI_SHELL 4)
- N1 31 전문값(cantilever/column_span/flat_plate 등) = EXPERT_INPUT_RISK
- G1/C1 명시 입력(도시가스/고압가스/화관법도급/산안유해물질 4 소비자 사실)
- SEMANTIC_PROOF 9축 = runtime 입력(SAFE 저장값 아님)

병렬 가능:
- taieng PR #27 문서의 "48 불변/FROZEN" 문구 = frontend denominator 정본 오사용 방지 정정
  (LEG 소비 48 ≠ SAFE frontend 입력 수; SAFE bForm 7 → 확대 대상)

Frozen 순서: DOC CLOSE ✅ SOURCE DESIGN ✅ SEMANTIC-PROOF ✅ GAS-CHEM ✅ WP3-BLOCKER-FIX ✅ SAFE-FRONT-PRESTATE ✅
  → BUILDING-LEG(WP-3 본선) → UI → 3-SECTOR CANARY(WP-2, live E2E deferred)

3섹터 상태:
- INDUSTRIAL = backend LIVE/CLOSED · frontend MERGED+DEPLOYED/CLOSED (GATE-5 canary deferred)
- CONSTRUCTION = backend LIVE/CLOSED · frontend MERGED+DEPLOYED/CLOSED
- BUILDING = WP-1 CLOSED + 설계·판정 선행 전체 완료 · building-leg 본선 미착수

## STATUS
CODE/DB/LEG WRITE = 0 (이 CHECKPOINT). nexas 0. prj 0.
이 문서 = 세션 종료 상태 index. 각 값 authority = 원본 PR/문서.
