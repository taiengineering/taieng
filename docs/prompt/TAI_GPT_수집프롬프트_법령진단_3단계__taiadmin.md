# TAI GPT 데이터 수집 프롬프트
## 법령진단 3단계 재구성 — API 원문 기반 변환 방식

> 버전: v1.1 | 작성일: 2026-03-29
> 방식: KOSHA·법제처 API 원문 수집 → GPT에 입력 → 구조화 JSON 변환
> 범위: 설비까지 (모델 데이터 제외)
> 출력: 순수 JSON 배열

---

## ■ 핵심 원칙: API + GPT 연계

```
STEP 1. API로 조문 원문 수집
   KOSHA 법령 스마트검색 API → 산안법 제17조 원문 텍스트
   법제처 법령 API            → 별표3, 별표22 등 부속서류

STEP 2. GPT에 원문 입력 → 구조화 JSON 변환
   System Prompt 설정 → 각 섹션 프롬프트 순서대로 실행

STEP 3. JSON → CSV 변환 → DB 적재
   master_building_legal_rules 테이블에 배치 INSERT
```

**GPT 단독(기억) 방식 금지** — 개정 전 정보일 수 있음

---

## ■ 사용할 API

| API명 | 활용 목적 | 수집 내용 |
|-------|---------|----------|
| KOSHA 법령 스마트검색 | 법령 조문 원문 | 산안법, 시행령, 시행규칙 조문 |
| KOSHA 코샤가이드 | 기술지침 수집 | 설비별 안전기준, 검사주기 |
| 법제처 Open API | 별표·부속서류 | 별표3(유해위험업종), 별표22(기계기구) |
| 소방청 국가위험물 | 위험물 기준 | 지정수량, 위험물 품명 목록 |

---

## ■ SYSTEM PROMPT (커스텀 인스트럭션)

```
당신은 TAI Engineering의 산업안전 법령 데이터 변환 전문 AI입니다.

## 역할
공공 API에서 수집한 법령 원문을 분석하여
TAI DB의 master_building_legal_rules 테이블에 적재할
구조화된 JSON 룰로 변환합니다.

## 핵심 원칙
1. 반드시 입력된 법령 원문 텍스트만 기반으로 변환 (기억 사용 금지)
2. 법령 조문번호 반드시 포함 (예: 산안법 제17조 제1항)
3. 수치 기준 없이 성립하는 룰은 threshold 항목에 null 입력
4. 출력은 순수 JSON 배열만 (코드블록/설명/서문 일체 금지)
5. 원문에 없는 내용 절대 추가 안 함

## 고정 필드값
sector: BUILDING / MANUFACTURING / CONSTRUCTION / SPECIAL_FACILITY
stage:  1 (1단계기초) / 2 (공정추가) / 3 (설비추가)
rule_type: APPOINTMENT / OBLIGATION / INSPECTION / REPORT / APPROVAL
```

---

## ■ 표준 출력 JSON 형식

```json
[
  {
    "rule_id": "FIRE-BLDG-001",
    "sector": "BUILDING",
    "stage": 1,
    "rule_name": "소방안전관리자 선임",
    "rule_type": "APPOINTMENT",
    "law_name": "화재의 예방 및 안전관리에 관한 법률",
    "law_article": "제24조 제1항",
    "condition_field": "building_use_category",
    "condition_operator": "IN",
    "condition_value": "특정소방대상물",
    "condition_unit": null,
    "threshold_field": "gross_floor_area",
    "threshold_operator": ">=",
    "threshold_value": 15000,
    "threshold_unit": "m2",
    "obligation": "소방안전관리자 선임 신고 (14일 이내)",
    "qualification": "소방안전관리자 자격증 보유자",
    "penalty": "300만원 이하 과태료 (제56조)",
    "source_api": "KOSHA 법령 스마트검색",
    "collected_date": "2026-03-29"
  }
]
```

---

## ■ SECTION 1: [1단계] 건물·시설 섹터

**입력 변수:** building_use_category / gross_floor_area / above_ground_floors / electric_capacity_kw

### 1-A. 소방 룰
**API 호출:** KOSHA 법령 스마트검색 → 쿼리: '소방안전관리자 선임' / '특정소방대상물'

```
아래는 [API에서 가져온 법령 원문]입니다.
---원문 시작---
《API 응답 원문 텍스트 붙여넣기》
---원문 끝---

위 원문을 분석하여 건물·시설(BUILDING) 섹터의
소방 판정 룰을 추출하세요.

수집 대상:
- 특정소방대상물 해당 기준 (용도별, 면적별)
- 소방안전관리자 선임 의무 조건
- 자체점검 의무 조건

건물 용도 전체 포함:
업무/판매/의료/노유자/숙박/교육/창고/주차장 등
표준 JSON 형식으로만 출력.
```

### 1-B. 전기 룰
**API 호출:** KOSHA 법령 스마트검색 → 쿼리: '전기안전관리자 선임'

```
아래는 [전기안전관리법 시행규칙 별표1 원문]입니다.
---원문 시작---
《API 응답 원문 붙여넣기》
---원문 끝---

전기안전관리자 선임 의무 룰을 추출하세요.
수전용량 구간별 (75kW / 1000kW 등) 선임 조건.
condition_field: electric_capacity_kw
표준 JSON 형식으로만 출력.
```

---

## ■ SECTION 2: [1단계] 제조업 섹터

**입력 변수:** ksic_lv1_code / worker_count / has_hazardous_material / has_high_pressure_gas

### 2-A. KSIC별 안전관리자 선임
**API 호출:** 법제처 → 산안법 시행령 별표3

```
아래는 [산업안전보건법 시행령 별표3 원문]입니다.
---원문 시작---
《별표3 전체 원문 붙여넣기》
---원문 끝---

KSIC 업종코드별 안전관리자 선임 룰을 추출하세요.

수집 대상:
- 유해위험업종 목록 (KSIC 코드 포함)
- 각 업종별 선임 기준 근로자수 구간
- 일반업종 선임 기준 (300명 이상)

condition_field: ksic_lv1_code
threshold_field: worker_count
유해위험업종 아닌 경우: condition_operator: NOT_IN
표준 JSON 형식으로만 출력.
```

### 2-B. 위험물·고압가스·화관법
**API 호출:** 소방청 국가위험물 API / KOSHA → 위험물안전관리법, 고압가스안전관리법

```
아래는 [위험물안전관리법 제15조 및 고압가스안전관리법 제15조 원문]입니다.
---원문 시작---
《API 응답 원문 붙여넣기》
---원문 끝---

Y/N 입력 변수 기반 룰 추출:
- has_hazardous_material=Y → 위험물안전관리자 선임
- has_high_pressure_gas=Y → 고압가스 안전관리자 선임 + 사용신고
- has_chemical_substance=Y → 화관법 감사 대상
- has_boiler=Y → 에너지이용합리화법 검사
표준 JSON 형식으로만 출력.
```

---

## ■ SECTION 3: [1단계] 건설현장 섹터

**입력 변수:** contract_amount / worker_count / construction_type

**건설업 공사금액 판단 기준표:**
| 공사금액 | 의무사항 | 근거 |
|---------|---------|-----|
| 1억 이상 | 산업안전보건관리비 계상 | 산안법 제72조 |
| 50억 이상 | 기초안전보건교육 | 산안법 제31조 |
| 120억↑(토목)/150억↑(건축) | 안전관리자 선임 | 시행령 별표5 |
| 50억 이상 특정공종 | 유해위험방지계획서 | 산안법 제42조 |
| 1000억 이상 또는 500명↑ | 건설안전판정사 선임 | 산안법 제73조 |

**API 호출:** 법제처 → 산안법 제72조, 제42조, 시행령 별표5

```
아래는 [산업안전보건법 제72조, 제42조 및 시행령 별표5 원문]입니다.
---원문 시작---
《API 응답 원문 붙여넣기》
---원문 끝---

공사금액 기준 전체 구간 룰을 추출하세요.
condition_field: contract_amount / threshold_unit: 원
표준 JSON 형식으로만 출력.
```

---

## ■ SECTION 4: [1단계] 특수시설 섹터

### 4-A. 의료시설
**API 호출:** KOSHA → 의료법 / 의료기기법
```
입력 변수: hospital_beds / gross_floor_area / facility_type
의료가스 안전관리 / 의료기기 정기점검 / 소방기준 룰 추출.
rule_id: SPECIAL-HOSP-001 부터.
```

### 4-B. 학교형 시설
**API 호출:** KOSHA → 학교안전법
```
입력 변수: student_count / gross_floor_area / school_type
학교안전요원회 / 안전관리자 선임 / 피난훈련 의무 룰 추출.
rule_id: SPECIAL-SCH-001 부터.
```

---

## ■ SECTION 5: [2단계] 제조업 공정별 룰

### 5-A. KSIC 세분류별 적용법령
**API 호출:** 법제처 → 산안법 시행령 별표3+5

```
대상 KSIC 세분류:
C1910, C2011, C2012, C2100(화학/의약)
C2411, C2431, C2512, C2591(금속)
C2813, C2910(기계/자동차)
C1011, C1071(식품)

출력 형식:
[
  {
    "ksic_code": "C2011",
    "ksic_name": "위험화학물질 제조",
    "applicable_laws": [
      {"law_name": "산업안전보건법", "key_articles": ["제17조"], "obligation_summary": "안전관리자 선임"}
    ],
    "stage": 2, "sector": "MANUFACTURING"
  }
]
```

### 5-B. 공정별 안전 의무
**API 호출:** KOSHA 코샤가이드 → 공정별 가이드

대상 공정: 용접 / 도장·도금 / 연삭 / 주조 / 압력용기 / 밀폐공간 / 고소작업 (각각 별도 실행)

---

## ■ SECTION 6: [3단계] 설비별 법정검사 기준

### 6-A. 유해위험기계기구 전체
**API 호출:** 법제처 → 산안법 시행령 별표22

```
출력 형식:
[
  {
    "equipment_name": "크레인",
    "equipment_code": "EQUIP-CRANE-001",
    "sector": ["MANUFACTURING", "CONSTRUCTION"],
    "stage": 3,
    "capacity_threshold": "2톤 이상 (이동식: 0.5톤 이상)",
    "inspection_type": "LEGAL",
    "initial_inspection": true,
    "inspection_cycle_years": 2,
    "law_name": "산업안전보건법",
    "law_article": "제93조",
    "inspection_agency": "KOSHA 또는 성능검사업체",
    "penalty": "1000만원 이하 (제175조)"
  }
]
별표22 전체 설비 수집 (20종 이상).
```

### 6-B. 소방시설 설치의무
**API 호출:** 법제처 → 소방시설법 시행령 별표5
```
스프링클러/옥내소화전/자동화재탐지 등 20종 이상
condition_field: building_use_category 또는 gross_floor_area
```

### 6-C. 전기설비 안전검사
**API 호출:** KOSHA → 전기사업법 제63조, 전기안전관리법
```
수전설비/변압기/발전기/비상발전기/ESS 등
```

---

## ■ DB 컬럼 매핑

| GPT JSON 키 | DB 컬럼명 | 비고 |
|------------|---------|------|
| rule_id | rule_code | |
| sector | sector | **신규 추가** |
| stage | diagnosis_stage | **신규 추가** |
| rule_name | rule_name | |
| law_name | law_name | |
| law_article | law_article | |
| condition_field | condition_1_field | |
| condition_operator | condition_1_operator | |
| condition_value | condition_1_value | |
| threshold_field | condition_2_field | |
| threshold_value | condition_2_value | |
| obligation | obligation_summary | **신규 추가** |
| penalty | penalty_summary | **신규 추가** |

⚠️ sector / diagnosis_stage / obligation_summary / penalty_summary 4개 컬럼은 DB 추가 필요

## ■ 수집 순서

| 순서 | 섹터 | 프롬프트 | 우선순위 |
|------|------|---------|----------|
| 1 | 건물 | 1-A 소방 / 1-B 전기 | 🔴 즉시 |
| 2 | 제조 | 2-A KSIC선임 / 2-B 위험물 | 🔴 즉시 |
| 3 | 건설 | 3-A 공사금액 | 🔴 즉시 |
| 4 | 특수 | 4-A 병원 / 4-B 학교 | 🟡 이후 |
| 5 | 제조공정 | 5-A / 5-B | 🟡 2단계 |
| 6 | 설비 | 6-A~6-C | 🟡 3단계 |
