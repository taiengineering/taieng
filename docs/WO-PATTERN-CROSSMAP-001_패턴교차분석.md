# WO-PATTERN-CROSSMAP-001
# 입력 패턴 ↔ 법령 Trigger 패턴 교차 분석

**작성일:** 2026-06-24 | **상태:** 완료 (연결 원칙 확정 전용)
**선행:** WO-INPUT-PATTERN-DISCOVERY-001 / WO-LAW-TRIGGER-HIERARCHY-001
**금지:** condition_mapping_candidate INSERT / 개별 조문 매핑 / 후보군 대량생성 / 엔진 수정 / CONFIRMED 판정
**목적:** 이번 WO는 "매핑 생성"이 아니라 "매핑 방식 정의"다.

> 어떤 입력 패턴이 어떤 법령 Trigger를 발생시킬 수 있는지 연결 원칙만 확정한다.

---

## 산출물 A: 입력 패턴 목록

| 코드 | 패턴 | 개수 |
|---|---|---|
| P1 | BOOLEAN_EXISTENCE | 55 |
| P2 | NUMERIC_THRESHOLD | 18 |
| P3 | NUMERIC_QUANTITY | 7 |
| P4 | CODE_SELECT | 7 |
| P5 | TABLE_COLLECTION | 4 |
| P6 | EXTERNAL_LOOKUP | 6 |
| P7 | TEXT_TRIGGER | 2 |

## 산출물 B: 법령 Trigger 목록

| 코드 | Trigger | 조문수 |
|---|---|---|
| L1 | WORK_EXISTS | 189 |
| L2 | EQUIPMENT_EXISTS | 153 |
| L3 | MATERIAL_EXISTS | 45 |
| L4 | FACILITY_EXISTS | 17 |
| L5 | DIRECT_THRESHOLD | 30 |
| L6 | APPENDIX_THRESHOLD | 102 |
| L7 | COMPOUND | 4 |
| L8 | TRUE_UNIVERSAL | 359 |
| L9 | FRAGMENT | 46 |

---

## 산출물 C: Crossmap Matrix

| 입력 패턴 | 법령 Trigger | 관계 | 설명 |
|---|---|---|---|
| P1 BOOLEAN_EXISTENCE | L1 WORK_EXISTS | **DIRECT** | has_diving=true → 잠수작업 의무 |
| P1 BOOLEAN_EXISTENCE | L2 EQUIPMENT_EXISTS | **DIRECT** | has_boiler=true → 보일러 의무 |
| P1 BOOLEAN_EXISTENCE | L3 MATERIAL_EXISTS | **DIRECT** | has_chemical=true → 화학물질 의무 |
| P1 BOOLEAN_EXISTENCE | L4 FACILITY_EXISTS | **DIRECT** | has_confined_space=true → 밀폐공간 의무 |
| P1 BOOLEAN_EXISTENCE | L8 TRUE_UNIVERSAL | NO_LINK | 무조건 의무는 입력 무관 |
| P2 NUMERIC_THRESHOLD | L5 DIRECT_THRESHOLD | **DIRECT** | building_area>=400 → 본조 직접 판정 |
| P2 NUMERIC_THRESHOLD | L6 APPENDIX_THRESHOLD | **CONDITIONAL** | worker_count>=50 → 별표 필요 |
| P2 NUMERIC_THRESHOLD | L7 COMPOUND | CONDITIONAL | 면적 OR 인원 복합 |
| P3 NUMERIC_QUANTITY | L6 APPENDIX_THRESHOLD | CONDITIONAL | crane_count → 단독 의무 아님, 결합 |
| P3 NUMERIC_QUANTITY | (대부분) | NO_LINK | 단순 수량은 트리거 아님 |
| P4 CODE_SELECT | L1/L2 (sector 경유) | **CONDITIONAL** | ksic_major → 업종별 의무 |
| P4 CODE_SELECT | L8 TRUE_UNIVERSAL | **CONDITIONAL** | sector → 무조건 의무 후보화 핵심 |
| P5 TABLE_COLLECTION | L1 WORK_EXISTS | **DIRECT** | process_list 각 행 → 작업 트리거 반복 |
| P5 TABLE_COLLECTION | L2 EQUIPMENT_EXISTS | **DIRECT** | equipment_list 각 행 → 설비 트리거 반복 |
| P6 EXTERNAL_LOOKUP | L5 DIRECT_THRESHOLD | **CONDITIONAL** | total_floor_area(API) → 면적 임계 |
| P6 EXTERNAL_LOOKUP | L4 FACILITY_EXISTS | CONDITIONAL | building_use_type → 시설 분류 |
| P6 EXTERNAL_LOOKUP | L3 MATERIAL_EXISTS | CONDITIONAL | built_year<2009 → has_asbestos 파생 |
| P7 TEXT_TRIGGER | (모든 Trigger) | **NO_LINK** | 주소 자체는 의무 발생 원인 아님 |
| P7 TEXT_TRIGGER | P6 실행 | (API 트리거) | 주소 → 건축물대장 API 호출 |
| (없음) | L8 TRUE_UNIVERSAL | UNIVERSAL | sector 일괄, 입력 불필요 |
| (없음) | L9 FRAGMENT | ISOLATE | parent 의존, 격리 |

---

## 산출물 D: TRUE_UNIVERSAL 처리 정책

```
TRUE_UNIVERSAL(359)은 입력값과 직접 연결하지 않는다.

후보화 공식:
  sector 소속 + 서비스 scope + executor 일치
  → 입력값 없이 후보 생성

예:
  "제조업 사업장은 안전보건교육을 실시하여야 한다"
  → INDUSTRIAL sector이면 무조건 후보
  → has_* 입력 불필요

처리 경로:
  P4 CODE_SELECT(ksic_major) → sector 확정
  → sector에 속한 모든 TRUE_UNIVERSAL 의무 일괄 후보화

→ TRUE_UNIVERSAL은 "입력 → Trigger" 경로가 아니라
  "sector → 일괄적용" 경로를 탄다.
```

**핵심:** TRUE_UNIVERSAL의 유일한 입력 의존은 sector(P4 CODE_SELECT). 나머지 입력과 무관.

---

## 산출물 E: FRAGMENT 격리 정책

```
FRAGMENT(46)은 독립 매핑 금지.

이유:
  "이 경우 ~하여야 한다" — 단독으로 의미 불완전
  parent semantic_clause 없이는 무슨 의무인지 불명

처리 원칙:
  1. parent semantic_clause 연결 시도 (source_part_id 상위)
  2. parent 있으면 → parent의 Trigger 상속
  3. parent 없으면 → 격리 (매핑 대상 제외)

→ FRAGMENT는 입력 패턴과 직접 연결하지 않는다.
→ parent 조문의 Trigger를 따라간다.
```

---

## 산출물 F: COMPOUND 처리 정책

```
COMPOUND(4)는 단일 입력 패턴으로 확정하지 않는다.

실제 조합 유형:
  THRESHOLD OR THRESHOLD  (면적 400㎡ OR 인원 50명)

확장 가능 조합 (HIDDEN 285 재분류 시 증가 예상):
  NUMERIC_THRESHOLD + BOOLEAN_EXISTENCE
  NUMERIC_THRESHOLD + CODE_SELECT
  BOOLEAN_EXISTENCE + MATERIAL_EXISTS

처리 원칙:
  1. COMPOUND는 2개 이상 입력 패턴이 AND/OR로 결합
  2. 각 입력 패턴을 개별 Trigger로 분해
  3. 결합 연산자(AND/OR) 보존
  4. 단일 Trigger로 축약 금지

예:
  "400㎡ 이상 OR 50명 이상 → 경보설비"
  = (P2 building_area ≥400) OR (P2 worker_count ≥50) → 1 의무
  → building_area 단독 = DIRECT
  → 복합 전체 = COMPOUND (OR 보존)
```

---

## 연결 원칙 3종 정의 (TASK-002)

```
DIRECT (직접 연결):
  입력 패턴 하나 → Trigger 하나 → 의무 하나
  조문에 조건이 명시되어 추가 데이터 불필요
  예: P1 has_diving → L1 잠수작업 (DIRECT)

CONDITIONAL (조건부 연결):
  연결은 가능하나 추가 데이터/판정 필요
  예: P2 worker_count → L6 APPENDIX (별표 데이터 필요)
  예: P4 ksic_major → L8 UNIVERSAL (sector 경유)

NO_LINK (연결 금지):
  입력 패턴이 Trigger를 발생시키지 않음
  예: P7 주소 → 의무 직접 발생 안 함 (API 트리거일 뿐)
  예: P3 단순 수량 → 트리거 아님
```

---

## 핵심 발견

### 발견 1: P1 BOOLEAN이 가장 깨끗한 DIRECT

```
P1 BOOLEAN_EXISTENCE(55) → L1/L2/L3/L4 EXISTS Trigger
= 전부 DIRECT

has_diving → 잠수작업
has_boiler → 보일러
has_chemical → 화학물질
has_confined_space → 밀폐공간

→ 입력세계 56% + 법령세계 EXISTS군 = 가장 명확한 매핑 라인.
→ 첫 후보군 생성은 여기서 시작해야 함.
```

### 발견 2: THRESHOLD는 DIRECT와 CONDITIONAL로 갈린다

```
P2 → L5 DIRECT_THRESHOLD = DIRECT (본조 수치, 조문만으로 판정)
P2 → L6 APPENDIX_THRESHOLD = CONDITIONAL (별표 데이터 필요)

→ building_area>=400은 즉시 매핑 가능 (DIRECT)
→ worker_count>=50은 appendix 입력 후 가능 (CONDITIONAL)
→ APPENDIX 7건 병목이 THRESHOLD 매핑의 관문.
```

### 발견 3: 주소(P7)는 Trigger가 아니라 API 실행 스위치

```
P7 TEXT_TRIGGER(주소) → 모든 Trigger와 NO_LINK
단, P6 EXTERNAL_LOOKUP 실행 트리거

→ 주소 입력 자체는 의무를 발생시키지 않음.
→ 주소 → 건축물대장 API → 6개 필드 생성 → 그 필드가 Trigger.
→ 주소는 "입력의 입력" (메타 트리거).
```

### 발견 4: TRUE_UNIVERSAL은 sector 단일 의존

```
TRUE_UNIVERSAL(359)은 has_* 55개와 전부 NO_LINK.
유일한 연결: P4 CODE_SELECT(ksic_major) → sector

→ 무조건 의무는 "입력 → Trigger"가 아니라 "sector → 일괄".
→ 사업장이 sector만 선택하면 359건 후보가 자동 생성됨.
→ 이게 진단 결과의 기본 베이스라인.
```

### 발견 5: TABLE_COLLECTION은 Trigger 반복기

```
P5 process_list(table) → L1 WORK_EXISTS 반복
P5 equipment_list(table) → L2 EQUIPMENT_EXISTS 반복

→ 표의 각 행이 독립 Trigger 발생.
→ 공정 10개 등록 → WORK Trigger 10개.
→ input_staging_relation의 공정-설비 관계망이 여기서 활용됨.
```

---

## 산출물 G: 다음 WO 범위 (최종 매핑 단계 설계)

```
패턴 기반 후보군 생성 파이프라인:

  입력 패턴
      ↓
  법령 Trigger (DIRECT/CONDITIONAL 분류)
      ↓
  후보군 생성 (pattern → trigger → 의무)
      ↓
  검증 (조문 직독)
      ↓
  condition_mapping_candidate

다음 WO-PATTERN-CANDIDATE-GENERATION-001 범위:
  1순위: P1 BOOLEAN → L1/L2/L3/L4 EXISTS (DIRECT, 가장 깨끗)
  2순위: P2 THRESHOLD → L5 DIRECT_THRESHOLD (DIRECT)
  보류:  P2 → L6 APPENDIX (appendix 입력 선행 필요)
  별도:  TRUE_UNIVERSAL → sector 일괄 (입력 무관 경로)
  격리:  FRAGMENT (parent 연결 후)
```

---

## 성공 기준 답변

```
Q: BOOLEAN 입력은 어떤 법령 Trigger와 연결 가능한가?
A: WORK/EQUIPMENT/MATERIAL/FACILITY EXISTS와 DIRECT 연결.

Q: NUMERIC 입력은 어떤 Trigger와 연결 가능한가?
A: DIRECT_THRESHOLD는 DIRECT, APPENDIX_THRESHOLD는 CONDITIONAL.

Q: 주소 입력은 직접 Trigger인가, API 실행 Trigger인가?
A: API 실행 Trigger. 주소 자체는 NO_LINK, 건축물대장 API를 호출하는 스위치.

Q: 무조건 의무는 입력 없이 어떻게 후보화하는가?
A: sector 소속 + 서비스 scope + executor 일치로 일괄 후보화. has_* 입력 불필요.

Q: 단편 조문은 왜 독립 매핑하면 안 되는가?
A: "이 경우" 등 단독으로 의미 불완전. parent 조문의 Trigger를 상속해야 함.
```

---

## 다음 단계

```
WO-PATTERN-CROSSMAP-001 (현재) — 완료
      ↓
WO-PATTERN-CANDIDATE-GENERATION-001
  처음으로 패턴 기반 후보군 생성
  1순위: P1 BOOLEAN → EXISTS Trigger (DIRECT)
```

---

*WO-PATTERN-CROSSMAP-001 완료. 연결 원칙만 정의. 매핑 생성 없음.*
*핵심: P1 BOOLEAN→EXISTS가 가장 깨끗한 DIRECT. THRESHOLD는 DIRECT/APPENDIX 분기.*
*주소는 API 스위치. UNIVERSAL은 sector 일괄. FRAGMENT는 parent 상속.*
