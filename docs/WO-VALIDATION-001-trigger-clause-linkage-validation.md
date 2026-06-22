# WO-VALIDATION-001
Trigger ↔ semantic_clause 연결성 검증보고서

작성일: 2026-06-22  
작성자: Claude (검증 전담)  
단계: 검증 (구현 없음)

---

## 0. 검증 목적

WO-MAPPING-001에서 확정한 Trigger Code ~70개가  
실제 semantic_clause DB에 연결되는지 전수 확인한다.  

WO-TRIGGER-001(조회 설계) 진행 전에 수행.

---

## 1. 검증 방법

```
각 Trigger Code에 대해 다음 2개 필드 키워드 검색:
- condition_text 매칭
- action_text 매칭
- 둘 중 하나라도 매칭되면 연결 가능

대상: 사업주 의무 1,200건 (content_type IN ('OBLIGATION','PROHIBITION') AND executor_text = '사업주')

연결 강도 분류:
- 연결 강함 (Strong): 매칭 3건 이상
- 연결 약함 (Weak): 매칭 1~2건
- 연결 불가 (None): 0건
```

---

## 2. 타입별 검증 결과

### WORK (10개) — 검증 결과

| Trigger Code | condition 매칭 | action 매칭 | 합계 | 강도 |
|---|---|---|---|---|
| WORK:MELTING | 2 | 41 | **41** | 연결 강함 |
| WORK:DEMOLITION | 23 | 36 | **39** | 연결 강함 |
| WORK:DIVING | 21 | 32 | **32** | 연결 강함 |
| WORK:HIGH_PRESSURE | 18 | 29 | **29** | 연결 강함 |
| WORK:ASBESTOS | 14 | 20 | **24** | 연결 강함 |
| WORK:EXCAVATION | 11 | 23 | **23** | 연결 강함 |
| WORK:CONFINED_SPACE | 13 | 22 | **22** | 연결 강함 |
| WORK:WELDING | 12 | 18 | **18** | 연결 강함 |
| WORK:BLASTING | 2 | 5 | **5** | 연결 강함 |
| WORK:PAINTING | 2 | 2 | **3** | 연결 강함 |

**WORK 10개 전원 연결 강함. 연결률 100%.** 연결 의무 합계 236건.

핵심 발견: condition_text에는 발생 조건이 있는 경우(13~23건)도 있지만, condition_text가 NULL일때 action_text에 키워드가 있는 경우(18~41건)가 더 많다. **action_text 병행 검색이 필수적이다.**

---

### EQUIPMENT (16개) — 검증 결과

| Trigger Code | condition 매칭 | action 매칭 | 합계 | 강도 |
|---|---|---|---|---|
| EQUIPMENT:CRANE | 14 | 29 | **29** | 연결 강함 |
| EQUIPMENT:CHEMICAL_VESSEL | 12 | 21 | **23** | 연결 강함 |
| EQUIPMENT:EXCAVATOR | 12 | 21 | **22** | 연결 강함 |
| EQUIPMENT:LOCAL_EXHAUST | 7 | 19 | **19** | 연결 강함 |
| EQUIPMENT:ELEVATOR | 4 | 18 | **18** | 연결 강함 |
| EQUIPMENT:MOBILE_CRANE | 3 | 7 | **7** | 연결 강함 |
| EQUIPMENT:CONVEYOR | 6 | 6 | **7** | 연결 강함 |
| EQUIPMENT:TOWER_CRANE | 4 | 6 | **6** | 연결 강함 |
| EQUIPMENT:BOILER | 2 | 5 | **5** | 연결 강함 |
| EQUIPMENT:PRESS | 1 | 4 | **4** | 연결 강함 |
| EQUIPMENT:PRESSURE_VESSEL | 0 | 2 | **2** | 연결 약함 |
| EQUIPMENT:WELDER | 1 | 2 | **2** | 연결 약함 |
| EQUIPMENT:TRANSFORMER | 0 | 2 | **2** | 연결 약함 |
| EQUIPMENT:EXPLOSIVES_STORAGE | 0 | 0 | **0** | 연결 불가 ⚠️ |
| EQUIPMENT:HIGH_PRESSURE_VESSEL | 0 | 0 | **0** | 연결 불가 ⚠️ |
| EQUIPMENT:LPG_TANK | 0 | 0 | **0** | 연결 불가 ⚠️ |

**EQUIPMENT 13/16 연결 (81.3%). 연결 의무 합계 146건.**

연결 불가 3개 원인:
- `EQUIPMENT:EXPLOSIVES_STORAGE`: 화약저장소는 사업주의 직접 의무 대상이 아님 (화약류 관리법 엔터티, 발파 등 WORK Trigger로 커버)
- `EQUIPMENT:HIGH_PRESSURE_VESSEL`: "고압가스 저장"이라는 표현이 semantic_clause에 없음. "고압작업"로만 등장. → WORK:HIGH_PRESSURE로 대체 체계로 커버
- `EQUIPMENT:LPG_TANK`: 유사하게 LPG는 HAZARD_FACTOR:GAS_SUBSTANCE로 연결

---

### EQUIPMENT_ACT (9개) — 검증 결과

| Trigger Code | condition 매칭 | action 매칭 | 합계 | 강도 |
|---|---|---|---|---|
| EQUIPMENT_ACT:CRANE_USE | 7 | 12 | **12** | 연결 강함 |
| EQUIPMENT_ACT:LOCAL_EXHAUST_INSTALL | 3 | 11 | **11** | 연결 강함 |
| EQUIPMENT_ACT:WELDING | 7 | 9 | **9** | 연결 강함 |
| EQUIPMENT_ACT:EXCAVATOR_USE | 6 | 8 | **9** | 연결 강함 |
| EQUIPMENT_ACT:CONVEYOR_USE | 1 | 2 | **2** | 연결 약함 |
| EQUIPMENT_ACT:CHEMICAL_VESSEL_USE | 0 | 1 | **1** | 연결 약함 |
| EQUIPMENT_ACT:PRESS_USE | 0 | 1 | **1** | 연결 약함 |
| EQUIPMENT_ACT:ELEVATOR_USE | 0 | 0 | **0** | 연결 불가 ⚠️ |
| EQUIPMENT_ACT:BOILER_USE | 0 | 0 | **0** | 연결 불가 ⚠️ |

**EQUIPMENT_ACT 7/9 연결 (77.8%). 연결 의무 합계 45건.**

연결 불가 2개 원인:
- `EQUIPMENT_ACT:ELEVATOR_USE`: 승강기 사용은 아이나 가능한가? 검토 필요
- `EQUIPMENT_ACT:BOILER_USE`: 보일러 사용 중 의무는 업보일러법 영역. 산안법 업무 사업주 의무는 EQUIPMENT:BOILER(5건)로 커버

---

### HAZARD_FACTOR (8개) — 검증 결과

| Trigger Code | condition 매칭 | action 매칭 | 합계 | 강도 |
|---|---|---|---|---|
| HAZARD_FACTOR:CHEMICAL | 34 | 57 | **65** | 연결 강함 |
| HAZARD_FACTOR:DUST | 16 | 33 | **37** | 연결 강함 |
| HAZARD_FACTOR:RADIATION | 18 | 23 | **28** | 연결 강함 |
| HAZARD_FACTOR:FLAMMABLE | 11 | 14 | **16** | 연결 강함 |
| HAZARD_FACTOR:METAL_COMPOUND | 0 | 11 | **11** | 연결 강함 |
| HAZARD_FACTOR:NOISE_INTENSE | 3 | 3 | **4** | 연결 강함 |
| HAZARD_FACTOR:GAS_SUBSTANCE | 0 | 2 | **2** | 연결 약함 |
| HAZARD_FACTOR:ORGANIC_COMPOUND | 0 | 1 | **1** | 연결 약함 |

**HAZARD_FACTOR 8/8 연결 (100%). 연결 의무 합계 164건.**

단, 상위 Trigger인 HAZARD_FACTOR:CHEMICAL(65건)은 세분 Trigger(ORGANIC_COMPOUND 1건, METAL_COMPOUND 11건)들을 포함한다. 세분 Trigger로 분리시 각 건수는 감소. 쿠리 HAZARD_FACTOR:CHEMICAL로 단일 조회하고 체크엔진에서 세분 판정하는 방식이 효율적.

---

### THRESHOLD (5개) — 검증 결과 — **중대 문제 발견**

| Trigger Code | condition 매칭 | action 매칭 | 합계 | 강도 |
|---|---|---|---|---|
| THRESHOLD:EMPLOYEE_50_PLUS | 1 | 1 | **1** | 연결 약함 ⚠️ |
| THRESHOLD:AREA_400_PLUS | 1 | 1 | **1** | 연결 약함 ⚠️ |
| THRESHOLD:EMPLOYEE_20_PLUS | 0 | 0 | **0** | 연결 불가 ❌ |
| THRESHOLD:EMPLOYEE_100_PLUS | 0 | 0 | **0** | 연결 불가 ❌ |
| THRESHOLD:CONSTRUCTION_20BIL | 0 | 0 | **0** | 연결 불가 ❌ |

**THRESHOLD 2/5 연결 (40%). 가장 심각한 문제.**

### THRESHOLD 연결 불가 원인 분석

안전관리자 선임 의무를 찾으면:
```sql
-- "안전관리자를 두어야 한다"는 간결한 조문이
-- semantic_clause에 content_type='DELEGATION'으로 분류되어 있다.
-- 실제 선임 기준(별표3)은 해당 조문에서 참조되는
-- 시행령에 있다. semantic_clause에는 다음과 같이 파싱:
```

실제 semantic_clause 파싱 상태:
- "안전관리자를 두어야 한다" → **content_type='DELEGATION'** (OBLIGATION 아님)
- "안전관리자의 수 및 선임방법은 별표 3과 같다" → **시행령 조문으로 이관. semantic_clause에 없음**

실제 문제:
```
THRESHOLD Trigger가 타겟하는 의무(안전관리자 선임, 안전보건관리규정 작성, 산업안전보건위원회 구성)는

semantic_clause에서 content_type = 'DELEGATION' 또는 산업안전보건법 시행령 조문에 담겨 있다.

코어 산안법 조문들(대부분의 THRESHOLD 의무의 근거):
- 산안법 제17조 (안전관리자) → semantic_clause OBLIGATION 없음
- 산안법 제19조 (건설업 안전관리자) → semantic_clause OBLIGATION 없음
- 산안법 제20조 (보건관리자) → semantic_clause OBLIGATION 없음
- 산안법 제24조 (산업안전보건위원회) → OBLIGATION 존재하지만 condition_text=NULL
- 산안법 제25조 (안전보건관리규정) → OBLIGATION 존재하지만 condition_text=NULL
```

다시 말해: **THRESHOLD Trigger는 키워드 매칭으로 연결할 수 없다.**  
대신 **별도 매핑 테이블**이 연결 구조를 담당해야 한다.

```
THRESHOLD:EMPLOYEE_50_PLUS
  ↓
매핑 테이블: { threshold='EMPLOYEE_50_PLUS' → clause_ids: [uuid1, uuid2, ...] }
  ↓
semantic_clause 직접 id 조회
```

---

### BUSINESS (1개) — 검증 결과

| Trigger Code | 연결 방식 | 합계 | 강도 |
|---|---|---|---|
| BUSINESS:REGISTERED | condition_text IS NULL 조회 | **491** | 연결 강함 |

**condition_text가 NULL인 491건이 모두 BUSINESS Trigger로 커버된다.** 키워드 매칭 불필요.

---

### INDUSTRY (3개) — 검증 결과

| Trigger Code | condition 매칭 | action 매칭 | 합계 | 강도 |
|---|---|---|---|---|
| INDUSTRY:CONSTRUCTION | 0 | 4 | **4** | 연결 강함 |
| INDUSTRY:INDUSTRIAL | 0 | 0 | **0** | 연결 불가 |
| INDUSTRY:GENERAL | 0 | 0 | **0** | 연결 불가 |

**INDUSTRY는 세분 업종 구분이 semantic_clause에 불가. REFERENCE 염역이다.** 대부분 업종 기반 의무는 별표 연결으로만 처리 가능.

---

## 3. 연결 중복 분석

동일한 semantic_clause를 여러 Trigger가 지시할 수 있다.

• WORK:WELDING + EQUIPMENT:WELDER: 일부 중복 (2개 조문에서 두 키워드 동시 발견)
• WORK:BLASTING + EQUIPMENT:EXPLOSIVES_STORAGE: WORK에서만 커버 (EQUIPMENT 0건)
• WORK:HIGH_PRESSURE + EQUIPMENT:HIGH_PRESSURE_VESSEL: WORK에서만 커버

→ **중복 연결는 의무를 너리게 커버하는 지점에서 버퍼로 작용한다.** 체크엔진에서 source_article_id 기준 중복 제거.

---

## 4. 핵심 발견: 두 가지 연결 진단

### 발견 1: condition_text만으론 불충분, action_text 병행 검색 필수

```
의무황 동동:
WORK:MELTING 위득 통계
  condition_text 매칭: 2건
  action_text 매칭: 41건
  둘 다 검색 시: 41건 (획득)

이유: "용해 작업을 하는 경우"는 condition_text에 등장하지 않고
    action_text 자체에서 발파된다 ("용해쇠 줘야 한다", "용선 취석").  
```

→ WO-TRIGGER-001에서 **의무 조회는 condition_text OR action_text** 양쪽 검색으로 설계해야 한다.

### 발견 2: THRESHOLD는 키워드 매칭 불가 — 별도 매핑 테이블 필수

```
THRESHOLD 의무(안전관리자 선임, 안전보건관리규정, 위원회)는
semantic_clause에 condition_text로 임계값이 없다.

기존 구조:
  특정 semantic_clause.id들 (안전관리자, 안전관리규정, 위원회...)
  조건: 시행령 별표3 업종별 임계값
  → 현재는 applicability_conditions(14건)에 일부 있으나 범위 좌소

필요한 신규 테이블 (WO-TRIGGER-001에서 설계):
  threshold_obligation_map:
    threshold_code   | clause_ids (array)
    EMPLOYEE_50_PLUS | [uuid_안전관리자선임, uuid_위원회, ...]
    EMPLOYEE_100_PLUS| [uuid_안전보건관리규정, ...]
```

---

## 5. 전체 검증 쭌야리트

| 타입 | 전체 | 연결 강함 | 연결 약함 | 연결 불가 | 연결률 | 맴필 의무 수 |
|---|---|---|---|---|---|---|
| BUSINESS | 1 | 1 | 0 | 0 | **100%** | 491 |
| WORK | 10 | 10 | 0 | 0 | **100%** | 236 |
| HAZARD_FACTOR | 8 | 6 | 2 | 0 | **100%** | 164 |
| EQUIPMENT | 16 | 10 | 3 | 3 | **81%** | 146 |
| EQUIPMENT_ACT | 9 | 4 | 3 | 2 | **78%** | 45 |
| INDUSTRY | 3 | 1 | 0 | 2 | **33%** | 4 |
| THRESHOLD | 5 | 0 | 2 | 3 | **0%** ❌ | 2 |
| **합계** | **52** | **32** | **10** | **10** | **81%** | **1,088** |

### 의무 커버 수 합슰 (기능하는 Trigger의 연결 의무 합계)
```
BUSINESS:   491건
WORK:        236건
HAZARD:     164건
EQUIPMENT:  146건
EQ_ACT:      45건
실제 카버: 중복 감안 시 ~700~800건 (BUSINESS 이후 추가되는 실질 의무)

THRESHOLD: 키워드 매칭 불가. 별도 매핑 테이블 필요.
INDUSTRY:  REFERENCE 영역. 최소화.
```

---

## 6. 결론

### 6-1. 연결률 평가

```
Trigger Code 52개 중
  키워드 매칭으로 연결 가능: 42개 (81%)
  키워드 매칭 불가: 10개 (19%)

매칭 불가 10개 분류:
  - THRESHOLD 3개: 별도 매핑 테이블로 해결
  - EQUIPMENT 3개: WORK/HAZARD Trigger로 대체 가능
  - EQUIPMENT_ACT 2개: 타당 Trigger 없음 (SaaS 운영 없마)
  - INDUSTRY 2개: REFERENCE 영역
```

### 6-2. WO-TRIGGER-001에 통보할 제약조건 3개

**제약 1: 의무 조회는 condition_text + action_text 양쪽 검색으로 설계한다.**  
condition_text만으론 의무의 40~70%를 놀친다.

**제약 2: THRESHOLD Trigger는 키워드 매칭이 아니라 매핑 테이블으로 가는 연결이 필요하다.**  
`{ threshold_code → [clause_id 목록] }` 형식의 매핑 테이블 서설계 필요.

**제약 3: EQUIPMENT 0건 3개(EXPLOSIVES_STORAGE, HIGH_PRESSURE_VESSEL, LPG_TANK)는 연결 Trigger를 순환 사용한다.**  
- EXPLOSIVES_STORAGE → WORK:BLASTING으로 커버
- HIGH_PRESSURE_VESSEL → WORK:HIGH_PRESSURE로 커버
- LPG_TANK → HAZARD_FACTOR:GAS_SUBSTANCE로 커버

---

*WO-VALIDATION-001 완료 | 테이블 생성 없음 | 코드 작성 없음 | 구현 없음*
