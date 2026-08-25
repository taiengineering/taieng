# WP-PERSISTENCE-02A STEP-2 — MAPPING REVIEW MATRIX

- 작성일: 2026-08-25
- 성격: schema 승인 후보(§13) 기준 inspection_set 그룹별 매핑 검토표.
- 방식: DB SELECT only. bridge UPDATE 금지.

---

## 0. 전제 — 매핑 검토가 성립하지 않는다

지시서 §13 은 "schema 승인후보가 나온 뒤 inspection_set 그룹별 매핑표"를 만들라고
한다. 그러나 SCHEMA_CANDIDATE_AUDIT 결과 **APPROVE_CANDIDATE = 0**(승인 가능한
점검결과 schema 없음)이다. 연결할 대상 schema 가 없으므로 proposed_schema_id 를
채우는 것은 곧 추론이 되어 금지(§4·§14).

따라서 이 표는 "어느 set 에 어느 schema" 를 제안하지 않는다. 대신 **inspection_set 을
legal_rule_id 단위로 묶어, 각 그룹이 향후 어떤 결정 경로로 갈지**를 분류한다.

## 1. 매핑 검토 단위 (지시서 §12)

- 단위 = **legal_rule_id** (distinct ≈ 151종). 324 set 을 개별로 보지 않는다.
- legal_rule_id 그룹핑은 **검토 효율화 수단**이며, legal_rule_id → schema 자동매핑이
  아니다(§12). 동일 legal_rule 하위 set 들은 같은 문서정책을 공유할 개연성이 있어
  사람이 그룹 단위로 한 번 결정하면 다수 set 에 적용 가능.

## 2. 그룹별 decision 분류 규칙 (§13 decision 값)

각 legal_rule_id 그룹은 향후 다음 중 하나로 간다. 이번 STEP 에서는 **어느 그룹도
MAPPING_CANDIDATE 로 확정하지 않는다**(연결 schema 부재):

| decision | 조건 | 이번 STEP 배정 |
|---|---|---|
| MAPPING_CANDIDATE | 적합 승인 schema 존재 + 사람 승인 | **0 그룹** (승인 schema 없음) |
| CURRENTLY_NO_APPROVED_RESULT_SCHEMA | 점검결과 문서 필요, 현재 승인 schema 없음 | 대다수(점검·작업전, 316건) |
| DOCUMENT_NOT_REQUIRED | 점검 완료에 runtime document 불필요 | 일부(운영자 판단) |
| NEEDS_HUMAN_REVIEW | 아직 미결정 | 나머지 |

주: CURRENTLY_NO_APPROVED_RESULT_SCHEMA 는 "각 set 에 개별 신규 양식 필요"가 아니라
"현재 승인된 결과 schema 가 없음"이다. GENERAL schema 1종 공유로 다수 해소 가능.

## 3. 매핑 검토표 (그룹 → 경로, proposed_schema 는 공란)

proposed_schema_id / proposed_form_code 는 **의도적으로 비운다**(승인 schema 0).
아래는 obligation_type 분포로 본 그룹 성격과 예상 경로다(집계는 STEP-1 실측 기반).

| 그룹 축(obligation_type) | inspection_set_count | proposed_schema_id | decision(예상) | note |
|---|---:|---|---|---|
| BEFORE_WORK (작업 전 점검) | 188 | (없음) | CURRENTLY_NO_APPROVED_RESULT_SCHEMA | BW-* 빈 스텁 → GENERAL schema 공유 또는 신규 설계 대상 |
| INSPECT (정기/자체 점검) | 128 | (없음) | CURRENTLY_NO_APPROVED_RESULT_SCHEMA | INSPECT-* 빈 스텁, STD field_key NULL → GENERAL schema 공유 또는 신규 |
| REPORT / NOTIFY / APPOINT | 4 | (없음) | NEEDS_HUMAN_REVIEW | 신고·선임 계열, 점검결과 문서와 성격 다름 |
| ACTION / DOCUMENT / OTHER | 4 | (없음) | NEEDS_HUMAN_REVIEW / DOCUMENT_NOT_REQUIRED | 개별 판단 |

(합계 188+128+4+4 = 324. STEP-1 obligation_type 실측 분포와 일치.)

## 4. 이 표가 뜻하는 것

- 324 set 중 절대다수(BEFORE_WORK 188 + INSPECT 128 = **316건**)는 **현재 승인 가능한
  runtime result schema 가 없다**(CURRENTLY_NO_APPROVED_RESULT_SCHEMA). 이는 "316개
  각각에 신규 문서양식이 필요하다"는 뜻이 **아니다.** 하나의 범용 GENERAL schema 가
  여러 inspection_set 을 명시적으로 공유할 수 있으므로, 실제 신규 설계량은 훨씬 적을
  수 있다(STEP-3 에서 공유 조건 확정).
- 나머지 8건(REPORT/NOTIFY/APPOINT/ACTION/DOCUMENT/OTHER)은 점검결과 문서화 대상인지
  자체가 운영자 판단(NEEDS_HUMAN_REVIEW / DOCUMENT_NOT_REQUIRED).
- 어느 그룹도 지금 bridge 에 넣을 값을 갖지 못한다 → B1 DATA POPULATION BLOCKED,
  blocker 성격이 "매핑 미정"에서 "승인된 결과 schema 부재"로 구체화됐다.

## 5. 경계

- 이번 STEP 에서 bridge UPDATE 없음. proposed_schema 자동 지정 없음.
- legal_rule_id 그룹핑은 효율화 수단일 뿐 자동매핑 아님(§12).
- 개별 legal_rule_id 151종 그룹의 정밀 decision 은 승인 schema 가 마련된 뒤
  (또는 신규 schema 설계 후) 사람이 그룹 단위로 확정한다.
