# WO-INPUT-BINDING-ARCHITECTURE-001
# 입력표준 → 의무생성기 Binding Layer 규격

**작성일:** 2026-06-24 | **상태:** 완료 (바인딩 규격 정의, 읽기 전용)
**선행:** WO-OBLIGATION-INSTANCE-IMPLEMENTATION-001
**금지 (전부 준수):** 새 매핑/Trigger/Harvest/Review/법령분석 없음. 변환 계층만 정의.
**목적:** 입력표준 → obligation_generator 연결 규격 정의.

> "입력이 있냐 없냐"가 아니라, 만들어진 입력표준을 생성기 언어로 변환하는 계층.

---

## 결론 먼저

```
입력표준과 generator는 이미 같은 언어를 쓴다.

  EXISTS (has_*): generator 요구 28개 → 입력표준 100% 일치 (MISSING 0)
  SCOPE (sector/ksic): facility_profiles에 정규화 완료
  THRESHOLD (numeric): facility_profiles에 9개 *_value + *_state 완비

→ Binding Layer는 "변환"이 아니라 "조립"이다.
→ 정규화 거의 불필요. 필드명이 이미 일치.
→ 다음 WO에서 즉시 구현 가능.
```

---

## TASK-001: generator 요구 입력 전수

```
generator(cmc CONFIRMED 452)가 실제 요구하는 입력:

EXISTS형 (has_*) — 28개 distinct:
  has_hazardous_material(68) has_confined_space(50+18)
  has_dust_work(37) has_chemical_substance(32)
  has_asbestos_demo(30) has_crane(25) has_asbestos(23)
  has_excavation(23) has_diving(22+5) has_scaffold(22)
  has_high_place_work(19) has_welding(18) has_pile_work(17)
  has_elevator(14) has_radiation(12) has_boiler(8)
  has_pressure_vessel(7) has_forklift(7) has_conveyor(7)
  has_demolition(6) has_grinding(6) has_tower_crane(5+2)
  has_high_pressure_gas(4+2+1) has_rolling(4) has_blasting(4+1)
  has_press(4) has_gondola(3) has_injection(1)

SCOPE형:
  sector (INDUSTRIAL/CONSTRUCTION/BUILDING)
  ksic_code (sector 추론용)

THRESHOLD형 (현재 cmc 거의 없음, 향후):
  worker_count, floor_area, electrical_kw, gas_capacity 등

UNIVERSAL형:
  입력 불필요 (sector만) — 단 현재 CONFIRMED 0
```

---

## TASK-002: diagnosis_input_fields 대조 (1:1 매핑)

```
★ generator 요구 has_* 28개 전부 입력표준에 존재.
   MISSING = 0건.

매핑 (전부 1:1, 변환 불필요):
  generator.has_welding      ← diagnosis_input_fields.has_welding
  generator.has_crane        ← diagnosis_input_fields.has_crane
  generator.has_excavation   ← diagnosis_input_fields.has_excavation
  generator.has_confined_space ← diagnosis_input_fields.has_confined_space
  ... (28개 전부 동일 field_code)

→ 입력표준 설계 시 이미 generator와 같은 명명 사용.
→ field_type='boolean'으로 통일.
→ sector도 입력표준에 명시됨 (INDUSTRIAL/CONSTRUCTION/BUILDING).
```

| generator 요구 | 입력표준 field_code | 변환 |
|---|---|---|
| has_* 28개 | 동일 (has_*) | 없음 (직접) |
| sector | facility_profiles.sector | 직접 |
| ksic_code | facility_profiles.ksic_code | 직접 |
| worker_count | facility_profiles.regular_workers_value / total_workers_value | 선택 |
| building_area | facility_profiles.floor_area_value | 직접 |
| electrical_kw | facility_profiles.electrical_kw_value | 직접 |
| gas_capacity | facility_profiles.gas_capacity_value | 직접 |

---

## TASK-003: 입력 정규화 규칙

```
EXISTS (has_*):
  정규화 불필요. 입력표준 field_code = generator input_field.
  facility_profiles.input_fields JSON 또는
  진단 입력 boolean을 그대로 사용.

SCOPE:
  sector NULL → ksic_code로 추론
    C* → INDUSTRIAL
    F* (건설) → CONSTRUCTION
    건물용도 → BUILDING

THRESHOLD (worker_count 동의어 정규화):
  worker_count = COALESCE(
    total_workers_value,      -- 우선
    regular_workers_value)    -- 차선
  building_area = floor_area_value
  → *_state='PROVIDED'인 것만 THRESHOLD 평가에 사용.
  → 'MISSING'이면 obligation status='MISSING_DATA'.

→ 정규화 규칙은 "동의어 흡수"와 "sector 추론"뿐.
→ 필드명 변환은 거의 없음 (이미 일치).
```

---

## TASK-004: API 입력 (건축물대장)

```
건축물대장 API (building_register):
  주소 → building_register 조회
    → total_floor_area  → generator.building_area (floor_area_value)
    → building_use      → generator.use_code (use_code_value)
    → built_year        → (현재 cmc THRESHOLD 미사용)
    → main_structure    → (현재 cmc THRESHOLD 미사용)

흐름:
  주소 입력 → building_register API
    → facility_profiles.*_value 채움 (provenance='API')
    → generator가 facility_profiles에서 읽음

→ API는 facility_profiles를 채우는 소스.
→ generator는 facility_profiles만 보면 됨 (API 직접 호출 안 함).
→ provenance로 입력/추론/API 구분 가능.
```

---

## TASK-005: Generator Input Contract

```json
{
  "factory_id": "uuid",
  "sector": "INDUSTRIAL",          // facility_profiles.sector
  "ksic_code": "C28",              // sector 추론 fallback

  // THRESHOLD (facility_profiles.*_value, state=PROVIDED만)
  "worker_count": 50,              // total_workers_value
  "building_area": 5000,           // floor_area_value
  "electrical_kw": 300,            // electrical_kw_value
  "gas_capacity": 100,             // gas_capacity_value

  // EXISTS (has_*, 입력표준과 1:1)
  "has_welding": true,
  "has_crane": false,
  "has_excavation": true,
  "has_confined_space": false,
  "has_chemical_substance": true
  // ... 28개 has_* (입력된 것만 true)
}
```

```
Contract 생성 규칙:
  1. facility_profiles(factory_id) 읽기
  2. sector/ksic_code → 그대로
  3. *_value (state='PROVIDED') → 숫자 필드
  4. input_fields/진단 boolean → has_*
  5. 누락 has_*는 false (기본)
```

---

## TASK-006: Gap 측정

```
입력표준(diagnosis_input_fields 98개) 기준:

generator가 실제 요구하는 입력 (CONFIRMED 452 기준):
  EXISTS has_* 28개  → 즉시 연결 가능 (100% 일치)
  SCOPE 2개 (sector, ksic) → 즉시 연결
  THRESHOLD numeric → facility_profiles에 완비 (단 cmc THRESHOLD 거의 없음)

Gap 분류:
  즉시 generator 연결 가능:  30개 (has_* 28 + sector + ksic)
  정규화 필요:               2~3개 (worker_count 동의어, sector 추론)
  추가 변환 필요:            0개

→ 입력표준 98개 중 generator가 쓰는 것은 ~30개.
→ 나머지 68개는 THRESHOLD/APPENDIX/미래 확장용 (현 cmc 미사용).
→ Gap 거의 없음. 바인딩은 조립 수준.
```

---

## Binding Layer 전체 구조

```
[입력 수집]
  진단 UI → diagnosis_input_fields 기준 입력
  주소 → building_register API
        ↓
[저장]
  facility_profiles (정규화 저장)
    sector/ksic_code
    *_value/*_state (provenance 추적)
    input_fields (has_*)
        ↓
[Binding Layer]  ← 이번 WO 정의
  facility_profiles → Generator Input Contract
    sector 추론 (NULL이면 ksic)
    worker_count 동의어 흡수
    has_* 직접 매핑 (변환 없음)
        ↓
[Generator]  (WO-OBLIGATION-GENERATOR)
  Input Contract → cmc 452 매칭 → obligation_instance
        ↓
[Check Engine / 6W]
```

---

## 핵심 발견

### 발견 1: 입력표준과 generator가 같은 언어를 쓴다

```
has_* 28개 전부 1:1 일치. MISSING 0.
→ 입력표준 설계 시 이미 Trigger 명명과 통일됨.
→ Binding은 "번역"이 아니라 "전달".
→ 17회차 작업이 일관된 명명 체계를 유지했음을 입증.
```

### 발견 2: facility_profiles가 모든 입력을 정규화 보유

```
SCOPE(sector/ksic) + THRESHOLD(9 numeric) + EXISTS(input_fields).
provenance로 입력/추론/API/기본값 구분.
→ generator는 이 한 테이블만 읽으면 됨.
→ API도 facility_profiles를 채우는 소스로 수렴.
```

### 발견 3: Gap이 거의 없다

```
즉시 연결 30개 / 정규화 2~3개 / 추가변환 0.
→ 입력 바인딩은 큰 작업이 아님.
→ facility_profiles → Contract → generator 조립만.
→ 다음 WO에서 즉시 구현 가능.
```

### 발견 4: 입력표준 98개 중 generator 사용은 ~30개

```
나머지 68개는 THRESHOLD/APPENDIX/미래 확장용.
→ 현재 cmc는 EXISTS 중심이라 has_* 28개가 핵심.
→ THRESHOLD 보강 시 worker_count 등 numeric 활성화.
→ 입력표준은 generator보다 앞서 설계됨 (여유 보유).
```

---

## 성공 기준 답변

```
diagnosis_session → Input Contract → obligation_generator
→ obligation_instance를 실제 구현할 수 있을 만큼
입력 바인딩 규격이 완성됐는가?

✅ 완성.
  - has_* 28개 1:1 매핑표 확정 (변환 불필요)
  - sector/ksic/numeric 바인딩 확정
  - API → facility_profiles → Contract 흐름 확정
  - Generator Input Contract JSON 규격 확정
  - Gap: 즉시연결 30 / 정규화 2~3 / 추가변환 0
```

---

## 다음 단계

```
WO-INPUT-BINDING-ARCHITECTURE-001 (현재) — 완료. 바인딩 규격.
      ↓
WO-INPUT-BINDING-IMPLEMENTATION-001
  facility_profiles → Generator Input Contract 빌더 구현
  → Contract → generator → obligation_instance 실제 실행
  → 실제 factory의 facility_profiles로 의무 생성 검증
      ↓
(병행) UNIVERSAL 310 REVIEW → CONFIRMED 승격
  → baseline 포함 완전 생성
```

---

## 현재 위치

```
매핑 완료 (cmc 452 CONFIRMED)
  ↓
의무생성기 완료 (obligation_instance 75건 실증)
  ↓
입력 바인딩 규격 완료 ← 지금 여기
  ↓
입력 바인딩 구현 (다음)
  ↓
실제 진단 실행
  ↓
Check Engine
```

---

*WO-INPUT-BINDING-ARCHITECTURE-001 완료. 읽기 전용 바인딩 규격.*
*핵심: has_* 28개 입력표준과 100% 일치(MISSING 0). 바인딩은 조립 수준.*
*facility_profiles가 SCOPE+THRESHOLD+EXISTS 정규화 보유. Gap 거의 없음.*
