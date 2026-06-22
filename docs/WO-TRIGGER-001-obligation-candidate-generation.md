# WO-TRIGGER-001
Trigger 기반 의무후보 생성 설계서

작성일: 2026-06-22
작성자: Claude (설계 전담)
단계: 해결책 강구 (구현 없음)

---

## 0. 설계 전제

WO-VALIDATION-001 결과:
- Trigger 연결률 81% (52개 중 42개 키워드 매칭 가능)
- THRESHOLD/INDUSTRY/REFERENCE는 키워드 매칭 불가 → 별도 Route
- condition_text + action_text 양방향 검색 필수

두 Route가 확정된다:
- **Route A**: 키워드 매칭 → semantic_clause 직접 조회
- **Route B**: 조건판정 → applicability_conditions 경유

---

## 1. Route A 설계 — 직접 조회

### 대상 Trigger 타입

BUSINESS, WORK, EQUIPMENT, EQUIPMENT_ACT, HAZARD_FACTOR

### 조회 구조

```
Trigger Code
  ↓
키워드 패턴 매핑 테이블 조회
  ↓
semantic_clause 검색
  조건: content_type IN ('OBLIGATION','PROHIBITION')
        AND executor_text = '사업주'
        AND (condition_text OR action_text) MATCHES 키워드 패턴
  ↓
의무후보 생성
```

### 핵심 원칙: 양방향 검색 필수

condition_text만 검색하면 의무의 40~70%를 누락한다.

실증:
- WORK:MELTING — condition_text: 2건 / action_text: 41건 / 합계: 41건
- WORK:DEMOLITION — condition_text: 23건 / action_text: 36건 / 합계: 39건
- WORK:DIVING — condition_text: 21건 / action_text: 32건 / 합계: 32건

의무 조회는 COALESCE(condition_text,'') || action_text 전체를 대상으로 한다.

### BUSINESS 특수 처리

```
BUSINESS:REGISTERED → condition_text IS NULL 조회
이유: condition_text IS NULL = 모든 사업장에 무조건 적용
대상: 491건 (사업주 의무 전체의 40.9%)
```

### Trigger별 키워드 패턴

| Trigger Code | 검색 패턴 | 비고 |
|---|---|---|
| BUSINESS:REGISTERED | condition_text IS NULL | 무조건 발생 |
| WORK:CONFINED_SPACE | (밀폐공간\|산소결핍\|황화수소\|밀폐된 공간) | 동의어 포함 |
| WORK:BLASTING | (발파\|화약류\|폭발물) | |
| WORK:DIVING | (잠수\|잠함\|잠수작업자) | |
| WORK:ASBESTOS | (석면\|석면해체\|석면분진) | |
| WORK:HIGH_PRESSURE | (고압작업\|고압가스\|기압조절실) | |
| WORK:WELDING | (용접\|용단) | |
| WORK:PAINTING | (도장\|분사도장\|도료) | |
| WORK:EXCAVATION | (굴착\|굴착공사) | |
| WORK:DEMOLITION | (해체\|철거) | |
| WORK:MELTING | (용해\|용융\|주조\|용선) | |
| EQUIPMENT:CRANE | (크레인\|양중기) | 양중기 동의어 필수 |
| EQUIPMENT:TOWER_CRANE | (타워크레인) | CRANE 패턴에 포함 |
| EQUIPMENT:MOBILE_CRANE | (이동식 크레인\|이동식크레인) | CRANE 패턴에 포함 |
| EQUIPMENT:PRESS | (프레스) | |
| EQUIPMENT:PRESSURE_VESSEL | (압력용기) | |
| EQUIPMENT:CONVEYOR | (컨베이어) | |
| EQUIPMENT:ELEVATOR | (승강기\|리프트\|엘리베이터) | |
| EQUIPMENT:BOILER | (보일러) | |
| EQUIPMENT:WELDER | (용접기\|용접전원\|아크용접) | WORK:WELDING과 중복 허용 |
| EQUIPMENT:CHEMICAL_VESSEL | (화학설비\|반응기\|혼합기) | |
| EQUIPMENT:LOCAL_EXHAUST | (국소배기\|집진기\|후드) | |
| EQUIPMENT:EXCAVATOR | (굴착기\|차량계 건설기계\|건설기계) | |
| EQUIPMENT_ACT:CRANE_USE | (크레인 사용\|크레인을 사용하여) | |
| EQUIPMENT_ACT:LOCAL_EXHAUST_INSTALL | (국소배기 설치\|국소배기장치를 설치) | |
| EQUIPMENT_ACT:WELDING | (용접작업\|용접 작업을 하는 경우) | |
| EQUIPMENT_ACT:EXCAVATOR_USE | (차량계 건설기계 작업\|굴착기 사용) | |
| HAZARD_FACTOR:CHEMICAL | (관리대상 유해물질\|허가대상 유해물질\|금지유해물질\|화학물질) | |
| HAZARD_FACTOR:DUST | (분진\|분진작업\|광물성 분진) | |
| HAZARD_FACTOR:RADIATION | (방사선\|방사성물질\|방사선업무) | |
| HAZARD_FACTOR:FLAMMABLE | (인화성\|가연성 물질\|인화성 액체) | |
| HAZARD_FACTOR:METAL_COMPOUND | (금속류\|납\|수은\|크롬\|망간) | |
| HAZARD_FACTOR:NOISE_INTENSE | (강렬한 소음\|소음작업\|충격소음) | |

---

## 2. Route B 설계 — 조건판정

### 대상 Trigger 타입

THRESHOLD, INDUSTRY, REFERENCE

### Route B 구조

```
Trigger Code
  ↓
applicability_conditions 조회
  조건: metric MATCHES Trigger + 소비자 입력값 충족 여부 판정
  ↓
충족 시: appendix_no → law_article → semantic_clause id 조회
  ↓
의무후보 생성
```

### applicability_conditions 실증 데이터 (14건 현황)

실제 등록 예시:
```
law_name: 산업안전보건법 시행령
appendix_no: 별표 3
metric: METRIC:EMPLOYEE_COUNT
operator: >=
threshold_value: 50.0
threshold_unit: 명
action_type: APPOINTMENT
action_text: 고위험 제조업군 50명 이상 499명 미만 안전관리자 1명
scope_type: INDUSTRY
scope_values: ["C10","C11","C19","C20","C21","C24"]
```

### THRESHOLD 조건판정 흐름

```
THRESHOLD:EMPLOYEE_50_PLUS
  ↓
applicability_conditions 조회:
  WHERE metric = 'METRIC:EMPLOYEE_COUNT'
    AND operator = '>='
    AND threshold_value <= [소비자 employee_count]
  ↓
scope_values(업종코드 목록)과 소비자 ksic_code 교집합 확인
  ↓
충족 시: appendix_no → law_article.article_no → semantic_clause 조회
  ↓
의무후보 생성
```

### Route B 연결 경로 실증

```
applicability_conditions.appendix_no = "제17조"
  ↓
law_article.article_no = 17, law_name = '산업안전보건법'
  ↓
semantic_clause.source_article_id = law_article.id
  WHERE executor_text = '사업주' AND content_type = 'OBLIGATION'
  ↓
clause_id: 66772b0d-516d-4eae-b5ec-c99729e63d3c
("사업주는 사업장에 안전관리자를 두어야 한다...")

연결 경로 실증 완료.
```

### Route B 현재 한계

```
현재 applicability_conditions 14건만 등록:
  - 별표3 안전관리자: 7건
  - 산안법 제29조 교육: 3건
  - 산안법 제36조 위험성평가: 1건
  - 산안법 제129조 건강진단: 1건
  - 산안규칙 제19조 경보설비: 1건
  - 산안법 제16조 관리감독자: 1건

WO-APPENDIX-COLLECT-001 완료 후 대폭 확장 필요.
현재는 위 14건에 한해서만 Route B 동작.
```

---

## 3. 의무후보 데이터 구조

### 최소 구조

```json
{
  "candidate_id": "uuid",
  "semantic_clause_id": "uuid",
  "trigger_codes": ["WORK:CONFINED_SPACE"],
  "trigger_route": "A",
  "match_source": "action_text",
  "confidence": "HIGH",
  "reason": "action_text에서 '밀폐공간' 키워드 직접 매칭"
}
```

### 필드 정의

| 필드 | 타입 | 의미 |
|---|---|---|
| candidate_id | uuid | 후보 고유 ID |
| semantic_clause_id | uuid | 매칭된 조문 ID |
| trigger_codes | text[] | 발생 Trigger (복수 가능) |
| trigger_route | enum(A, B) | 조회 경로 |
| match_source | enum(condition_text, action_text, applicability_condition) | 매칭 필드 |
| confidence | enum(HIGH, MEDIUM, LOW) | 신뢰도 |
| reason | text | 매칭 근거 요약 |

### confidence 판정 기준

```
HIGH   — condition_text 직접 매칭 (조건이 명시되어 있음)
MEDIUM — action_text 매칭 (조건 없이 내용에서 키워드 발견)
LOW    — Route B (applicability_conditions 경유, 업종 범위 추정 포함)
```

### 체크엔진이 최소로 필요한 정보

```
1. semantic_clause_id         → 원문 조회용
2. trigger_codes              → 어떤 조건으로 발생했는가
3. trigger_route              → A/B 경로 구분
4. confidence                 → 검증 우선순위
5. executor_text (조문에서)    → 주체 재검증용
6. condition_text (조문에서)   → 조건 재검증용
7. source_article_id (조문에서) → 중복 제거용
```

---

## 4. 다중 Trigger 처리 정책

### 기본 원칙: 독립 조회 후 합집합

```
입력:
  {BUSINESS:REGISTERED, THRESHOLD:EMPLOYEE_50_PLUS, WORK:CONFINED_SPACE, EQUIPMENT:CRANE}

처리:
  Step 1. BUSINESS:REGISTERED → Route A → 491건
  Step 2. THRESHOLD:EMPLOYEE_50_PLUS → Route B → N건
  Step 3. WORK:CONFINED_SPACE → Route A → 22건
  Step 4. EQUIPMENT:CRANE → Route A → 29건
  Step 5. 합집합 (by semantic_clause_id)
```

### 교집합 사용 안 하는 이유

```
교집합 = 모든 Trigger 동시 만족 의무만 추출
→ 법령은 조건 하나에 의무 하나가 발생
→ WORK:CONFINED_SPACE만으로 밀폐공간 의무 발생
→ 교집합 사용 시 의무 심각하게 누락

합집합 = 각 Trigger에 해당하는 의무 모두 수집
→ 이후 체크엔진에서 실제 조건 충족 여부 재검증
```

### 처리 순서

```
BUSINESS → THRESHOLD → WORK → EQUIPMENT → EQUIPMENT_ACT → HAZARD_FACTOR
이유: BUSINESS가 가장 넓은 범위. 이후 Trigger들은 특수 조건 추가.
우선순위는 없음. 모든 Trigger 독립 처리 후 합집합.
```

---

## 5. 중복 의무 처리 정책

### 실증 데이터

178건 condition_based 의무 중 다중 Trigger 동시 매칭: 10건 (5.6%)

예시:
- EQUIPMENT:CRANE + WORK:DEMOLITION → "크레인 해체 작업 시 조치" 2건
- WORK:WELDING + EQUIPMENT:WELDER → "아크용접기 안전장치" 2건

### 정책: 의무후보는 1건, trigger_codes는 배열로 기록

```json
{
  "candidate_id": "uuid-001",
  "semantic_clause_id": "f1013bf7-...",
  "trigger_codes": ["EQUIPMENT:CRANE", "WORK:DEMOLITION"],
  "primary_trigger": "EQUIPMENT:CRANE",
  "confidence": "HIGH"
}
```

중복 제거 기준: semantic_clause_id 동일 → 통합 후 trigger_codes 배열에 모두 기록

근거: 동일 조문에서 발생하는 의무는 1개. 복수 Trigger 매칭은 해당 사업장이 복수 조건을 만족함을 의미하며, 의무를 강화하는 정보다.

---

## 6. 동의어 처리 정책

### 필수 동의어 (실증 기반)

밀폐공간 동의어:
```
"밀폐공간"으로만 찾으면 누락:
  - "밀폐된 공간에서 스프레이 건을 사용하여..."
  - "산소결핍증이 있거나 유해가스에 중독되었을 경우..."
패턴: (밀폐공간|산소결핍|황화수소|밀폐된 공간)
```

크레인 동의어:
```
"크레인"으로만 찾으면 누락:
  - "양중기의 달기 와이어로프..." 5건 누락
  - "순간풍속...양중기를 사용하여..." 1건 누락
패턴: (크레인|양중기)
추가 의무 발견: 7건
```

### 동의어 관리 원칙

```
동의어 사전은 DB 테이블로 관리. 코드 하드코딩 금지.
구조:
  trigger_code        | keyword_pattern
  WORK:CONFINED_SPACE | (밀폐공간|산소결핍|황화수소|밀폐된 공간)
  EQUIPMENT:CRANE     | (크레인|양중기)

확장 기준: 산업안전보건 법령에서 실제 사용되는 표현에 한정.
일반 사전적 동의어 확장 금지 (과잉 Trigger 방지).
```

---

## 7. 체크엔진 전달 구조

### 의무후보 풀 최종 구조

```json
{
  "factory_id": "uuid",
  "diagnosis_context": {
    "trigger_codes": ["BUSINESS:REGISTERED", "WORK:CONFINED_SPACE", "EQUIPMENT:CRANE"],
    "employee_count": 80,
    "ksic_code": "25112"
  },
  "candidates": [
    {
      "candidate_id": "uuid-001",
      "semantic_clause_id": "uuid",
      "trigger_codes": ["BUSINESS:REGISTERED"],
      "trigger_route": "A",
      "match_source": "condition_text_null",
      "confidence": "HIGH",
      "reason": "무조건 발생 의무"
    },
    {
      "candidate_id": "uuid-022",
      "semantic_clause_id": "uuid",
      "trigger_codes": ["WORK:CONFINED_SPACE"],
      "trigger_route": "A",
      "match_source": "condition_text",
      "confidence": "HIGH",
      "reason": "condition_text에서 '밀폐공간' 직접 매칭"
    },
    {
      "candidate_id": "uuid-057",
      "semantic_clause_id": "uuid",
      "trigger_codes": ["EQUIPMENT:CRANE", "WORK:DEMOLITION"],
      "trigger_route": "A",
      "match_source": "action_text",
      "confidence": "MEDIUM",
      "reason": "action_text에서 크레인+해체 동시 매칭"
    }
  ]
}
```

### 체크엔진이 이 구조로 수행하는 검증

```
검증 1. executor_text 재확인 (semantic_clause에서 직접 읽기)
검증 2. confidence=MEDIUM 후보 조건 재검증
검증 3. Route B 후보: employee_count + ksic_code 교차검증
검증 4. source_article_id 기준 중복 의무 최종 제거
검증 5. 우선순위 산정 (P1~P4)
```

---

## 8. 예상 의무후보 건수

### 단일 Trigger 기준

| Trigger | 예상 후보 |
|---|---|
| BUSINESS:REGISTERED | 491건 |
| HAZARD_FACTOR:CHEMICAL | 65건 |
| WORK:MELTING | 41건 |
| HAZARD_FACTOR:DUST | 37건 |
| WORK:DEMOLITION | 39건 |
| WORK:DIVING | 32건 |
| HAZARD_FACTOR:RADIATION | 28건 |
| EQUIPMENT:CRANE | 29건 |
| WORK:HIGH_PRESSURE | 29건 |

### 복합 입력 시 예상 후보 (중복 제거 후)

```
예시 입력:
  employee_count=80, has_confined_space=true, equipment=[CRANE]

후보 추정:
  BUSINESS:  491건 (기저)
  WORK:CONFINED_SPACE: 22건 (고유분)
  EQUIPMENT:CRANE: 약 15건 (BUSINESS 미중복분)
  THRESHOLD: Route B, 약 5~10건

  총 예상: 530~540건
  중복 제거 후: 510~530건

최종 체크엔진 입력 규모: 사업장 유형별 300~600건 예상
```

### 중복 발생 비율

실증: 178건 중 다중 Trigger 매칭 10건 = 5.6%
→ 중복 비율 낮음. 중복 처리 로직이 병목될 가능성 낮음.

---

## 9. WO-CHECK-001 전달 항목

체크엔진 상세설계에서 확정해야 할 것:

```
1. confidence=MEDIUM 후보 재검증 기준
   → action_text 매칭은 조건 충족을 보장하지 않음
   → 어떤 기준으로 PASS/DROP 판정하는가?

2. Route B 후보의 업종 교차검증 방법
   → scope_values vs 소비자 ksic_code (2자리 vs 4자리 정합성)

3. THRESHOLD 수치 검증
   → employee_count >= threshold_value AND ksic_code in scope_values 동시 충족

4. 우선순위 P1~P4 산정 방법
   → penalty_numeric 기준 구체적 임계값

5. 최종 의무목록 규모 목표치
   → 300~600건 입력 → 50~150건 출력 예상
```

---

*WO-TRIGGER-001 완료 | 테이블 생성 없음 | 코드 작성 없음 | 구현 없음*
