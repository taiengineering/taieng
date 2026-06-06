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

## 2. BUILDING 대조 분류

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

## 3. GPT 질문 프롬프트 (엔진 담당에게 그대로 전달)

```
[역할] 당신은 TAI Safe 법령엔진(판정 로직·런타임 매칭·엔진 데이터) 담당입니다.
저는 소비자 입력부(법령진단/SaaS 입력 화면) 표준화 담당입니다.
입력 데이터를 표준화하려면 "엔진이 실제로 판정에 사용하는 입력 항목"을 정확히 알아야 합니다.
추측 금지 — 엔진 코드/데이터 근거로만 답하고, 불확실하면 "확인불가"로 표시하세요.
엔진을 수정하지 마세요. 지금은 "엔진이 무엇을 읽는지" 보고만 필요합니다.

[배경 사실]
- 입력 정의: diagnosis_input_fields (sector='BUILDING', is_active=true), 약 36개 필드.
- 엔진 입력 스키마: schemas/legal_engine.py 의 DiagnoseStep1Body
  = 타입 지정 필드 + 열린 input(dict) 둘 다 존재.
- BUILDING에서 스키마 타입 필드와 이름이 일치하는 건 아래 A 6개뿐.
  나머지는 열린 input으로만 들어오거나(C), 이름이 다릅니다(B).

[질문] 아래 각 항목에 대해 표로 답하세요.
형식:  입력코드 | 엔진사용(Y/N/확인불가) | 엔진이 받는 코드명(다르면 매핑) | 영향 주는 법령·판정(한 줄)

A. 이름 일치(엔진 직결 추정):
building_use_type(건물용도), total_floor_area(연면적), floor_count(지상층수),
worker_count(상시근로자수), electric_capacity(수전용량), elevator_count(승강기대수)

B. 이름/형태 불일치 — 매핑 확인 필요:
has_gas(가스시설) ↔ has_high_pressure_gas?
has_chemical(화학물질) ↔ has_chemical_substance?
has_hazmat_storage(위험물저장소) / has_oil_storage(유류저장) ↔ has_hazardous_material?
is_energy_intensive(에너지다소비 O/X) ↔ annual_energy_toe(숫자)?

C. 엔진 사용 여부 불명(열린 input 경유) — 사용/미사용 판정 요청:
address, basement_count, built_year, main_structure, has_safety_manager,
has_emergency_gen, emergency_gen_kw, escalator_count, has_mech_parking, mech_parking_count,
has_sprinkler, has_fire_hydrant, has_smoke_control, has_emergency_broadcast,
has_water_tank, water_tank_ton, has_septic_tank, septic_tank_ton, has_cooling_tower,
has_asbestos, is_multi_use, multi_use_type, has_central_hvac, is_complex_building, underground_area

D. 엔진 스키마엔 있는데 BUILDING 입력 화면엔 없음 — 누락인지/입력 필요한지 확인:
floor_area(바닥면적), employee_count(종업원수), gas_capacity_kg·gas_capacity_m3(가스용량),
has_boiler·boiler_capacity_kw(보일러), annual_energy_toe(연간에너지)

[추가 1건] multi_use_type(다중이용 업종)은 선택 목록(코드)이 비어 있습니다.
엔진이 이 값을 쓴다면, 어떤 코드 목록이어야 하는지 알려주세요.
```

## 4. 다음 단계
- GPT 답 수신 → C(약 25개) "표준화 대상 / 자유입력 OK" 확정, B(5개) 이름 매핑 확정, D 누락 여부 확정.
- 그 후 4단계: 입력 화면(`tadmin/.../diagnosis-input-building.html`) 정합화 — 한 화면씩.
- 산업(INDUSTRIAL)·건설(CONSTRUCTION)은 BUILDING 검증 후 동일 패턴 반복.
