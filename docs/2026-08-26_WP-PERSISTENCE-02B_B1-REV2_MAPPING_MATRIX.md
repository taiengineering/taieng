# WP-PERSISTENCE-02B B1 REV-2 — MAPPING MATRIX

- 상태: **CORRECTED / PENDING GPT VERIFICATION**
- 모드: artifact correction only
- 생성일: 2026-08-26
- 소스: production Supabase `vwlahtguyggrhvslabax` (SELECT-only 재접지) + GitHub remote 실측
- **부모 정본: `01d4519b1b6cc6a90b71eacd193b47bb5837d0e2`** (WP-PERSISTENCE-02B STEP-0 ARCHITECTURE REBASE, SEALED). B1은 STEP-0을 직접 상속. (REV-1의 "909bb825" 표기 폐기.)

```
DB MUTATION     = 0
CODE MUTATION   = 0
BRIDGE UPDATE   = 0
DEPLOY          = 0
REPO COMMIT     = 0
COMMIT AUTHORIZATION = NOT GRANTED
MAPPING MUTATION     = NOT GRANTED
```

## 0. STEP-0 SEALED 아키텍처 (재확인, 재개방 대상 아님)

- `runtime_inspection_bridge` = inspection_set → presentation schema **explicit resolution SoT**. 새 mapping table 없음.
- GENERAL presentation schema = **이미 생성·승인 완료** (`GEN-INSPECT-RESULT-001`, uuid `dc79ac3c-388c-42dc-b029-3dd9bda54a47`, status `APPROVED_FOR_RUNTIME_USE`, live 재확인).
- B1의 유일한 schema target = 위 GENERAL schema. mapping 목적 = document form 탐색이 **아니라** approved GENERAL presentation schema 연결 자격 심사.
- invariant: set당 active 0..1 / APPROVED_FOR_RUNTIME_USE만 / fallback·LLM inference 금지 / mapping 자체 side effect 0.

## 1. 모집단 (live 재실측)

| 항목 | 값 |
|---|---|
| inspection_sets | 327 (전건 is_active) |
| runtime_inspection_bridge | 324 |
| bridge_with_schema (runtime_form_schema_id NOT NULL) | 0 |
| safety_inspections / results | 2 / 8 |
| item_count = 0 / = 16 | 3 / 324 |
| set까지 추적 가능한 result 보유 | 1 |

불변식: **bridged ⟺ item_count=16** (324 일치) · result sample 추적 가능 set = 1 (`7fee7518`) · current_schema_id 전건 NULL(=bridge 미바인딩. 바인딩은 mutation이라 미승인 상태에서 NULL이 정상).

## 2. B1 HUMAN REVIEW = COMPLETE (판정)

| decision | reason_code | n |
|---|---|---|
| ELIGIBLE | ELIGIBLE_RESULT_SAMPLE_MULTIROW | 1 |
| NON_ELIGIBLE | NON_INSPECTION_OBLIGATION | 2 |
| EXCEPTION | EXCEPTION_SOURCE_MISMATCH | 1 |
| EXCEPTION | EXCEPTION_NO_RESULT_SAMPLE | 323 |

```
TOTAL                    = 327
ELIGIBLE                 = 1     (7fee7518 소방시설공사업법 점검)
NON_ELIGIBLE             = 2     (a41f5ac7 APPOINT, 61b6e5c9 REPORT)
EXCEPTION                = 324   (SOURCE_MISMATCH 1 + NO_RESULT_SAMPLE 323)
DUPLICATE / UNCOVERED    = 0 / 0

GENERAL MAPPING PROPOSED = 1     (ELIGIBLE → dc79ac3c, proposal only)
MAPPING MUTATION APPROVED= 0
```

상태 해석:
- **HUMAN REVIEW 완료**. "324 전건 HUMAN_REVIEW 대기" 표현 폐기.
- 323 EXCEPTION_NO_RESULT_SAMPLE = mapping candidate **확정 아님**. 추가 evidence(result sample) 없이는 **UNRESOLVED**.
- EXCEPTION_SOURCE_MISMATCH 1 = 별도 source-data investigation 대상.
- AUTO_APPROVABLE = 0 은 "자동추론 mapping 금지"라는 역사적 사실로만 유지. 심사 자체는 human이 수행 완료.

## 3. proposed vs mutation (REV-1 계약 위반 정정)

`proposed_schema_id`와 `mutation_authorized`는 별개 개념. ELIGIBLE 1건에 GENERAL UUID를 **제안**하되 DB 반영은 없음:

```
7fee7518-0e77-445c-b822-d5178d069b3c
  proposed_schema_id  = dc79ac3c-388c-42dc-b029-3dd9bda54a47
  mutation_authorized = NO
나머지 326건: proposed_schema_id blank
검증: proposed_schema_id non-null = 1 · mutation_authorized=NO = 327
```

## 4. REV-1 → REV-2 정정 (STEP-0 회귀 복원)

1. parent baseline 909bb825 → **01d4519b** (STEP-0 SEALED). remote HEAD 실측 확인.
2. SCHEMA_RUNTIME_APPROVAL: "NOT GRANTED/deferred" 삭제 → GENERAL schema **ALREADY GRANTED/SEALED**(02A STEP-4D). B1은 schema 승인 재개방 안 함.
3. CSV proposed_schema_id: ELIGIBLE → GENERAL UUID (mutation NO 유지).
4. BLOCKER_DECISION: 새 mapping table/새 schema/323 candidate 승인/canonical-key-blocker 서술 전면 삭제. bridge=SoT, target=GEN-INSPECT-RESULT-001로 정정. B1 architecture blocker 없음.
5. verdict: "HUMAN REVIEW 대기" → **COMPLETE**, GENERAL MAPPING PROPOSED=1.
- 유지(REV-1 정확분): photo 0/8, FLAG-6 해소(set_item_id identity 보존), SOURCE_MISMATCH 재분류, PROVEN=multi_row fit / UNPROVEN=top-level source binding(Composer), 15컬럼 계약.

## 5. 무결성 증명

```
Python MD5_ID     = 9113e294cf7a86aaea81ab91b5186df0
Postgres MD5_ID   = 9113e294cf7a86aaea81ab91b5186df0   MATCH
Python MD5_TRIPLE = 39422b8ec3995cde7b40a574340b9a9f
Postgres MD5_TRIPLE=39422b8ec3995cde7b40a574340b9a9f   MATCH
```
327행 (id+name+category) production과 byte 동일. GENERAL schema uuid·status와 remote HEAD도 live 재확인(EVIDENCE E8/E9).

## 6. 산출물 / NEXT

- `B1_REV2_mapping_review_327.csv` (15컬럼 × 327행)
- MAPPING_EVIDENCE / SCHEMA_RUNTIME_APPROVAL / BLOCKER_DECISION (REV-2)
- NEXT = GPT 검증 → 이후 ELIGIBLE 1건 explicit mapping mutation 승인 여부 판단. commit·bridge UPDATE·composer 착수 금지.
