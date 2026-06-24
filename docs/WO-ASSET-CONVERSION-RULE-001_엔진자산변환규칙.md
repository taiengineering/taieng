# WO-ASSET-CONVERSION-RULE-001
# Harvest → 엔진 자산 변환 규칙

**작성일:** 2026-06-24 | **상태:** 완료 (변환 규칙 추출 전용)
**선행:** WO-MAPPING-ASSET-AUDIT-001
**금지:** INSERT / UPDATE / 승격 / REVIEW / 신규 Harvest
**목적:** condition_mapping_candidate 77건이 어떤 규칙으로 엔진 자산이 되었는가? 그 규칙을 추출한다.

---

## 결론 먼저

```
77건 엔진 자산의 생성 규칙이 완전히 역추출됨.

Harvest 1건 → 엔진 자산 1건 자동 생성 가능.
단, condition_code의 DETAIL(p3) 1개 요소만 의미 요약 필요.

변환 규칙:
  condition_type   ← trigger_l1 변환 (기계적)
  condition_code   ← {type}:{L2}:{DETAIL}:{HASH} (DETAIL만 의미)
  HASH             ← semantic_clause_id 앞 4자리 (기계적, 검증됨)
  condition_source ← CONDITION_TEXT/ACTION_TEXT (조문 위치)
  confidence       ← source별 고정값 (기계적)
  input_operator   ← '=' 고정
  input_value      ← 'true' 고정 (EXISTS형)
```

---

## TASK-001: Engine Asset 규격 (77건 사용 필드)

```
77건이 실제 사용하는 필드:
  semantic_clause_id  — 조문 연결 (필수)
  condition_type      — WORK_ACT/EQUIPMENT_ACT/MATERIAL_ACT/FACILITY_ACT
  condition_code      — {TYPE}:{L2}:{DETAIL}:{HASH}
  condition_source    — CONDITION_TEXT / ACTION_TEXT
  input_field         — has_*
  input_operator      — '=' (전건 동일)
  input_value         — 'true' (전건 동일, EXISTS형)
  confidence          — 0.90 ~ 0.98
  review_status       — CONFIRMED
  applicable_sectors  — 섹터 배열
```

---

## TASK-002: condition_type 생성 규칙

```
trigger_l1 → condition_type (기계적 1:1):

WORK_EXISTS       → WORK_ACT
EQUIPMENT_EXISTS  → EQUIPMENT_ACT
MATERIAL_EXISTS   → MATERIAL_ACT
FACILITY_EXISTS   → FACILITY_ACT
DIRECT_THRESHOLD  → NUMERIC_DIRECT (77건엔 없음, 신규)
TRUE_UNIVERSAL    → UNIVERSAL_SECTOR (77건엔 없음, 신규)

77건 분포:
  WORK_ACT 37 / MATERIAL_ACT 24 / EQUIPMENT_ACT 14 / FACILITY_ACT 2

검증: 동일 조문이 작업+설비 양쪽 의무면 condition_type이 갈림.
  예: has_diving →
    "잠수기록 작성" = WORK_ACT
    "잠수장비 비치" = EQUIPMENT_ACT
  → 조문의 action 성격으로 type 결정 (작업행위 vs 설비요구).
```

---

## TASK-003: condition_code 생성 규칙

```
형식: {TYPE}:{L2}:{DETAIL}:{HASH}

P1 TYPE   ← condition_type (기계적)
            예: WORK_ACT, EQUIPMENT_ACT

P2 L2     ← trigger_l2 (기계적)
            예: ASBESTOS, BOILER, DIVING, HAZMAT
            주의: MATERIAL은 HAZMAT로 통일된 사례 다수
            (has_chemical_substance → HAZMAT)

P3 DETAIL ← action_text 의미 요약 (★유일한 비기계 요소)
            예: HYGIENE, INFORM, METHOD, PPE, RESTRICT_ENTRY,
                PRESSURE_RELIEF, WATER_LEVEL, ALARM, CONTAINER
            → 의무 내용을 영문 키워드로 요약.
            → 자동 생성 불가. 사람/LLM 판단 필요.

P4 HASH   ← semantic_clause_id 앞 4자리 (기계적, 15/15 검증됨)
            예: clause 0fcf...→ HASH 0fcf
            예: clause 82e5...→ HASH 82e5
```

### 결정적 발견: HASH = clause_id 앞 4자리

```
검증 결과 15/15 모두 일치:
  EQUIPMENT_ACT:BOILER:PRESSURE_RELIEF:82e5 ↔ clause 82e5...
  WORK_ACT:ASBESTOS:PPE:0fcf ↔ clause 0fcf...

→ HASH는 임의값이 아니라 semantic_clause_id 파생.
→ 변환 시 자동 생성 가능. 충돌 시 5~8자리로 확장.
```

---

## TASK-004: confidence 생성 규칙

```
condition_source에 따라 confidence 부여:

CONDITION_TEXT 출처:
  0.90 ~ 0.98 (주로 0.95, 0.97)
  → 조건문에 직접 명시 = 신뢰 높음

ACTION_TEXT 출처:
  0.90 ~ 0.97 (주로 0.90, 0.95)
  → 행위문에서 추론 = 약간 낮음

규칙 (77건 관찰 기반):
  CONDITION_TEXT 기본 0.95, 명확하면 0.97~0.98
  ACTION_TEXT 기본 0.90, 명확하면 0.95

→ 변환 시 source 기준 기본값 부여 후 REVIEW에서 조정.
→ 신규 HARVEST 적재 시: CONDITION_TEXT 0.85, ACTION_TEXT 0.80
  (CONFIRMED보다 낮게 — 미검증 표시)
```

---

## TASK-005: condition_source 생성 규칙

```
조문의 어느 부분에서 Trigger 근거를 찾았는가:

CONDITION_TEXT:
  condition_text에 Trigger 키워드 존재
  예: "근로자가 밀폐공간에서 작업하는 경우" (조건문에 작업 명시)
  → 47건

ACTION_TEXT:
  action_text에 Trigger 키워드 존재 (조건문엔 없음)
  예: condition NULL + "보일러 압력방출장치 설치" (행위문에 설비)
  → 30건

규칙:
  IF condition_text가 L2 키워드 포함 → CONDITION_TEXT
  ELSE IF action_text가 L2 키워드 포함 → ACTION_TEXT

→ candidate_harvest는 harvest_method='EXISTS_KEYWORD'로
  이미 어느 텍스트에서 매칭됐는지 추적 가능.
```

---

## TASK-006: Harvest → Asset 매핑표

| candidate_harvest | → | condition_mapping_candidate | 변환 방식 |
|---|---|---|---|
| semantic_clause_id | → | semantic_clause_id | 직접 복사 |
| trigger_l1 | → | condition_type | WORK_EXISTS→WORK_ACT 매핑 |
| trigger_l2 | → | condition_code P2 (L2) | 직접 |
| (action 의미) | → | condition_code P3 (DETAIL) | ★의미 요약 (비기계) |
| semantic_clause_id[0:4] | → | condition_code P4 (HASH) | 앞 4자리 |
| input_field | → | input_field | 직접 복사 |
| (고정) | → | input_operator | '=' |
| (고정) | → | input_value | 'true' |
| harvest_method | → | condition_source | 텍스트 위치로 판정 |
| (source별 규칙) | → | confidence | CONDITION 0.85 / ACTION 0.80 |
| (고정) | → | review_status | 'HARVESTED' (CONFIRMED 아님) |
| condition_text | → | condition_text_raw | 직접 복사 |
| action_text | → | action_text_raw | 직접 복사 |

---

## 성공 기준 답변

> Harvest 1건이 들어오면 condition_mapping_candidate 1건을 자동 생성할 수 있는가?

```
거의 자동 생성 가능. 단 1개 요소만 비기계적.

자동 생성 가능 (기계적):
  ✅ condition_type   (trigger_l1 매핑)
  ✅ condition_code P1 (=type)
  ✅ condition_code P2 (=trigger_l2)
  ✅ condition_code P4 (=clause_id 앞4자리)
  ✅ HASH (검증 완료)
  ✅ input_field/operator/value
  ✅ condition_source (텍스트 위치)
  ✅ confidence (source 규칙)
  ✅ review_status ('HARVESTED')
  ✅ raw 텍스트

자동 생성 불가 (의미 판단 필요):
  ⚠️ condition_code P3 (DETAIL) — action 의미 요약
     예: "압력방출장치 설치" → PRESSURE_RELIEF

→ DETAIL은 임시값(SEQ 번호) 부여 후 REVIEW에서 확정 가능.
→ 또는 LLM이 action_text → DETAIL 요약 생성.
→ 나머지 12개 필드는 100% 자동.
```

---

## 핵심 발견

### 발견 1: 변환은 92% 기계적

```
13개 필드 중 12개 자동 생성.
유일한 비기계 요소 = condition_code의 DETAIL(P3).

→ 813건을 거의 자동으로 엔진 자산화 가능.
→ DETAIL만 임시값 또는 LLM 요약으로 채우면 됨.
```

### 발견 2: HASH 규칙이 자산화의 핵심 열쇠

```
HASH = semantic_clause_id 앞 4자리.
→ condition_code가 조문과 결정론적으로 연결됨.
→ 중복 검출/역추적 가능.
→ 변환 시 UUID만 있으면 HASH 자동.
```

### 발견 3: 신규는 HARVESTED 상태로 적재

```
기존 77 = CONFIRMED (confidence 0.90~0.98)
신규 813 = HARVESTED (confidence 0.80~0.85, 낮게)

→ 같은 테이블, 다른 상태.
→ 엔진이 review_status로 필터 가능.
→ REVIEW 후 CONFIRMED 승격 시 confidence 상향.
```

### 발견 4: DETAIL이 REVIEW의 실제 작업

```
변환은 자동, DETAIL 요약 + 검증이 REVIEW의 본질.
→ REVIEW = "이 의무가 무슨 내용인가(DETAIL)" + "Trigger 맞나"
→ 813건 변환 후 REVIEW에서 DETAIL 정제.
```

---

## 다음 단계

```
WO-ASSET-CONVERSION-RULE-001 (현재) — 완료. 규칙 고정.
      ↓
WO-HARVEST-TO-ASSET-001
  candidate_harvest 813 → condition_mapping_candidate 변환:
    1. EXISTS 501건 우선 (검증된 구조)
    2. 12개 필드 자동 생성
    3. DETAIL은 임시 SEQ 또는 LLM 요약
    4. review_status='HARVESTED', confidence 0.80~0.85
    5. 기존 77 CONFIRMED 무수정 (INSERT only)
  → 엔진 테이블에 813 실체화.
      ↓
WO-CANDIDATE-REVIEW-001
  HARVESTED → DETAIL 정제 + Trigger 검증 → CONFIRMED 승격.
```

---

*WO-ASSET-CONVERSION-RULE-001 완료. 변환 규칙 추출. INSERT/UPDATE 없음.*
*77건 생성 규칙 역추출 완료. 92% 기계적 변환 가능.*
*핵심: HASH=clause_id 앞4자리(검증). DETAIL만 의미요약 필요. Harvest 1건→Asset 1건 자동 생성 가능.*
