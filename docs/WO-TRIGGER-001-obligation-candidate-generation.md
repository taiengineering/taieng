# WO-TRIGGER-001
Trigger 기반 의무후보 생성 설계서

작성일: 2026-06-22
Unit 다계: 해결책 강구 (구현 없음)

---

## 1. Route A 설계 — 직접조회 방식

### 1-1. 대상 Trigger

```
BUSINESS / WORK / EQUIPMENT / EQUIPMENT_ACT / HAZARD_FACTOR
```

### 1-2. 조회 구조

```
Trigger Code
  ↓
[Trigger 키워드 세트 조회]
  condition_text MATCHES keyword_set
  OR action_text MATCHES keyword_set
  AND content_type IN ('OBLIGATION','PROHIBITION')
  AND executor_text = '사업주'
  ↓
의무후보 풀
```

**필수 원칙: condition_text OR action_text 양쪽 검색**

검증 결과:
- WORK:MELTING: condition 매칭 2건, action 매칭 41건 → action만 조회 시 95% 누라
- WORK:DEMOLITION: condition 23, action 36 → 양쪽 합산 39건 (4건 중복)
- condition만 조회 시 평균 40% 손실 발생

### 1-3. 필드별 조회 전략

| Trigger Type | condition_text 사용 | action_text 사용 | 이유 |
|---|---|---|---|
| BUSINESS | 사용 안 함 (IS NULL 조회) | X | 조건 없음 = NULL |
| WORK | ✓ | ✓ | 키워드가 action에 주로 있음 |
| EQUIPMENT | ✓ | ✓ | 설비명이 action에 많이 등장 |
| EQUIPMENT_ACT | ✓ | ✓ | 사용행위 조합어 action에 집중 |
| HAZARD_FACTOR | ✓ | ✓ | 유해인자명 action에 많이 등장 |

### 1-4. Trigger Code → 키워드 세트 매핑

```
BUSINESS:REGISTERED
  키워드: []
  조회: condition_text IS NULL

WORK:CONFINED_SPACE
  키워드: ["밀폐공간", "산소결핵", "황화수소"]
  동의어: ["밀폐된 공간"] (2건 추가 확인)

WORK:DIVING
  키워드: ["잠수", "잠함", "잠수작업자"]

WORK:HIGH_PRESSURE
  키워드: ["고압작업", "고압가스", "기압조절실"]

WORK:WELDING
  키워드: ["용접", "용단"]

WORK:ASBESTOS
  키워드: ["석면", "석면해체", "석면분진"]

WORK:BLASTING
  키워드: ["발파", "화약류", "폭발물"]

WORK:EXCAVATION
  키워드: ["굴착", "굴착공사", "굱착작업"]

WORK:DEMOLITION
  키워드: ["해체", "철거", "해체작업"]

WORK:MELTING
  키워드: ["용해", "용융", "주조", "용선"]

WORK:PAINTING
  키워드: ["도장", "분사도장", "도료"]

EQUIPMENT:CRANE
  키워드: ["크레인", "양중기"]  ← 동의어 포함
  확장 안 함: 타워크레인, 이동식크레인은 별도 코드로

EQUIPMENT:CHEMICAL_VESSEL
  키워드: ["화학설비", "반응기", "혼합기"]

EQUIPMENT:LOCAL_EXHAUST
  키워드: ["국소배기", "집진기", "후드"]

EQUIPMENT:EXCAVATOR
  키워드: ["굴착기", "차량계 건설기계", "건설기계"]

HAZARD_FACTOR:CHEMICAL
  키워드: ["관리대상 유해물질", "허가대상 유해물질", "금지유해물질", "화학물질"]

HAZARD_FACTOR:DUST
  키워드: ["분진", "분진작업", "광물성 분진"]

HAZARD_FACTOR:RADIATION
  키워드: ["방사선", "방사성물질", "방사선업무"]
```

---

## 2. Route B 설계 — 조건판정 방식

### 2-1. 대상 Trigger

```
THRESHOLD / INDUSTRY / REFERENCE
```

### 2-2. 조건판정 구조

```
Trigger Code
  ↓
[applicability_conditions 테이블 조회]
  threshold_code MATCHES, metric MATCHES, ksic_code 포함 확인
  ↓
[appendix_no → law_article.article_no 매핑]
  ↓
[semantic_clause.source_article_id 조회]
  content_type IN ('OBLIGATION','PROHIBITION')
  AND executor_text = '사업주'
  ↓
의무후보 풀
```

### 2-3. Route B 데이터 소스 확정

실데이터 검증으로 확인:

**applicability_conditions (14건)** 구조:
```
law_name + appendix_no  → 다음과 같이 연결
  산안법 시행령 별표 3 + 50명 + C10 → 안전관리자 선임 의무
  산안법 제17조     + employee >= 1  → 안전관리자 선임 의무
```

**appendix_no → law_article 연결 방식**:
```
appendicx_no = "제17조"
  → law_article WHERE law_id = [산안법 id] AND article_no = 17
  → semantic_clause WHERE source_article_id = [article.id]
      AND executor_text = '사업주'
      AND content_type = 'OBLIGATION'
  → clause_id: 66772b0d... ("...안전관리자를 보좌하고...")
```

**실증된 Route B 연결 경로**:
- 산안법 제17조 → clause_id `66772b0d` 1건 (OBLIGATION, executor='사업주')
- 산안법 제18조 → 보건관리자 선임 조문
- 산안법 제24조 → 산업안전보건위원회 구성 조문
- 산안법 제25조 → 안전보건관리규정 작성 조문

### 2-4. THRESHOLD 판정 로직

```
입력값 (employee_count, ksic_code)
  ↓
[applicability_conditions 필터]
  metric = 'METRIC:EMPLOYEE_COUNT'
  AND operator = '>='
  AND threshold_value <= employee_count
  AND (scope_values ∩ ksic_prefix) ≠ ∅  ← 업종 교집합
  ↓
[조건 충족 항목] → appendix_no → clause_id
  ↓
의무후보
```

**현재 한계**: applicability_conditions가 14건만 있어 별표3 전체를 커버하지 못한다. WO-APPENDIX-COLLECT-001 완료 후 실질 비율 확대. 이 전까지는 14건 범위닌 판단 가능.

---

## 3. 의무후보 데이터 구조

```json
{
  "candidate_id": "uuid",
  "semantic_clause_id": "uuid",
  "trigger_code": "WORK:CONFINED_SPACE",
  "trigger_route": "A",
  "match_field": "action_text",
  "match_keyword": "밀폐공간",
  "confidence": "HIGH",
  "reason": "action_text 키워드 매칭"
}
```

### 필드 정의

| 필드 | 타입 | 설명 |
|---|---|---|
| candidate_id | uuid | 의무후보 단위 식별자 |
| semantic_clause_id | uuid (FK) | 연결된 semantic_clause.id |
| trigger_code | text | 발생시키거나
| trigger_route | A/B | 직접조회 vs 조건판정 |
| match_field | condition/action/null | Route A에서 매칭된 필드 |
| match_keyword | text/null | 실제 매칭된 키워드 |
| confidence | HIGH/MED/LOW | HIGH: condition 매칭 / MED: action 매칭 / LOW: 별표 경유 |
| reason | text | 체크엔진 판정 근거 |

### confidence 기준

```
HIGH: condition_text에 키워드 직접 매칭
  → \"...\ubc00\ud3d0\uacf5\uac04\uc5d0\uc11c \uc791\uc5c5\uc744 \ud558\ub294 \uacbd\uc6b0\" → 조건이 매칭

MED: action_text에만 키워드 매칭 (condition_text는 NULL이거나 불일치)
  → "보늘러를 \uc804담하는 \uc548전관리자를..." → 조건 불명확하나 의무 연관성 높음

LOW: Route B (applicability_conditions 경유)
  → 별표 조건에 의해 생성되었으나 clause 연결이 소수
```

### 체크엔진에 기대하는 필수 정보

```
체크엔진 입력:
  semantic_clause_id     → clause 원문 확인
  trigger_code           → Trigger 종류 확인
  confidence             → 검증 우선순위
  소비자 입력 원본   → employee_count, ksic_code, has_* 등

체크엔진 결정:
  통과 / 제거 (주체 없음, 조건 불충족, 별표 미충족)
  통과 시 최종 의무 목록에 포함
```

---

## 4. 다중 Trigger 처리 정책

### 4-1. 독립 조회후 UNION

```
입력: {
  employee_count: 80,
  has_confined_space: true,
  equipment_assets: ["CRANE"]
}

Trigger Code Set:
  BUSINESS:REGISTERED
  THRESHOLD:EMPLOYEE_50_PLUS
  WORK:CONFINED_SPACE
  EQUIPMENT:CRANE

처리:
  [1] BUSINESS:REGISTERED → Route A (condition IS NULL) → 491건
  [2] THRESHOLD:EMPLOYEE_50_PLUS → Route B (applicability_conditions) → 리스트 N건
  [3] WORK:CONFINED_SPACE → Route A (키워드) → 22건
  [4] EQUIPMENT:CRANE → Route A (키워드) → 29건

  전체 UNION → source_article_id 기준 중복 제거
  → 최종 의무후보 풀
```

### 4-2. 우선순위

```
독립 조회, UNION 전략. 교집합 방식 불사용.

근거:
  WORK:CONFINED_SPACE와 EQUIPMENT:CRANE은 독립적으로 의무를 발생시키지,
  둘 다 해당하는 사업장은 두 용어 모두의 의무를 받는다.
  교집합 사용 시 없는 의무를 놈칐 수 있다.

조회 순서 (성능):
  Route B (THRESHOLD) → 결과 소수 (몇 개), 먼저 조회
  Route A BUSINESS → 491건 대량조회, 마지막
  Route A 나머지 → Trigger 순서대로
```

---

## 5. 중복 의무 처리 정책

### 정책: source_article_id 기준 1건 유지, 트리거 목록만 눈적

```
예시:
  EQUIPMENT:CRANE → 크레인 조문 X 파치 (source_article_id = AAA)
  EQUIPMENT_ACT:CRANE_USE → 동일 조문 X 파치 (source_article_id = AAA)

  갰결: 의무후보 1건가 (source_article_id AAA)
             trigger_codes: ["EQUIPMENT:CRANE", "EQUIPMENT_ACT:CRANE_USE"]
             confidence: HIGH (두 트리거 중 높은 것 선택)

반대 경우:
  WORK:CONFINED_SPACE → 조문 Y
  HAZARD_FACTOR:CHEMICAL → 조문 Y (0건 확인됨 — 실제 중복 없음)

만약 중복 발생 시:
  trigger_codes 집합에 둘 다 저장
  confidence 엄가는 직통 (OR 논리)
```

**거부 정책: source_article_id가 아닌 semantic_clause.id 기준 중복 제거**

이유: 같은 조문의 다른 파트(PART)들이 각각 다른 의무일 수 있다.
example: 제17조의 1항, 2항, 3항 이 모두 다른 의무를 정의할 수 있음.

---

## 6. 동의어 처리 정책

### 동의어 필요 검증 결과

| Trigger | 주 키워드 | 동의어 | 추가 의무 |
|---|---|---|---|
| WORK:CONFINED_SPACE | 밀폐공간 | 밀폐된 공간 | +2건 |
| EQUIPMENT:CRANE | 크레인 | 양중기 | +5건 (condition NULL이 많음) |
| WORK:WELDING | 용접 | 아크용접 | 바로 용접 안에 포함됨 |

### 동의어 사전 주요 엔트리 (WO-TRIGGER-001 시점 확정분)

```
WORK:CONFINED_SPACE → ["밀폐공간", "산소결합", "황화수소", "밀폐된 공간"]
EQUIPMENT:CRANE     → ["크레인", "양중기"]
WORK:DIVING         → ["잠수", "잠함", "잠수작업자"]
WORK:HIGH_PRESSURE  → ["고압작업", "고압가스", "기압조절실"]
WORK:ASBESTOS       → ["석면", "석면해체", "석면분진"]
WORK:BLASTING       → ["발파", "화약류", "폭발물", "화약", "낙뜜"]
WORK:EXCAVATION     → ["굵착", "굱착공사", "굱착작업"]
HAZARD_FACTOR:CHEMICAL → ["관리대상 유해물질", "허가대상 유해물질", "금지유해물질", "화학물질", "유해물질"]
```

동의어 확장은 하드코딩 금지. 별도 관리 테이블(키워드 사전)으로 추후 확장할 수 있게 설계.

---

## 7. 체크엔진 전달 구조

### 채크엔진 입력 패키지

```json
{
  "factory_id": "uuid",
  "diagnosis_id": "uuid",
  "input_snapshot": {
    "ksic_code": "C2511",
    "employee_count": 80,
    "has_confined_space": true,
    "equipment_assets": ["CRANE"],
    "hazard_factors": []
  },
  "trigger_codes": [
    "BUSINESS:REGISTERED",
    "THRESHOLD:EMPLOYEE_50_PLUS",
    "WORK:CONFINED_SPACE",
    "EQUIPMENT:CRANE",
    "EQUIPMENT_ACT:CRANE_USE"
  ],
  "candidates": [
    {
      "candidate_id": "...",
      "semantic_clause_id": "...",
      "trigger_code": "WORK:CONFINED_SPACE",
      "trigger_route": "A",
      "match_field": "condition_text",
      "match_keyword": "밀폐공간",
      "confidence": "HIGH",
      "reason": "condition_text 매칭"
    }
  ]
}
```

### 체크엔진이 수행하는 검증

```
[V1] executor_text 필터: '사업주' 아당시 제거
[V2] condition 충족 검증: confidence=MED 이하는 후보에 대해 condition_text 재판단
[V3] 별표 임계값 검증: THRESHOLD Route B 후보에 한정 (employee_count, ksic 조합 확인)
[V4] 중복 제거: source_article_id 동일 후보 통합
```

---

## 8. 예상 후보 건수

### 실데이터 기반 추정

```
[Route A 의무후보 (condition NULL + 키워드 매칭)]

BUSINESS:REGISTERED       491건 (condition=NULL 전체)
WORK 합계              236건 (Trigger별 합산, 중복 미제거)
HAZARD_FACTOR 합계      164건
EQUIPMENT 합계          146건
EQUIPMENT_ACT 합계       45건

원루 UNION 총: ~700~900건
Trigger 간 중복 (10건 확인) 감안 시: ~680~870건

[Route B 의무후보]
THRESHOLD 회차당        5~15건 추정 (applicability_conditions 14건 기준)

[의무후보 풀 총계]
최소 (기본 사업장): ~500건 (BUSINESS만)
표준 (크레인+밀폐공간 등 복합 사업장): ~600~750건
고위험 (화학설비+다수 Trigger): ~850~950건

체크엔진 통과 예상: 후보의 60~70% 통과
  → 최종 의무 목록: 300~600건 예상
```

---

## WO-CHECK-001에 넘길 제약조건

```
[C1] Route A MED 후보 재판단
  action_text 매칭만 시: confidence=MED
  체크엔진이 condition_text 뢰치 확인 후 통과 여부 결정

[C2] Route B 후보 충족성 검증 방식
  employee_count + ksic_code + threshold_value 조합 판단

[C3] 후보 중복 제거
  source_article_id 동일 시 trigger_codes 병합, clause 단일화

[C4] executor_text 다중 파싱 예외 처리
  executor_text ≠ '사업주'인 것 전체 제거
  파싱 오류로 통과된 좌보 executor("지도·조언하", "정하") 제거
```

---

*WO-TRIGGER-001 완료 | 테이블 생성 없음 | 코드 작성 없음 | 구현 없음*
