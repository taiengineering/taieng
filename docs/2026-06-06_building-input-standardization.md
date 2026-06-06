# BUILDING 입력 표준화 — 대조 진단표 + GPT 질문 프롬프트

> 작성: 2026-06-06 · 단계: 2단계(입력 데이터 ↔ 엔진 입력 대조) · 산출물 = 진단 문서(수정 아님)
> Supabase: `vwlahtguyggrhvslabax` · 입력 정의: `diagnosis_input_fields` (sector='BUILDING', is_active=true)
> 엔진 입력 스키마: `tai-api/schemas/legal_engine.py` `DiagnoseStep1Body`

## 0. 목적·경계
- 목적: 소비자 입력 데이터 표준화 (사용자 UI 감안). 표준화 대상 = **엔진에 영향을 주는 값**.
- 경계(불변): 법령엔진 판정 로직·스키마·데이터 모델(`factories`/`factory_process`/`equipment_assets`)·입력 화면 본 로직 = GPT 영역, 미수정(읽기는 허용).
- 원칙: 엔진 사용 여부가 불확실한 항목은 **추측 금지 → 코드/데이터 근거로만 확정**(임의 데이터 금지).

## 1. 핵심 사실
- 엔진 입력 스키마 `DiagnoseStep1Body` = 타입 지정 필드 + **열린 `input`(dict)** 둘 다 존재.
- 그러나 **판정에 쓰이는 컨텍스트는 `normalize_input(inp)`** (facility_ctx 아님). §5 참조.

## 2. BUILDING 대조 분류 (스키마 이름매칭 기준 초안 — §5/§6이 우선)
**A. 이름 일치(6):** 건물용도, 연면적, 지상층수, 상시근로자수, 수전용량, 승강기대수.
**B. 이름/형태 불일치(5):** 가스시설↔고압가스, 화학물질↔화학물질, 위험물저장소/유류↔위험물, 에너지다소비(O/X)↔연간에너지(숫자).
**C. 불명(약25):** 지하층수·건축연도·주구조·안전관리자선임·비상발전기·에스컬레이터·기계식주차장·소방4종·저수조·정화조·냉각탑·석면·다중이용(여부·업종)·중앙공조·복합건축물·지하주차장면적.
**D. 스키마엔 있으나 화면 없음:** 바닥면적·종업원수·가스용량·보일러·연간에너지.
**🔧 결함:** 다중이용 업종(multi_select) 선택목록 비어 있음.

## 3. (참고) GPT 질문 프롬프트 — 현재는 Claude가 §5·§6에서 직접 답함
형식: 입력코드 | 엔진사용(Y/N/확인불가) | 엔진 코드명 | 판단 근거(파일/함수/룰키/조건) | 영향 법령. 마지막 3목록(①유지 ②엔진엔있고화면없음 ③화면엔있고엔진미사용). 근거 없으면 "확인불가", 추측 Y 금지.

## 4. 다음 단계
- §5·§6 기준 → ② 이름 정합 우선 → 건물용도→시설유형 매핑 → 화면 간소화/누락 추가.
- 4단계: 입력 화면(`tadmin/.../diagnosis-input-building.html`) 정합화 — 한 화면씩.
- 산업(INDUSTRIAL)·건설(CONSTRUCTION)은 BUILDING 검증 후 동일 패턴 반복.

## 5. Claude 검증 답변 (코드·DB 추적 — §2보다 우선)

**경로(라이브):** 입력 → `run_diagnose_step1_v510`(`legal_v510_svc.py`)에서 `inp` 구성 → `normalize_input(inp)`(`input_normalizer.py`) → `_check_rule_conditions`(`legal_rules.py`)가 `context.get(condition_code)`로 조건 1개 조회 → 룰은 `fetch_diagnosis_rules`(`legal_diagnosis_rules.py`), 운영=레거시 `master_building_legal_rules_legacy_contaminated`.

**메커니즘:** 룰마다 `condition_code` 1개. 입력 키가 normalize 후 그 코드와 **정확히 같아야** 작동. `ALIAS_MAP`(total_floor_area→building_area, electric_capacity→electrical_capacity_kw, floors→floor_count, gas_capacity→gas_capacity_kg, workers→worker_count, contract_amount_eok→contract_amount). 불리언→1/0. 미등록 키는 그대로.

**① 엔진이 실제로 쓰는 입력 (레거시 룰 수 BUILDING+COMMON):**
연면적→building_area(117), 승강기→elevator_count(58), 다중이용여부 is_multi_use(43), 수전용량→electrical_capacity_kw(32), 지상층수→floor_count(27), 상시근로자수→worker_count(13), 안전관리자선임 has_safety_manager(1).

**② 룰은 있으나 입력 이름이 어긋나 값이 버려짐 (정합화 핵심):**
- 상시근로자수: 룰 90개가 `employee_count` ↔ 입력 `worker_count`(별칭 없음) → 90개 미작동
- 위험물/화학/고압가스/가스용량: 룰 `is_hazardous_material`(47)·`has_chemical_substance`(38)·`has_high_pressure_gas`(33)·`gas_capacity_kg`(56)·`gas_capacity_m3`(27) ↔ 입력 `has_hazmat_storage·has_oil_storage·has_chemical·has_gas`
- 에너지: 룰 `annual_energy_toe`(17) ↔ 입력 `is_energy_intensive`(O/X)

**③ 매칭 condition_code 없음 (엔진 미사용):**
주소·지하층수·건축연도·주구조·비상발전기·에스컬레이터·기계식주차장·소방4종·저수조·정화조·냉각탑·석면·다중이용업종(multi_use_type)·중앙공조·복합건축물·지하주차장면적·**건물용도(building_use_type)**.

**§2 정정:** `building_use_type` = 미사용(레거시 condition_code 아님). `is_multi_use` = 실사용(43). §5가 우선.

**근거 파일:** `legal_v510_svc.py`, `input_normalizer.py`(ALIAS_MAP), `legal_rules.py`(_check_rule_conditions), `legal_diagnosis_rules.py`(fetch_rules_v1); 룰 수 = `master_building_legal_rules_legacy_contaminated`(is_active, stage1) 집계.

## 6. 보강 조사 — 남은 확인 종결 (2026-06-06)

**(1) 라이브 엔진 경로 = 레거시 확정 (코드 근거).**
`legal_runtime_fetch.py` 헤더: "[CATALOG ONLY - NOT DIAGNOSIS SOURCE] runtime_metadata_resolution = 법령 카탈로그. 진단 경로 격리됨(2026-05-31)". `USE_RUNTIME_ENGINE` 기본 false, `USE_V2_ENGINE` 기본 false. → 진단은 `fetch_rules_v1`(레거시) 기본·설계상 경로. (누가 `TAI_USE_V2_ENGINE=true`로 켜면 master_rule_v2 경로로 변경 — 운영 설정 아님.)

**(2) 역방향 갭 — "엔진은 검사하는데 입력 소스가 아예 없는 조건"(진짜 누락):**
- **건물용도가 0개 룰을 구동.** building_use_type은 condition_code가 아니고, 거기서 시설유형 플래그(is_medical_facility·is_hospital_or_clinic·is_officetel_or_lodging·is_apartment_or_elderly·is_residential_or_care·is_warehouse·is_parking_area 등)를 **파생하지 않음** → 시설유형 룰 전부 미작동. 건물용도→시설유형 코드 매핑 필요.
- `building_grade`(13건): 입력 소스 없음.
- `employee_count`(90건): 입력 worker_count만 → 별칭 필요(②와 동일, 최대 임팩트).
- `hospital_beds`(5)·`student_count`(4): 의료/학교 건물 룰이 쓰나 BUILDING 화면엔 없음(SPECIAL_FACILITY 입력에만 존재).

**(3) 표준화 우선순위(결론):** ① 이름 정합(employee_count·위험물·가스·에너지) → ② 건물용도→시설유형 매핑 → ③ 화면 간소화(§5-③). 이 셋이 06-03 READY 0건의 직접 원인.

## 7. 산업·건설 + 미확인 3건 + 실제폼 발견 (2026-06-06)

### 7-1. 섹터 그룹 (`get_sector_groups`, legal_helpers.py)
- BUILDING→[COMMON,BUILDING,…] · MANUFACTURING→[COMMON,MANUFACTURING,…] · CONSTRUCTION→[COMMON,CONSTRUCTION,…]. 결합그룹은 stage1 0건.
- 레거시 stage1 활성: COMMON 861 · BUILDING 425 · MANUFACTURING 288 · CONSTRUCTION 176. COMMON은 전 섹터 공통.

### 7-2. INDUSTRIAL (룰=MANUFACTURING+COMMON) — diagnosis_input_fields 기준
- 사용(이름 일치): total_floor_area→building_area, electric_capacity→electrical_capacity_kw, **has_chemical_substance**(MFG17+COMMON38), **has_high_pressure_gas**(MFG36+COMMON33), **has_boiler**(MFG5), worker_count(MFG9+COMMON11), has_safety_manager(1). → BUILDING과 달리 위험물·가스·보일러 코드 일치.
- 이름 불일치: has_hazardous_material↔is_hazardous_material(124); worker_count↔employee_count(63); ksic_major↔is_factory_registered(35, 라이브 normalize 미파생); gas_capacity_kg(97) 숫자입력 없음.
- 매칭 없음: address, ksic_sub, has_hazmat_storage, has_dust_work, has_noise_work, has_confined_space, has_radiation. process_list/equipment_list=stage2/3.

### 7-3. CONSTRUCTION (룰=CONSTRUCTION+COMMON) — diagnosis_input_fields 기준
- 금액 룰: contract_amount(65)+construction_amount(34)=99 (엔진은 contract_amount_eok에서 파생).
- 사용: construction_type(1); is_construction_site(4, 코드가 1로 채움); worker_count→COMMON(11). employee_count(CONS7+COMMON42) 미작동.
- 매칭 없음(stage1): project_duration, project_address, has_subcontractor, subcontractor_count, 위험작업 불리언 전부, operation_shift. 입력없는 룰코드: TUNNEL_*, WATER_*, is_hazardous_material(5), building_area(4), electric_capacity(2).

### 7-4. 미확인 3건 — 종결
- (1) 섹터명: **엔진코드 MANUFACTURING = 표시코드 INDUSTRIAL**, SPECIAL_FACILITY=BUILDING. 변환 `routers/anonymous_diagnosis.py`(_SECTOR_NORMALIZE, SECTOR_BY_KIND). v510 라우터는 MANUFACTURING만 허용(INDUSTRIAL 불가).
- (다중엔진) **무료진단=`run_diagnose_step1_runtime`(runtime_metadata_resolution)+고정 프리셋**. v510(factory_id)=레거시. 진입점마다 엔진 다름.
- (3) 건설 위험작업 불리언(has_excavation 등) stage1·stage2 **직접 미소비**. stage2는 process_id(→process_lv3→PROCESS_LV3_CONDITION_MAP)·equipment_type_code(→EQUIPMENT_CODE_CONDITION_MAP)·work_types로 has_* 생성(`code_condition_resolver.py`).

### 7-5. ★실제 입력폼 ≠ diagnosis_input_fields (중대 발견)
실제 tadmin 폼 `diagnosis-input-construction.html`(safe.taieng.co.kr):
- 금액 필드명 = **contract_amount_eok** (project_amount 아님; project_amount는 DB정의에만 존재).
- 근로자 = **direct_workers + total_workers** (worker_count 아님).
- 위험토글 = has_tunnel_work, has_bridge_work, has_excavation, has_crane, has_high_work, has_blasting, has_electrical_work, has_gas_work, has_chemical_work + has_safety_manager/health_manager/safety_training/ppe/emergency_plan.
- construction_type 값 = 건축공사/토목공사/산업설비/조경공사/전문건설/기타.
- **엔드포인트: 폼은 엔진 직접호출 아님** → `POST /diagnosis/create`(또는 PATCH `/diagnosis/{id}`)로 input_data 저장 후 `diagnosis-step2.html`로 이동. 엔진 매핑은 `/diagnosis` 처리에서.
- **→ 세 곳이 서로 다름: (a) diagnosis_input_fields DB · (b) 실제 tadmin HTML 폼 · (c) 엔진 condition_code. 표준화는 (b)↔(c) 기준으로 재도출 필요. §2·§5·§6·§7-2·7-3은 (a) 기준이므로 (b) 확인 후 갱신해야 함.**
