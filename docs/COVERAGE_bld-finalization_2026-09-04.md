# BUILDING FINALIZATION — COVERAGE (2026-09-04)

> WO-BLD-FINALIZATION 커버리지 매트릭스. 3섹터 SAFE 법령진단 → 공식 LEG runtime 연결.
> authority = 각 PR/배포. 이 문서는 커버리지 index.

## REPO ANCHORS
- tai-api main = 0ae502e0 (industrial/construction/building-leg route 전부, Railway 배포 SUCCESS 44b00733)
- tai-admin main = a8d837db (3섹터 진단 연결, Cloudflare Pages 배포)
- taieng main = f359861e (설계·판정 문서)
- LEG SoT = leg-prod wrfcedzgdrfupenzqhur

## 3-SECTOR ROUTE COVERAGE

| 섹터 | LEG route | backend runtime | tai-admin 연결 | route smoke | regression | live E2E |
|------|-----------|-----------------|----------------|-------------|------------|----------|
| INDUSTRIAL | /diagnose/industrial-leg | safe_industrial_leg_runtime | runDiagnosis MANUFACTURING 분기 | 422 PASS | PASS | DEFERRED(운영 QA) |
| CONSTRUCTION | /diagnose/construction-leg | safe_construction_leg_runtime | construction-extraction | 422 PASS | PASS | DEFERRED(운영 QA) |
| BUILDING | /diagnose/building-leg | safe_building_leg_runtime | runDiagnosis BUILDING 분기 | 422 PASS | PASS | DEFERRED(운영 QA) |

route smoke: unauth POST empty body → HTTP 422 (route deployed + schema gate 정상, 404 아님).
live E2E(AUTH→ownership→runtime→run_leg_diagnosis→/rtm/evaluate→full_result)는 미실행 → 운영 QA 이관.

## BUILDING FINALIZATION — PR/TEST COVERAGE

| PR | repo | 내용 | test |
|----|------|------|------|
| #256 | tai-api | building-leg route + runtime + schema (industrial 대칭) | building-leg 6 passed |
| #257 | tai-api | PATCH-A has_chemical_substance exact-key + alias 차단(화관법 C1) | PATCH-A 5 passed |
| #62 | tai-admin | BUILDING→building-leg 연결 + PATCH-B/B-1/B-2 | buildBuildingSafeInput 7 + canRunBuildingLeg 4 |

### PATCH 커버리지 (BUILDING)
- PATCH-A: has_chemical_substance _LEG_INPUT_FIELDS 누락 → build_facility BUILDING exact-key passthrough
- PATCH-A-1: has_chemical alias 이중생성(_LEG_CODE_TO_CONSUMER) → BUILDING sector alias 차단
- PATCH-B: prefill 자동승격 방지 → buildBuildingSafeInput(prefill 스냅샷 대비 변경분만)
  차단: building_use_code→building_use_type, building_area→total_floor_area,
        employee_count→worker_count, is_hazardous_material→has_hazardous_material
- PATCH-B-1: pf=null UNKNOWN 소실 → pure {} + production fail-closed(bFormPrefilled null)
- PATCH-B-2: stale snapshot → loadFactoryProfile 시작 bFormPrefilled=null + canRunBuildingLeg(loaded≠fid 차단)

### 입력 계약 커버리지 (buildBuildingSafeInput)
- 미확인(prefill 미변경) = omit
- 명시 false = false 보존
- 명시 0 = 0 보존
- 명시값 = value 전송
- pf=null(prefill 미로드/실패) = {} (fail-closed)
- semantic auto-promotion = 0 (4축 차단)

## 선행 설계·판정 커버리지 (이 세션)
- WP-1: 현존 오판정 결함(B1/B2/B3 default overwrite + B5 elevator + form_data + RAW firewall) = FULL CLOSED/배포
- AUDIT R2: LEG consumed 48 + ownership 5-class (taieng #24)
- SOURCE DESIGN A1~A7: acquisition 계약 (taieng #25)
- SEMANTIC-PROOF: 9축 PROOF_FAIL → SAFE 재사용 3축(OWNED_EXACT)만 (taieng #26)
- GAS-CHEM DECISION: G1/C1 input_split + WP3-BLOCKER 2건 (taieng #27)
- WP3-BLOCKER-FIX: GAS/CHEM OVER-CLAIM 제거 (tai-api, 배포)
- SAFE-FRONT-PRESTATE: SAFE bForm 7, LEG48 기준 U1~U4

## SAFE 재사용 커버리지 (BUILDING, SEMANTIC-PROOF 반영)
- OWNED_EXACT 3 (factories SAFE READ): floor_count, has_boiler, is_multi_use
- runtime/UI override: 나머지 45 + GAS-CHEM G1/C1 3 (SafeBuildingConsumerInput 48)
- 대장 파생(main_purpose_name/building_area 등): 실데이터 0.1~7% NULL + semantic FAIL → 미사용

## STATUS
IMPLEMENTATION = PASS · MERGE = PASS · DEPLOY = PASS · 3-SECTOR ROUTE SMOKE = PASS
LIVE FUNCTIONAL E2E = DEFERRED / 운영 QA 이관
BUILDING IMPLEMENTATION TRACK = CLOSED

운영 QA 1회 확인(production functional evidence): valid auth + owned factory/site + valid body
  → HTTP 2xx + status=success + full_result (3섹터 각 1회)

CODE/DB/LEG WRITE = 0 (이 문서). nexas 0. prj 0.
