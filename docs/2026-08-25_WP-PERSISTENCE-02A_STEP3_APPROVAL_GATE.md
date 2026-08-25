# WP-PERSISTENCE-02A STEP-3 — APPROVAL GATE

- 작성일: 2026-08-25
- 성격: 지시서 §17(G1–G10) + §18(316 공유조건) + §19(제외조건) + §20(false MAPPED).
- 이번 STEP 은 gate 를 **정의**만 한다. 실제 승인/DB 변경 없음.

---

## 1. Schema Approval Gate G1–G10 (지시서 §17)

GENERAL schema 가 APPROVED_FOR_RUNTIME_USE 로 승격되려면 전 항목 PASS 필요.
현재 설계가 각 gate 를 어떻게 충족하는지(설계 레벨 자기점검):

| Gate | 기준 | 설계 충족 |
|---|---|---|
| G1 | 특정 법률 공식서식으로 오인되지 않음 | form_type=CUSTOM, sector=NULL, form_name "범용", 법령 미종속 → 충족 |
| G2 | source_inspection_id anchor 와 충돌 없음 | payload 에 source_inspection_id 미저장, FK anchor 만 truth → 충족 |
| G3 | inspection metadata 표현 가능 | 헤더 필드(subject/inspected_at/title/inspector_display) → 충족 |
| G4 | source result N → inspection_results N lossless | result_id 1:1, count 불변식, silent drop/merge 0 → 충족 |
| G5 | raw result code 보존 | raw_code=result_code 원값, display label 분리 → 충족 |
| G6 | 비고/조치정보 손실 없음 | note(item별, inspection_results[].note) 보존 → 충족 (문서레벨 요약은 v1 미포함) |
| G7 | evidence 연결 가능 | inspection_results[].photo_url/photo_urls 참조 보존 → 충족 |
| G8 | tenant boundary 유지 | factory/company = 서버 chain, 사용자 필드 아님(§12) → 충족 |
| G9 | actor/inspector boundary 유지 | inspector_display(표시) ⊥ created_by(actor), 승격 금지(§11) → 충족 |
| G10 | renderer silent-drop 없음 | 저장 레벨 0; 표 렌더는 ENHANCEMENT_REQUIRED 로 분리(모든 item 출력 요구) → 저장 충족 |

- 설계 레벨에서 G1–G9 = 충족, G10 = 저장 레벨 충족(렌더 표는 후속 조건부).
- **단 실제 APPROVED_FOR_RUNTIME_USE 승격은 사람 승인 행위**이며, 이번 STEP 에서 하지
  않는다(status=CANDIDATE 로만 설계).

---

## 2. 316 inspection_set 공유 조건 (지시서 §18)

```
BEFORE_WORK 188 + INSPECT 128 = 316  (CURRENTLY_NO_APPROVED_RESULT_SCHEMA)
```
GENERAL schema 1종을 316 에 **자동 연결하지 않는다.** 아래 조건 **전부** 만족하는
set 만 향후 bridge 에 GENERAL 을 **명시적으로** mapping:

```
SHARE ELIGIBILITY (AND 조건):
  E1. 수행 결과가 safety_inspection / safety_inspection_results 구조로 저장됨
  E2. 별도 공식 법정서식 자체가 그 결과의 truth 가 아님
  E3. GENERAL document 의 목적이 그 set 에서 "증거 보존"임
  E4. operator 가 explicit mapping 을 승인함
```
- 4개 AND 를 만족하는 set 만 GENERAL 공유 대상. 하나라도 불충족이면 공유 안 함.
- 자동 일괄 매핑 금지. operator explicit 승인이 최종 게이트.

---

## 3. GENERAL mapping 제외 조건 (지시서 §19)

아래에 해당하면 GENERAL 에 **억지 연결하지 않는다**:
```
EXCLUDE:
  X1. 외부 검사기관 발행 성적서가 최종 evidence 인 경우
      (INSPECT-BOIL-001/ELEV-002/WORKEN 계열 — STEP-2 REJECT 근거와 일치)
  X2. 법정 지정양식 자체가 반드시 결과문서인 경우
  X3. safety_inspection 이 단순 workflow trigger 일 뿐 결과문서 생성 대상이 아닌 경우
  X4. 별도 domain-specific runtime schema 가 필요한 경우
```
- 이들은 GENERAL 공유 목록에서 제외. 각자 기존 별도 document flow 유지.

---

## 4. false MAPPED 323건 (지시서 §20)

```
정본 규칙:
  MAPPED = runtime_form_schema_id IS NOT NULL
           AND schema.status = 'APPROVED_FOR_RUNTIME_USE'
현재: false MAPPED 323 (schema_id NULL), true MAPPED 0
```
- 이번 STEP 에서 **교정하지 않는다.** DB UPDATE 0.
- GENERAL schema 승인(APPROVED_FOR_RUNTIME_USE) 이후 별도 APPLY WP 에서:
  1) 전면 false MAPPED → NEEDS_HUMAN_REVIEW,
  2) SHARE ELIGIBILITY 만족 + operator 승인분만 → MAPPED(schema_id 동시 기록).

---

## 5. gate 종합

```
SCHEMA APPROVAL GATE      = DEFINED (G1–G10, 설계 레벨 G1–G9 충족 / G10 저장 충족)
316 SHARING ELIGIBILITY   = RULE DEFINED (E1–E4 AND, operator explicit)
GENERAL EXCLUSION         = RULE DEFINED (X1–X4)
false MAPPED 교정          = APPLY LATER (이번 STEP 미실행)
```
