# WO-LAW-PATTERN-DISCOVERY-001
# 법령 패턴 발견

**작성일:** 2026-06-24 | **상태:** 완료 (법령세계 압축 전용)
**선행:** WO-LAW-CODE-ARCHITECTURE-001 / WO-INPUT-PATTERN-DISCOVERY-001
**금지:** 입력필드 연결 / 입력패턴 연결 / 매핑 생성 / condition_mapping 수정 / 후보군 생성
**목적:** 58,495 semantic_clause를 "무슨 내용"이 아니라 "무슨 역할"로 압축한다.

> 입력세계: 98필드 → 7패턴.
> 법령세계: 58,495조문 → N패턴.

---

## 결론 먼저

```
58,495 조문 → Role 7종 → 사업주 의무 한정 8개 법령 패턴.

전체 조문 Role 분포:
  OBLIGATION  28,213 (48%)
  AUTHORITY   10,352 (18%)  ← 행정기관 권한, UNUSED
  DELEGATION   8,999 (15%)  ← 위임, 직접의무 아님
  DEFINITION   6,439 (11%)  ← 정의
  PROHIBITION  1,622 (3%)
  NULL           695 (1%)
  STATEMENT      389 (1%)

TAI Safe 매핑 대상(사업주·관리주체·도급인) = 약 1,572건
이를 8개 법령 패턴으로 압축.
```

---

## TASK-002: Role 후보군 (귀납 확정 7종)

| Role | 건수 | 비율 | TAI Safe 대상 |
|---|---|---|---|
| OBLIGATION | 28,213 | 48% | ✅ (사업주분만) |
| AUTHORITY | 10,352 | 18% | ❌ 행정기관 권한 |
| DELEGATION | 8,999 | 15% | △ 위임 (appendix 연결만) |
| DEFINITION | 6,439 | 11% | ❌ 정의 |
| PROHIBITION | 1,622 | 3% | ✅ (사업주분만) |
| NULL | 695 | 1% | ❌ 미분류 |
| STATEMENT | 389 | 1% | ❌ 선언 |

---

## TASK-003: IF 조건 구조

전체 조문의 조건 존재 비율:
```
OBLIGATION:  HAS_IF 12,313 / NO_IF 15,900  (44% 조건부)
AUTHORITY:   HAS_IF 4,888 / NO_IF 5,464
DEFINITION:  HAS_IF 1,796 / NO_IF 4,643
PROHIBITION: HAS_IF 437 / NO_IF 1,185
```

**IF는 독립 Role이 아니라 OBLIGATION/PROHIBITION의 내부 구조** (LAW-CODE-ARCHITECTURE 재확인).

### 사업주 의무 조건부(IF) 780건의 조건 성격

| 조건 패턴 | 건수 | 비율 |
|---|---|---|
| IF_ACTIVITY (작업·취급·사용·설치 조건) | 571 | 73% |
| IF_OTHER (기타 조건) | 244 | 31% |
| IF_NUMERIC (수치 조건) | 30 | 4% |

**핵심:** 법령 조건의 73%가 "작업/취급/설치하는 경우" 형태.
→ 입력 패턴 P1 BOOLEAN_EXISTENCE("X가 있는가")와 의미 대응.
수치 조건(IF_NUMERIC)은 4%뿐 — 대부분 별표/시행령에 위임(아래 참조).

---

## TASK-004: Appendix 의존도

```
사업주 의무 중 DELEGATION_위임 = 102건

위임 구조:
  본조: "안전관리자를 두어야 한다" (조건 없음)
    ↓ "대통령령으로 정한다"
  시행령 별표: employee_count >= 50 (실제 기준)
    ↓
  appendix_condition (현재 7건만 입력)

→ 수치 임계값(THRESHOLD)은 본조에 없고 별표에 있음.
→ 그래서 IF_NUMERIC이 본조에선 4%뿐.
→ 실제 THRESHOLD 의무는 DELEGATION + appendix_condition 결합으로 발생.
```

**대표 사례:**
```
법 제17조 안전관리자 → 시행령 별표3 (50인/500인/1000인)
법 제19조 관리담당자 → 시행령 별표5 (20인)
법 제25조 관리규정   → 시행규칙 별표2 (100인)
```

---

## TASK-005: Fragment 조문

| Fragment 유형 | 건수 | 독립 매핑 |
|---|---|---|
| FRAGMENT_조건단편 ("이 경우", "그 장소", "전항") | 34 | ❌ 상위 조문 필요 |
| FRAGMENT_행위단편 ("이를", "그것을") | 12 | ❌ 상위 조문 필요 |

**총 46건 (사업주 의무의 약 3%)이 단독 매핑 불가.**
parent 조문(source_part_id 상위) 연결 없이는 의미 불완전.
→ 최대 오탐 위험 군. 별도 패턴으로 격리.

---

## LAW_PATTERN_CATALOG (8개 패턴)

| pattern_code | pattern_name | role | IF | appendix | fragment | 조문수 | 대표 |
|---|---|---|---|---|---|---|---|
| **L1_ACTIVITY_OBLIGATION** | 작업조건부 의무 | OBL | ✅작업 | ❌ | ❌ | 571 | 밀폐공간 작업 시 측정 |
| **L2_PLAIN_OBLIGATION** | 무조건 의무 | OBL | ❌ | ❌ | ❌ | 644 | 압력방출장치 설치 |
| **L3_OTHER_CONDITION** | 기타조건 의무 | OBL | ✅기타 | ❌ | ❌ | 244 | (다양) |
| **L4_NUMERIC_OBLIGATION** | 수치조건부 의무 | OBL | ✅수치 | ❌ | ❌ | 30 | 400㎡ 이상 경보설비 |
| **L5_DELEGATION_THRESHOLD** | 위임형(별표 임계) | DELEGAT | ❌ | ✅ | ❌ | 102 | 안전관리자 선임기준 |
| **L6_PROHIBITION** | 금지 | PROHIB | △ | ❌ | ❌ | 108 | 탑승 금지 |
| **L7_FRAGMENT** | 단편조각 | OBL/PROHIB | △ | ❌ | ✅ | 46 | "이 경우", "그 장소" |
| **L8_DELEGATION_PLAIN** | 단순위임 | DELEGAT | ❌ | ❌ | ❌ | (위임 나머지) | 대통령령으로 정한다 |

**TAI Safe 사업주 의무 핵심 = L1~L7 (약 1,745건)**

---

## 패턴별 특징 (행동 기술)

### L1_ACTIVITY_OBLIGATION (작업조건부 의무) — 571건, 최대

```
행동: "X 작업/설비/물질이 있으면 → Y 의무"
구조: condition_text(작업 명시) + action_text(의무)
예:   "근로자가 밀폐공간에서 작업하는 경우 → 산소농도 측정"
→ 입력 P1 BOOLEAN과 대응될 후보 (이번엔 연결 안 함)
```

### L2_PLAIN_OBLIGATION (무조건 의무) — 644건

```
행동: 조건 없이 항상 적용
구조: condition_text NULL + action_text(의무)
예:   "보일러에 압력방출장치를 설치하여야 한다"
→ sector 소속 또는 설비 보유만으로 발동 (UNIVERSAL 성격)
```

### L4_NUMERIC_OBLIGATION (수치조건부) — 30건

```
행동: 본조에 직접 수치 명시
예:   "연면적 400㎡ 이상 → 경보설비"
→ 본조 수치는 희소(30건). 대부분 L5(위임)로 빠짐.
```

### L5_DELEGATION_THRESHOLD (위임형 임계) — 102건

```
행동: 본조는 의무만, 임계값은 별표
구조: 본조(DELEGATION) + appendix_condition(수치)
예:   본조 "안전관리자를 둔다" + 별표 "50인 이상"
→ THRESHOLD 의무의 진짜 원천. appendix 연결 필수.
```

### L7_FRAGMENT (단편조각) — 46건

```
행동: 단독으로 의미 불완전
예:   "이 경우 ...", "그 장소에 ..."
→ parent 조문 없이 매핑 불가. 격리 필요.
```

---

## 핵심 발견

### 발견 1: 법령세계도 2개 패턴이 지배

```
L1_ACTIVITY(571) + L2_PLAIN(644) = 1,215건 (70%)

법령 의무의 70%가:
  "작업/설비/물질이 있으면 의무" (조건부)
  "무조건 의무" (항상)

→ 입력세계와 동일하게 2패턴 지배 구조.
```

### 발견 2: 입력 패턴 ↔ 법령 패턴 대응 윤곽 (관찰만)

```
입력 P1 BOOLEAN_EXISTENCE (55) ←관찰→ 법령 L1_ACTIVITY (571)
입력 P2 NUMERIC_THRESHOLD (18) ←관찰→ 법령 L4_NUMERIC(30) + L5_DELEGATION(102)
입력 P4 CODE_SELECT (7)        ←관찰→ 법령 sector 분류

주의: 이번 WO에서는 연결하지 않는다. 대응 가능성만 관찰.
다음 WO-PATTERN-CROSSMAP-001에서 실제 비교.
```

### 발견 3: THRESHOLD는 본조가 아니라 별표에 산다

```
본조 직접 수치(L4): 30건
위임형 별표(L5):   102건

→ 수치 의무의 77%가 별표(appendix)에 위임.
→ THRESHOLD 매핑은 semantic_clause가 아니라 appendix_condition이 핵심.
→ 그런데 appendix_condition은 현재 7건만 입력됨.
→ 별표 데이터 입력이 THRESHOLD 매핑의 병목.
```

### 발견 4: 매핑 대상은 전체의 3%뿐

```
58,495 조문 중:
  TAI Safe 사업주·관리주체·도급인 의무 = 약 1,745건 (3%)
  나머지 97% = 행정권한·정의·위임·타집행자 (UNUSED)

→ 법령 매핑의 실제 작업 범위는 1,745건.
→ 이 중 L7 Fragment 46건은 격리.
→ 순수 매핑 대상 약 1,700건.
```

---

## 성공 기준 답변

> 58,000 조문을 N개 패턴으로 설명할 수 있는가?

```
✅ 가능.

전체: Role 7종
사업주 의무: 8개 법령 패턴 (L1~L8)
  L1 작업조건부   571
  L2 무조건       644
  L3 기타조건     244
  L4 수치조건      30
  L5 위임형임계   102
  L6 금지         108
  L7 단편          46
  L8 단순위임     (나머지)

이제 "58,495 조문"이 아니라 "8개 법령 패턴"으로 말할 수 있다.
```

---

## 입력 vs 법령 패턴 대조표 (다음 WO 예고)

| 입력 패턴 | 법령 패턴 | 대응 |
|---|---|---|
| P1 BOOLEAN_EXISTENCE (55) | L1 ACTIVITY (571) | 작업/설비/물질 존재 |
| P2 NUMERIC_THRESHOLD (18) | L4 NUMERIC(30)+L5 DELEGATION(102) | 임계값 |
| P3 NUMERIC_QUANTITY (7) | — | 보조 |
| P4 CODE_SELECT (7) | sector 분류 | 업종 |
| P5 TABLE_COLLECTION (4) | L1 반복 | 다수 공정·설비 |
| P6 EXTERNAL_LOOKUP (6) | L4 NUMERIC | API 수치 |
| P7 TEXT_TRIGGER (2) | — | API 트리거 |
| (없음) | L2 PLAIN (644) | **입력 무관 무조건 의무** |
| (없음) | L7 FRAGMENT (46) | 격리 |

**주목:** L2_PLAIN(644) — 입력값과 무관하게 발동하는 무조건 의무가 법령에서 가장 많음.
입력 패턴에 대응이 없음. sector 소속만으로 발동하는 UNIVERSAL 군.

---

## 다음 단계

```
WO-LAW-PATTERN-DISCOVERY-001 (현재) — 완료
      ↓
WO-PATTERN-CROSSMAP-001
  입력 패턴 7개 ↔ 법령 패턴 8개 실제 비교
  - P1 BOOLEAN ↔ L1 ACTIVITY 대응 검증
  - P2 THRESHOLD ↔ L5 DELEGATION 대응 검증
  - L2 PLAIN(입력무관) 처리 방안
  - L7 FRAGMENT 격리 방안
```

---

*WO-LAW-PATTERN-DISCOVERY-001 완료.*
*58,495 조문 → 8개 법령 패턴. L1 ACTIVITY(571)+L2 PLAIN(644)이 70% 지배.*
*핵심: 매핑 대상은 3%(1,745건). THRESHOLD는 별표에 위임. L2 무조건의무는 입력 무관.*
