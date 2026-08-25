# WP-PERSISTENCE-02B B1 REV-2 — MAPPING EVIDENCE

- 상태: CORRECTED / PENDING GPT VERIFICATION
- 소스: production `vwlahtguyggrhvslabax` (SELECT-only) + GitHub remote, 2026-08-26
- 부모 정본: `01d4519b` (STEP-0 SEALED)

## E1. 체인 정의 (스키마 실측)

```
safety_inspection_results.inspection_set_item_id
  → inspection_set_items.id → .inspection_set_id → inspection_sets.id
```
safety_inspections 에 inspection_set_id 컬럼 없음. result→set 추적은 위 체인이 유일.

## E2. photo evidence (정정 1, 유지)

8행 집계: photo_url non-empty=0, photo_urls('[]' 제외) non-empty=0, result_code=8, note=3, value_text=5, value_number=0. ⇒ TOTAL photo evidence = 0/8.

## E3. inspection별 분포 + set 해소

| inspection_id | rows | set_item_id 有 | 해소 set | result_code | note | value_text | value_number |
|---|---|---|---|---|---|---|---|
| 217f0c15 | 5 | 0 | 0 | 5 | 0 | 5 | 0 |
| 3f9cf36f | 3 | 3 | 1 | 3 | 3 | 0 | 0 |

217f0c15(5행) set_item_id 전부 NULL → orphan(set 추적 불가). 3f9cf36f(3행) → 정확히 1 set(`7fee7518`). ⇒ set 추적 가능 result = 1 set.

## E4. ELIGIBLE identity 해소 (정정 2 / FLAG-6, 유지)

| result_id | result.item_name | result_code | set_item_id | item_seq | set_item_name | is_active | set |
|---|---|---|---|---|---|---|---|
| 6b3ac8bb | NULL | NORMAL | eddb23a3 | 1 | 외관 상태 점검 | true | 7fee7518 |
| baf2a402 | NULL | NORMAL | 90c198f4 | 2 | 작동 시험 | true | 7fee7518 |
| e707d159 | NULL | NORMAL | 5afdb267 | 3 | 안전장치 확인 | true | 7fee7518 |

result.item_name NULL 이나 inspection_set_item_id → active set_item exact resolution = identity loss 없음. lazy compose 에서 set_item_id → item_name 복원. ELIGIBLE 유지. observed_value_types=raw_code,note / repeated_row_fit=YES / special_layout_required=NO / photo·value_text·value_number 없음.

## E5. zero-item 3 set (정정 3, 유지)

| id | name | obligation_type | summary | item_count | bridge | 판정 |
|---|---|---|---|---|---|---|
| a41f5ac7 | 안전관리자 선임 | APPOINT | 안전관리자 선임 | 0 | N | NON_ELIGIBLE |
| 61b6e5c9 | 유해위험요인 신고 | REPORT | 유해위험요인 신고 | 0 | N | NON_ELIGIBLE |
| 7c2423dd | 안전보건교육 실시 | INSPECT | 안전보건교육 실시 | 0 | N | EXCEPTION_SOURCE_MISMATCH |

`7c2423dd`: obligation_type=INSPECT vs name/summary=교육 충돌 → 이름 기반 판정 금지에 따라 EXCEPTION_SOURCE_MISMATCH 격리(별도 source-data investigation 대상).

## E6. 불변식 실측 (default 323 정당성)

total=327 / bridged=324 / bridged_and_item16=324 (bridge⟺16 일치) / with_result_sample=1 / category_nonnull=84 / schema_nonnull=0. ⇒ item16 & bridge=Y & result 없음 323건은 결정적으로 EXCEPTION_NO_RESULT_SAMPLE. 개별 조회 불필요.

## E7. transcription 무결성 (md5 교차검증)

```
Python/Postgres MD5_ID     = 9113e294cf7a86aaea81ab91b5186df0   MATCH
Python/Postgres MD5_TRIPLE = 39422b8ec3995cde7b40a574340b9a9f   MATCH
```
구성: ORDER BY id::text, TAB(chr9)/LF(chr10), category=COALESCE(inspection_category,''). 327행 base = production byte 동일.

## E8. GENERAL schema 승인 상태 (live 재확인, 정정 2 근거)

runtime_form_schema 조회 (status=APPROVED_FOR_RUNTIME_USE 행은 1개뿐):
```
id          = dc79ac3c-388c-42dc-b029-3dd9bda54a47
form_name   = 점검 결과 기록서 (범용)   (= GEN-INSPECT-RESULT-001)
document_family = DOCUMENT
field_count = 5
status      = APPROVED_FOR_RUNTIME_USE
version     = 1
created_at  = 2026-08-25 14:12:52+00
```
⇒ GENERAL presentation schema 승인은 이미 GRANTED/SEALED. B1은 승인을 재개방하지 않고 이 schema에 대한 set 연결 자격만 심사.

## E9. parent baseline (GitHub remote 실측)

`taiengineering/taieng` 최신 HEAD:
```
01d4519b1b6cc6a90b71eacd193b47bb5837d0e2
docs(WP-PERSISTENCE-02B STEP-0): ARCHITECTURE REBASE (NO MUTATION)
parent = 3860cdbe (02A STEP-4D-PREP)
```
커밋 본문 확인: runtime_inspection_bridge = presentation schema resolution SoT(새 테이블 없음), APPROVED_FOR_RUNTIME_USE만, fallback·LLM inference 금지, mapping side effect 0, NEXT = B1 explicit mapping(HUMAN REVIEW 선행). ⇒ B1 parent 정본 = 01d4519b.

## PROVEN / UNPROVEN (유지)

- PROVEN: observed inspection_results multi_row structure fit.
- UNPROVEN(=Composer 단계 책임): top-level View Model source binding (inspection_subject 등).
