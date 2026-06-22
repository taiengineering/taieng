# WO-MAPPING-001
입력값 → Trigger Code 매핑 규칙 설계서

작성일: 2026-06-22  
작성자: Claude (설계 전담)  
단계: 해결책 강구 (구현 없음)

---

## 0. 설계 전제

**과잉 Trigger 금지 원칙** (가장 먼저 확정)

```
금지: KSIC상 용접공정 가능성이 높다 → WORK:WELDING 발생
허용: 사용자가 용접공정을 실제 등록했다 → WORK:WELDING 발생
허용: 사용자가 용접기를 실제 보유한다고 등록했다 → EQUIPMENT:WELDER 발생
```

→ Trigger는 반드시 **소비자가 직접 입력하거나 명시적으로 등록한 데이터**에서만 생성된다.  
KSIC, 공정 추천 데이터(ksic_process_map, process_equipment_map)는 Trigger 생성 소스가 아니다.

---

## 1. Trigger Type 정의

| 타입 | 의미 | 입력 소스 | 커버 의무 유형 |
|---|---|---|---|
| **BUSINESS** | 사업장 존재 | 사업장 등록 행위 자체 | 모든 사업장 공통 의무 |
| **THRESHOLD** | 수치 임계값 | employee_count, building_area, construction_amount | 규모 기반 의무 |
| **INDUSTRY** | 업종 기반 | ksic_code (법령이 업종을 직접 조건으로 명시한 경우만) | 업종 특수 의무 |
| **EQUIPMENT** | 설비 보유 | equipment_assets.equipment_type_code | 설비 보유 기반 의무 |
| **EQUIPMENT_ACT** | 설비 사용/설치 행위 | equipment_assets 등록 + 사용상태 | 설비 사용/설치 시 의무 |
| **WORK** | 특수 위험 작업 수행 | has_* flag, factory_process.process_lv2 | 특수 작업 기반 의무 |
| **HAZARD_FACTOR** | 유해인자 취급 | hazard_factor_codes [신규 입력 필요] | 유해인자 취급 의무 |
| **EVENT** | 런타임 이벤트 | SaaS 운영 중 발생 데이터 | 이벤트 후속 의무 |
| **REFERENCE** | 별표/참조조문 의존 | 별표 데이터 구축 후 처리 | 열거조항 기반 의무 |

**EVENT와 REFERENCE는 초기 법령진단에서 제외한다.**  
EVENT: SaaS 운영 중 (점검 결과 이상, 사고 발생, 설비 변경)  
REFERENCE: WO-APPENDIX-COLLECT-001 완료 후 별도 처리

---

## 2. Trigger Code 표준

형식: `TRIGGER_TYPE:TRIGGER_VALUE`

TRIGGER_VALUE는 영문 대문자 + 언더스코어. 한글 금지.

```
예시:
BUSINESS:REGISTERED
THRESHOLD:EMPLOYEE_50_PLUS
THRESHOLD:EMPLOYEE_100_PLUS
THRESHOLD:AREA_400_PLUS
INDUSTRY:CONSTRUCTION
INDUSTRY:MANUFACTURING_HIGH_RISK
EQUIPMENT:CRANE
EQUIPMENT:PRESS
EQUIPMENT_ACT:CRANE_USE
EQUIPMENT_ACT:CRANE_INSTALL
WORK:CONFINED_SPACE
WORK:BLASTING
WORK:WELDING
HAZARD_FACTOR:NOISE
HAZARD_FACTOR:DUST
```

---

## 3. 규칙 A: 직접 변환 (Boolean/명시 입력 → Trigger)

실데이터 기준 각 flag의 의무 커버 건수 포함.

### 3-1. has_* Flag 변환표

| input_field | input_value | trigger_code | trigger_type | 커버 의무 건수 | 비고 |
|---|---|---|---|---|---|
| has_confined_space | true | WORK:CONFINED_SPACE | WORK | 21건 | 밀폐공간 작업 전체 |
| has_blasting | true | WORK:BLASTING | WORK | 4건 | 발파 작업 |
| has_diving | true | WORK:DIVING | WORK | 27건 | 잠수 작업 |
| has_asbestos_demo | true | WORK:ASBESTOS | WORK | 24건 | 석면 해체·제거 |
| has_tower_crane | true | EQUIPMENT:TOWER_CRANE | EQUIPMENT | 6건 | 타워크레인 보유 |
| has_high_pressure_gas | true | WORK:HIGH_PRESSURE | WORK | 21건 | 고압작업 포함 |
| has_chemical_substance | true | HAZARD_FACTOR:CHEMICAL | HAZARD_FACTOR | 65건 | 화학물질/관리대상/허가대상 |
| has_boiler | true | EQUIPMENT:BOILER | EQUIPMENT | 5건 | 보일러 보유 |

**WORK:HIGH_PRESSURE 설명**: `has_high_pressure_gas`는 고압가스 보유를 의미하나, 실제 법령 조건은 "고압작업"과 "고압가스" 두 갈래다. 두 Trigger를 모두 생성한다.

→ `has_high_pressure_gas = true` → `WORK:HIGH_PRESSURE` + `EQUIPMENT:HIGH_PRESSURE_VESSEL`

### 3-2. sector 변환표

| input_field | input_value | trigger_code | trigger_type | 비고 |
|---|---|---|---|---|
| sector | CONSTRUCTION | INDUSTRY:CONSTRUCTION | INDUSTRY | 건설업 전용 조문 |
| sector | INDUSTRIAL | INDUSTRY:INDUSTRIAL | INDUSTRY | 제조/산업 기반 |
| sector | BUILDING | INDUSTRY:BUILDING | INDUSTRY | 건물 관리 기반 |

---

## 4. 규칙 B: 임계값 변환 (수치 → Trigger)

### 4-1. employee_count 임계값

실데이터 확인: semantic_clause에 "상시 50명" 직접 명시 의무 존재.
핵심 임계값은 별표 참조이나, 조문 직접 명시분은 아래로 처리.

| field | operator | value | trigger_code | 관련 의무 |
|---|---|---|---|---|
| employee_count | >= | 20 | THRESHOLD:EMPLOYEE_20_PLUS | 안전보건관리담당자 선임 |
| employee_count | >= | 50 | THRESHOLD:EMPLOYEE_50_PLUS | 안전보건위원회(일부), 경보설비 |
| employee_count | >= | 100 | THRESHOLD:EMPLOYEE_100_PLUS | 안전보건관리규정 작성 |
| employee_count | >= | 300 | THRESHOLD:EMPLOYEE_300_PLUS | 안전관리자 선임(고위험 외) |
| employee_count | >= | 500 | THRESHOLD:EMPLOYEE_500_PLUS | 보건관리자 추가 선임 |
| employee_count | >= | 1000 | THRESHOLD:EMPLOYEE_1000_PLUS | 산업보건의 선임 |

**주의**: 안전관리자 선임 기준(별표3)은 업종별로 다르다. `THRESHOLD:EMPLOYEE_*` + `INDUSTRY:*` 조합으로 체크엔진에서 최종 판별.

### 4-2. building_area 임계값

| field | operator | value | trigger_code | 관련 의무 |
|---|---|---|---|---|
| building_area | >= | 400 | THRESHOLD:AREA_400_PLUS | 경보용 설비 설치 (연면적 400㎡ 이상 또는 상시 50명 이상) |

**OR 조건 처리**: `THRESHOLD:AREA_400_PLUS` OR `THRESHOLD:EMPLOYEE_50_PLUS` → 어느 하나 충족 시 의무 발생. 체크엔진에서 OR 로직 처리.

### 4-3. construction_amount 임계값

| field | operator | value | trigger_code | 관련 의무 |
|---|---|---|---|---|
| construction_amount | >= | 2,000,000,000 | THRESHOLD:CONSTRUCTION_20BIL | 건설업 안전관리자 선임 |
| construction_amount | >= | 800,000,000 | THRESHOLD:CONSTRUCTION_8BIL | 건설업 산업안전보건관리비 |

**주의**: 건설업 기준금액은 별표 참조이므로 정확한 수치는 WO-APPENDIX-COLLECT-001 후 확정.

---

## 5. 규칙 C: 분류 변환 (코드 → Trigger)

### 5-1. equipment_type_code → EQUIPMENT/EQUIPMENT_ACT Trigger

실데이터 기준 설비코드 전수 분석 결과:

| equipment_type_code | 대표 설비명 | trigger_code (EQUIPMENT) | trigger_code (EQUIPMENT_ACT) | 커버 의무 건수 |
|---|---|---|---|---|
| CRANE | 크레인 | EQUIPMENT:CRANE | EQUIPMENT_ACT:CRANE_USE | 24건 |
| PRESS | 프레스 | EQUIPMENT:PRESS | EQUIPMENT_ACT:PRESS_USE | 4건 |
| PRESSURE_VESSEL | 압력용기 | EQUIPMENT:PRESSURE_VESSEL | EQUIPMENT_ACT:PRESSURE_VESSEL_USE | 2건 |
| CONVEYOR | 컨베이어 | EQUIPMENT:CONVEYOR | EQUIPMENT_ACT:CONVEYOR_USE | 7건 |
| 008 | 용접기 | EQUIPMENT:WELDER | EQUIPMENT_ACT:WELDING | 18건 |
| 011 | 반응기/혼합기/화학설비 | EQUIPMENT:CHEMICAL_VESSEL | EQUIPMENT_ACT:CHEMICAL_VESSEL_USE | 23건 |
| 013 | 열교환기 | EQUIPMENT:HEAT_EXCHANGER | EQUIPMENT_ACT:HEAT_EXCHANGER_USE | 0건 |
| 014 | 보일러 | EQUIPMENT:BOILER | EQUIPMENT_ACT:BOILER_USE | 5건 |
| 021 | 이동식크레인 | EQUIPMENT:MOBILE_CRANE | EQUIPMENT_ACT:MOBILE_CRANE_USE | 7건 |
| 024 | 컨베이어(숫자코드) | EQUIPMENT:CONVEYOR | EQUIPMENT_ACT:CONVEYOR_USE | 7건 |
| 025 | 승강기/엘리베이터 | EQUIPMENT:ELEVATOR | EQUIPMENT_ACT:ELEVATOR_USE | 18건 |
| 029 | 증류탑/화학설비 | EQUIPMENT:DISTILLATION | EQUIPMENT_ACT:DISTILLATION_USE | 0건 |
| 030 | 화약저장소 | EQUIPMENT:EXPLOSIVES_STORAGE | — | 7건 |
| 036 | 집진기/국소배기장치 | EQUIPMENT:LOCAL_EXHAUST | EQUIPMENT_ACT:LOCAL_EXHAUST_INSTALL | 45건 |
| 040 | 굴착기/차량계건설기계 | EQUIPMENT:EXCAVATOR | EQUIPMENT_ACT:EXCAVATOR_USE | 34건 |
| 001 | 수전변압기 | EQUIPMENT:TRANSFORMER | — | 2건 |
| 007 | 분전반/정류기 | EQUIPMENT:DISTRIBUTION_PANEL | — | 0건 |
| 010 | 발전기 | EQUIPMENT:GENERATOR | — | 0건 |
| 027 | 고압가스 저장탱크 | EQUIPMENT:HIGH_PRESSURE_VESSEL | — | (고압 관련) |
| 028 | LPG 저장탱크 | EQUIPMENT:LPG_TANK | — | (가스 관련) |

**EQUIPMENT_ACT 생성 규칙**:
- 설비 등록 시 → EQUIPMENT:XXX 생성 (보유)
- 설비 사용 상태 = '사용중' 또는 운영 중인 공정에 연결된 경우 → EQUIPMENT_ACT:XXX_USE 추가 생성
- 설비 최초 설치 이벤트 → EQUIPMENT_ACT:XXX_INSTALL (EVENT 계층, 초기 진단 제외)

### 5-2. factory_process.process_lv2 → WORK Trigger

실데이터 기준 공정명-법령 매핑 가능 목록:

| source | process_lv2 | trigger_code | 커버 의무 건수 | 비고 |
|---|---|---|---|---|
| factory_process | 용접용단 | WORK:WELDING | 18건 | 용접기(008) 보유와 중복 가능 |
| factory_process | 도장 | WORK:PAINTING | 3건 | 분사도장 포함 |
| factory_process | 굴착 | WORK:EXCAVATION | 23건 | 굴착기(040) 보유와 중복 가능 |
| factory_process | 해체 | WORK:DEMOLITION | 39건 | 건물 해체 작업 |
| factory_process | 용해 | WORK:MELTING | 41건 | 용융금속 취급 |
| factory_process | 주조 | WORK:CASTING | 41건 | 용해와 중복 카운트 가능 |
| factory_process | 열처리 | WORK:HEAT_TREATMENT | 0건 | 직접 의무 거의 없음 |

**중요 원칙**: factory_process는 **사용자가 실제 등록한 공정**에서만 Trigger를 생성한다.  
ksic_process_map 추천 공정은 Trigger 소스가 아니다.

### 5-3. ksic_code → INDUSTRY Trigger

KSIC는 대부분 REFERENCE(별표) 판별용이다. 조문에 업종이 직접 명시된 경우만 INDUSTRY Trigger 사용.

| ksic_code 패턴 | trigger_code | 적용 조건 |
|---|---|---|
| F(45~47) 건설업 | INDUSTRY:CONSTRUCTION | 건설업 전용 서식/보고 |
| C(10~33) 제조업 고위험 | INDUSTRY:MANUFACTURING_HIGH_RISK | 별표3 고위험 업종 (별표 구축 후 확정) |
| 기타 | INDUSTRY:GENERAL | 일반 사업장 조건 |

**주의**: INDUSTRY Trigger 생성은 최소화한다. 대부분의 업종 기반 의무는 REFERENCE 처리 영역.

---

## 6. 유해인자 Trigger 목록 (신규 입력 필요)

현재 `has_chemical_substance` boolean 1개로는 65건의 화학물질 의무를 구분할 수 없다.
유해인자를 세분화해야 의무를 정확하게 특정할 수 있다.

| 신규 입력 후보 | trigger_code | 필요한 이유 | 관련 의무 건수 |
|---|---|---|---|
| 소음작업 (강렬한 소음) | HAZARD_FACTOR:NOISE_INTENSE | 청력보호구 지급, 청력보존 프로그램 | 3건 |
| 충격소음작업 | HAZARD_FACTOR:NOISE_IMPACT | 동일 | 3건 |
| 분진작업 | HAZARD_FACTOR:DUST | 집진기 설치, 작업환경측정 | 45건(집진기 포함) |
| 관리대상 유해물질 (유기화합물) | HAZARD_FACTOR:ORGANIC_COMPOUND | 보호구, 국소배기, 측정 | 다수 |
| 관리대상 유해물질 (금속류) | HAZARD_FACTOR:METAL_COMPOUND | 동일 | 다수 |
| 관리대상 유해물질 (가스상) | HAZARD_FACTOR:GAS_SUBSTANCE | 경보설비 (100L/일 이상) | 2건 |
| 허가대상 유해물질 | HAZARD_FACTOR:PERMIT_REQUIRED | 금지유해물질에 준하는 보호 | 4건 |
| 금지유해물질 | HAZARD_FACTOR:PROHIBITED | 전용 보호구, 전용 저장 | 4건 |
| 방사선 작업 | HAZARD_FACTOR:RADIATION | 방사선관리구역, 피폭관리 | 3건 |
| 위험물 취급 (인화성) | HAZARD_FACTOR:FLAMMABLE | 소화설비, 저장기준 | 다수 |
| 위험물 취급 (가연성 가스) | HAZARD_FACTOR:COMBUSTIBLE_GAS | 경보설비 | 다수 |

**입력 UI 설계 제안** (구현 아님, 구조만):
```
유해인자 분류 (다중 선택 체크박스)
  □ 소음작업 (강렬한 소음 / 충격소음)
  □ 분진작업 (광물성 / 금속성 / 목재성)
  □ 유기화합물 취급 (톨루엔, 벤젠 등)
  □ 금속류 취급 (납, 수은, 크롬 등)
  □ 가스상 유해물질 (일산화탄소 등)
  □ 허가대상 유해물질
  □ 금지유해물질
  □ 방사선 작업
  □ 인화성 액체 취급
  □ 가연성 가스 취급
```

---

## 7. 과잉 Trigger 방지 원칙 (정식 확정)

### 원칙 1: 입력 기반 생성만 허용
```
허용: has_confined_space = true → WORK:CONFINED_SPACE
금지: ksic_code = 'C2511' → WORK:WELDING (KSIC가 용접 가능성 암시하더라도)
```

### 원칙 2: KSIC의 역할 제한
```
KSIC는 Trigger 직접 생성 소스가 아니다.
예외: sector = CONSTRUCTION → INDUSTRY:CONSTRUCTION (업종이 직접 법령 조건인 경우)
 KSIC가 별표 업종 분류에 해당하는지 → REFERENCE 처리 (별표 구축 후)
```

### 원칙 3: EQUIPMENT와 EQUIPMENT_ACT 분리
```
EQUIPMENT:CRANE   = 크레인을 보유하고 있다 (자산 등록)
EQUIPMENT_ACT:CRANE_USE = 크레인을 현재 사용 중이다 (운용 상태)
EQUIPMENT_ACT:CRANE_INSTALL = 크레인을 새로 설치하는 행위 (EVENT 영역)

초기 진단: EQUIPMENT + EQUIPMENT_ACT:*_USE 생성
런타임:   EQUIPMENT_ACT:*_INSTALL은 EVENT로 처리
```

### 원칙 4: EVENT는 초기 진단에서 분리
```
EVENT는 SaaS 운영 중 발생하는 데이터로부터 생성된다.
초기 법령진단(안전관리설계서 발행) 시점에는 EVENT Trigger 없음.

포함 안 되는 것:
  - 점검 결과 이상 발견 → 즉시 보수 의무
  - 중대재해 발생 → 보고 의무
  - 설비 변경 → 재검토 의무
이것들은 SaaS 운영 레이어에서 별도 처리.
```

### 원칙 5: 공정 추천 데이터 사용 금지
```
ksic_process_map: KSIC → 공정 추천 (Trigger 소스 ❌)
process_equipment_map: 공정 → 설비 추천 (Trigger 소스 ❌)

오직 factory_process에 사용자가 직접 등록한 공정만 사용.
```

---

## 8. 완료 조건 검증: 입력 예시 → Trigger Code Set

### 예시 1 (작업지시서 제공)
```json
입력:
{
  "ksic_code": "25112",
  "employee_count": 80,
  "has_confined_space": true,
  "equipment_assets": ["CRANE"]
}

생성 Trigger Code Set:
{
  "trigger_codes": [
    "BUSINESS:REGISTERED",        // 사업장 존재 (항상 생성)
    "THRESHOLD:EMPLOYEE_50_PLUS", // 80 >= 50
    "WORK:CONFINED_SPACE",        // has_confined_space = true
    "EQUIPMENT:CRANE",            // equipment_assets에 CRANE
    "EQUIPMENT_ACT:CRANE_USE"     // CRANE 보유 → 사용 중으로 간주
  ]
}
```

### 예시 2 (제조업, 복합 설비)
```json
입력:
{
  "ksic_code": "20119",
  "employee_count": 150,
  "sector": "INDUSTRIAL",
  "has_chemical_substance": true,
  "has_high_pressure_gas": true,
  "equipment_assets": ["PRESS", "008", "036"],
  "factory_process": ["용접용단", "도장"]
}

생성 Trigger Code Set:
{
  "trigger_codes": [
    "BUSINESS:REGISTERED",
    "THRESHOLD:EMPLOYEE_50_PLUS",
    "THRESHOLD:EMPLOYEE_100_PLUS",
    "HAZARD_FACTOR:CHEMICAL",         // has_chemical_substance
    "WORK:HIGH_PRESSURE",             // has_high_pressure_gas
    "EQUIPMENT:HIGH_PRESSURE_VESSEL", // has_high_pressure_gas
    "EQUIPMENT:PRESS",
    "EQUIPMENT_ACT:PRESS_USE",
    "EQUIPMENT:WELDER",               // 008
    "EQUIPMENT_ACT:WELDING",          // 008
    "EQUIPMENT:LOCAL_EXHAUST",        // 036
    "EQUIPMENT_ACT:LOCAL_EXHAUST_INSTALL",
    "WORK:WELDING",                   // factory_process 용접용단
    "WORK:PAINTING",                  // factory_process 도장
    "INDUSTRY:INDUSTRIAL"
  ]
}
```

### 예시 3 (건설업)
```json
입력:
{
  "sector": "CONSTRUCTION",
  "employee_count": 30,
  "construction_amount": 5000000000,
  "has_tower_crane": true,
  "has_blasting": true
}

생성 Trigger Code Set:
{
  "trigger_codes": [
    "BUSINESS:REGISTERED",
    "THRESHOLD:EMPLOYEE_20_PLUS",
    "THRESHOLD:CONSTRUCTION_20BIL",  // 50억 >= 20억
    "INDUSTRY:CONSTRUCTION",
    "EQUIPMENT:TOWER_CRANE",
    "WORK:BLASTING"
  ]
}
```

---

## 9. WO-TRIGGER-001에 넘길 산출물

다음 단계인 WO-TRIGGER-001(Trigger Code → semantic_clause 의무후보 조회 설계)에서 필요한 것:

### 필수 인계 항목

1. **Trigger Code 전체 목록** (본 문서 §2~7)
2. **각 Trigger Code의 의무 조회 키워드**

```
Trigger Code          → semantic_clause 조회 키워드
------------------------------------------------------
WORK:CONFINED_SPACE   → condition_text LIKE '%밀폐공간%'
WORK:BLASTING         → condition_text LIKE '%발파%'
WORK:DIVING           → condition_text LIKE '%잠수%'
WORK:ASBESTOS         → condition_text LIKE '%석면%'
WORK:HIGH_PRESSURE    → condition_text LIKE '%고압작업%' OR '%고압가스%'
WORK:WELDING          → condition_text LIKE '%용접%' OR '%용단%'
WORK:PAINTING         → condition_text LIKE '%도장%' OR '%분사도장%'
WORK:EXCAVATION       → condition_text LIKE '%굴착%'
WORK:DEMOLITION       → condition_text LIKE '%해체%' OR '%철거%'
WORK:MELTING          → condition_text LIKE '%용해%' OR '%용융%' OR '%주조%'
EQUIPMENT:CRANE       → condition_text LIKE '%크레인%'
EQUIPMENT:PRESS       → condition_text LIKE '%프레스%'
EQUIPMENT:WELDER      → action_text LIKE '%용접%'
EQUIPMENT:CONVEYOR    → condition_text LIKE '%컨베이어%'
EQUIPMENT:ELEVATOR    → condition_text LIKE '%승강기%' OR '%리프트%'
EQUIPMENT:BOILER      → condition_text LIKE '%보일러%'
EQUIPMENT:LOCAL_EXHAUST → condition_text LIKE '%국소배기%' OR '%집진기%'
EQUIPMENT:EXCAVATOR   → condition_text LIKE '%굴착기%' OR '%차량계 건설%'
EQUIPMENT:CHEMICAL_VESSEL → condition_text LIKE '%화학설비%'
EQUIPMENT:TOWER_CRANE → condition_text LIKE '%타워크레인%'
BUSINESS:REGISTERED   → condition_text IS NULL (무조건 발생)
THRESHOLD:*           → 체크엔진 처리 (별표 수치 비교)
HAZARD_FACTOR:CHEMICAL → condition_text LIKE '%관리대상%' OR '%허가대상%' OR '%금지유해%'
HAZARD_FACTOR:NOISE_INTENSE → condition_text LIKE '%소음작업%' OR '%충격소음%'
HAZARD_FACTOR:DUST    → condition_text LIKE '%분진%'
```

3. **OR 조건 의무 목록**
   - `THRESHOLD:AREA_400_PLUS` OR `THRESHOLD:EMPLOYEE_50_PLUS` → 경보설비 설치
   - 체크엔진에서 OR 로직 처리 필요

4. **REFERENCE 처리 대상 목록** (초기 진단 제외)
   - 안전관리자 선임 (시행령 별표3 업종별 기준)
   - 안전보건관리규정 작성 (시행령 별표1 기준)
   - 건설업 안전관리자 (공사금액 + 업종 조합)

---

*WO-MAPPING-001 완료 | 테이블 생성 없음 | 코드 작성 없음 | 구현 없음*
