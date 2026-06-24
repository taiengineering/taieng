# WO-HARVEST-TO-OPERATION-001
# HARVEST → REVIEW → CONFIRMED 운영 승격 체계

**작성일:** 2026-06-24 | **상태:** 완료 (운영 규격 확정 전용)
**선행:** WO-CANDIDATE-HARVEST-001
**금지:** 새 Trigger 발견 / 패턴 재분석 / Coverage 분석 / 법령 재분류
**목적:** 813 HARVESTED를 어떤 기준으로 운영 자산으로 승격할 것인가?

> 새 발견 단계 아님. 이미 수확된 자산을 운영 자산으로 만드는 단계.

---

## 결론 먼저

```
운영 라인 확정:

  candidate_harvest (813, HARVESTED)
        ↓ REVIEW (4개 기준)
        ↓ Trigger Group 단위
  condition_mapping_candidate (CONFIRMED)
        ↓
  Check Engine → 6W → 출력

승격 규격:
  harvest.trigger_l1 → cmc.condition_type
  harvest.semantic_clause_id → cmc.semantic_clause_id
  harvest.trigger_l2 → cmc.condition_code 구성요소
  REVIEW 통과 → cmc.review_status='CONFIRMED'

우선순위: WORK → EQUIPMENT → MATERIAL → FACILITY → UNIVERSAL
단위: 조문 1건씩 아님. Trigger Group(DIVING 전체) 단위.
```

---

## TASK-001: HARVESTED 상태 정의

```
HARVESTED의 의미 (확정):

조건 (4개 모두 충족된 상태):
  ✅ Trigger 연결 완료     — 입력→Trigger→조문 경로 존재
  ✅ Scope 통과            — 범위 밖 191건 제외됨
  ✅ 자동 생성 완료        — 키워드 기반 기계 수확
  ❌ 아직 사람 검토 없음    — 조문 직독 검증 전

→ HARVESTED = "구조적으로 후보 자격은 있으나 미검증"
→ 신뢰도 미정. confidence 부여 안 됨.
→ 운영(Check Engine)에 투입 불가 상태.
```

---

## TASK-002: REVIEW 기준 정의

```
REVIEW는 오직 4개만 본다. (그 외 금지)

① Trigger 적합성
   이 조문이 정말 이 Trigger 때문에 발생하는가?
   예: has_diving → 이 조문이 정말 잠수작업 의무인가?

② 조문 의미 적합성
   condition_text + action_text가 사업주 안전의무인가?
   범위 밖/단편/위임이 아닌 실질 의무인가?

③ 중복 여부
   같은 조문이 여러 Trigger에 수확됐는가?
   대표 Trigger 1개 선정 또는 다중 유지 결정.

④ 설명문 생성 가능 여부
   "입력 X → Trigger Y → 의무 Z" 1문장이 성립하는가?
   (VALIDATION-001의 EXPLAINABLE 방식)

→ REVIEW에서 안 보는 것:
   정확도 점수화, 법령 재분류, 새 Trigger 탐색,
   Coverage 재계산, 패턴 재발견.
```

---

## TASK-003: CONFIRMED 승격 기준

```
4개 모두 충족 시 CONFIRMED 승격:

  ✅ Trigger 적합   (① 통과)
  ✅ 조문 적합      (② 통과)
  ✅ 설명 가능      (④ 통과)
  ✅ 중복 정리 완료 (③ 처리)

하나라도 실패 시:
  REJECTED (exclude_reason 기록)
  또는 HOLD (재검토 대기)

→ CONFIRMED = 운영 투입 가능. confidence 0.90+ 부여.
→ Check Engine이 이 조문을 진단 결과로 출력 가능.
```

---

## TASK-004: candidate_harvest → condition_mapping_candidate 규격

### 필드 매핑표

| candidate_harvest | condition_mapping_candidate | 변환 규칙 |
|---|---|---|
| semantic_clause_id | semantic_clause_id | 직접 |
| trigger_l1 | condition_type | WORK_EXISTS→WORK_ACT 등 |
| trigger_l2 | condition_code (구성) | `{type}:{L2}:{세부}:{해시}` |
| input_field | input_field | 직접 |
| condition_text | condition_text_raw | 직접 |
| action_text | action_text_raw | 직접 |
| harvest_method | condition_source | EXISTS_KEYWORD→CONDITION_TEXT |
| (REVIEW 결과) | review_status | CONFIRMED/REJECTED |
| (REVIEW 결과) | confidence | 0.90~0.98 |
| (REVIEW 생성) | explanation → 별도 | 1문장 설명문 |

### Trigger → condition_type 변환

```
WORK_EXISTS       → WORK_ACT
EQUIPMENT_EXISTS  → EQUIPMENT_ACT
MATERIAL_EXISTS   → MATERIAL_ACT
FACILITY_EXISTS   → FACILITY_ACT
DIRECT_THRESHOLD  → NUMERIC_DIRECT
TRUE_UNIVERSAL    → UNIVERSAL_SECTOR

→ 기존 77 CONFIRMED가 이미 WORK_ACT/EQUIPMENT_ACT/MATERIAL_ACT/
  FACILITY_ACT 사용 중. 신규도 동일 체계로 정합.
```

### condition_code 생성 규칙

```
형식: {condition_type}:{trigger_l2}:{세부}:{해시8자리}

예 (기존 패턴 준수):
  WORK_ACT:DIVING:RECORD:a3f9c2b1
  EQUIPMENT_ACT:BOILER:PRESSURE:7d2e8f04
  MATERIAL_ACT:ASBESTOS:PPE:b15c9a3e

→ 기존 77건 형식과 100% 동일.
```

---

## TASK-005: REVIEW 우선순위 정책

```
813건 전부 한 번에 보지 않는다.

P1 WORK_EXISTS     233  ← 가장 깨끗한 DIRECT, 먼저
P2 EQUIPMENT_EXISTS 90
P3 MATERIAL_EXISTS 157
P4 FACILITY_EXISTS  21
P5 TRUE_UNIVERSAL  310  ← sector 일괄, 마지막
   DIRECT_THRESHOLD  2  ← APPENDIX 보강 후

근거:
  EXISTS 4종(501건)은 VALIDATION-001에서 100% 설명 검증됨.
  → 가장 안전한 승격 라인. 먼저 운영화.
  UNIVERSAL(310)은 sector 일괄이라 개별 검토보다
  그룹 정책으로 일괄 처리. 마지막.
```

---

## TASK-006: REVIEW 단위 확정

```
조문 1건씩 아님. Trigger Group 단위로 REVIEW.

단위 예:
  WORK.DIVING 전체 (27건) → 한 번에 REVIEW
  WORK.BLASTING 전체 (4건) → 한 번에 REVIEW
  EQUIPMENT.CRANE 전체 (25건) → 한 번에 REVIEW

이유:
  같은 L2는 같은 입력(has_diving)에서 출발.
  조문들이 의미상 한 묶음 (잠수 의무군).
  → 그룹 단위로 보면 Trigger 적합성을 일괄 판정 가능.
  → 개별 조문 813번 보는 것보다 ~40개 그룹으로 압축.

REVIEW 그룹 수:
  WORK 12 + EQUIPMENT 12 + MATERIAL 5 + FACILITY 4
  + UNIVERSAL 6 = 약 39개 그룹.
  → 813건을 39개 단위로 검토.
```

---

## 운영 라인 전체도

```
[수집 완료]
  input_staging (8,882 + 198,278)
  semantic_clause (58,495)

[구조 완료]
  입력 7패턴 / 법령 8 Trigger 2계층
  SCOPE FILTER (범위밖 191 제거)

[수확 완료] ← 현재
  candidate_harvest 813 (HARVESTED)

[운영 승격] ← 이 WO가 정의
  REVIEW (39 Trigger Group, 4기준)
       ↓
  condition_mapping_candidate (CONFIRMED)

[운영 가동]
  Check Engine → 6W 분해 → 진단 출력
  (설계문서 기존 구현 존재)
```

---

## 성공 기준 답변

```
Q: HARVESTED는 무엇인가?
A: Trigger 연결 + Scope 통과 + 자동생성 완료,
   단 사람 검토 전. 구조적 후보 자격은 있으나 미검증.
   운영 투입 불가.

Q: REVIEW는 무엇을 검증하는가?
A: 4가지만. ①Trigger 적합성 ②조문 의미 적합성
   ③중복 여부 ④설명문 생성 가능 여부.

Q: CONFIRMED는 언제 되는가?
A: 4기준 모두 충족 시. Trigger 적합 + 조문 적합
   + 설명 가능 + 중복 정리 완료. confidence 0.90+ 부여.

Q: 813건을 어떤 순서로 승격하는가?
A: WORK(233) → EQUIPMENT(90) → MATERIAL(157)
   → FACILITY(21) → UNIVERSAL(310) → THRESHOLD(2).
   Trigger Group 단위(약 39그룹)로 검토.
```

---

## 핵심 발견

### 발견 1: 기존 운영 테이블이 신규 수확과 완전 정합

```
condition_mapping_candidate의 condition_type
(WORK_ACT/EQUIPMENT_ACT/MATERIAL_ACT/FACILITY_ACT)이
harvest의 Trigger와 1:1 대응.

→ 새 테이블/컬럼 불필요.
→ 기존 77 CONFIRMED와 같은 규격으로 승격 가능.
→ 운영 구조가 이미 Trigger 사고로 설계되어 있었음.
```

### 발견 2: REVIEW는 39그룹으로 압축됨

```
813건 개별 검토 = 비현실적.
Trigger Group 단위 = 39그룹.

→ has_diving 27건을 "잠수 의무군"으로 한 번에 판정.
→ 검토 부하 813 → 39로 20배 감소.
```

### 발견 3: EXISTS 먼저가 안전 승격 경로

```
EXISTS 501건은 VALIDATION-001에서 검증된 구조.
UNIVERSAL 310건은 sector 정책으로 일괄.

→ 검증된 것부터 운영화.
→ 17회차 "검증 안 된 것 먼저 확정" 실패 차단.
```

---

## 다음 단계

```
WO-HARVEST-TO-OPERATION-001 (현재) — 완료
      ↓
WO-CANDIDATE-REVIEW-001
  P1 WORK_EXISTS 12그룹부터 REVIEW 시작
  - WORK.DIVING 27건 그룹 직독
  - 4기준 판정 → CONFIRMED/REJECTED
  - condition_mapping_candidate로 승격 INSERT
  주의: Trigger Group 단위, 조문 직독(숫자 아님)
      ↓
WO-APPENDIX-HARVEST-001 (병행)
  appendix_condition 별표 입력 → THRESHOLD 보강
```

---

*WO-HARVEST-TO-OPERATION-001 완료. 운영 승격 체계 확정.*
*HARVESTED→REVIEW(4기준,39그룹)→CONFIRMED 라인 정의.*
*핵심: 기존 운영 테이블과 완전 정합. EXISTS 먼저. Trigger Group 단위 검토.*
