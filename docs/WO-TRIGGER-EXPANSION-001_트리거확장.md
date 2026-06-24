# WO-TRIGGER-EXPANSION-001
# NO_TRIGGER 정복 — Trigger 확장

**작성일:** 2026-06-24 | **상태:** 완료 (NO_TRIGGER 분석 전용)
**선행:** WO-TRIGGER-LAW-MAPPING-001
**금지:** 후보군 생성 / condition_mapping 생성 / 입력필드 생성 / 새 구조 생성
**질문:** 520건은 왜 현재 Trigger에 안 들어가는가?

> 1,025건은 이미 설명됨. 프로젝트를 움직이는 정보는 설명 안 되는 520건 안에 있다.

---

## 결론 먼저

```
NO_TRIGGER 520건의 정체가 4가지로 밝혀짐:

1. 범위 밖(OUT_OF_SCOPE)      76건  → TAI Safe 대상 아님 (제외)
2. UNIVERSAL 흡수 가능        141건  → 신규 Trigger 아님 (기존 흡수)
3. 신규 Trigger 필요           33건  → 운반·전기·추락 (진짜 신규)
4. WORK 일반작업 + 미분류잔여  270건  → 추가 정밀분류 필요

→ 진짜 신규 Trigger는 3종뿐: TRANSPORT, ELECTRICAL, FALL_PREVENT (33건)
→ 520건의 절반은 범위밖 또는 기존 흡수.
→ 현 Trigger 체계는 거의 최종에 가깝다.
```

---

## TASK-001: NO_TRIGGER 520건 전수 분류

### 1차 분류 (LAW-MAPPING-001 재확인)

| 유형 | 건수 |
|---|---|
| 기타(미세분류) | 311 |
| 점검·정비 | 72 |
| 일반기계방호 | 40 |
| 교육·보호 | 32 |
| 운반·하역작업 | 25 |
| 전기작업 | 16 |
| 작업환경 | 12 |
| 추락방지 | 10 |
| 화재·폭발 | 2 |

### "기타" 311건 정밀 분류

| 유형 | 건수 | 성격 |
|---|---|---|
| 일반조치(포괄) | 128 | UNIVERSAL 성격 |
| 미분류 | 97 | **범위 밖 다수** |
| 문서·기록 | 35 | UNIVERSAL |
| 표지·게시 | 19 | UNIVERSAL |
| 신고·보고 | 17 | UNIVERSAL |
| 출입통제 | 9 | UNIVERSAL/WORK |
| 환기·배기 | 5 | FACILITY |
| 작업계획 | 1 | WORK |

---

## TASK-002: 결정적 발견 — 범위 밖 조문 혼입

미분류 97건 직독 결과, **TAI Safe 산업안전 범위 밖 조문이 대량 혼입**:

| 범위 밖 유형 | 건수 | 실제 법령 | executor 의미 |
|---|---|---|---|
| OUT_주택법 | 52 | 주택법 | 사업주체 = 건설시행사(분양) |
| OUT_파견법 | 13 | 파견법 | 파견사업주/사용사업주 |
| OUT_공동주택관리 | 8 | 공동주택관리법 | 관리주체 = 아파트 관리사무소 |
| OUT_근로기준 | 2 | 근로기준법 | 출산·육아휴가 |
| OUT_기타법 | 1 | 투자유치법 | 첨단투자지구 |
| **합계** | **76** | | **TAI Safe 대상 아님** |

```
핵심: "사업주"라는 단어가 같아도 법이 다르다.
  산업안전보건법 "사업주" = TAI Safe 대상 ✅
  주택법 "사업주체" = 분양 시행사 ❌
  파견법 "파견사업주" = 인력파견업체 ❌
  공동주택관리법 "관리주체" = 아파트 관리소 ❌

→ executor_text LIKE '%사업주%'만으로 필터하면
  다른 법의 사업주체가 섞여 들어옴.
→ NO_TRIGGER 520 중 76건(15%)이 애초에 범위 밖이었음.
```

---

## TASK-003: 신규 Trigger 승격 판정

승격 조건 3개 모두 충족해야 신규:
```
① 독립 입력필드 필요
② 독립 법령군 존재
③ 기존 Trigger로 설명 불가
```

### IN_산업안전 444건 정밀 분류

| 후보 | 건수 | 승격 판정 |
|---|---|---|
| 미분류잔여 | 142 | 추가 분석 필요 |
| WORK_일반작업 | 129 | 기존 WORK_EXISTS 하위 (신규 L2) |
| INSPECT (점검·정비) | 59 | **UNIVERSAL 흡수** |
| DOC_REPORT (문서·신고) | 37 | **UNIVERSAL 흡수** |
| 포괄조치 | 28 | **UNIVERSAL 흡수** |
| **TRANSPORT (운반·하역)** | 19 | **신규 Trigger ✅** |
| EDU_PPE (교육·보호구) | 17 | **UNIVERSAL 흡수** |
| **FALL_PREVENT (추락방지)** | 8 | **신규 Trigger ✅** |
| **ELECTRICAL (전기작업)** | 6 | **신규 Trigger ✅** |

### 신규 Trigger 3종 승격 검증

```
TRANSPORT (운반·하역) — 19건
  ① 입력필드: has_forklift/has_crane 있으나 "하역작업" 별도 필요 △
  ② 법령군: 차량·하역·양중·줄걸이 독립 존재 ✅
  ③ 기존 설명: EQUIPMENT(지게차)와 WORK(하역) 경계 — 부분만 ✅
  → 승격: 조건부 (has_lifting_work 입력 추가 시)

ELECTRICAL (전기작업) — 6건
  ① 입력필드: has_temp_electric 있으나 "전기작업" 별도 △
  ② 법령군: 감전·충전부·접지·절연 독립 ✅
  ③ 기존 설명: 불가 ✅
  → 승격: 조건부 (has_electrical_work 입력 추가 시)

FALL_PREVENT (추락방지) — 8건
  ① 입력필드: has_high_place_work/has_scaffold 존재 ✅
  ② 법령군: 개구부·난간·안전대·방망 독립 ✅
  ③ 기존 설명: WORK 하위로 가능 △
  → 승격: WORK_EXISTS 하위 L2로 흡수 권장 (독립 아님)
```

---

## TASK-004: Trigger 확장안 (4분류)

| 분류 | 건수 | 처리 |
|---|---|---|
| **범위 밖 제외** | 76 | TAI Safe 대상 아님. 필터에서 제거 |
| **UNIVERSAL 흡수** | 141 | INSPECT59+DOC37+포괄28+EDU17 → sector 일괄 |
| **신규 Trigger** | 25 | TRANSPORT19 + ELECTRICAL6 (FALL은 WORK흡수) |
| **WORK L2 추가/미분류** | 278 | WORK_일반작업129 + FALL8 + 미분류잔여142 |

### 확장된 Trigger 체계

```
기존 8 Trigger 유지 +
신규 2 Trigger 승격:
  TRANSPORT_EXISTS  (운반·하역, has_lifting_work)
  ELECTRICAL_EXISTS (전기작업, has_electrical_work)

흡수:
  추락방지 → WORK_EXISTS.FALL_PREVENT (L2)
  점검·정비·문서·교육 → TRUE_UNIVERSAL

→ 최종 Trigger: 기존 8 + 신규 2 = 10종
```

---

## TASK-005: Coverage 재계산

```
사업주 의무 1,572건 기준 재계산:

[범위 밖 제거 후 실제 대상]
  1,572 - 76(범위밖) = 1,496건 (TAI Safe 실제 대상)

[Coverage]
  기존 CONNECTED       1,025
  + UNIVERSAL 흡수       141
  + 신규 Trigger(운반·전기) 25
  + WORK L2(일반작업+추락) 137
  ────────────────────────
  = 1,328건 설명 가능

  Coverage = 1,328 / 1,496 = 88.8%

  잔여 미분류: 142건 (9.5%) — 추가 정밀분류 대상

→ 65% → 89%로 상승.
→ 범위 밖 76건 제거 + UNIVERSAL 흡수가 커버리지 견인.
```

---

## 핵심 발견

### 발견 1: NO_TRIGGER의 15%는 애초에 범위 밖

```
76건이 주택법·파견법·공동주택관리법의 "사업주체".
산업안전보건법 사업주가 아님.

→ executor 필터를 산업안전보건법으로 한정해야 함.
→ 이것을 모르고 후보군 생성했으면
  분양·파견·관리비 의무가 공장에 매핑되는 오류 발생.
→ 17회차 "잠수작업이 제조업에 선임의무로" 같은 오탐의 원인.
```

### 발견 2: 진짜 신규 Trigger는 2종뿐

```
TRANSPORT (운반·하역) 19건
ELECTRICAL (전기작업) 6건

→ 나머지는 전부 기존 Trigger로 흡수 가능.
→ 현 Trigger 체계가 거의 완성형이었음.
→ "구조가 흔들릴" 위험이 매우 낮음.
```

### 발견 3: UNIVERSAL이 NO_TRIGGER의 진짜 정체

```
점검·정비59 + 문서37 + 포괄28 + 교육17 = 141건이
모두 "입력 조건 없는 일반 의무" = UNIVERSAL.

→ NO_TRIGGER가 아니라 "UNIVERSAL 미인식"이었음.
→ condition_text는 있으나 실질은 sector 일괄 의무.
→ UNIVERSAL 693 + 141 = 834건이 진짜 UNIVERSAL 규모.
```

### 발견 4: 미분류 142건이 마지막 숙제

```
WORK도 EQUIPMENT도 UNIVERSAL도 아닌 142건.
→ 조문 직독 또는 LLM 분류 필요.
→ 이게 진짜 마지막 NO_TRIGGER.
→ 전체의 9.5%.
```

---

## 성공 기준 답변

> 현재 Trigger 체계는 최종 체계인가? 어떤 Trigger가 더 필요한가?

```
거의 최종이다. 신규 2종만 추가하면 89% 커버.

추가 필요 Trigger:
  TRANSPORT_EXISTS  (운반·하역, 19건)
  ELECTRICAL_EXISTS (전기작업, 6건)

흡수로 해결:
  추락방지 → WORK L2
  점검·정비·문서·교육·포괄 → UNIVERSAL

제외:
  범위 밖 76건 (주택법·파견법·공동주택관리법)

남은 숙제:
  미분류 142건 (9.5%) → 추가 정밀분류

→ 구조는 흔들리지 않는다. 신규 2 Trigger + 범위 필터만 추가.
```

---

## 다음 단계 권고

```
WO-TRIGGER-EXPANSION-001 (현재) — 완료
      ↓
WO-SCOPE-FILTER-001 (선행 권장)
  executor를 산업안전보건법으로 한정
  범위 밖 76건(주택법·파견법·공동주택) 제거 규칙 확정
      ↓
WO-PATTERN-CANDIDATE-GENERATION-001
  이제 89% 커버 + 범위 필터로 후보군 생성
  1순위: EXISTS Trigger (WORK/EQUIPMENT/MATERIAL/FACILITY)
  2순위: 신규 TRANSPORT/ELECTRICAL
  baseline: UNIVERSAL sector 일괄
  격리: 미분류 142 + FRAGMENT
```

---

*WO-TRIGGER-EXPANSION-001 완료. NO_TRIGGER 520건 정체 규명.*
*범위밖 76 + UNIVERSAL흡수 141 + 신규Trigger 25 + WORK/미분류 278.*
*핵심: 진짜 신규는 TRANSPORT/ELECTRICAL 2종뿐. 범위 밖 76건 발견. Coverage 65%→89%.*
