# GPT 질의 — Phase 3 WO 설계 요청

**작성일**: 2026-06-17  
**용도**: 16차 Phase 2 완료 후 GPT엔게 전달

---

## 한 문장 요약

> Phase 3은 C1 평가기에 업종 매칭 필터를 추가하여 오판정을 없애는 작업이다. 실제로 해당되는 업종 조건만 MATCH로 넘기는 것이 목표다.

---

## Phase 2 완료 상태

**Phase 2 SC 전체 PASS:**
- SC-01: ApplicabilityCondition 7건 생성 ✅
- SC-02~04: 화성 제2공장 REQUIRED 1명, pilot 100% 일치 ✅
- SC-05~06: UNKNOWN 보존, 빈 사업장 전체 UNKNOWN ✅

---

## Phase 2에서 발견된 문제

**오판정 발견:**

화성 제2공장 (INDUSTRIAL, C28 전기장비 제조업, 280명) 평가 시 7건 중 4건이 MATCH:

```
토사석 광업(071)        ≥0 50명 → MATCH  ❌ (제조업 C28과 무관)
식료품 제조업 등 고위험   ≥0 50명 → MATCH  ❌ (전기장비 제조업과 다르는 업종)
운수 및 창고업(49~52)    ≥0 50명 → MATCH  ❌ (H49~52는 C28과 다른 업종)
제1호~27호 외의 사업 (일반) ≥0 50명 → MATCH  ✅ (적절 — C28은 일반 조항 해당)
```

**예상 정답 (화성 제2공장 C28 기준):**
```
토사석 광업(071)        → NOT_APPLICABLE (C28 ≠ B071)
식료품 제조업 등 고위험   → NOT_APPLICABLE (C28 ≠ C10/C11)
운수 및 창고업(49~52)    → NOT_APPLICABLE (C28 ≠ H49~H52)
제1호~27호 외의 사업 (일반) → MATCH  (C28은 일반 조항 해당)
```

**원인:**
ApplicabilityCondition에 KSIC 코드 매칭 로직이 없음.
현재 C1 평가기는 `regular_workers` 수치만 비교하고 업종 필터가 없음.

---

## 현재 ApplicabilityCondition 실측

```
industry_name              | threshold | 업종 KSIC 페더
식료품 제조업 등 고위험제조업군 | 50, 500   | C10, C11
운수 및 창고업(49~52)    | 50, 500   | H49, H50, H51, H52
제1호~27호 외의 사업        | 50, 1000  | 모든 업종 (상기 제외)
토사석 광업(071)         | 50        | B071
```

**좌표 요약:**
- `appendix_condition.ksic_code`: null (현재 저장 안 됨)
- `appendix_condition.industry_name`: 텍스트만 있음
- `FacilityProfile.ksic_code`: "C28" (입력값)

---

## GPT엔게 질문

**질문 1. 업종 매칭 설계 방향**

업종별 ApplicabilityCondition에서 FacilityProfile.ksic_code를 필터하는 방법을 판정해주세요.

후보 A: `appendix_condition`에 `ksic_prefix` 코드 목록 케럼 추가
```sql
ALTER TABLE applicability_conditions
ADD COLUMN ksic_prefixes TEXT[];  -- ["C10", "C11"] 또는 NULL(일반 조항)
```
후보 B: C1 평가기에 industry_name 텍스트 매칭 로직 추가
("식료품" 포함 → C10/C11만 허용 등)

후보 C: 배타업종 방식
("제1호~27호 외의 사업" 조만 is_general=true,
나머지는 명시 업종 KSIC 코드로 필터)

어떤 방향이 맞는지, 또는 복수 병행인지 판정해주세요.

---

**질문 2. "제1호~27호 외의 사업" 일반 조항 처리**

"제1호~27할를 제외한 모든 업종"은 C28에 적용됩니다 (정답).
C1 평가기에서 이 일반 조항을 명시 업종 조항과 구분하는 방법을 알려주세요.

다시 말해 C28 사업장에서:
- "토사석 광업(071)" → 평가 건너끄기 (skip)
- "식료품 제조업 등" → 평가 건너끄기 (skip)
- "운수 및 창고업" → 평가 건너끄기 (skip)
- "제1호~27호 외의 사업" → MATCH 대상 (적절)

어떤 구조로 구현해야 하는지 판정해주세요.

---

**질문 3. Phase 3 산출물 정의**

Phase 3에서 생성해야 하는 것과 금지 목록을 확정해주세요.

후보 산출물:
- `applicability_conditions.ksic_prefixes` 코럼 추가
- `applicability_conditions.is_general` boolean 코럼 추가
- C1 평가기 업종 필터 로직 추가
- 화성 제2공장 기준 재평가: 4건 MATCH → 1건 MATCH

---

**질문 4. Phase 3 성공 기준**

Claude가 구현 후 검증 가능한 형태로 작성해주세요.

기대값 예시:
```
SC-01: 화성 제2공장 (C28, 280명)
  MATCH = 1건 ("제1호~27호 외의 사업" 만)
  NOT_APPLICABLE = 3건 (토사석/식료품/운수창고)
  verdict = REQUIRED 1명

SC-02: 토사석 광업 사업장 (B071, 60명)
  토사석 광업 조건 MATCH
  일반 조항 MATCH
  verdict = REQUIRED 1명

SC-03: 식료품 제조업 (C10, 600명)
  식료품 제조업 조건 MATCH (2명 조건)
  verdict = REQUIRED 2명

SC-04: 빈 사업장 (null명)
  전체 7건 UNKNOWN
  verdict = UNKNOWN
```

---

**질문 5. 업종 KSIC 코드 매핑 데이터**

`appendix_condition.industry_name`과 KSIC 코드 매핑 테이블을 제안해주세요.

현재 확인된 매핑:
```
"식료품 제조업, 음료 제조업 등 고위험 제조업군"
  → KSIC prefix: C10, C11, C19, C20, C21, C24
  (산안법 시행령 별표 3 제1호~제17호에 명시된 업종)

"운수 및 창고업(49~52)"
  → KSIC prefix: H49, H50, H51, H52

"토사석 광업(071)"
  → KSIC: B071 (소분류코드)

"제1호~27호 외의 사업"
  → is_general = true (KSIC 코드 제한 없음)
  → 단, 상기 업종에 이미 해당된 KSIC는 제외
```

GPT가 위 매핑을 검토하고 코드 리스트를 확정해주세요.

---

## 절대 금지 (범위 고정)

```
Phase 3 범위 밖:
  안전관리자 외 법령 확장 (보건관리자 등)
  obligation_result 생성
  diagnosis_result 생성
  Registry 구현
  FacilityProfile 수정
  factories 수정
  Track A 수정
  pilot_safety_manager_api 삭제
```

GPT는 WO 설계 문서 수준으로 답변해주세요.

---

## 참고 문서

- Phase 2 WO: `docs/2026-06-17_WO_V4_PHASE2_001.md`
- Phase 1 WO: `docs/2026-06-17_WO_V4_PHASE1_001.md`
- Phase 0A: `docs/2026-06-16_WO_V4_PHASE0_001.md`
- 기획서: `docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md` (v2.1)
