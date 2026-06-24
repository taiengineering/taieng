# WO-REALITY-CHECK-001
# 현황 감사 — 실측 vs 추론 구분

**작성일:** 2026-06-24 | **상태:** 완료 (읽기 전용 검증)
**금지 (전부 준수):** 새 Trigger/Pattern/Harvest/Candidate/Mapping 생성 / Review / CONFIRMED 변경 / DDL / INSERT / UPDATE
**핵심 질문:** 우리가 믿는 숫자 중 실제 측정된 것은 무엇이고, 추론으로 굳어진 것은 무엇인가?

> 모든 숫자를 문서 인용 없이 실제 COUNT(*)로 재측정.

---

## [실측값] — 방금 SQL로 확인됨

| 항목 | 실측값 | SQL 근거 |
|---|---|---|
| condition_mapping_candidate 총건수 | **797** | COUNT(*) |
| CONFIRMED | **452** | review_status='CONFIRMED' |
| HARVESTED | **310** | review_status='HARVESTED' |
| REJECTED | **35** | review_status='REJECTED' |
| PENDING | **0** | review_status='PENDING' |
| candidate_harvest 총건수 | **813** | COUNT(*) |
| semantic_clause 총건수 | **58,495** | COUNT(*) |
| appendix_condition 건수 | **7** | COUNT(*) |
| 사업주 대상 조문 (OBL/PROHIB + 사업주/관리주체/도급인) | **1,572** | COUNT(*) |
| BUILDING UNIVERSAL baseline | **289** | condition_type='NONE' + BUILDING |
| BUILDING 전체 자산 | **341** | 'BUILDING'=ANY(sectors) |

---

## [추론값] — 문서엔 있으나 실측과 다르거나 근거 약함

### 1. "사업주 대상 1,381건" → 실측 1,572건

```
문서값: 1,381 (SCOPE FILTER로 191 제외 후 추정)
실측값: 1,572 (raw, executor 필터만)

→ 1,381 = 1,572 - 191(범위밖) 계산값.
→ 191 범위밖 제거는 키워드 추정이었고 cmc에 반영 안 됨.
→ 1,381은 "계산된 추론값", 1,572가 실측.
```

### 2. "APPENDIX_THRESHOLD 102" → 부분 실측, 부분 추론

```
실측 가능 부분:
  OBLIGATION/PROHIBITION 중 별표·대통령령 참조 = 103건 ✅
  (이전 "102"와 거의 일치, 측정 시점차)

추론 부분:
  "이 102건이 THRESHOLD Trigger로 작동한다" = 추론.
  실제 candidate_harvest의 THRESHOLD 수확 = 2건뿐.
  APPENDIX_THRESHOLD 수확 = 0건.

→ "위임 참조 조문 103" = 실측.
→ "APPENDIX_THRESHOLD Trigger 102건 존재" = 추론 (수확 0).
→ appendix_condition 7건이라 실제 임계값 판정 불가.
```

### 3. "DELEGATION 위임 102" → 실측 56건

```
사업주 DELEGATION 전체 = 56건 (실측)
별표 참조 OBLIGATION = 103건 (실측, 다른 기준)

→ 문서의 "위임형 102"는 두 측정의 혼선.
→ DELEGATION role 자체는 56건.
→ 별표 참조 의무문은 103건.
→ 둘은 다른 것. 문서가 뭉뚱그림.
```

---

## [미검증값] — 측정 불가 또는 앱 코드 소관

### 1. "BUILDING baseline 289가 실제 엔진 출력인가?"

```
실측: cmc에 BUILDING UNIVERSAL 289건 존재 ✅
미검증: 엔진이 실제로 289건을 출력하는가?

이유:
  - UNIVERSAL 289건은 전부 review_status='HARVESTED'.
  - UNIVERSAL CONFIRMED = 0건 (실측).
  - 엔진이 HARVESTED를 출력에 포함하는지는
    앱 코드(FastAPI) 소관 — DB로 확인 불가.

→ "289 자산 존재" = 실측.
→ "289 진단 출력" = 미검증 (앱 필터 미확인 + HARVESTED 미승격).
```

### 2. "엔진 실동작 제조 75 / 건설 51"

```
실측: SQL로 cmc 조회 시 그만큼 매칭됨 ✅
미검증: 실제 FastAPI 엔진이 같은 SQL을 쓰는가?

→ VALIDATION-001은 "SQL 재현"이지 "엔진 실행"이 아님.
→ Claude가 엔진 로직을 SQL로 모사한 것.
→ 실제 엔진 코드 실행 결과는 확인 안 됨.
```

---

## TASK-001: 엔진 런타임 경로 (ENGINE_RUNTIME_PATH)

```
1. 엔진이 읽는 테이블:
   condition_mapping_candidate (추정 — 앱 코드 미확인)
   DB 내 뷰/함수 0개 → 앱에서 직접 쿼리.

2. 엔진 실행 SQL:
   DB로 확인 불가 (FastAPI 코드 소관).
   Claude가 모사한 SQL: WHERE review_status=? + input_field + sector.

3. cmc 외 사용 테이블:
   FK로 cmc 참조하는 테이블 0개.
   → cmc가 독립 매핑 테이블.

4. candidate_harvest 실행 경로 연결:
   ❌ 연결 안 됨.
   뷰 0 / 함수 0 / FK 0.
   → candidate_harvest는 순수 staging. 엔진 미연결.
   → 813건은 cmc로 변환된 것만 (410 EXISTS + 310 UNIVERSAL) 의미.
```

---

## TASK-003: WO 출처 감사

| 주장 | 결론 | 근거 SQL | 실측 | 추론 |
|---|---|---|---|---|
| CONFIRMED 452 | 452 | YES | YES | NO |
| HARVESTED 310 | 310 | YES | YES | NO |
| REJECTED 35 | 35 | YES | YES | NO |
| cmc 총 797 | 797 | YES | YES | NO |
| harvest 813 | 813 | YES | YES | NO |
| semantic_clause 58,495 | 58,495 | YES | YES | NO |
| appendix 7 | 7 | YES | YES | NO |
| BUILDING UNIVERSAL 289 | 289 | YES | YES | NO |
| 사업주 1,572 | 1,572 | YES | YES | NO |
| **사업주 1,381** | 1,572 | NO | NO | **YES (계산값)** |
| **APPENDIX_THRESHOLD 102** | 수확 0 | 부분 | 부분 | **YES (Trigger 작동은 추론)** |
| **제조 75 / 건설 51 출력** | SQL재현 | YES(모사) | 부분 | **YES (엔진 실행 아님)** |
| **BUILDING baseline 289 출력** | 자산만 | YES(자산) | 부분 | **YES (출력 미검증)** |

---

## TASK-004: 미해결 질문 답변

```
1. APPENDIX_THRESHOLD 102는 실측인가 추론인가?
   → 추론. "별표 참조 조문 103" 실측은 있으나,
     THRESHOLD Trigger 작동/수확은 0건. appendix 7건 병목.

2. BUILDING baseline 289는 실제 엔진 출력인가 계산값인가?
   → 자산 존재는 실측(289). 엔진 출력은 미검증.
     전부 HARVESTED(미승격), 앱의 HARVESTED 필터 미확인.

3. 사업주 1,381건은 실제 SQL인가 문서 집계인가?
   → 문서 집계(추론). 실측은 1,572.
     1,381 = 1,572 - 191(범위밖 키워드 추정, cmc 미반영).

4. CONFIRMED 452는 현재 DB 상태인가 WO 결과값인가?
   → 현재 DB 상태(실측). COUNT(*)=452 확인.
```

---

## [현재 엔진이 실제로 할 수 있는 것]

```
✅ cmc에 452 CONFIRMED 매핑 존재 (실측).
✅ EXISTS 입력(has_*) → 매핑 조회 가능 (SQL 재현 확인).
✅ REJECTED 35건은 조회 안 됨 (필터 동작 — SQL 확인).
✅ sector별 매핑 분리됨 (COMMON 0, NULL 0).
✅ 762건(CONFIRMED+HARVESTED)이 조회 가능 상태.
```

## [현재 엔진이 아직 못 하는 것]

```
❌ UNIVERSAL baseline 출력 — 전부 HARVESTED, CONFIRMED 0.
   엔진이 HARVESTED를 출력하는지 미확인.
❌ THRESHOLD 판정 — appendix 7건뿐, 수확 0. 50인/75kW 등 미작동.
❌ BUILDING 소방·승강기 — SCOPE HOLD로 미수확.
❌ 실제 FastAPI 엔진 실행 검증 — Claude는 SQL 모사만 했음.
❌ candidate_harvest 813 → 엔진 미연결 (staging 격리).
```

---

## TASK-005: 다음 작업 가능 여부 판정

```
A. 현재 엔진으로 실제 진단 수행 가능?
   부분 가능. EXISTS 452 CONFIRMED는 동작.
   단 UNIVERSAL 미승격, THRESHOLD 없음 → 불완전 진단.

B. 매핑 자산 부족?
   부분. EXISTS는 충분, UNIVERSAL은 미승격, THRESHOLD 부재.

C. THRESHOLD 부족?
   YES. appendix 7건, 수확 0. 가장 큰 공백.

D. BUILDING 자산 부족?
   YES. 소방·승강기 HOLD. baseline만 있음.

E. 실측 검증 먼저 필요?
   ★ YES. 다음 두 가지가 미검증:
     - 실제 FastAPI 엔진이 cmc를 어떻게 쿼리하는가
     - HARVESTED를 출력에 포함하는가
   → 이걸 확인 안 하면 "엔진 동작"은 여전히 추론.
```

---

## 다음 WO 권고

```
1순위: 실제 엔진 코드 확인 (앱 레벨)
  - FastAPI가 cmc를 읽는 쿼리 확인
  - review_status 필터 로직 확인
  - HARVESTED 포함 여부 확인
  → "엔진 동작"을 추론에서 실측으로.

2순위: UNIVERSAL 310 REVIEW → CONFIRMED 승격
  - 현재 baseline이 HARVESTED라 출력 불확실
  - CONFIRMED로 올려야 확실히 동작

보류: THRESHOLD/BUILDING 확장
  - appendix 입력은 별도 큰 작업
  - 엔진 검증 후
```

---

## 핵심 결론

```
실측으로 확인된 것 (믿어도 됨):
  cmc 797 = CONFIRMED 452 + HARVESTED 310 + REJECTED 35
  사업주 의무 1,572 (raw)
  appendix 7
  BUILDING 자산 341

추론으로 굳어진 것 (재확인 필요):
  "사업주 1,381" → 실제 1,572 (191 제거는 미반영 추정)
  "APPENDIX_THRESHOLD 102" → 수확 0 (별표참조 103은 별개)
  "엔진 출력 제조75/건설51" → SQL 모사, 엔진 실행 아님
  "BUILDING baseline 289 출력" → 자산만, HARVESTED 미승격

가장 큰 미검증:
  실제 FastAPI 엔진이 cmc를 어떻게 읽는지 한 번도 확인 안 함.
  지금까지 "엔진 동작"은 전부 Claude의 SQL 재현이었음.
```

---

*WO-REALITY-CHECK-001 완료. 읽기 전용. INSERT/UPDATE/DDL 없음.*
*실측: cmc 797(452/310/35), 사업주 1,572, appendix 7.*
*추론: 사업주 1,381, APPENDIX 102, 엔진 출력 수치, baseline 출력.*
*최대 미검증: 실제 엔진 코드의 cmc 쿼리 방식 — 다음 1순위.*
