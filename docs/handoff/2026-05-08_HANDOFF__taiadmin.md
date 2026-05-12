# HANDOFF 2026-05-08 — 분해기 v2.0 본 적용 완료, Stage 09 진입 직전

## 오늘 진짜 산출물

분해기 v2.0 pipeline 8 stage 완성 + 143,549 part 전체 본 적용 완료.

### 본 적용 결과 (DB 실제)

| 테이블 | rows | 비고 |
|---|---|---|
| `semantic_clause` | **160,372** | 4종 part_type 100% 처리 |
| `semantic_clause_relation` | **147,721** | self-ref 6,869 + duplicate 3,196 폐기 |
| 데이터 무결성 | ✅ | 모든 FK·CHECK 통과 (broken=0) |

### content_type 분포 (8종)

| 카테고리 | count | % |
|---|---|---|
| OBLIGATION | 76,642 | 47.8% |
| DEFINITION | 23,515 | 14.7% |
| AUTHORITY | 22,383 | 14.0% |
| DELEGATION | 14,576 | 9.1% |
| NULL (enumeration 본질) | 13,344 | 8.3% |
| PROHIBITION | 3,192 | 2.0% |
| PENALTY | 3,165 | 2.0% |
| EXEMPTION | 2,132 | 1.3% |
| STATEMENT | 1,423 | 0.9% |

### relation_type 분포 (DB 실제, 6종)

| 종류 | count |
|---|---|
| enumeration | 84,481 |
| cross_reference | 43,645 |
| sentence_seq | 8,266 |
| proviso | 6,670 |
| parallel_seq | 3,373 |
| exemption | 1,286 |

### 부모 상속 효과
- `inherited_from_clause_id` 채워진 자식: **78,160 (48.7%)**
- 상속 필드 변경: content_type 65,535 / executor 38,856 / how 23,247 / where 18,335 / cycle 3,099 / exception_marker 6,785

## 잔존 결함 (다음 사이클 대상, 매핑·법령엔진 결과 본 후 결정)

| 결함 | 영향 |
|---|---|
| Stage 07 cross_reference self-ref | 6,869건 폐기 |
| Stage 07 cross_reference 중복 | 2,939건 폐기 |
| Stage 07 exemption 중복 | 257건 폐기 |
| Stage 04 종결어미 미커버 (no_match) | 77,820건 NULL |
| Stage 05 verb_stem_rejected 검증 보류 | 20,912건 (R-12 정확도 미검증) |
| 6하원칙 채움률 낮음 | where 10.7% / what 60.2% / how 17.8% |

## DDL 변경 이력 (오늘)

1. `semantic_clause`에 7컬럼 추가 (where_text/what_text/how_text/exception_marker + parent_clause_id/relation_type/relation_marker)
2. `semantic_clause` 컬럼 정리 (parent_clause_id/relation_type/relation_marker 삭제 → 매핑 테이블로 이전)
3. `semantic_clause_relation` 신규 테이블 (9컬럼, 8종 relation_type CHECK)
4. relation_type CHECK 8종으로 확장 (exemption + cross_reference 추가)
5. `inherited_from_clause_id` 컬럼 + FK + 인덱스 추가
6. `semantic_clause_content_type_check` 8종 확장 (PENALTY + EXEMPTION 추가)
7. 마스터 11 테이블 truncate cascade (백업 10개 보존)
8. semantic_clause + relation 본 적용 INSERT
9. `inherited_from_clause_id` FK 일시 드롭 (INSERT용) → INSERT 후 재생성·검증 통과
10. EXEMPTION 복구 UPDATE (STATEMENT → EXEMPTION 2,132건)

## 백업 (참고/학습용 보존)

| 백업 테이블 | rows |
|---|---|
| semantic_clause_backup_pre_redecompose_20260509 | 58,495 |
| master_rule_v2_backup_20260509 | 58,495 |
| master_rule_executor_backup_20260509 | 64,159 |
| master_rule_condition_backup_20260509 | 26,322 |
| master_rule_v2_value_backup_20260509 | 6,147 |
| master_rule_v2_relation_backup_20260509 | 373 |
| master_rule_exception_backup_20260509 | 12 |
| master_rule_scope_backup_20260508_pre_recall | 5,015 |
| master_rule_scope_mapping_backup_20260508_pre_recall | 922 |
| master_rule_scope_threshold_backup_20260508_pre_recall | 71 |

## 작업 방식 정착 (내일 이후도 동일)

1. **DDL 사전 점검 필수** — CHECK + FK + UNIQUE (오늘 누락으로 결함 누적, 내일은 master_rule_v2 사전 점검 완료 상태)
2. **Cursor 자체 patch 금지** — 에러 시 즉시 STOP + stderr 보고 (오늘 정착)
3. **정직 보고 5개 강제** — 모집단·분모 / "X% 완료" 금지 / 성공·실패·미처리 함께 / 미실행 표기 / 모르면 NULL
4. **대량 작업은 Python + 사용자 터미널 실행** — railway run
5. **사용자는 큰 분기점에서만 GO/NO-GO**, 작업·분석·수정은 Claude 자율

## 내일 시작점 — Stage 09 (master_rule_v2 변환)

### 사전 점검 완료 (오늘 끝)

| 결함 | 처리 방향 |
|---|---|
| `master_rule_v2.rule_kind` CHECK에 EXEMPTION 없음 | DDL 변경 (Claude 직접) |
| `master_rule_executor.role` CHECK는 'ALTERNATIVE_EXECUTOR' | Cursor 코드 변경 (4월 말 'ALTERNATIVE' → 'ALTERNATIVE_EXECUTOR') |
| `master_rule_v2_relation.relation_type` 4종만 (has_penalty/penalty_for/derived_from/reference_to) | 매핑 변환: cross_reference→reference_to / proviso→derived_from / exemption→derived_from |

### 내일 작업 순서

1. **DDL 변경**: `master_rule_v2.rule_kind` CHECK에 'EXEMPTION' 추가 (Claude 직접, 1줄 SQL)
2. **Stage 09 작업지시서 작성** (`docs/extraction/CURSOR_TASK_2026-05-XX_pipeline_v20_stage09.md`)
   - 4월 말 `convert_clause_to_rule.py` (29KB) 베이스
   - v2.0 신규 필드 매핑 (where_text/what_text/how_text → master_rule_v2 필드)
   - inherited_from_clause_id 활용 (자식 의미절은 부모로부터 상속받은 정보 그대로 변환)
   - semantic_clause_relation → master_rule_v2_relation 매핑 변환 (4종 매핑 룰)
   - ALTERNATIVE → ALTERNATIVE_EXECUTOR 변경
3. Cursor에 push → dry-run → 본 적용
4. 검증 SQL — rule_kind 분포, sectors 분포, scope 통계
5. 외부 사전 매핑 단계 (industry_master / ksic_process_map / process_equipment_map) 진입 준비

### 핵심 파일 위치

| 파일 | 역할 |
|---|---|
| `tai-admin/docs/extraction/scripts/decompose_v2/` | 분해기 v2.0 pipeline (Cursor 로컬, 미push) |
| `docs/extraction/RULE_CATALOG_v20.md` | 룰 카탈로그 (20개) |
| `docs/extraction/CURSOR_TASK_2026-05-09_decompose_v20.md` | 분해기 v2.0 작업지시서 |
| `docs/extraction/scripts/convert_clause_to_rule.py` | 4월 말 변환기 (Stage 09 베이스) |

## 전체 흐름 (몰입 방지 reminder)

```
[완료] 분해기 v2.0 본 적용 (semantic_clause 160,372 + relation 147,721)
   ↓
[다음 — 내일] Stage 09: master_rule_v2 변환 (1:1, 부속 테이블 함께)
   ↓
[다음] 외부 사전 매핑 (industry_master 501 / ksic_process_map 6,957 / process_equipment_map 187,319)
   ↓
[다음] master_rule_scope INSERT
   ↓
[다음] 법령엔진 simulator: 사업장 입력 → 적용 의무 출력 검증
   ↓
[검증 결과로 결정] 분해기 추가 보강 vs 매핑 보강 vs 출력 알고리즘 보강
```

목적: **법령엔진이 사업장 입력 → 맞는 의무를 출력**. 분해기 100% 완벽 추구 금지.
