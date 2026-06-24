# WO-HARVEST-TO-ASSET-001
# candidate_harvest → condition_mapping_candidate 엔진 자산 변환

**작성일:** 2026-06-24 | **상태:** 완료 (실제 변환·적재)
**선행:** WO-ASSET-CONVERSION-RULE-001
**금지:** 기존 77 CONFIRMED 수정 / CONFIRMED 신규 생성 / Trigger 재정의 / 패턴 재분석 / harvest 삭제
**목적:** EXISTS Trigger 후보를 엔진이 읽는 condition_mapping_candidate로 변환 적재.

> 분석 아닌 적재. 엔진이 77건만 보던 상태 → HARVESTED 자산이 운영 테이블에 진입.

---

## 결론 먼저

```
EXISTS 501건 → 운영 테이블에 410건 HARVESTED 적재 완료.

condition_mapping_candidate 최종:
  CONFIRMED  77   (기존, 무수정 유지) ✅
  HARVESTED 410   (신규 적재)
  ─────────────────
  합계      487

엔진은 이제 77건이 아니라 487건을 읽는다.
(단, HARVESTED는 review_status로 필터하여 검토 전 표시)
```

---

## TASK-001: 적재 전 중복 확인

```
EXISTS 수확 총: 501건
이미 cmc에 존재 (clause+input_field): 75건 → 제외
candidate_harvest 내부 중복 (같은 조문 다중 Trigger): 16건 → DISTINCT 제거
실제 신규 적재: 410건
```

---

## TASK-002~005: 변환 규칙 적용 + INSERT

### 적용된 변환 규칙

```
condition_type:
  WORK_EXISTS → WORK_ACT
  EQUIPMENT_EXISTS → EQUIPMENT_ACT
  MATERIAL_EXISTS → MATERIAL_ACT
  FACILITY_EXISTS → FACILITY_ACT

condition_code: {type}:{L2}:AUTO{seq}:{hash4}
  예: WORK_ACT:DIVING:AUTO1:abcd
      EQUIPMENT_ACT:BOILER:AUTO1:17ea
  - hash4 = semantic_clause_id 앞 4자리
  - AUTO{seq} = DETAIL 임시값 (REVIEW에서 의미 요약 교체)

input_operator = '='
input_value = 'true'
confidence = 0.80 (CONFIRMED보다 낮게 — 미검증)
review_status = 'HARVESTED'
condition_source = CONDITION_TEXT (조건문 근거) / ACTION_TEXT
applicable_sectors = diagnosis_input_fields.sector에서 자동 채움
```

### 적재 중 해결한 제약조건

```
1. cmc_applicable_sectors_required_check
   → applicable_sectors NOT NULL 필수.
   → candidate_harvest는 sector 미보유였음.
   → diagnosis_input_fields에서 input_field별 sector 조인하여 채움.

2. cmc_review_status_check (PENDING/CONFIRMED/REJECTED만)
   → HARVESTED 추가 (기존 값 보존, 확대만).
   → ALTER로 4개 값 허용.

3. cmc_unique_sector_mapping (clause+field+value+sectors UNIQUE)
   → candidate_harvest 내 같은 조문 다중수확 충돌.
   → DISTINCT ON + ON CONFLICT DO NOTHING으로 해결.
```

---

## TASK-006: 적재 결과 확인

| 검증 항목 | 결과 | 판정 |
|---|---|---|
| 기존 CONFIRMED 77 유지 | 77 | ✅ |
| 신규 HARVESTED | 410 | ✅ |
| condition_code 중복 | 0 | ✅ |
| COMMON 섹터 | 0 | ✅ |
| NULL 섹터 | 0 | ✅ |

### condition_type별 HARVESTED 분포

| condition_type | HARVESTED |
|---|---|
| WORK_ACT | 183 |
| MATERIAL_ACT | 136 |
| EQUIPMENT_ACT | 82 |
| FACILITY_ACT | 9 |
| **합계** | **410** |

---

## 산출물 A~F 요약

```
A. 적재 대상 수:      EXISTS 501
B. 중복 제외 수:      91 (cmc기존 75 + harvest내부 16)
C. 실제 INSERT 수:    410
D. condition_type별:  WORK 183 / MATERIAL 136 / EQUIPMENT 82 / FACILITY 9
E. review_status별:   CONFIRMED 77 / HARVESTED 410
F. 보류 사유:
   - TRUE_UNIVERSAL 310 (sector 일괄, 2차)
   - DIRECT_THRESHOLD 2 (APPENDIX 보강 후)
   - APPENDIX_THRESHOLD (appendix_condition 입력 선행)
   - COMPOUND/FRAGMENT (별도 처리)
```

---

## 핵심 발견

### 발견 1: 엔진 자산이 5배로 실체화

```
이전: 77 CONFIRMED만 엔진이 읽음.
현재: 487건 (77 CONFIRMED + 410 HARVESTED).

→ 엔진이 EXISTS 후보 410건을 읽을 수 있게 됨.
→ review_status='HARVESTED' 필터로 검토 전/후 구분.
→ Harvest가 staging 로그 → 운영 자산으로 전환됨.
```

### 발견 2: 제약조건이 데이터 품질을 강제

```
cmc 테이블의 3개 제약조건이 적재를 막았고,
그 덕분에 데이터 품질이 강제됨:
  - sector 필수 → NULL sector 불가
  - unique 키 → 중복 매핑 불가
  - review_status enum → 임의 상태 불가

→ 제약조건이 17회차 오탐의 안전망 역할.
→ candidate_harvest(제약 없음)와 cmc(제약 강함)의 차이 확인.
```

### 발견 3: DETAIL은 AUTO{seq} 임시값

```
condition_code의 DETAIL을 AUTO1, AUTO2로 임시 부여.
예: WORK_ACT:DIVING:AUTO1:abcd

→ REVIEW에서 "RECORD", "ASCENT_SPEED" 등 의미 요약으로 교체.
→ 적재는 완료, 의미 정제는 REVIEW 작업.
```

---

## 성공 기준 답변

```
condition_mapping_candidate에
  기존 77 CONFIRMED 그대로 유지 ✅
  EXISTS 후보 410건 HARVESTED 추가 ✅

→ 엔진은 더 이상 77건만 보지 않는다.
→ 운영 테이블에 검토 전 자산(HARVESTED) 진입 완료.
→ 이후 REVIEW는 상태 전이(HARVESTED→CONFIRMED) 작업.
```

---

## 다음 단계

```
WO-HARVEST-TO-ASSET-001 (현재) — 완료. EXISTS 410 적재.
      ↓
WO-CANDIDATE-REVIEW-001
  HARVESTED 410 → 상태 전이:
    1. Trigger Group 단위 (DIVING, BOILER 등)
    2. 조문 직독 → Trigger 적합성 검증
    3. DETAIL(AUTO) → 의미 요약 교체
    4. 통과 → review_status='CONFIRMED', confidence 상향
    5. 부적합 → 'REJECTED' + exclude_reason
      ↓
WO-HARVEST-TO-ASSET-002 (선택)
  TRUE_UNIVERSAL 310 sector 일괄 적재
      ↓
WO-APPENDIX-HARVEST-001
  appendix_condition 입력 → THRESHOLD 적재
```

---

*WO-HARVEST-TO-ASSET-001 완료. EXISTS 410건 HARVESTED 적재.*
*cmc: CONFIRMED 77(유지) + HARVESTED 410. 엔진 자산 5배 실체화.*
*핵심: Harvest→운영자산 전환 완료. 제약조건이 품질 강제. DETAIL은 REVIEW에서 정제.*
