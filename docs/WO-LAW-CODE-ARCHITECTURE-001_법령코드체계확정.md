# WO-LAW-CODE-ARCHITECTURE-001
# 법령 코드 체계 확정

**작성일:** 2026-06-23 | **상태:** 확정
**선행:** WO-STAGE-OBJECTIVE-001
**WO-STAGE-OBJECTIVE-001 검증:** Q1(법령 원본 분석) ✅ / Q2(패턴 발견) ✅ / Q3(매핑 생성 목적 없음) ✅ / Q4(원칙 위반 없음) ✅

---

## 핵심 질문에 대한 답변

> **법령은 실제로 무엇으로 구성되는가?**

```
법령은 7개 역할(Role)의 조합이다.

OBL          의무   — 사업주는 ~하여야 한다
PROHIB       금지   — ~하여서는 아니 된다
IF           조건   — ~하는 경우, ~할 때
DEF          정의   — ~란 ~를 말한다
DELEGAT      위임   — 대통령령으로 정한다
AUTH         권한   — 할 수 있다 (재량)
STAT         선언   — ~로 한다 (확인적 규정)
```

현재 DB에서 EXCEPTION(예외)·PENALTY(벌칙)·REFERENCE(참조)는
독립 content_type이 아니라 OBL·PROHIB·IF 내부에 혼합 존재한다.

---

## 산출물 A: LAW_ROLE_CATALOG

### A-1. 역할 코드 체계 (7종 확정)

| Role 코드 | 한국어 | DB content_type | 건수 | 비율 | 정의 |
|---|---|---|---|---|---|
| **OBL** | 의무 | OBLIGATION | 29,665 | 50.7% | "~하여야 한다" — 사업주에게 작위 의무 부과 |
| **AUTH** | 권한 | AUTHORITY | 10,470 | 17.9% | "~할 수 있다" — 행정기관 재량권 부여. **TAI Safe 서비스 범위 외** |
| **DELEGAT** | 위임 | DELEGATION | 9,055 | 15.5% | "대통령령으로 정한다" — 하위 법령으로 기준 위임. **직접 의무 아님** |
| **DEF** | 정의 | DEFINITION | 6,471 | 11.1% | "~란 ~를 말한다" — 용어 정의. **직접 의무 아님** |
| **PROHIB** | 금지 | PROHIBITION | 1,742 | 3.0% | "~하여서는 아니 된다" — 작위 금지 의무 부과 |
| **NULL** | 미분류 | NULL | 702 | 1.2% | content_type 미입력. 분석 필요 |
| **STAT** | 선언 | STATEMENT | 390 | 0.7% | "~로 한다" — 확인적·선언적 규정 |

**총 58,495건.**

### A-2. IF(조건)는 독립 Role이 아니다 — 핵심 발견

TASK-002 분석 결과:

```
condition_text가 있는 조문 = IF가 내포된 OBL·PROHIB
condition_text가 없는 조문 = 조건 없이 항상 적용되는 OBL·PROHIB
```

| content_type | condition_text + action_text 모두 있음 | action_text만 있음 |
|---|---|---|
| OBLIGATION | 13,154건 (44%) | 16,511건 (56%) |
| PROHIBITION | 475건 (27%) | 1,267건 (73%) |
| DELEGATION | 1,369건 (15%) | 7,686건 (85%) |

**결론:** IF는 별도 content_type이 아니라 OBL·PROHIB의 내부 구조다.
조문의 실제 패턴은 `[IF] + OBL` 또는 `OBL` (IF 없음) 두 가지로 나뉜다.

### A-3. 사업주 의무만 존재하는가 — executor 분포

executor_text 상위 값:
```
사업주     1,200건  ← TAI Safe 핵심 대상
정하       1,324건  ← 행정기관 (AUTH/DELEGAT 혼입)
해당하     1,248건  ← 단편 조각 (선행 조문 의존)
기후에너지환경부장관  1,039건  ← 행정기관 (UNUSED)
시도지사   916건    ← 행정기관 (UNUSED)
```

**TAI Safe 서비스 대상 executor:**
```
사업주          1,200건  — 핵심
관리주체         202건   — BUILDING 섹터 가능
도급인           (별도 탐색 필요)
```

---

## 산출물 B: LAW_PATTERN_CATALOG

### B-1. 조문 구조 패턴 (4종 확정)

패턴은 `condition_text 존재 여부` × `action_text 구조`로 귀납됨.

#### Pattern P1: `IF + OBL` — 조건부 의무

```
condition_text: "사업주는 [조건]하는 경우"
action_text:    "[의무 내용]하여야 한다"

예시:
  사업주는 근로자가 밀폐공간에서 작업을 하는 경우
  → 작업 전 산소·유해가스 농도를 측정하여야 한다.
```

**condition_text 하위 패턴:**

| 하위 패턴 코드 | 설명 | 발견 예시 |
|---|---|---|
| P1-WORK | 특정 작업 수행 시 | 사업주는 근로자가 [작업명]을 하는 경우 |
| P1-EQUIP | 특정 설비 사용·설치 시 | 사업주는 [설비명]을 사용하는 경우 |
| P1-MATERIAL | 특정 물질 취급 시 | 사업주는 근로자가 [물질명]을 취급하는 경우 |
| P1-NUMERIC | 수치 조건 충족 시 | 연면적이 400㎡ 이상이거나 상시 50명 이상 |
| P1-EVENT | 사건 발생 시 | 사업주는 점검 결과 이상을 발견한 경우 |
| P1-ENUM | 열거 조건 중 하나 해당 시 | 다음 각 호의 어느 하나에 해당하는 경우 |
| P1-FRAGMENT | 단편 (선행 조문 의존) | 이 경우 / 그 장소 / 작업장 내부 |

#### Pattern P2: `OBL` — 무조건 의무

```
condition_text: NULL
action_text:    "[의무 내용]하여야 한다"

예시:
  (조건 없음)
  → 보일러 압력방출장치를 설치하여야 한다.
```

- 56%의 OBLIGATION이 이 패턴
- 입력값 독립적 — has_* 또는 sector 소속만으로 발동
- → **UNIVERSAL Path 대상**

#### Pattern P3: `DELEGAT` — 위임형

```
condition_text: NULL 또는 위임 조건
action_text:    "대통령령으로 정한다" / "고용노동부령으로 정한다"

예시:
  (조건 없음) → 안전관리자의 선임 기준은 대통령령으로 정한다.
```

- 의무 내용이 이 조문에 없고 하위 법령에 있음
- 직접 매핑 불가 — appendix_condition 또는 하위 law_article로 연결 필요
- **THRESHOLD Path의 원천이 여기서 나옴**

#### Pattern P4: `PROHIB` — 금지

```
condition_text: NULL 또는 금지 조건
action_text:    "[행위]하여서는 아니 된다"

예시:
  사업주는 근로자가 금지유해물질을 취급하는 경우
  → 관련 설비를 설치하여서는 아니 된다.
```

- PROHIBITION 1,742건 중 475건이 조건 포함 (P4-IF)
- 나머지 1,267건은 무조건 금지 (P4-ALWAYS)

---

### B-2. 법령 패턴 조합 코드 체계

```
패턴 코드 구조:
  [Role]-[Condition]-[Obligation]

예시:
  OBL-WORK-INSTALL      작업 조건 → 설치 의무
  OBL-EQUIP-INSPECT     설비 조건 → 점검 의무
  OBL-NUMERIC-APPOINT   수치 조건 → 선임 의무
  OBL-NONE-INSTALL      조건 없음 → 설치 의무 (UNIVERSAL)
  PROHIB-MATERIAL-USE   물질 조건 → 사용 금지
  DELEGAT-NONE-DECREE   위임 → 시행령 기준
```

### B-3. Obligation 행위 패턴 (action_text에서 귀납)

```
INSTALL     설치하여야 한다
APPOINT     두어야 한다 / 선임하여야 한다
SUBMIT      제출하여야 한다 / 신고하여야 한다
PREPARE     수립하여야 한다 / 작성하여야 한다
INSPECT     점검하여야 한다 / 확인하여야 한다
RESTRICT    금지하여야 한다 / 제한하여야 한다
EDUCATE     교육하여야 한다
PROVIDE     지급하여야 한다 / 제공하여야 한다
MEASURE     측정하여야 한다
NOTIFY      고지하여야 한다 / 알려야 한다
STOP        중단하여야 한다 / 철거하여야 한다
MAINTAIN    유지하여야 한다 / 관리하여야 한다
```

---

## 산출물 C: LAW_UNUSED_CATALOG

### C-1. TAI Safe 서비스 범위 외 법령 (UNUSED 분류 기준)

| 구분 | 법령 | 건수 | UNUSED 사유 |
|---|---|---|---|
| 행정기관 권한 | AUTH 전체 (10,470건) | 10,470 | executor가 행정기관. 사업주 의무 아님 |
| 타 부처 법령 | 파견법·고용산재보험료징수법 등 | 87 | 산업안전 범위 외 |
| 주택·건설 행정 | 주택법·공동주택관리법 | 91 | 건물관리 아닌 부동산 행정 |
| 정의·선언 조문 | DEF(6,471) + STAT(390) | 6,861 | 의무 없음. 참조용만 사용 |
| 위임 조문 | DELEGAT(9,055) | 9,055 | 직접 의무 없음. appendix 연결만 사용 |

**UNUSED 합계 추정: 약 26,564건 (45.4%)**

### C-2. TAI Safe 서비스 범위 내 법령 (IN-SCOPE)

| 구분 | 법령 | 건수 |
|---|---|---|
| **핵심** | 산업안전보건기준에 관한 규칙 | 990건 (사업주 의무) |
| **핵심** | 산업안전보건법 | 90건 (사업주 의무) |
| **핵심** | 산업안전보건법 시행규칙 | 53건 (사업주 의무) |
| **핵심** | 산업안전보건법 시행령 | 8건 (사업주 의무) |
| **확장 검토** | 공동주택관리법 | 4건 (관리주체 의무) |
| **확장 검토** | 공동주택관리법 시행령 | 23건 (관리주체 의무) |

**IN-SCOPE 합계: 약 1,168건 (executor = 사업주·관리주체)**

---

## 핵심 확정: 법령 코드 체계

### 법령 코드 = Role × Condition × Obligation

```
입력 세계:
  [섹션]-[입력타입]-[입력코드]
  예: IND-KSIC-C20 / CON-PROCESS-발파굴착 / BLD-NUMERIC-building_area

법령 세계:
  [Role]-[Condition패턴]-[Obligation패턴]
  예: OBL-WORK-INSTALL / OBL-NUMERIC-APPOINT / PROHIB-MATERIAL-USE

매핑:
  입력코드 ↔ 법령코드
  IND-MATERIAL-has_chemical → OBL-MATERIAL-INSTALL (국소배기장치)
  BLD-NUMERIC-building_area-400 → OBL-NUMERIC-INSTALL (경보설비)
  CON-EQUIP-has_tower_crane → OBL-EQUIP-MAINTAIN (벽체지지)
```

---

## TASK-003 특수 패턴 4종

| 특수 패턴 | 설명 | DB 근거 | 처리 방식 |
|---|---|---|---|
| **별표의존형** | 의무 기준이 별표에 있고 본조는 위임만 | DELEGAT 1,369건 중 appendix_ref 40건 | appendix_condition 테이블 연결 |
| **시행령위임형** | 본법 → 시행령으로 위임 | delegation_to_decree 25건 | law_article (시행령) 연결 |
| **시행규칙위임형** | 본법 → 시행규칙으로 위임 | delegation_to_rule 31건 | law_article (시행규칙) 연결 |
| **단편조각형** | 선행 조문 없이는 의미 없는 단편 | P1-FRAGMENT (이 경우 / 그 장소) | 부모 조문(parent_id) 연결 필요 |

**단편조각형이 가장 큰 오탐 원인.** "이 경우" / "그 장소" 단독 조문은 standalone 매핑 불가. parent_id 추적 필요.

---

## 다음 단계

```
WO-LAW-CODE-ARCHITECTURE-001 (현재) — 완료
      ↓
WO-INPUT-STAGING-001    INDUSTRIAL 입력 원본 전수 수집
                        (법령 코드 체계 확정됐으므로 병행 가능)
      ↓
WO-LAW-STAGING-001      법령 원본 전수 수집
                        semantic_clause → Role/Pattern 분류
      ↓
WO-PATTERN-MAPPING-001  입력코드 ↔ 법령코드 교차 매핑 시작
```

---

*WO-LAW-CODE-ARCHITECTURE-001 완료.*
*법령 7개 Role 확정 / 4개 조문 구조 패턴 확정 / UNUSED 45.4% 식별.*
*핵심: IF는 독립 Role 아님 — OBL·PROHIB의 내부 구조. 단편조각형이 오탐 주요 원인.*
