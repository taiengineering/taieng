# WO-HARVEST-TO-ASSET-002
# TRUE_UNIVERSAL 310건 엔진 자산 변환·적재

**작성일:** 2026-06-24 | **상태:** 완료 (UNIVERSAL 적재)
**선행:** WO-ENGINE-OPERATION-VALIDATION-001
**금지:** EXISTS 매핑 수정 / 기존 452 CONFIRMED 수정 / BUILDING HOLD 해제 / APPENDIX / Trigger 재정의
**목적:** sector baseline 의무를 엔진이 읽을 수 있게 TRUE_UNIVERSAL 적재.

> UNIVERSAL은 입력값 없이 sector만으로 발동 → 모든 진단 결과의 뼈대.

---

## 결론 먼저

```
TRUE_UNIVERSAL 310건 → cmc에 HARVESTED 적재 완료.

condition_mapping_candidate 최종:
  CONFIRMED 452  (기존, 무수정)
  HARVESTED 310  (UNIVERSAL 신규, condition_type='NONE')
  REJECTED   35
  ───────────────
  합계      797

sector baseline 효과:
  INDUSTRIAL:   공통 214 + 전용 12 = 226 baseline
  CONSTRUCTION: 공통 214 + 전용 9  = 223 baseline
  BUILDING:     공통 214 + 전용 75 = 289 baseline ★

→ 건물(이전 EXISTS 0건)이 이제 289건 baseline 획득.
```

---

## TASK-001: 대상 확인

```
TRUE_UNIVERSAL 후보: 310건
  distinct 조문: 310 (중복 없음)
  IN_SCOPE: 310 (전부 scope 통과)
```

---

## TASK-002: 변환 규칙 (스키마가 이미 지원)

```
cmc 스키마가 UNIVERSAL을 이미 설계상 지원:
  condition_type='NONE'              ✅ 제약 허용
  null_condition_class='A_UNIVERSAL' ✅ 제약 허용
  input_field NULL                    ✅ nullable

적용된 변환:
  condition_type = 'NONE'
  condition_code = 'NONE:UNIVERSAL:{DETAIL}{seq}:{HASH}'
  condition_source = 'MANUAL'
  input_field = NULL (sector만으로 발동)
  input_operator = NULL
  input_value = NULL
  null_condition_class = 'A_UNIVERSAL'
  review_status = 'HARVESTED'
  confidence = 0.80

DETAIL 의미코드:
  EDUCATION / REPORT / POSTING / DOCUMENT /
  INSPECT / INSTALL / PROVIDE / GENERAL
```

---

## TASK-003: applicable_sectors 채우기

조문 내용으로 sector 귀속 판정:

| sector | 건수 | 판정 근거 |
|---|---|---|
| INDUSTRIAL,CONSTRUCTION,BUILDING (공통) | 214 | sector 한정 표현 없음 → 전체 공통 |
| BUILDING | 75 | 건축물·소방·승강기·다중이용 |
| INDUSTRIAL | 12 | 제조·공정·생산·설비 |
| CONSTRUCTION | 9 | 건설공사·도급인·발주자·가설 |

**COMMON 금지 준수: 전체 공통은 3개 sector 배열로 명시 적재.**

---

## TASK-004~005: 중복 제외 + INSERT

```
중복 기준: semantic_clause_id + condition_type='NONE' + sectors
이미 cmc에 있는 NONE: 0건 (신규 영역)
실제 INSERT: 310건
ON CONFLICT DO NOTHING 적용.
```

---

## TASK-006: 검증

| 항목 | 결과 | 판정 |
|---|---|---|
| UNIVERSAL HARVESTED | 310 | ✅ |
| null_condition_class='A_UNIVERSAL' | 310 | ✅ |
| input_field NULL (정상) | 오류 0 | ✅ |
| 기존 CONFIRMED 452 유지 | 452 | ✅ |
| 기존 77 무수정 (reviewer NULL) | 77 | ✅ |
| condition_code 중복 | 0 | ✅ |
| COMMON sector | 0 | ✅ |
| NULL sector | 0 | ✅ |

---

## 산출물 A~E 요약

```
A. 대상 수:      310 (distinct 310, in_scope 310)
B. 실제 INSERT:  310
C. sector 분포:  공통 214 / BUILDING 75 / INDUSTRIAL 12 / CONSTRUCTION 9
D. 중복 제외:    0 (신규 영역)
E. 검증:         전 항목 통과. input_field NULL 정상, A_UNIVERSAL 310
```

---

## 핵심 발견

### 발견 1: 건물(BUILDING)이 baseline을 획득

```
실동작 검증(VALIDATION-001)에서 건물 = 0건이었음.
이제 건물 = 289 baseline (공통 214 + 건물전용 75).

→ 건물 진단이 "빈 결과"에서 "교육·보고·점검·게시 등
  baseline 의무 289건"으로 전환.
→ 소방·승강기 EXISTS는 여전히 HOLD이나,
  일반 안전관리 의무는 채워짐.
```

### 발견 2: 스키마가 UNIVERSAL을 이미 설계

```
condition_type='NONE' + null_condition_class='A_UNIVERSAL'
+ input_field nullable이 제약조건에 이미 존재.

→ 운영 테이블이 처음부터 3-class 구조 설계:
  A_UNIVERSAL (입력무관) / B_HIDDEN_COND / C_OUT_OF_SCOPE
→ UNIVERSAL 적재가 스키마와 정합.
```

### 발견 3: 입력 없는 의무의 적재 방식 확립

```
EXISTS: input_field='has_*' + input_value='true'
UNIVERSAL: input_field=NULL + sector만

→ 엔진 조회 분기:
  EXISTS → "입력값 매칭"
  UNIVERSAL → "sector 매칭만"
→ 두 경로가 cmc 한 테이블에서 condition_type로 구분.
```

### 발견 4: 공통 의무가 다수 (214/310 = 69%)

```
UNIVERSAL의 69%가 sector 무관 전체 공통.
→ 교육·보고·점검·문서 등 모든 사업장 기본 의무.
→ 어느 sector든 최소 214건 baseline 보장.
→ 진단의 "기본 뼈대" 역할 확인.
```

---

## 성공 기준 답변

```
condition_mapping_candidate에 TRUE_UNIVERSAL baseline이
HARVESTED 상태로 추가됐는가?

✅ 310건 추가 (condition_type='NONE', A_UNIVERSAL).
✅ 엔진은 이제 sector baseline + EXISTS 특화를 동시 조회 가능.

엔진 조회 결과 (예상):
  제조업: baseline 226 + EXISTS 특화(welding/crane/chemical 등)
  건설업: baseline 223 + EXISTS 특화(excavation/scaffold 등)
  건물:   baseline 289 + EXISTS 특화(석면/밀폐/보일러)
```

---

## 다음 단계

```
WO-HARVEST-TO-ASSET-002 (현재) — 완료. UNIVERSAL 310 적재.
      ↓
WO-CANDIDATE-REVIEW-002
  UNIVERSAL 310 REVIEW → CONFIRMED 승격
  - sector 귀속 적합성 검증
  - DETAIL 정제 (GENERAL → 구체 의미)
  - HIDDEN_COND 의심분 재분류 (HIERARCHY-001의 285건 경고)
      ↓
WO-APPENDIX-HARVEST-001
  THRESHOLD 보강 (worker_count 50인 등)
      ↓
엔진 재검증: baseline + EXISTS 통합 출력 확인
```

---

## 주의: UNIVERSAL REVIEW 필요성

```
HIERARCHY-001 경고: UNIVERSAL 644 중 285건이
action_text에 숨은 조건 보유(HIDDEN_ACTIVITY/THRESHOLD).

이번 310건은 "action_text에 숨은조건 없음" 필터로 추출됐으나,
REVIEW에서 재확인 필요:
  - 진짜 무조건인가
  - sector 귀속이 맞는가
  - BUILDING 75건에 소방·승강기 HOLD 법령이 섞였는가

→ 현재 HARVESTED 상태로 보류. CONFIRMED 전 검증.
```

---

*WO-HARVEST-TO-ASSET-002 완료. TRUE_UNIVERSAL 310 적재.*
*cmc: CONFIRMED 452 + HARVESTED 310(UNIVERSAL) + REJECTED 35 = 797.*
*핵심: 건물 baseline 0→289 획득. condition_type='NONE'+A_UNIVERSAL. 스키마 정합.*
