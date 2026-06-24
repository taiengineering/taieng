# WO-MAPPING-ASSET-AUDIT-001
# 매핑 자산 실체화 여부 감사

**작성일:** 2026-06-24 | **상태:** 완료 (읽기 전용 감사)
**선행:** WO-HARVEST-TO-OPERATION-001
**질문:** 현재 813 Harvest는 엔진이 읽을 수 있는 매핑 자산인가?

---

## 답: 아니오 (경우 2)

```
candidate_harvest 813건은 엔진이 읽는 운영 매핑 자산이 아니다.

근거:
  ① 엔진 운영 테이블 = condition_mapping_candidate (여전히 77건)
  ② candidate_harvest = 별도 staging 테이블 (813건, HARVESTED)
  ③ 813건 중 운영 테이블에 반영된 신규 = 0건
     (68개 조문은 기존 77건과 겹치는 것일 뿐, 신규 승격 아님)
  ④ candidate_harvest에 운영 규격 필드 전무
     (condition_code/condition_type/confidence/review_status 없음)

→ 패턴 정의 완료, Trigger 정의 완료, Harvest 완료.
   그러나 운영용 매핑 자산은 아직 미실체화.
→ 다음 단계는 Review가 아니라 Harvest → Mapping Asset 변환.
```

---

## TASK: 3가지 결정적 확인

### 확인 1: 엔진이 읽는 테이블은 무엇인가?

```
엔진 운영 테이블 = condition_mapping_candidate
  현재 행 수: 77 (전부 CONFIRMED)
  → 이 테이블이 Check Engine의 입력원.

candidate_harvest = 수확 staging
  현재 행 수: 813 (전부 HARVESTED)
  → 엔진이 읽지 않는 중간 테이블.

DB 내 뷰/함수 확인:
  condition_mapping_candidate 참조 뷰: 0
  candidate_harvest 참조 뷰: 0
  → 엔진은 애플리케이션(FastAPI)에서 직접 쿼리.
  → 어느 테이블을 쿼리하든 candidate_harvest는 미연결.
```

### 확인 2: 813건이 운영 테이블에 반영됐는가?

```
condition_mapping_candidate: 77건 (변동 없음)
harvest 813건 중 cmc에 이미 있는 조문: 68개

→ 68개는 "신규 승격"이 아님.
  기존 77 CONFIRMED가 이미 쓰던 조문과 겹치는 것.
→ 순수 신규 581 조문(649-68)은 운영 테이블에 0건 반영.
→ Harvest는 운영 라인과 분리되어 있음.
```

### 확인 3: candidate_harvest가 자산 형태인가?

```
운영 규격 필드 존재 여부:
  condition_code     ❌ 없음
  condition_type     ❌ 없음
  condition_source   ❌ 없음
  confidence         ❌ 없음
  review_status      ❌ 없음 (status='HARVESTED'만 있음)
  input_operator     ❌ 없음
  input_value        ❌ 없음

candidate_harvest 보유 필드:
  trigger_l1, trigger_l2, semantic_clause_id,
  input_field, condition_text, action_text,
  harvest_method, scope_status, status, overlap_flag

→ 수확 기록용 필드만 있음.
→ 엔진이 요구하는 condition_code/confidence 등 운영 규격 전무.
→ "매핑 자산"이 아니라 "수확 로그".
```

---

## 현재 상태 정밀 진단

```
[완료된 것]
  입력 패턴 7종          ✅
  법령 Trigger 8종 2계층  ✅
  SCOPE FILTER           ✅
  Harvest 813건          ✅ (단, staging 테이블에만)
  운영 승격 체계 설계     ✅ (WO-HARVEST-TO-OPERATION-001)

[미완성]
  Harvest → 운영 규격 변환  ❌
  condition_mapping_candidate 적재  ❌ (77건 그대로)
  엔진-Harvest 연결        ❌

→ 엔진은 존재하고 77건으로 작동 중.
→ 813건은 엔진 밖에 대기 중.
→ 문제는 엔진이 아니라 "매핑 테이블 실체화".
```

---

## 경우 1 vs 경우 2 판정

| 질문 | 경우 1 (자산화됨) | 경우 2 (미실체화) | 실제 |
|---|---|---|---|
| 엔진이 813을 읽는가? | 예 | 아니오 | **경우 2** |
| 운영 규격 필드 있는가? | 예 | 아니오 | **경우 2** |
| cmc에 반영됐는가? | 예 | 아니오 | **경우 2** |
| 다음 단계 | Review=품질향상 | Harvest→Asset 변환 | **변환** |

```
판정: 경우 2.
  Harvest 813은 중간 staging 테이블에만 존재.
  엔진은 아직 생산라인에 연결 안 됨.
  매핑 테이블 생성(실체화)이 다음 작업.
```

---

## 성공 기준 답변

> 현재 813 Harvest는 엔진이 읽을 수 있는 매핑 자산인가?

```
아니오.

candidate_harvest는:
  ✅ Trigger 연결 완료 (trigger_l1/l2)
  ✅ 조문 연결 완료 (semantic_clause_id)
  ✅ 입력 연결 완료 (input_field, EXISTS 503건)
  ❌ 운영 규격 미보유 (condition_code/confidence/review_status)
  ❌ 운영 테이블 미반영 (cmc 여전히 77)
  ❌ 엔진 미연결

→ "재사용 가능한 매핑 테이블"이 아니라 "수확 결과 로그".
→ 엔진(condition_mapping_candidate, 77건)과 분리됨.
```

---

## 핵심 발견

### 발견 1: Harvest와 운영이 물리적으로 분리

```
candidate_harvest (813) ←연결 없음→ condition_mapping_candidate (77)

→ HARVEST-TO-OPERATION-001에서 "규격"은 정의했으나
  실제 변환/적재는 아직 안 일어남.
→ 규격 문서 ≠ 실체화된 자산.
```

### 발견 2: 운영 규격 변환이 진짜 다음 작업

```
필요한 것:
  1. candidate_harvest.trigger_l1 → condition_type 변환
  2. condition_code 생성 ({type}:{L2}:{세부}:{해시})
  3. confidence 부여
  4. review_status 부여
  5. condition_mapping_candidate로 INSERT

→ 이것이 "Harvest → Mapping Asset 변환".
→ Review(품질)는 그 다음.
```

### 발견 3: 엔진은 이미 완성, 자산만 부족

```
Check Engine은 77건으로 정상 작동 중.
→ 엔진 코드는 문제없음.
→ 813건을 운영 규격으로 변환해 cmc에 넣으면
  즉시 엔진이 813건 기반으로 진단 가능.
→ 병목은 엔진이 아니라 매핑 자산 실체화 한 단계.
```

---

## 다음 단계 (판정 결과 기반)

```
WO-MAPPING-ASSET-AUDIT-001 (현재) — 완료. 판정: 경우 2.
      ↓
WO-HARVEST-TO-MAPPING-ASSET-001 (다음, 변환 작업)
  candidate_harvest 813 → 운영 규격 변환:
    1. EXISTS 501건 우선 (검증된 구조)
    2. trigger_l1 → condition_type 매핑
    3. condition_code 생성
    4. review_status='HARVESTED'로 cmc INSERT
       (CONFIRMED 아님 — REVIEW 전이므로)
    5. 기존 77 CONFIRMED는 무수정 유지
  → 엔진이 읽는 테이블에 813 실체화.
      ↓
WO-CANDIDATE-REVIEW-001
  cmc에 적재된 HARVESTED → 조문 직독 → CONFIRMED 승격.
  (이제 엔진 테이블 안에서 상태 전이)
```

---

## 주의: 변환 시 보존 원칙

```
- 기존 condition_mapping_candidate 77 CONFIRMED 무수정.
- 신규 813은 review_status='HARVESTED'로 적재 (CONFIRMED 아님).
- condition_code 해시는 중복 충돌 방지.
- 변환은 INSERT만, 기존 행 UPDATE 금지.
```

---

*WO-MAPPING-ASSET-AUDIT-001 완료. 읽기 전용 감사.*
*판정: 경우 2 — Harvest는 staging 로그, 운영 자산 미실체화.*
*핵심: 엔진(77건)과 Harvest(813건) 분리. 다음은 Review 아닌 Mapping Asset 변환.*
