# WO-CONDITION-MIGRATION-001
# condition_mapping_candidate 마이그레이션 결과 보고서

**작성일:** 2026-06-23 | **상태:** 완료

---

## 1. 적용 DDL 문서명

`docs/WO-CONDITION-DDL-004_최종확정안.md`

---

## 2. 적용 SHA

- DDL-004 문서 SHA: `39ed192`
- 마이그레이션 적용 후 commit: `2bd5e26`

---

## 3. 적용 Schema

`public`

근거: 참조 테이블(semantic_clause, law_article, law_article_part, appendix_condition) 전부 `public` schema 확인 후 컨벤션 일치.

---

## 4. 생성 테이블명

`public.condition_mapping_candidate`

---

## 5. 생성 인덱스 목록 (12개)

| 인덱스명 | 타입 | 대상 | 조건 |
|---|---|---|---|
| `condition_mapping_candidate_pkey` | BTREE | id | — |
| `cmc_unique_condition_code` | BTREE (UNIQUE) | condition_code | — |
| `cmc_unique_sector_mapping` | BTREE (UNIQUE NULLS NOT DISTINCT) | semantic_clause_id, input_field, input_value, applicable_sectors | — |
| `idx_cmc_applicable_sectors_gin` | **GIN** | applicable_sectors | — |
| `idx_cmc_condition_code` | BTREE | condition_code | — |
| `idx_cmc_condition_type` | BTREE | condition_type | — |
| `idx_cmc_input_field` | BTREE | input_field | `WHERE review_status = 'CONFIRMED'` |
| `idx_cmc_input_field_value` | BTREE | input_field, input_value | `WHERE review_status = 'CONFIRMED'` |
| `idx_cmc_review_status` | BTREE | review_status, condition_type | — |
| `idx_cmc_semantic_clause` | BTREE | semantic_clause_id | — |
| `idx_cmc_source_article` | BTREE | source_article_id | — |
| `idx_cmc_appendix_condition` | BTREE | appendix_condition_id | `WHERE appendix_condition_id IS NOT NULL` |

---

## 6. 생성 Trigger 목록

| Trigger명 | 이벤트 | 타이밍 | 함수 |
|---|---|---|---|
| `trg_cmc_updated_at` | UPDATE | BEFORE | `update_cmc_updated_at()` |

---

## 7. 검증 쿼리 결과

| 검증 항목 | 기대값 | 실제값 | 판정 |
|---|---|---|---|
| 테이블 존재 확인 | `public.condition_mapping_candidate` 1건 | 확인 | ✅ PASS |
| 인덱스 수 | 12개 | 12개 | ✅ PASS |
| COMMON 삽입 시도 | ERROR (CHECK 위반) | `cmc_applicable_sectors_check` 위반 오류 발생 | ✅ PASS |
| COMMON 데이터 건수 | 0 | 0 | ✅ PASS |
| 유효하지 않은 섹터 | 0 | 0 | ✅ PASS |
| trigger 존재 | `trg_cmc_updated_at` | BEFORE UPDATE 확인 | ✅ PASS |
| GIN 인덱스 존재 | `idx_cmc_applicable_sectors_gin` (GIN) | 확인 | ✅ PASS |
| GIN 실 조회 성능 | 데이터 1,000건+ 후 확인 예정 | 초기 빈 테이블 — 보류 | ⏳ 보류 (정상) |

**전체 판정: PASS (실 조회 성능은 초기 데이터 적재 후 확인)**

---

## 8. 실패/경고 사항

없음.

---

## 9. 선행 조건 확인 결과

| 항목 | 결과 |
|---|---|
| PostgreSQL 버전 | 17.6 — UNIQUE NULLS NOT DISTINCT 지원 확인 |
| condition_mapping_candidate 사전 존재 | 미존재 — 충돌 없음 |
| update_cmc_updated_at 함수 사전 존재 | 미존재 — 충돌 없음 |
| semantic_clause | public schema 존재 |
| law_article | public schema 존재 |
| law_article_part | public schema 존재 |
| appendix_condition | public schema 존재 |

---

## 10. 다음 단계 권고

### WO-CONDITION-SEED-001 (다음 작업)

`has_*` 기반 초기 매핑 적재 설계.

**condition_code 생성 규칙 확정 후 GPT 배치 시작.**

```
형식: {SECTOR_PREFIX}-{TYPE_CODE}-{SEQUENCE}
예시:
  IND-WORK-001   = INDUSTRIAL / WORK_ACT
  CON-EQUIP-014  = CONSTRUCTION / EQUIPMENT_ACT
  BLD-THRES-003  = BUILDING / THRESHOLD
```

**has_* → applicable_sectors 매핑 기준:**

| has_* 필드 | applicable_sectors |
|---|---|
| has_chemical_substance, has_high_pressure_vessel, has_special_chemical | ['INDUSTRIAL'] |
| has_tower_crane, has_scaffolding, has_blasting, has_diving | ['CONSTRUCTION'] |
| has_elevator, has_escalator, has_fire_equipment | ['BUILDING'] |
| has_confined_space, has_asbestos_demo | ['INDUSTRIAL', 'CONSTRUCTION'] |
| 범용 안전보건관리체계, 교육 | ['INDUSTRIAL', 'CONSTRUCTION', 'BUILDING'] |

### 이후 예정 순서

1. WO-CONDITION-SEED-001 — has_* 기반 초기 매핑 적재
2. WO-CONDITION-SEED-002 — THRESHOLD / appendix_condition 매핑
3. WO-CONDITION-VERIFY-001 — VCF-02 기준 condition_mapping 조회 검증
4. WO-CONDITION-VERIFY-002 — VCF-01 현실 사업장 과매핑/누락 검증

---

*WO-CONDITION-MIGRATION-001 완료.*
