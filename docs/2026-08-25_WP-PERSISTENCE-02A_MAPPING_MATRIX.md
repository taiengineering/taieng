# WP-PERSISTENCE-02A STEP-1 — MAPPING MATRIX

- 작성일: 2026-08-25
- 모드: READ-ONLY MAPPING DESIGN / APPROVAL PREPARATION (DB SELECT only, mutation 0)
- BASELINE tai-api@`2b10e3a6` / REVIEW-TIME main@`2780acf8` (relevant diff 0)
- DB: `vwlahtguyggrhvslabax`

---

## 0. 집계 (지시서 §18·§27)

```
TOTAL INSPECTION SETS      = 324
RUNTIME FORM SCHEMAS        = 323 (status = CANDIDATE 전건)

MAPPING CLASSIFICATION
AUTO_APPROVABLE            = 0
HUMAN_REVIEW               = 324
UNMAPPED                   = 0   (주: schema pool 은 존재하므로 "schema 없음" 아님)
CONFLICT                   = 0

합계 검증: 0 + 324 + 0 + 0 = 324  ✓ (일치)

SCHEMA RUNTIME ELIGIBILITY (323 candidate)
RECOMMEND APPROVE_FOR_RUNTIME_USE = 0
NEEDS_HUMAN_REVIEW                = 323
NOT_USED                          = 0 (이번 STEP 미판정 — 매핑 미확정이므로 사용 여부 결정 불가)
```

---

## 1. 핵심 판정 — AUTO_APPROVABLE = 0 (exact key 부재)

STEP 3(공통 KEY 탐색) 결과, inspection_set 과 runtime_form_schema 사이에
**exact / structural canonical key 가 존재하지 않는다.** 따라서 지시서 §9 의
AUTO_APPROVABLE 6조건 중 1번(exact structural evidence)부터 충족 불가.
→ E1/E2 등급 매핑 0건 → AUTO_APPROVABLE 0건.

근거는 MAPPING_EVIDENCE 참조. 요지:
- inspection_set 원천 축 = **법령규칙**(legal_rule_id 예: `AIRACT-002`, 315/324, 151종)
- runtime_form_schema 원천 축 = **2계열**:
  - document_forms 260건 (doc_id populated / form_code NULL)
  - document_form_master 63건 (form_code populated / doc_id NULL)
- 두 축을 잇는 exact key 부재:
  - document_forms 계열 접점 = law_ref(자유텍스트) ↔ legal_rule_id → E4(§3 금지)
  - document_form_master 계열 form_code 63건 ↔ inspection_set_code / legal_rule_id /
    legal_rule_code exact 비교 = **전건 0**. template_id ↔ schema.source_id = 0.
  - work_schedules.form_code(현행/old/snapshot 전부 0/66), canonical mapping record
    (DB/live code) 부재.
→ E1(DIRECT IDENTITY)=0, E2(STRUCTURAL EXACT)=0 → AUTO_APPROVABLE=0.

## 2. 왜 전건 HUMAN_REVIEW 이고 UNMAPPED 가 아닌가

- UNMAPPED(지시서 §11)는 "schema 없음 / 대응 문서 자체가 없음 / 이름 유사성밖에 없음"
  을 포함한다.
- 그러나 현재는 **schema pool(323건)이 존재**하고, 상당수 inspection_set 은
  같은 법령 계열의 문서서식이 pool 안에 있을 개연성이 있다(예: 소방 점검 ↔ 소방
  점검결과보고서). 다만 그 연결을 **자동으로 확정할 exact key 가 없을 뿐**이다.
- 이 상황에서 개별 set 을 "UNMAPPED(대응 없음)"로 단정하는 것 자체가 또 하나의
  추론이 된다(없음을 증명하려면 텍스트 판단이 필요 → §3 위반).
- 따라서 정직한 분류 = **전건 HUMAN_REVIEW**: "exact key 는 없으나 pool 에 후보가
  있을 수 있어 사람이 판단해야 함". 사람 검토 과정에서 일부는 UNMAPPED /
  NEW_FORM_REQUIRED 로 확정될 것이다(그 판정은 사람 몫, 이번 STEP 아님).

## 3. MATRIX (지시서 §17 형식) — 대표 행 + 규칙

324행 전량을 개별 나열하는 것은 (a) exact 후보가 없어 candidate_schema_id 를
채울 수 없고(채우면 추론), (b) Markdown 부적절하므로, **규칙 기반 요약 + 표본**
으로 제출한다. 개별 candidate 확정은 사람 검토 입력이 있어야 가능.

| 분류 규칙 | inspection_set 조건 | candidate_schema_id | evidence_grade | mapping_decision | schema_runtime_decision |
|---|---|---|---|---|---|
| R1 전건 | legal_rule_id 축 존재(315) 또는 부재(9) 무관 | (미정 — exact 후보 없음) | E4/E0 | HUMAN_REVIEW | NEEDS_HUMAN_REVIEW |

- candidate_schema_id 는 exact key 부재로 **어떤 값도 자동 지정하지 않는다**
  (지시서 §3·§9 준수). 후보 제시는 사람 검토 단계에서 근거와 함께 이뤄져야 한다.
- candidate_count = 0 (exact 기준). 텍스트 근접 후보는 근거 등급 E4 라 자동 후보로
  세지 않는다.

## 4. 분류 합계 재확인

```
324 inspection_set 전건 → HUMAN_REVIEW
합계 = 324 = TOTAL  ✓
AUTO_APPROVABLE 0 / UNMAPPED 0 / CONFLICT 0
```

CONFLICT 0 근거: 애초에 exact direct mapping 이 0 이므로 "서로 다른 direct 근거
충돌"이 발생할 수 없다(지시서 §12). CONFLICT 표 = 해당 없음(빈 표).

## 5. STOP CONDITION 충족 (지시서 §26)

다음 두 STOP 조건이 실측으로 충족됨:
- "exact source key 가 존재하지 않음" ✓
- "대부분 name/text match 밖에 없음" ✓
→ STOP 은 실패가 아니라 정상. 전건을 HUMAN_REVIEW 로 남긴다.
→ 이번 STEP 에서 어떤 자동 매핑도 생성하지 않는다.
