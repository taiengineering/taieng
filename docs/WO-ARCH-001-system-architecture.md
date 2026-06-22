# WO-ARCH-001
법령의무도출 시스템 전체설계서

작성일: 2026-06-22  
작성자: Claude (설계 전담)  
단계: 아키텍처 확정 (구현 없음)

---

## 핵심 질문 4개 답변

### 질문 1: 이 시스템의 중심축은 무엇인가?

**의무발생조건(Obligation Trigger Condition)** 이다.

엔진도, Scope도, KSIC도 아니다.

근거: WO-PROBLEM-001에서 확인한 것처럼 사업주 의무 1,200건의 발생 조건은 조문 자체에 이미 명시되어 있다. "밀폐공간에서 작업을 하는 경우", "크레인을 사용하는 경우", "보호구를 지급하는 경우" 이것들이 조건이다. 이 조건들을 소비자 입력값과 연결하는 것이 시스템의 핵심이다.

```
중심축 = 조건(Condition) ↔ 입력(Input) 매칭
```

엔진은 이 매칭을 보조하는 수단이지, 중심이 아니다.

---

### 질문 2: 엔진은 어디까지 필요한가?

**레벨 4(25.7%)만 엔진이 필요하다.**

| 구간 | 처리 방식 | 엔진 필요 |
|---|---|---|
| 레벨 1: BUSINESS (40.9%) | 사업장 등록 = 즉시 발생 | ❌ |
| 레벨 2: EQUIPMENT/WORK (23.1%) | 입력값 매핑 테이블 | ❌ |
| 레벨 3: MATERIAL_HAZARD (4.7%) | 유해인자 입력 + 매핑 | 부분 |
| 레벨 4: UNRESOLVED (25.7%) | 참조조문 해석, 이벤트 | ✅ |

레벨 1~3 합계 74.3%는 매핑 테이블만으로 처리 가능. 엔진은 레벨 4를 위해 존재한다.

---

### 질문 3: 매핑만으로 처리 가능한 비율은?

**74.3% (892/1,200건)**

단, 이것은 사업주 의무 1,200건 기준이다. 전체 semantic_clause 의무(29,665건)로 확장하면 비율은 다르다 — TAI 타겟이 아닌 주체(행정기관, 감리업자, 공단 등)의 의무가 제외되어야 한다.

---

### 질문 4: 레벨 4 25.7%는 어떤 구조로 처리할 것인가?

3가지로 분리한다.

```
25.7% (308건)
  ├── 열거조항 참조 (~260건): 별표 데이터 구축 → 매핑 테이블로 흡수
  │     WO-APPENDIX-COLLECT-001과 연결
  │     구축 후 레벨 2로 전환 가능
  │
  ├── 실시간 이벤트 (~17건): 런타임 레이어에서 처리
  │     점검 결과 이상 → 보수 의무 발생
  │     이것은 SaaS 운영 기능 영역
  │
  └── 구조적 UNRESOLVED (~31건): 화이트리스트 수작업
        의미가 불명확하거나 맥락 없이 판별 불가능한 조문
        인간 검토 후 수작업 등록
```

→ **레벨 4는 "엔진"이 해결하는 것이 아니라 3가지 서로 다른 방법으로 분리 처리한다.**

---

## 1. 시스템 최상위 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    법령의무도출 시스템                         │
│                                                              │
│  [소비자 입력]                                                │
│       ↓                                                      │
│  [입력 표준화 계층]  ← 업종/설비/작업/유해인자/인원/면적 정규화   │
│       ↓                                                      │
│  [조건 매칭 계층]   ← 입력값 → 의무발생조건 매핑 (중심축)       │
│       ↓                                                      │
│  [의무후보 생성 계층] ← 매칭된 조건 → semantic_clause 풀링     │
│       ↓                                                      │
│  [체크엔진 계층]    ← 레벨 4 처리 + 의무후보 검증              │
│       ↓                                                      │
│  [6W 보강 계층]    ← 누가/언제/어디서/무엇을/어떻게/왜 채움     │
│       ↓                                                      │
│  [정제 계층]       ← 중복 제거, 우선순위, 유형 분류            │
│       ↓                                                      │
│  [출력 계층]       ← 의무목록/일정/업무배정/안전관리설계서       │
└─────────────────────────────────────────────────────────────┘
```

**레이어는 7개, 중심은 조건 매칭 계층이다.**

---

## 2. 입력 계층 설계

### 현재 입력값 충분성 판단

| 입력 항목 | 현재 존재 | 충분성 | 비고 |
|---|---|---|---|
| 업종 (KSIC) | `ksic_code` ✅ | 충분 | |
| 근로자 수 | `employee_count` ✅ | 충분 | |
| 특수작업 | `has_*` boolean ✅ | 충분 | 8개 flag |
| 설비 등록 | `equipment_assets` ✅ | 충분 | equipment_type_code |
| 공정 등록 | `factory_process` ✅ | 충분 | process_id |
| 유해인자 | **없음** ❌ | **부족** | 신규 필요 |
| 시설 용도 | `building_use_code` △ | 부분 | 소방 기준 미포함 |
| 공사금액 | `construction_amount` ✅ | 충분 | 건설업 전용 |
| 위험물 | `is_hazardous_material` △ | 부분 | 종류 구분 없음 |

### 추가 필요한 입력값 (신규)

```
[추가 필요 입력 — 레벨 3 커버용]

유해인자 분류 (체크박스 다중선택)
  ├── 소음작업 (강렬한 소음 / 충격소음)
  ├── 분진작업 (광물성 / 금속성 / 목재성 / 합성수지)
  ├── 관리대상 유해물질 (유기화합물 / 금속류 / 산·알칼리 / 가스상)
  ├── 허가대상 유해물질 (베릴륨 등 12종)
  ├── 금지유해물질 (특별관리)
  └── 방사선 작업

위험물 종류 (현재 boolean → enum 필요)
  ├── 인화성 액체
  ├── 가연성 가스
  ├── 산화성 물질
  └── 독성 물질
```

### 입력 표준 모델 (7개 그룹)

```
GROUP 1: 사업장 기본
  - ksic_code (업종)
  - employee_count (근로자 수)
  - sector (산업/건물/건설)

GROUP 2: 시설
  - building_use_code (건물 용도)
  - building_area (면적)
  - floor_count (층수)

GROUP 3: 특수작업 Flag
  - has_confined_space
  - has_blasting
  - has_diving
  - has_asbestos_demo
  - has_tower_crane
  - has_high_pressure_gas
  - has_chemical_substance
  - has_boiler

GROUP 4: 설비 등록
  - equipment_assets (equipment_type_code 목록)

GROUP 5: 공정 등록
  - factory_process (process_id 목록)

GROUP 6: 유해인자 [신규]
  - hazard_factor_codes (다중선택)

GROUP 7: 공사/건설 전용
  - construction_amount
  - construction_type
```

---

## 3. 의무발생조건 표준체계

### 최종 분류 (8개 코드)

| 코드 | 의미 | 입력 매핑 |
|---|---|---|
| BUSINESS | 사업장 존재 | 사업장 등록 = 발생 |
| THRESHOLD | 수치 임계값 | employee_count 등 |
| INDUSTRY | 업종 기반 | ksic_code |
| EQUIPMENT | 설비 보유 | equipment_type_code |
| EQUIPMENT_ACT | 설비 사용/설치 행위 | 상태값 + 등록 |
| WORK | 특수 위험 작업 | has_* flag |
| HAZARD_FACTOR | 유해인자 취급 | hazard_factor_codes |
| EVENT | 조건부 이벤트 | 런타임 이벤트 |
| REFERENCE | 별표/참조조문 | 별도 처리 |

**기존 분류 대비 변경사항:**
- `EQUIPMENT` → `EQUIPMENT`(보유) + `EQUIPMENT_ACT`(행위) 분리
  - "크레인 있음"과 "크레인을 사용하는 경우"는 다른 조건
- `MATERIAL_HAZARD` → `HAZARD_FACTOR`로 명칭 통일
  - 물질 자체보다 "취급 행위"가 조건
- `UNRESOLVED_REFERENCE` → `REFERENCE`로 단순화
  - 처리 방법이 확정되어 있으므로

---

## 4. 매핑 계층 설계

**입력값은 Trigger Code로 변환된다.**

Trigger Code = 의무발생조건의 기계가독 표현.

```
입력값 → [매핑 테이블] → Trigger Code Set → 의무후보 조회

예시:
  equipment_type_code = 'CRANE'
      → Trigger Code: EQUIPMENT:크레인, EQUIPMENT_ACT:크레인_사용중

  has_confined_space = true
      → Trigger Code: WORK:밀폐공간

  hazard_factor_code = '소음작업'
      → Trigger Code: HAZARD_FACTOR:소음작업

  employee_count = 80
      → Trigger Code: THRESHOLD:50이상, THRESHOLD:100미만
```

### 매핑 레이어 구조

```
┌──────────────────────────────────────────────────────┐
│  매핑 레이어                                          │
│                                                      │
│  입력 → Trigger Code 변환 규칙 3종                   │
│                                                      │
│  규칙 A. 직접 변환 (1:1)                             │
│    has_confined_space=true → WORK:밀폐공간           │
│    has_blasting=true       → WORK:발파               │
│    equipment_type='CRANE'  → EQUIPMENT:크레인         │
│                                                      │
│  규칙 B. 임계값 변환 (수치 → 코드)                   │
│    employee_count >= 50    → THRESHOLD:50이상         │
│    employee_count >= 100   → THRESHOLD:100이상        │
│    construction_amount >= X → THRESHOLD:공사금액기준  │
│                                                      │
│  규칙 C. 분류 변환 (코드 → 업종그룹)                 │
│    ksic_code → INDUSTRY:제조업고위험                  │
│    ksic_code → INDUSTRY:건설업                       │
│    ksic_code → INDUSTRY:일반                         │
└──────────────────────────────────────────────────────┘
```

매핑 테이블은 DB 테이블이다. 코드가 아니다.

기존 `applicability_conditions`(14건)과 `condition_scopes`(14건)가 이 역할의 원형이나 현재 범위가 너무 좁다. 본 설계 기준으로 재구성 필요.

---

## 5. 의무후보 생성 계층 설계

```
Trigger Code Set → semantic_clause 조회 → 의무후보 풀

처리 구조:

  FOR each Trigger Code in Set:
      조회 대상: semantic_clause
        WHERE content_type IN ('OBLIGATION','PROHIBITION')
          AND executor_text = '사업주'         ← 주체 필터
          AND [조건 키워드] MATCHES Trigger Code ← 조건 필터
      → 의무후보 추가

  중복 제거 (동일 source_article_id 기준)
  → 의무후보 풀 확정
```

**핵심 설계 결정: 의무후보는 semantic_clause를 직접 조회한다.**

기존 `rule_candidate`(34,456건)나 `runtime_candidate`(7건)를 경유하지 않는다. 이 계층들은 현재 미완성 상태이며, semantic_clause가 원본이다.

---

## 6. 체크엔진 위치 설계

### 체크엔진이 받는 입력

```
입력:
  1. 의무후보 풀 (semantic_clause id 목록)
  2. 소비자 입력 전체 (Trigger Code Set + 원본 입력값)
  3. 별표 데이터 (구축 완료 시)
  4. 참조조문 데이터 (law_article_part)
```

### 체크엔진이 검증하는 것

```
검증 1. 주체 검증 (executor filter)
  "사업주"인가? 아닌가?
  → 아니면 제거

검증 2. 조건 충족 검증 (condition match)
  의무후보의 condition_text가
  소비자 입력으로 충족되는가?
  → 불충족이면 제거

검증 3. 별표 임계값 검증 (threshold check)
  employee_count >= 별표 기준값?
  ksic_code ∈ 별표 업종목록?
  → 미충족이면 제거

검증 4. 중복 의무 식별
  동일 법조문 → 다중 semantic_clause 발생 시 통합
```

### 체크엔진 동작 위치

```
의무후보 생성 계층 직후, 6W 보강 계층 직전.

타이밍: 진단 실행 시 1회 (배치 가능)
입력크기: 사업장당 의무후보 ~200~800건 예상
```

체크엔진은 "생성 후 검증"이지 "생성 전 필터링"이 아니다. 후처리 방식으로 설계한다.

---

## 7. 6W 보강 계층 설계

| 6W | 데이터 소스 |
|---|---|
| 누가 | executor_text (semantic_clause). "사업주" 고정. 실제 담당자는 SaaS 배정 계층 |
| 언제 | cycle_text (semantic_clause) + appendix_condition 별표 주기 데이터 |
| 어디서 | where_text (현재 전량 NULL). 대안: condition_text에서 장소 키워드 추출 |
| 무엇을 | action_text (semantic_clause) 의무 내용 원문 |
| 어떻게 | form_token, how_text + document_form_master 서식 연결 |
| 왜 | law_article.article_no + law_master.law_name + penalty_numeric |

**현재 구조적 공백: `where_text`가 전량 NULL.** "어디서" 항목은 condition_text 파싱으로 보완하거나 수작업 보강이 필요하다.

---

## 8. 정제 계층 설계

### 중복 제거 기준

```
1순위: source_article_id 동일 → 1개로 통합
2순위: action_text 유사도 80% 이상 → 검토 후 통합
3순위: 상위법-하위법 관계 → 하위법 우선 (더 구체적)
```

### 우선순위 기준

```
P1 (즉시): 과태료/벌칙 3년 이상 or 3,000만원 이상
P2 (중요): 과태료/벌칙 존재
P3 (일반): 의무 이행 (벌칙 없음)
P4 (권고): 노력 의무 (하여야 한다 → 할 수 있다)

근거 데이터: penalty_numeric, penalty_candidate
```

### 유형 분류 기준

```
점검 (INSPECTION):    주기적 확인 + 기록 의무
교육 (EDUCATION):     근로자 대상 교육 실시 의무
신고 (REPORTING):     행정기관 제출/신고 의무
선임 (APPOINTMENT):   자격자 선임/배치 의무
설치 (INSTALLATION):  설비/시설 설치 의무
작성 (DOCUMENTATION): 서류/계획서 작성 의무
조치 (MEASURE):       안전조치 이행 의무
제공 (PROVISION):     보호구/정보 제공 의무

분류 방법: action_text 동사 패턴 매핑
```

---

## 9. 출력 계층 설계

```
[산출물 1] 법령의무 목록
  - 의무명 (action_text 요약)
  - 근거 법조문
  - 발생조건 (Trigger Code)
  - 우선순위 (P1~P4)
  - 유형 (8종)
  - 벌칙 (과태료/벌금)

[산출물 2] 일정 (Schedule)
  - 의무 × 주기 → 캘린더 이벤트 생성
  - 최초 1회 / 매 분기 / 연 1회 / 수시

[산출물 3] 업무 배정
  - 의무 유형 → 담당자 그룹 매칭
  - TAI Safe 1인집중→분산 핵심 기능

[산출물 4] 안전관리설계서
  - 법령의무 목록 + 일정 + 담당 + 근거 조문 PDF
  - 현재 diagnosis_proposal.py v2.1.0 기반

[산출물 5] 점검항목
  - 점검 유형 의무 → inspection_set_items 생성
  - 기존 inspection_master와 연결
```

---

## 전체 데이터 흐름 요약

```
소비자 입력
  ksic_code, employee_count, has_*, equipment_assets,
  factory_process, hazard_factor_codes [신규]
       │
       ▼
[입력 표준화] → GROUP 1~7 정규화
       │
       ▼
[매핑 규칙 A/B/C] → Trigger Code Set 생성
  예: {BUSINESS, EQUIPMENT:크레인, WORK:밀폐공간, THRESHOLD:50이상}
       │
       ▼
[의무후보 생성] → semantic_clause 조회
  조건: executor_text='사업주' + Trigger Code 매칭
  → 의무후보 풀 (200~800건 예상)
       │
       ▼
[체크엔진]
  → 주체 필터 / 조건 충족 검증 / 별표 임계값 검증 / 중복 식별
  → 최종 의무 목록 (50~200건 예상)
       │
       ▼
[6W 보강]
  → 누가/언제/어디서/무엇을/어떻게/왜 채움
  → where_text 공백은 condition_text 파싱으로 보완
       │
       ▼
[정제]
  → 중복 제거 / 우선순위 / 유형 분류
       │
       ▼
[출력]
  → 법령의무 목록 / 일정 / 업무배정 / 안전관리설계서 / 점검항목
```

---

## 다음 단계 작업 정의

| 작업 | 대상 계층 | 핵심 산출물 |
|---|---|---|
| **WO-MAPPING-001** | 매핑 계층 | 입력값 → Trigger Code 변환 규칙 정의 |
| **WO-TRIGGER-001** | 의무후보 생성 계층 | Trigger Code → semantic_clause 조회 쿼리 설계 |
| **WO-CHECK-001** | 체크엔진 계층 | 검증 규칙 4종 상세 설계 |

우선순위: WO-MAPPING-001 → WO-TRIGGER-001 → WO-CHECK-001

---

*WO-ARCH-001 완료 | 테이블 생성 없음 | 코드 작성 없음 | 구현 없음*
