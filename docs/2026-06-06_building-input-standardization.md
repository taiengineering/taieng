# BUILDING 입력 표준화 — 대조 진단표 + GPT 질문 프롬프트

> 작성: 2026-06-06 · 단계: 2단계(입력 데이터 ↔ 엔진 입력 대조) · 산출물 = 진단 문서(수정 아님)
> Supabase: `vwlahtguyggrhvslabax` · 입력 정의: `diagnosis_input_fields` (sector='BUILDING', is_active=true)
> 엔진 입력 스키마: `tai-api/schemas/legal_engine.py` `DiagnoseStep1Body`

## 0. 목적·경계
- 목적: 소비자 입력 데이터 표준화 (사용자 UI 감안). 표준화 대상 = **엔진에 영향을 주는 값**.
- 경계(불변): 법령엔진 판정 로직·스키마·데이터 모델(`factories`/`factory_process`/`equipment_assets`)·입력 화면 본 로직 = GPT 영역, 미수정.
- 원칙: 엔진 사용 여부가 불확실한 항목은 **추측 금지 → GPT 확인 후 확정**(임의 데이터 금지).

## 1. 핵심 사실 (재조사 결과)
- 엔진 입력 스키마 `DiagnoseStep1Body` = 타입 지정 필드 + **열린 `input`(dict)** 둘 다 존재. → "표준입력 틀은 없으나 영향을 주는 값이 들어온다".
- BUILDING 입력 정의 활성 약 36개 중, 엔진 타입 필드와 **이름이 일치하는 건 6개뿐**.
- 나머지는 (B) 이름 불일치 또는 (C) 열린 `input` 경유 → 엔진 실사용 여부를 엔진 코드로 확인해야 확정.
- 표준/자유 구분은 `field_type`에 이미 존재(select·boolean·multi_select=코드형, number·text=값/자유), 모름 처리 정책은 `unknown_handler`에 존재(대부분 ALLOW_AND_ASK_AFTER, `has_safety_manager`=BLOCK_PAY).

## 2. BUILDING 대조 분류 (스키마 이름매칭 기준 초안 — §5가 우선)

**A. 엔진 직결 확정 (6) — 이름 일치, 표준화 1순위**
건물 용도, 연면적, 지상 층수, 상시 근로자 수, 수전용량, 승강기 대수.

**B. 이름/형태 불일치 (5) — 매핑·교정 확인 필요 (GPT)**
- 가스시설 유무 ↔ 엔진 고압가스 유무 (뜻 동일 여부도 확인)
- 화학물질 유무 ↔ 엔진 화학물질 (거의 동일, 코드만 다름)
- 위험물저장소 유무 / 유류저장 유무 ↔ 엔진 위험물
- 에너지다소비 여부(O/X) ↔ 엔진 연간에너지사용량(숫자) — 형태 다름

**C. 엔진 사용 여부 불명 (약 25) — 열린 input 경유, GPT 판정 필요**
지하 층수, 건축연도, 주구조, 안전관리자 선임, 비상발전기(유무·용량), 에스컬레이터, 기계식주차장(유무·대수), 소방 4종(스프링클러·소화전·제연·비상방송), 저수조(유무·용량), 정화조(유무·용량), 냉각탑, 석면, 다중이용업소(여부·업종), 중앙공조, 복합건축물, 지하주차장 면적.

**D. 엔진 스키마엔 있으나 입력 화면엔 없음 (누락 후보)**
바닥면적, 종업원 수(상시근로자와 별개), 가스 용량(숫자), **보일러(유무·용량) — 입력에 항목 자체 없음**, 연간에너지사용량(숫자).

**🔧 항목 결함 1건**: "다중이용 업종"(multi_select)은 선택 목록(코드)이 비어 있음 → 자유 기입 → 오입력 위험.

## 3. GPT 질문 프롬프트 (참고용 — 현재는 Claude가 §5에서 직접 답함)

```
[역할] 당신은 TAI Safe 법령엔진(판정 로직·런타임 매칭·엔진 데이터) 담당입니다.
저는 소비자 입력부(법령진단/SaaS 입력 화면) 표준화 담당입니다.
입력 데이터를 표준화하려면 "엔진이 실제로 판정에 사용하는 입력 항목"을 정확히 알아야 합니다.
엔진을 수정하지 마세요. 지금은 "엔진이 무엇을 읽는지" 보고만 필요합니다.

[근거 필수 — 가장 중요]
각 항목의 엔진사용 판단에는 다음 중 최소 1개를 반드시 표시하세요:
 · 참조한 파일명   · 참조한 함수명   · 참조한 룰/데이터 키   · 참조한 조건문 또는 매핑명
근거가 없으면 엔진사용 여부는 반드시 "확인불가"로 표시하세요. 추측으로 Y 처리하지 마세요.

[질문] 입력코드 | 엔진사용(Y/N/확인불가) | 엔진이 받는 코드명(다르면 매핑) | 판단 근거 | 영향 법령·판정
[마지막] 3개 목록: ①유지 ②엔진엔 있으나 화면에 없음 ③화면엔 있으나 엔진 미사용
```

## 4. 다음 단계
- §5 검증 결과 기준 → ② 이름 정합(엔진 키에 입력 코드 맞추기) 우선, ③ 화면 간소화, 누락 입력 추가 검토.
- 그 후 4단계: 입력 화면(`tadmin/.../diagnosis-input-building.html`) 정합화 — 한 화면씩.
- 산업(INDUSTRIAL)·건설(CONSTRUCTION)은 BUILDING 검증 후 동일 패턴 반복.

## 5. Claude 검증 답변 (코드·DB 추적 — 2026-06-06 추가, §2보다 우선)

**경로 추적(라이브 기준):**
입력 → `run_diagnose_step1_v510`(`services/legal_v510_svc.py`)에서 `inp` 구성 → `normalize_input(inp)`(`services/input_normalizer.py`) → `_evaluate_conditions`→`_check_rule_conditions`(`services/legal_rules.py`)가 `context.get(condition_code)`로 룰 조건 1개 조회 → 룰은 `fetch_diagnosis_rules`(`services/legal_diagnosis_rules.py`) 우선순위 RUNTIME>V2>레거시, 운영=레거시 `master_building_legal_rules_legacy_contaminated`.

**판정 메커니즘:** 룰마다 `condition_code` 1개. 입력 키가 normalize 후 그 코드와 **정확히 같아야** 작동. `ALIAS_MAP`은 짧음(total_floor_area→building_area, electric_capacity→electrical_capacity_kw, floors→floor_count, gas_capacity→gas_capacity_kg, workers→worker_count, contract_amount_eok→contract_amount). 불리언→1/0. 미등록 키는 그대로 통과.

**① 엔진이 실제로 쓰는 입력 (레거시 룰 수, BUILDING+COMMON):**
연면적→building_area(117), 승강기→elevator_count(58), 다중이용여부 is_multi_use→is_multi_use(43), 수전용량→electrical_capacity_kw(32), 지상층수→floor_count(27), 상시근로자수→worker_count(13), 안전관리자선임 has_safety_manager(1).

**② 룰은 있으나 입력 이름이 어긋나 값이 버려짐 (정합화 핵심 = 진짜 병목):**
- 상시근로자수: 룰 90개가 `employee_count`로 검사 ↔ 입력은 `worker_count`(별칭 없음) → 90개 미작동
- 위험물/화학/고압가스/가스용량: 룰 `is_hazardous_material`(47)·`has_chemical_substance`(38)·`has_high_pressure_gas`(33)·`gas_capacity_kg`(56)·`gas_capacity_m3`(27) ↔ 입력 `has_hazmat_storage·has_oil_storage·has_chemical·has_gas`
- 에너지: 룰 `annual_energy_toe`(17) ↔ 입력 `is_energy_intensive`(O/X)

**③ 매칭 condition_code 없음 (엔진 미사용):**
주소, 지하층수, 건축연도, 주구조, 비상발전기, 에스컬레이터, 기계식주차장, 소방 4종, 저수조, 정화조, 냉각탑, 석면, 다중이용업종(multi_use_type), 중앙공조, 복합건축물, 지하주차장면적, **건물용도(building_use_type)**.

**§2 대비 정정:** §2-A에 넣었던 `building_use_type`은 레거시 condition_code로 **미사용**. §2-C에 넣었던 `is_multi_use`는 **실사용(43)**. §2는 스키마 이름매칭 기준 초안, **§5(라이브 룰 기준)가 우선**.

**근거 파일:** `legal_v510_svc.py`, `input_normalizer.py`(ALIAS_MAP), `legal_rules.py`(_check_rule_conditions), `legal_diagnosis_rules.py`(fetch_rules_v1); 룰 수 = `master_building_legal_rules_legacy_contaminated`(is_active, diagnosis_stage=1) 집계.

**가장 큰 시사점:** 표준화 핵심은 "필드 추가"가 아니라 **이름 정합**. worker_count↔employee_count, has_chemical↔has_chemical_substance, has_hazmat/oil↔is_hazardous_material, has_gas↔has_high_pressure_gas(+가스용량), is_energy_intensive↔annual_energy_toe만 맞춰도 수백 개 룰 조건이 살아남(06-03 READY 0건과 직결).

**남은 확인(진행 중):** (1) 운영 엔진 플래그 실제값(Railway 환경변수) (2) 건물용도→시설유형 is_*(is_medical_facility·is_officetel_or_lodging 등) 미연결 갭 (3) hospital_beds·student_count 등 시설유형 입력 누락.
