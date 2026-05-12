# HANDOFF 2026-05-09 — 분해기 v2.0 본 적용 완료 + Stage 14 진입 전

## 0. 즉시 다음 작업

**Stage 14 (처벌 매핑)** — 사용자가 어제 정한 1순위. 금지·의무·처벌 매핑.

활용 가능 데이터 (이미 본 적용된 의미절):
- `semantic_clause` 160,372건 (content_type=PENALTY 3,165건 포함)
- `semantic_clause_relation` 147,721건 (relation_type=cross_reference 43,645건)

목표 산출:
- `master_rule_v2_relation` (CHECK 4종: has_penalty/penalty_for/derived_from/reference_to)
- 처벌 의미절(PENALTY) → 위반된 의무 의미절 매핑

## 1. 사용자가 강조한 법령엔진 4가지 데이터 (반드시 기억)

| ID | 데이터 | 의미 | 처리 우선순위 |
|---|---|---|---|
| **A** | scope (범위) | 사업장 입력 → 해당/비해당 판단 | 4 |
| **B** | 금지·의무·처벌 매핑 | 위반 시 어느 처벌 적용 | **1 (Stage 14, 다음 작업)** |
| **C** | 산업 분류 | 어느 산업·시설·공정에 적용 | 3 (Stage 10~12) |
| **D** | 의무 종류 | 어떤 의무인지 (점검/교육/보고/...) | 2 (Stage 09 내) |

**일부 몰입 경고**: scope를 먼저 시작했다가 진단 결과 임계값 0.26%로 어렵자 외부 사전 매핑(3순위)으로 자체 redirect → 사용자 redirect받아 우선순위 1로 복귀. 다음 창에서도 사용자가 정한 우선순위(1→2→3→4) 존중.

## 2. 어제(2026-05-09) 작업 결과 — 분해기 v2.0 본 적용 완료

### 2.1 데이터 적재 (완료)

| 테이블 | rows | 비고 |
|---|---|---|
| semantic_clause | 160,372 | 4종 part_type 모두 (paragraph 69,221 / clause 72,316 / subclause 12,165 / proviso 6,670) |
| semantic_clause_relation | 147,721 | 6종 (enumeration 84,481 / cross_reference 43,645 / sentence_seq 8,266 / proviso 6,670 / parallel_seq 3,373 / exemption 1,286). parallel_and/parallel_or 0건은 R-11 의도 |
| inherited 자식 의미절 | 78,160 (48.7%) | 부모 상속 작동 |

### 2.2 content_type 분포 (9종)

OBLIGATION 76,642 (47.8%) / DEFINITION 23,515 (14.7%) / AUTHORITY 22,383 (14.0%) / DELEGATION 14,576 (9.1%) / NULL 13,344 (8.3%, enumeration 본질) / PROHIBITION 3,192 (2.0%) / PENALTY 3,165 (2.0%) / EXEMPTION 2,132 (1.3%) / STATEMENT 1,423 (0.9%)

### 2.3 6하원칙 채움률

executor 63.9% / what 60.2% / how 32.3% / condition 28.3% / where 22.1% / exception_marker 8.6% / cycle 4.7% / recipient 2.6% / exception 3.9% / **form_token 0% / sectors 0%** (분해기 v2.0이 출력 안 함, Stage 09에서 추출 필요)

### 2.4 데이터 무결성 (모두 통과)

- broken_part / broken_relation_source / broken_relation_target = 0 / 0 / 0
- inherited_from_clause_id orphan = 0 (FK 재생성 통과)
- self_ref / duplicate_triplet 위반 = 0 / 0
- 마스터 11 테이블 모두 0 row (Stage 09 진입 전 깨끗)
- 신뢰 OK 데이터 보존: law_master 752 / law_article 33,862 / law_article_part 143,549

## 3. DDL 변경 누적 (어제 5회)

1. `semantic_clause_relation.relation_type` CHECK 6종 → **8종** 확장 (exemption + cross_reference 추가)
2. `semantic_clause` 컬럼 27 → **28** (inherited_from_clause_id self-FK 추가)
3. `semantic_clause.content_type` CHECK 6종 → **8종** 확장 (PENALTY + EXEMPTION 추가)
4. inherited_from_clause_id FK 일시 드롭 → INSERT → 재생성 (orphan 0 검증)
5. UPDATE: STATEMENT (review_reason='content_type_exemption_mapped') 2,132건 → EXEMPTION 복구

## 4. 백업 보존 (10개 — 참고/학습용)

- semantic_clause_backup_pre_redecompose_20260509 (58,495)
- master_rule_v2_backup_20260509 (58,495)
- master_rule_executor_backup_20260509 (64,159)
- master_rule_condition_backup_20260509 (26,322)
- master_rule_v2_value_backup_20260509 (6,147)
- master_rule_v2_relation_backup_20260509 (373)
- master_rule_exception_backup_20260509 (12)
- master_rule_scope_backup_20260508 (5,015)
- master_rule_scope_threshold_backup_20260508 (71)
- master_rule_scope_mapping_backup_20260508 (922)

## 5. Stage 14 진입 전 결정 사항 2건 (어제 보류)

| ID | 내용 | 권장 |
|---|---|---|
| **A** | `master_rule_v2.rule_kind` CHECK에 **EXEMPTION 추가** (현재 8종: OBLIGATION/PROHIBITION/AUTHORITY/DELEGATION/DEFINITION/STATEMENT/UNCLASSIFIED/PENALTY, EXEMPTION 없음) | DDL 변경 진행 |
| **C** | `master_rule_v2_relation.relation_type` CHECK 4종(has_penalty/penalty_for/derived_from/reference_to) 유지 + 매핑 변환 정책 | 변환 매핑 사용: cross_reference→reference_to, proviso→derived_from, exemption→derived_from. enumeration/parallel/sentence_seq는 변환 안 함 |
| **B** | `master_rule_executor.role` CHECK는 'ALTERNATIVE_EXECUTOR' (4월말 코드는 'ALTERNATIVE') | Cursor 코드 변경으로 처리 |

## 6. 어제 발생한 결함 + 해결 (사이클 1·2·3 누락 사항)

| 결함 | 원인 | 해결 |
|---|---|---|
| Stage 08 첫 chunk PGRST204 (classified_by_pattern 컬럼 없음) | 분해기 jsonl에 디버깅 컬럼 포함, DB 스키마와 불일치 | lib/db_schema.py 화이트리스트 필터 (28+9 컬럼) |
| Stage 08 CHECK 위반 (lowercase) | Cursor가 자체 진단으로 EXEMPTION→STATEMENT, lowercase 변환 추가 | DB CHECK를 8종 UPPERCASE로 확장 (Claude DDL) |
| Stage 08 self-ref 위반 6,869건 | Stage 07 cross_reference 룰이 self-ref 생성 | Stage 08 INSERT 직전 self-ref 필터링 (1줄) |
| Stage 08 UNIQUE 위반 3,196건 | Stage 07이 같은 (source, target, relation_type) 중복 생성 | Stage 08 INSERT 직전 dedupe |
| Stage 08 FK 위반 (master_rule_v2 RESTRICT) | semantic_clause truncate가 master_rule_v2에 막힘 | 마스터 11 테이블 truncate cascade (백업 후) |
| Stage 08 self-FK 위반 (inherited_from) | chunk INSERT 순서 무관하게 자식 먼저 들어감 | FK 일시 드롭 → INSERT → 재생성 |
| Cursor 자체 patch + 자동 retry 무한 루프 위험 | Cursor가 매 사이클마다 자체 진단·patch 시도 | "에러 시 즉시 STOP + stderr 보고, 자체 patch 절대 금지" 명시 |

## 7. 학습해야 할 것 (다음 창에서 먼저 학습)

### 7.1 핵심 원칙 (사용자 강조 — 절대 위반 금지)

**거짓말 방지 5원칙**:
1. 모집단·분모 항상 명시
2. "X% 완료"·"사실상 PASS" 금지
3. 성공·실패·미처리 함께 보고
4. 미실행을 실행했다 안 함
5. 모르면 모른다 (NULL + needs_review, 추측 금지)

**작업 원칙 (2026-05-05 확정)**:
- `ask_user_input_v0` (선택형 팝업) 사용 금지 — 텍스트로 직접 묻거나 즉시 실행
- 작업 목적: 진행률·건수 쌓기가 아니라 패턴 발견→룰 보강→재반복으로 옳은 방식 자체를 찾는 것
- "100% 완료"·"사실상 PASS" 등 검증 없는 완료 선언 금지
- 진행 옵션 다중 제시 전 "지금 진짜 검증해야 할 것은 무엇인가"부터 점검

**일부 몰입 방지**:
- 사이클별 룰 보강에 매몰 금지
- 매 사이클마다 새 룰 추가하다가 전체 방향 놓치지 말 것
- 사용자가 정한 우선순위 자체 redirect 금지 (어제 scope→매핑 redirect 사례 반복 금지)

### 7.2 코드 학습 (이미 fetch 완료, 다음 창에서 재학습 필요)

**Stage 14 처벌 매핑에 직접 활용**:
- 4월말 `convert_clause_to_rule.py` (29KB) — `infer_rule_kind` (PENALTY 어말 검출), `parse_when`, `classify_action_category` 13종, `classify_what_action` 9종
- 위치: `tai-admin/docs/extraction/scripts/convert_clause_to_rule.py`

**참고만**:
- 4월말 `extract_scope_from_clauses.py` (33KB) — scope 작업 시 활용 (Stage 13)

### 7.3 DB 스키마 사전 점검 (Stage 14 진입 전 필수)

- `master_rule_v2.rule_kind` CHECK 정확 확인 (EXEMPTION 누락)
- `master_rule_v2_relation` CHECK + UNIQUE 점검:
  - relation_type CHECK 4종 (has_penalty/penalty_for/derived_from/reference_to)
  - chk_no_self (source≠target)
  - UNIQUE (source_rule_id, target_rule_id, relation_type)
- `master_rule_v2.action_category_code` CHECK 14종

### 7.4 인프라 정보

- Supabase: `vwlahtguyggrhvslabax` (서울)
- Repo: `taiengineering/tai-admin` (main only)
- 작업 디렉토리: `~/Desktop/tai-engineering/tai-admin/docs/extraction/scripts/decompose_v2/`
- Stage 07 jsonl 보존: `data/07_clauses.jsonl` (259MB), `data/07_relations.jsonl` (42MB)
- Cursor MCP: github-tai (tai-api), github-tai-admin (tai-admin)
- 작업 분업: Claude 기획창 (설계·spec) / Cursor (코드 구현)

## 8. Stage 14 (처벌 매핑) 작업 진단 plan

### 8.1 Step 1 — 데이터 본질 분석 (Claude 직접 SQL)

```sql
-- A. PENALTY 의미절의 cross_reference 매핑 분포
-- 처벌 의미절(source) → 위반 의무 의미절(target) 매핑이 cross_reference로 잡혔는지
SELECT 
  COUNT(DISTINCT r.source_clause_id) AS penalty_with_xref,
  COUNT(*) AS total_xref_from_penalty
FROM semantic_clause_relation r
JOIN semantic_clause sc ON sc.id = r.source_clause_id
WHERE sc.content_type = 'PENALTY' AND r.relation_type = 'cross_reference';

-- B. PENALTY 의미절 source_text 패턴 분석 (위반 표현)
-- "...위반한 자는 ...에 처한다" 같은 패턴 빈도
SELECT 
  COUNT(*) FILTER (WHERE source_text ~ '위반한\s*자') AS pat_violator,
  COUNT(*) FILTER (WHERE source_text ~ '제\s*\d+\s*조') AS pat_article_ref,
  COUNT(*) FILTER (WHERE source_text ~ '제\s*\d+\s*항') AS pat_paragraph_ref,
  COUNT(*) AS total_penalty
FROM semantic_clause WHERE content_type = 'PENALTY';

-- C. PENALTY 의미절 sample 30건 (cross_reference 보유)
SELECT sc.id, sc.source_text,
  (SELECT COUNT(*) FROM semantic_clause_relation r 
   WHERE r.source_clause_id = sc.id AND r.relation_type = 'cross_reference') AS xref_count
FROM semantic_clause sc
WHERE sc.content_type = 'PENALTY'
ORDER BY random() LIMIT 30;
```

### 8.2 Step 2 — 매핑 룰 도출 (sample 분석 후)

PENALTY 의미절 → 위반 의무 의미절 매핑 가능성:
- 정량 평가 (cross_reference 활용 % vs 정규식 추가 필요 %)
- 4월말 코드의 PENALTY 처리 로직 학습

### 8.3 Step 3 — Stage 14 spec 작성

작업지시서 + DDL 변경 (rule_kind CHECK 확장) + Cursor 명령

## 9. 다음 창에서 절대 하지 말 것

1. ❌ scope 작업 자체 redirect (어제 사례 반복 금지)
2. ❌ Stage 09~12 우회 (사용자가 정한 1순위 = Stage 14)
3. ❌ Cursor 자체 patch 허용 (반드시 STOP + 보고 받기)
4. ❌ 사이클별 룰 보강 몰입 (매핑·법령엔진 결과 본 후 결정)
5. ❌ 매 응답에 새 룰 추가 (단발 spec → dry-run → 결과 → 결정)

## 10. 핵심 데이터 (다음 창에서 즉시 사용)

- semantic_clause: 160,372건 본 적용 완료
- semantic_clause_relation: 147,721건 본 적용 완료
- 마스터 11 테이블: 모두 0 (Stage 09~14 진입 대기)
- Stage 09~14 작업지시서 미작성 (4월 말 파이프라인 코드 학습 후 작성)
- 다음 작업 = **Stage 14 (처벌 매핑)** sample 진단부터
