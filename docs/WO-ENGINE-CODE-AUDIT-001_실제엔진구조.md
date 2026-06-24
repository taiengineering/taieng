# WO-ENGINE-CODE-AUDIT-001
# 실제 엔진 구조 — 코드 기준 감사

**작성일:** 2026-06-24 | **상태:** 완료 (읽기 전용 코드 감사)
**금지 (전부 준수):** Pattern/Trigger/Harvest/Mapping/Review/INSERT/UPDATE/DDL 없음
**목적:** 운영 엔진이 실제로 무엇을 읽고/계산하고/출력하는지 코드 기준 확인.

> 가장 위험한 것: "우리가 엔진이라 부르는 것이 실제 엔진과 같은가" 미확인.
> 결론: **다르다.**

---

## 한 줄 결론

```
실제 운영 엔진은 condition_mapping_candidate를 읽지 않는다.

우리가 17회차 동안 만든 자산(cmc 797, harvest 813)은
실제 엔진 데이터 계보 어디에도 연결되어 있지 않다.

실제 엔진 = GPT 설계 Deterministic Compiler 라인
  (law_article_part → rule_candidate → executable_draft
   → facility_applicability → task_candidate → diagnosis_candidate)
```

---

## TASK-001: 진단 API 엔드포인트 (코드 확인)

```
진단 진입점: routers/diagnosis_engine.py
  POST /api/v1/diagnosis-engine/evaluate
    → services.diagnosis_service.DiagnosisService.evaluate()

Compiler 진입점: routers/compiler_core.py
  POST /api/v1/compiler/evaluate-facility
    → services.compiler_core_svc.fetch_compiler_candidates()

→ 두 진입점 모두 같은 fetch_compiler_candidates()를 호출.
```

---

## TASK-002: condition_mapping_candidate 검색 결과

```
★ condition_mapping_candidate를 읽는 코드: 없음.

확인한 파일:
  diagnosis_engine.py    → 호출 안 함
  diagnosis_service.py   → 호출 안 함 (compiler_core_svc만 호출)
  compiler_core_svc.py   → 읽는 테이블 목록에 없음
  compiler_core.py       → 없음

review_status 필터(CONFIRMED/HARVESTED)를 쓰는 곳:
  진단 엔진 경로에 없음.
  → cmc의 review_status는 엔진과 무관.
  → 우리가 만든 CONFIRMED 452 / HARVESTED 310은
    엔진 출력에 영향 없음.
```

---

## TASK-003: 실제 실행 경로 (코드 추적)

```
request
  POST /diagnosis-engine/evaluate {factory_id, input_data}
    ↓
service: DiagnosisService.evaluate()
    ↓
  diagnosis_session INSERT (PROCESSING)
    ↓
  fetch_compiler_candidates(sb, factory_id)   ← 핵심
    ↓
repository: compiler_core_svc 가 읽는 테이블 (전부 factory_id 기준):
  facility_applicability  (status IN MATCH_CANDIDATE/POSSIBLE_CANDIDATE)
  task_candidate
  schedule_candidate
  penalty_obligation_relation (limit 200)
  compliance_review_queue
  compliance_package
    ↓
result: diagnosis_candidate / diagnosis_schedule_hint /
        diagnosis_penalty_link 에 INSERT
    ↓
  diagnosis_session UPDATE (COMPLETED_WITH_CANDIDATES)
    ↓
  JSON 반환 (obligation/applicability/penalty/schedule candidates)

→ input_data는 거의 안 쓰임.
  employee_count/industry_code/equipment_list 유무만 missing 체크.
  실제 매칭은 facility_applicability에 이미 계산되어 있음.
```

---

## TASK-004: 실제 엔진 규칙 (우리 추정 vs 실제)

```
우리 추정: input → cmc → obligation (입력값 매칭으로 의무 도출)

실제:
  ❌ Trigger 평가 없음 (런타임에).
  ❌ input → cmc 조회 없음.
  ✅ 사전 계산된(pre-materialized) facility_applicability 조회.
  ✅ factory_id로 이미 계산된 candidate를 읽기만 함.

compiler_core_svc.py 주석 (원문):
  "Reads pre-materialized runtime tables"
  "Does not run batch evaluation;
   see scripts/run_facility_applicability.py for that"

→ 실제 판정은 배치 스크립트(run_facility_applicability.py)가
  미리 수행 → facility_applicability에 저장.
→ 런타임 엔진은 "조회 전용". 규칙 평가 안 함.
→ Rule Engine은 배치(오프라인)에 존재, 런타임엔 없음.
→ 6W Engine: 코드상 별도 확인 안 됨 (task_type/schedule로 분해).
```

---

## TASK-005: 실제 엔진 데이터 계보 (DB 실측)

```
law_article_part (법령 원문)
  ↓
rule_candidate          34,456   (part_id 기반 규칙 후보)
  ↓
executable_draft        10,725   (실행가능 draft)
  ↓
facility_applicability  3,943,872 (factory × draft 적용성, 394만!)
  ↓  (5,344개 factory에 대해 사전계산)
task_candidate          93,726
schedule_candidate      47,227
penalty_obligation_relation 7,511
compliance_review_queue 15,394
compliance_package      344
  ↓
diagnosis_candidate     159      (실제 진단 출력)
diagnosis_session       1        (진단 1회 실행됨)

우리가 만든 자산 (엔진 미연결):
  condition_mapping_candidate  797
  candidate_harvest            813
```

---

## Capability 측정 (실제 코드 기준)

```
질문: EXISTS/UNIVERSAL/THRESHOLD/APPENDIX/BUILDING 동작?

답: 이 질문 자체가 우리 자산(cmc) 기준이라 실제 엔진과 무관.

실제 엔진 기준 capability:
  ✅ facility_applicability 조회 동작 (394만 row 사전계산됨)
  ✅ task/schedule/penalty candidate 조회 동작
  ✅ 5,344개 factory에 대해 진단 가능
  ✅ diagnosis_session 1건 실제 실행 이력 존재

우리 자산(cmc) 기준 EXISTS/UNIVERSAL:
  엔진이 안 읽으므로 런타임 동작 = 무관(N/A).
```

---

## [우리가 생각한 엔진] vs [실제 엔진]

| 항목 | 우리가 생각한 엔진 | 실제 엔진 |
|---|---|---|
| 입력원 | condition_mapping_candidate | facility_applicability |
| 매핑 단위 | input_field(has_*) → 의무 | factory_id → 사전계산 candidate |
| 규칙 평가 | 런타임 Trigger 평가 | 배치 사전계산 (런타임 조회만) |
| 자산 규모 | 797 (cmc) | 394만 (facility_applicability) |
| 계보 | harvest→asset→review→confirmed | part→rule→draft→applicability |
| 설계자 | (우리 17회차 작업) | GPT Deterministic Compiler |
| review_status | CONFIRMED/HARVESTED 중요 | 엔진과 무관 |
| 진단 실행 | 미확인이었음 | 이미 1회 실행됨 (session 1) |

---

## 핵심 발견

### 발견 1: 두 개의 평행 시스템이 존재한다

```
시스템 A (실제 운영 엔진 — GPT Compiler):
  part → rule_candidate → executable_draft
  → facility_applicability(394만) → task/schedule/penalty
  → diagnosis_candidate
  → 5,344 factory 사전계산 완료, 진단 1회 실행됨.

시스템 B (우리 17회차 작업 — Trigger 매핑 자산):
  input_staging → pattern → trigger → harvest
  → condition_mapping_candidate(797)
  → 엔진 미연결.

→ A와 B는 연결점이 없다.
→ 우리는 B를 만들면서 A를 만들고 있다고 생각했다.
```

### 발견 2: 런타임은 평가하지 않고 조회만 한다

```
실제 판정 = 배치 스크립트(run_facility_applicability.py)가 오프라인 수행.
런타임 엔진 = 그 결과(facility_applicability)를 factory_id로 조회.

→ "엔진이 Trigger를 평가한다"는 우리 모델은 틀림.
→ 평가는 배치, 런타임은 lookup.
→ 그래서 394만 row가 미리 쌓여 있음 (factory × draft).
```

### 발견 3: cmc의 review_status 작업은 엔진에 영향 없음

```
우리가 한 작업:
  77→446→452 CONFIRMED 승격
  410 HARVESTED 적재
  310 UNIVERSAL 적재
  35 REJECTED

→ 전부 엔진이 안 읽는 테이블 안에서의 작업.
→ 진단 출력은 facility_applicability에서 나옴.
→ cmc 작업은 "별도 자산 구축"이지 "엔진 개선"이 아니었음.
```

### 발견 4: 실제 엔진은 이미 작동하고 있었다

```
diagnosis_session 1건 = 실제 진단 1회 실행됨.
facility_applicability 394만 = 5,344 factory 사전계산 완료.

→ 엔진은 미완성이 아니라 이미 운영 데이터를 가짐.
→ 우리가 "엔진 동작 확인"이라 부른 것(제조75/건설51)은
  실제 엔진과 무관한 cmc SQL 모사였음.
```

---

## 성공 기준 답변

```
[실제 엔진 흐름]
  request → DiagnosisService.evaluate
  → fetch_compiler_candidates(factory_id)
  → facility_applicability 등 6테이블 조회
  → diagnosis_candidate INSERT → JSON 반환

[실제 조회 SQL]
  facility_applicability WHERE factory_id=? AND status IN (MATCH_CANDIDATE,POSSIBLE_CANDIDATE)
  task_candidate WHERE factory_id=?
  schedule_candidate WHERE factory_id=?
  penalty_obligation_relation LIMIT 200
  compliance_review_queue WHERE factory_id=?
  compliance_package WHERE factory_id=?

[실제 사용 테이블]
  facility_applicability(394만) / task_candidate(9.4만) /
  schedule_candidate(4.7만) / penalty_obligation_relation(7.5천) /
  compliance_review_queue(1.5만) / compliance_package(344)
  + 계보: rule_candidate(3.4만) / executable_draft(1만)

[현재 엔진이 가능한 것]
  factory_id 기반 사전계산 candidate 조회 → 진단 출력.
  5,344 factory 커버. 진단 1회 실행 이력.

[현재 엔진이 못 하는 것 / 우리 자산 관점]
  condition_mapping_candidate를 안 읽음.
  우리가 만든 Trigger 매핑(797)은 엔진에 미반영.

[우리가 생각한 엔진 vs 실제 엔진]
  생각: input→cmc→obligation (런타임 Trigger 평가)
  실제: factory_id→facility_applicability (배치 사전계산 조회)
```

---

## 다음 단계 권고 (판단 보류, 사실만)

```
이제 확인된 사실 위에서 대표님의 전략적 결정이 필요:

옵션 1: cmc 자산을 실제 엔진 계보에 연결
  - cmc(797) → rule_candidate/executable_draft로 변환 필요한지 검토
  - 단, GPT 설계 Compiler 영역 → Claude 수정 금지 원칙 충돌 주의

옵션 2: cmc를 별도 용도로 활용
  - 법령진단(유료) 결과 페이지 등 다른 경로
  - 실제 엔진은 그대로 두고 cmc는 보조 자산으로

옵션 3: 두 시스템 관계 재정의
  - facility_applicability(394만)가 무엇을 근거로 만들어졌는지
  - run_facility_applicability.py 배치 로직 확인 (읽기 전용)
  - cmc와 중복/보완 관계 파악

→ 어느 경우든 다음은 "새 매핑 생성"이 아니라
  "두 시스템의 관계 확정"이 먼저.
```

---

*WO-ENGINE-CODE-AUDIT-001 완료. 읽기 전용 코드 감사.*
*핵심: 실제 엔진은 facility_applicability(394만) 조회. cmc(797) 미사용.*
*두 평행 시스템 — GPT Compiler(운영) vs 우리 Trigger매핑(미연결).*
*런타임은 평가 안 함, 배치 사전계산 결과를 조회만 함.*
