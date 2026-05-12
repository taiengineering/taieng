# LEGAL_RULE_PIPELINE.md

> **AI agent 작업 시작점.** 새 세션 시작 시 이 문서를 첫 번째로 읽어 30초 안에 현재 상태와 다음 액션을 파악할 수 있게 설계됨.
>
> Last verified: 2026-05-08

---

## 0. CURRENT STATE (30초 컨텍스트)

```yaml
project_id: vwlahtguyggrhvslabax       # Supabase 서울
repo: taiengineering/tai-admin (main only)
docs_path: docs/extraction/
scripts_path: docs/extraction/scripts/

pipeline_status:
  step_1_parsing:    done   # 33,862 articles / 143,549 parts
  step_2_decompose:  done   # semantic_clause 58,495 v1.9.1
  step_3_mapping:    pending # master_rule_v2 0 rows (스키마만 완료)
  step_4_views:      pending # 사용 정책 View 4개 미생성

next_action: |
  convert_clause_to_rule.py 작성 → dry-run sample 100 → 전체 변환
  작업지시서: docs/extraction/CURSOR_TASK_2026-05-08_convert_clause_to_rule.md

known_issue:
  convert_clause_to_rule_error: |
    실행 시 에러 발생. 메시지 미수집 상태.
    재시도 시 stderr 전체 보관 필수.
```

---

## 1. PIPELINE OVERVIEW

```
[원문]                       [Layer 1]                    [Layer 2]                   [Layer 3]
법제처 OpenAPI    →    law_master / law_article  →  semantic_clause     →   master_rule_v2
                       law_article_part            (의미절 + sectors[])     (5 테이블 구조)
                                                                                      ↓
                                                                            inspection_sets
                                                                            work_schedules
                                                                            (사업장 적용)

         Step 1                  Step 2                 Step 3
        파싱(완료)              분해(완료 v1.9.1)      매핑(대기)
```

**원칙**:
- AI/LLM 호출 0% (정규식 + 키워드 사전만)
- 모든 의미절 변환, 제외 없음 (rule_kind로 분류 보존, 사용 단계 필터링)
- 의미절 1 = 룰 1 (paragraph 단위 1:1, 81% 안전)
- 검증 없는 완료 선언 금지

---

## 2. TABLES — 스키마 + 현재 상태

### 2.1 Layer 1: 법령 파싱 산출물

| table | rows (2026-05-08) | 핵심 컬럼 | 비고 |
|---|---|---|---|
| `law_master` | ~366 | id, law_id, law_name | 법령 마스터 |
| `law_article` | 33,862 | id, source_law_id, article_no, article_type, article_internal_key, article_status_code, is_deleted_in_version | 조문 |
| `law_article_part` | 143,549 | id, article_id, part_text, part_type, depth | paragraph/항/호 등 |

**분해 대상**: `part_type='paragraph'` AND article_type='조문' AND `law_id != KEC` AND 폐지 조문 제외 → 49,997개.

### 2.2 Layer 2: 의미절 분해 산출물

| table | rows (2026-05-08) | 비고 |
|---|---|---|
| `semantic_clause` (본) | 58,495 | v1.9.1 + sectors[] + recipient_text |
| `semantic_clause_iter1` (백업) | 58,495 | 본 테이블과 동기화 |

**`semantic_clause` 핵심 컬럼 (23개)**:
```
id (uuid PK), source_part_id (FK), source_article_id (FK), clause_seq,
source_text, source_part_text,
condition_text, executor_text, action_text, recipient_text,
cycle_text, exception_text, form_token, alternative_kept_text,
content_type (OBLIGATION/PROHIBITION/AUTHORITY/DELEGATION/DEFINITION/STATEMENT/None),
applied_rules (text[]),
decomposition_version ('v1.9.1'),
needs_review (bool), review_reason,
sector (text), sectors (text[]),  -- sectors[]는 어제 sector 표준화 결과 (2026-05-07)
created_at, updated_at
```

**현재 분포**:
```yaml
content_type:
  OBLIGATION:    29,665   # 사업장 의무 (사업장 매칭 대상)
  AUTHORITY:     10,470   # 사업장 권한
  PROHIBITION:    1,742   # 사업장 금지
  DELEGATION:     9,055   # 정부 입법 행위 (executor 4,166는 위임받는 자)
  DEFINITION:     6,471   # 정의 (의무 어말 보유 106건은 분류 실패 룰 후보)
  STATEMENT:        390   # 진술
  None:             702   # 미분류 (의무 어말 보유 39건은 분류 실패 룰 후보)

executor_text:
  채움률:        99.0%   # 41,349 / 41,769 (rule cands)
  still_null:    421 (1.0%)
  사물 주어 review: 1,532

recipient_text:
  채움률 (보고/신고): 58.6%  # 5,309 / 9,067

sectors[]:
  보유:          58,334
  다중매핑:      32,525
  NULL (INACTIVE): 161

needs_review:    30,753 (52.6%)
```

### 2.3 Layer 3: master_rule_v2 (매핑 산출물 — 대기)

| table | rows | NOT NULL 컬럼 | 비고 |
|---|---|---|---|
| `master_rule_v2` (메인, 43컬럼) | **0** | rule_code, source_clause_id, source_article_id, source_law_id, what_action, sectors, why_obligation_summary, action_category_code, generation_method, status, needs_review, **rule_kind** (DDL 추가됨) | DDL 완료 |
| `master_rule_executor` | 0 | rule_id, role, role_label, sort_order | EXECUTOR/RECIPIENT/ALTERNATIVE 분리 |
| `master_rule_condition` | 0 | rule_id, condition_text, sort_order | 조건절 분리 |
| `master_rule_exception` | 0 | rule_id, exception_text, sort_order | 예외 (의미절에 5건뿐) |
| `master_rule_relation` | 0 | parent_rule_id, child_rule_id, relation_type | 룰 그룹화 (Phase B 후속) |

**`rule_kind` CHECK 값**:
```
OBLIGATION, PROHIBITION, AUTHORITY,    -- 사업장 매칭 대상
DELEGATION, DEFINITION, STATEMENT,     -- 참고용 (사업장 매칭 제외)
UNCLASSIFIED                            -- 검토 대상
```

---

## 3. STEP 1 — 법령 파싱 (완료, 재실행은 법령 개정 시)

이 섹션은 다른 핸드오프에서 이미 완료. 자세한 내용은 `HANDOFF_2026-05-05.md` 참조.

**상태**: 일반조문 20,711 / KEC 1,931 / NFTC·KDS 4,887 / 본칙 5,155 = total 32,684 articles 처리. drafts placeholder 2,431건 매핑 대기 (NFTC 1,335 + 일반 674 + 고시 141 + 기타 281).

---

## 4. STEP 2 — 의미절 분해 (완료, 재실행 가능)

### 4.1 스크립트

`docs/extraction/scripts/decompose_v1.py` — v1.9.1, 66KB. **운영 레포 보관** (법령 개정 시 재실행 필요한 파이프라인 자산).

### 4.2 알고리즘 핵심 (v1.9.1)

```
1. PATCH 0  — DELEGATION 우선 판정 (8 패턴)
2. PATCH 1  — FAKE_EXECUTOR 8 패턴 필터
3. PATCH A  — extract_executor_text 역순 추출
   (re.finditer로 "(\\S+?)(은|는|이|가)" 모든 후보 수집 →
    cleanup_subject_candidate (article ref + "에 따라" + 동사 prefix 제거) →
    select_best_subject_match ("은/는" 우선 + 조건절 밖 우선))
4. PATCH 5  — Article 단위 inherit (post-processing)
5. PATCH 6  — recipient_text 추출 (~에게 + 동사)
```

### 4.3 명령

```bash
cd docs/extraction/scripts/

# dry-run (sample 1000건 stratified)
railway run python3 decompose_v1.py --dry-run --sample-size 1000 --sampling stratified --seed 42

# 본 적용 — 모집단 전체
# ⚠️ --sample-size 명시 필수 (default 50, 누락 시 50건만 처리)
railway run python3 decompose_v1.py --apply --truncate-first --sample-size 100000 --sampling random 2>&1 | tee /tmp/decompose_apply.log
```

### 4.4 정상 출력 패턴

```
[INFO] 폐지 조문 제외: 1962건
[TRUNCATE] semantic_clause_iter1 비움 완료
[INFO] 모집단: 49997 paragraphs from 366 laws
[DECOMPOSE] 48035 parts → ~58,500 clauses
[DONE] inserted ~58,500 clauses into semantic_clause_iter1
```

`[DECOMPOSE]` 라인이 빠지면 **사고** (4.6 참조).

### 4.5 본 동기화 (iter1 → 본 테이블, sectors[] 보존)

**iter1 적용 후 본 테이블 갱신** — sectors[]/sector/sector_label 어제 표준화 작업 보존:

```sql
BEGIN;
UPDATE semantic_clause sc
SET 
  executor_text = ic.executor_text,
  recipient_text = ic.recipient_text,
  content_type = ic.content_type,
  applied_rules = ic.applied_rules,
  decomposition_version = ic.decomposition_version,
  needs_review = ic.needs_review,
  review_reason = ic.review_reason,
  action_text = ic.action_text,
  condition_text = ic.condition_text,
  cycle_text = ic.cycle_text,
  exception_text = ic.exception_text,
  form_token = ic.form_token,
  alternative_kept_text = ic.alternative_kept_text,
  updated_at = NOW()
FROM semantic_clause_iter1 ic
WHERE sc.source_part_id = ic.source_part_id 
  AND sc.clause_seq = ic.clause_seq;

-- 백업 일관성
TRUNCATE semantic_clause_iter1;
INSERT INTO semantic_clause_iter1 SELECT * FROM semantic_clause;
COMMIT;
```

자연키(`source_part_id, clause_seq`)는 100% 매칭 보장 — 분해 갯수가 같아서.

### 4.6 검증 SQL 7개

```sql
-- 1. 분포
SELECT decomposition_version, COUNT(*) FROM semantic_clause GROUP BY 1;
-- 예상: v1.9.1 / 58,495

-- 2. content_type 분포
SELECT content_type, COUNT(*) FROM semantic_clause WHERE sectors IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
-- 예상: OBLIGATION 29,665, AUTHORITY 10,470, DELEGATION 9,055, DEFINITION 6,471, ...

-- 3. executor 채움률
SELECT 
  COUNT(*) AS rule_total,
  COUNT(*) FILTER (WHERE executor_text IS NOT NULL) AS has_exec,
  ROUND(100.0 * COUNT(*) FILTER (WHERE executor_text IS NOT NULL) / COUNT(*), 1) AS pct
FROM semantic_clause
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY');
-- 예상: 41,769 / 41,349 / 99.0%

-- 4. 가짜 executor 잔존 (모두 0이어야)
SELECT 
  COUNT(*) FILTER (WHERE executor_text ~ '\s(또|또는|및|에)$') AS jal,
  COUNT(*) FILTER (WHERE executor_text ~ '령으로\s*정하?$') AS wiim,
  COUNT(*) FILTER (WHERE executor_text ~ '^다음\s*각\s*호') AS soobum,
  COUNT(*) FILTER (WHERE executor_text ~ '^필요한\s*사항(은|을)') AS pilyo,
  COUNT(*) FILTER (WHERE LENGTH(executor_text) < 2) AS too_short
FROM semantic_clause
WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY');
-- 예상: 모두 0

-- 5. recipient 채움률 (보고/신고)
SELECT 
  COUNT(*) AS report_total,
  COUNT(*) FILTER (WHERE recipient_text IS NOT NULL) AS has_recipient,
  ROUND(100.0 * COUNT(*) FILTER (WHERE recipient_text IS NOT NULL) / COUNT(*), 1) AS pct
FROM semantic_clause
WHERE action_text ~ '신고|보고|제출|통보|통지'
  AND content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY');
-- 예상: 9,067 / 5,309 / 58.6%

-- 6. sectors[] 보존 (어제 표준화 작업)
SELECT 
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE sectors IS NOT NULL) AS has_sectors,
  COUNT(*) FILTER (WHERE array_length(sectors, 1) >= 2) AS multi_mapping
FROM semantic_clause;
-- 예상: 58,495 / 58,334 / 32,525

-- 7. iter1 백업 일관성
SELECT 
  (SELECT COUNT(*) FROM semantic_clause) AS sc,
  (SELECT COUNT(*) FROM semantic_clause_iter1) AS ic;
-- 예상: 동일 (58,495 / 58,495)
```

---

## 5. STEP 3 — 의미절 → master_rule_v2 매핑 (대기)

### 5.1 스크립트 (작성 필요)

`docs/extraction/scripts/convert_clause_to_rule.py` — Cursor 작업 대기.

작업지시서: [`CURSOR_TASK_2026-05-08_convert_clause_to_rule.md`](CURSOR_TASK_2026-05-08_convert_clause_to_rule.md) (23KB).

### 5.2 변환 정책 — 모든 의미절 1:1 (제외 없음)

```python
def is_rule_candidate_v19(clause):
    """모든 의미절이 master_rule_v2 row가 됨. 분류는 rule_kind로 보존."""
    rule_kind = clause.content_type or 'UNCLASSIFIED'
    
    # None / DEFINITION 의무 어말 보유 시 content_type 역추론 (145건 보강)
    if clause.content_type in (None, 'DEFINITION'):
        if re.search(r'하여야\s*한다|해야\s*한다|할\s*수\s*있다|아니\s*된다|금지한다', 
                     clause.source_text or ''):
            if re.search(r'아니\s*된다|금지한다', clause.source_text):
                rule_kind = 'PROHIBITION'
            elif re.search(r'할\s*수\s*있다', clause.source_text):
                rule_kind = 'AUTHORITY'
            else:
                rule_kind = 'OBLIGATION'
    
    return rule_kind  # 항상 변환
```

### 5.3 핵심 결정 사항 (점검 5개 결과 반영)

```yaml
누락 위험:
  None + 의무 어말:        39건 → 변환 포함 (rule_kind 역추론)
  DEFINITION + 의무 어말: 106건 → 변환 포함 (rule_kind 역추론)
  DELEGATION executor 보유: 4,166건 → 정부 입법 행위, 사업장 매칭 제외 (rule_kind=DELEGATION 보존)

룰 그룹화 (paragraph 단위):
  1 part = 1 의미절: 81%   → 1:1 변환 OK
  1 part = 2 의미절: 17.2% → 1:1 변환 OK (대부분 다른 룰)
  1 part = 3+ 의미절: 1.7% → 1:1 변환 + master_rule_relation 후속 그룹화

신뢰도 알고리즘 (옵션 B):
  핵심 4요소 (WHO/WHAT/WHERE/WHY) 충족 = 0.7 base
  보조 (WHEN, HOW, recipient, condition) 각 +0.075
  최대 1.0
  
  근거: WHEN 14.5% / HOW 5.5%만 본 법령에 명시 (한국 법령 본질).
        cycle/form은 시행규칙·세부지침에 위임됨.

action_category_code: 13 + 'OTHER' = 14 카테고리
  21,039건 (50.4%) → 'OTHER' (대부분 추상적 의무)

EXCEPTION: 무시 (의미절에 5건뿐, v2.0 분해기 보강 사안)

scope (where):
  10.2%만 키워드 보유 (산업/설비/인원/면적/공사금액)
  90% 룰은 sectors[]만으로 사업장 매칭
  Phase B 후속 — 시행규칙 분해로 보강
```

### 5.4 명령

```bash
cd docs/extraction/scripts/

# dry-run sample 100 → 사람 검토
railway run python3 convert_clause_to_rule.py --dry-run --sample-size 100

# 전체 변환
# ⚠️ --sample-size 명시 필수 (default 100)
railway run python3 convert_clause_to_rule.py --apply --truncate-first --sample-size 100000 2>&1 | tee /tmp/convert_apply.log
```

### 5.5 검증 SQL 8개 (변환 후)

```sql
-- 1. row 수
SELECT COUNT(*) FROM master_rule_v2;
-- 예상: 58,495

-- 2. rule_kind 분포 (semantic_clause.content_type과 일치 + None 698→UNCLASSIFIED)
SELECT rule_kind, COUNT(*) FROM master_rule_v2 GROUP BY 1 ORDER BY 2 DESC;
-- 예상: OBLIGATION ~29,700, AUTHORITY ~10,500, DELEGATION ~9,000, DEFINITION ~6,400, ...

-- 3. FK 무결성
SELECT COUNT(*) FROM master_rule_v2 mrv
LEFT JOIN semantic_clause sc ON mrv.source_clause_id = sc.id
WHERE sc.id IS NULL;
-- 예상: 0

-- 4. master_rule_executor 분포
SELECT role, COUNT(*) FROM master_rule_executor GROUP BY 1;
-- 예상: EXECUTOR ~41,000, RECIPIENT ~11,000, ALTERNATIVE ~?

-- 5. master_rule_condition 행 수
SELECT COUNT(*) FROM master_rule_condition;
-- 예상: ~18,500+ (split 후)

-- 6. action_category 분포
SELECT action_category_code, COUNT(*) FROM master_rule_v2 GROUP BY 1 ORDER BY 2 DESC;
-- 예상: OTHER ~21,000, REPORT ~9,000, INSPECTION ~4,900, ...

-- 7. confidence 분포
SELECT 
  CASE 
    WHEN generation_confidence >= 0.85 THEN 'high'
    WHEN generation_confidence >= 0.7 THEN 'medium'
    ELSE 'low'
  END AS bucket,
  COUNT(*)
FROM master_rule_v2 GROUP BY 1;
-- 예상: medium ~80%, high ~15%, low ~5%

-- 8. sectors 보존
SELECT COUNT(*) FROM master_rule_v2 WHERE sectors IS NULL OR sectors = '{}';
-- 예상: 161 (INACTIVE)
```

---

## 6. STEP 4 — 사용 정책 View 4개 (대기)

매핑 완료 후 별도 마이그레이션:

```sql
-- 6.1 사업장 매칭용 (가장 중요)
CREATE OR REPLACE VIEW master_rule_v2_active AS
SELECT mrv.*
FROM master_rule_v2 mrv
WHERE mrv.rule_kind IN ('OBLIGATION', 'PROHIBITION', 'AUTHORITY')
  AND mrv.status = 'VALIDATED'
  AND array_length(mrv.sectors, 1) > 0;

-- 6.2 정부 행위 분석용
CREATE OR REPLACE VIEW master_rule_v2_government AS
SELECT * FROM master_rule_v2 WHERE rule_kind = 'DELEGATION';

-- 6.3 정의 참고용
CREATE OR REPLACE VIEW master_rule_v2_definitions AS
SELECT * FROM master_rule_v2 WHERE rule_kind = 'DEFINITION';

-- 6.4 검토 대상
CREATE OR REPLACE VIEW master_rule_v2_review_queue AS
SELECT * FROM master_rule_v2
WHERE rule_kind = 'UNCLASSIFIED' OR needs_review = true;
```

---

## 7. INCIDENT LOG (사고 + 복구)

### 7.1 [2026-05-08] decompose_v1.py --sample-size default 50 사고

**증상**: `--apply --truncate-first` 실행 시 58 clauses만 INSERT 후 종료. `[DECOMPOSE]` 라인 누락.

**원인**: argparse `--sample-size` 기본값 = 50. `--apply` 시 명시 안 해서 50건만 처리.

**복구 SQL** (안전망 — 본 테이블에서 iter1로 통째 복사):
```sql
TRUNCATE semantic_clause_iter1;
INSERT INTO semantic_clause_iter1 SELECT * FROM semantic_clause;
```
본 테이블은 v1.7.1 그대로 보존되어 데이터 손실 없음.

**정정 명령**:
```bash
railway run python3 decompose_v1.py --apply --truncate-first --sample-size 100000 --sampling random
```

**v2.0 권장**: `--sample-size` default를 모집단 처리값(예: 200000)으로 변경하거나, `--all` 옵션 추가.

---

## 8. VERSION HISTORY

### 분해기 (decompose_v1.py)

| version | 일자 | 핵심 변경 | executor 채움률 |
|---|---|---|---|
| v1.0 | 2026-05-04 | 초기 룰 13개 | — |
| v1.4 | 2026-05-05 | KEC 완료 | — |
| v1.7 | 2026-05-06 | 5요소 추출 강화 | ~70% |
| v1.7.1 | 2026-05-06 | 법 인용 prefix 제거 | 76.4% |
| v1.8 v2 | 2026-05-08 | DELEGATION 재분류 + FAKE 8 + recipient | 77.3% (sample) |
| v1.9 | 2026-05-08 | 역순 추출 본체 재설계 | 94.4% (sample) |
| **v1.9.1** | **2026-05-08** | **회귀 수정 + cleanup 강화** | **99.0% (모집단)** ⭐ |

### 매핑 (convert_clause_to_rule.py)

미작성. 작업지시서 [`CURSOR_TASK_2026-05-08_convert_clause_to_rule.md`](CURSOR_TASK_2026-05-08_convert_clause_to_rule.md) 기반.

---

## 9. V2.0 BACKLOG (남은 사안)

| # | 사안 | 영향도 | 비고 |
|---|---|---|---|
| 1 | "위원에게는" lookbehind 한계 — `(?<!에)는`이 "에게"의 "게" 뒤 "는" 통과 | 낮음 | sample 1건 발견 |
| 2 | "작성ㆍ보관하" — split_or 분해 단계 결함 | 중간 | parallel 분해 알고리즘 검토 |
| 3 | EXCEPTION 추출 빈약 (5건뿐) | 낮음 | 분해기 보강 |
| 4 | DELEGATION executor NULL 강제 규칙 4,166건 미적용 | 낮음 | content_type=DELEGATION이지만 executor 보유 |
| 5 | scope 보강 — 시행규칙/시행령 분해 | 높음 | 별도 파이프라인 |
| 6 | drafts placeholder 2,431건 매핑 | 중간 | NFTC 1,335 + 일반 674 + 고시 141 + 기타 281 |
| 7 | action_category 미분류 21,039건 → 키워드 매칭 강화 | 중간 | 또는 사람 검토로 점진 보강 |
| 8 | 사물 주어 1,532건 정확도 점검 | 중간 | needs_review로 마크됨 |
| 9 | decompose_v1.py `--all` 옵션 추가 | 낮음 | 사고 재발 방지 |

---

## 10. 작업 원칙 (불변)

1. AI/LLM 호출 0%
2. 검증 없는 완료 선언 금지 (v1.8 → v1.9 → v1.9.1 점진적 검증으로 99% 도달)
3. 패턴 발견 → 룰 보강 → 재반복
4. **누락 (false negative) 방지가 잘못 변환보다 어렵다**
5. 모든 의미절 변환, 사용 정책은 사용 단계 (View)에서 결정
6. ask_user_input_v0 사용 금지 (텍스트로 직접)
7. 200줄+ 파일은 GitHub MCP 직접 수정 금지 → Cursor 로컬
8. 분해기는 운영 레포 보관 (법령 개정 시 재실행 필요한 파이프라인 자산)
9. **본 적용 전 안전망 복구 필수** (TRUNCATE iter1 + INSERT FROM semantic_clause)
10. `--sample-size` 명시 필수 (default 50/100 사고 학습)

---

## 11. 참조 문서 (history)

이 통합 문서가 운영 진실. 다음 문서들은 history 추적용 보존:

```
docs/extraction/
├── HANDOFF_2026-05-05.md            # KEC + Phase1/2 완료
├── HANDOFF_2026-05-06_evening.md    # v1.7.1 본 적용
├── HANDOFF_2026-05-07.md            # sector 표준화 + 다중매핑 + master_rule_v2 Phase A
├── HANDOFF_FINAL_2026-05-07.md      # 어제 통합
├── HANDOFF_2026-05-08.md            # v1.9.1 본 적용 통합
│
├── PATTERN_MINING_2026-05-08.md     # v1.8 사전 채굴
├── PATTERN_MINING_2026-05-08_v2.md  # v1.9 사전 채굴 (역순 추출)
│
├── CURSOR_TASK_2026-05-08_decompose_v18_v2.md   # v1.8 v2 작업지시서
├── CURSOR_TASK_2026-05-08_decompose_v19.md      # v1.9 작업지시서 (메인)
├── CURSOR_TASK_2026-05-08_decompose_v191.md     # v1.9.1 작업지시서 (회귀 수정)
├── CURSOR_TASK_2026-05-08_convert_clause_to_rule.md  # 매핑 작업지시서 (대기)
│
├── DESIGN_master_rule_v2_2026-05-07.md  # master_rule_v2 5 테이블 스키마
│
└── scripts/
    └── decompose_v1.py              # 분해기 v1.9.1 (운영 레포 보관)
```

---

## 12. 새 세션 시작 방식 (이 문서 사용법)

**다음 Claude 세션 시작 프롬프트**:
> `docs/extraction/LEGAL_RULE_PIPELINE.md` 보고 시작. 다음 액션 진행.

또는 더 명시적으로:
> 통합 파이프라인 문서 (LEGAL_RULE_PIPELINE.md) 보고 → 0번 CURRENT STATE의 next_action 실행.

이 문서는 **30초 안에 컨텍스트 파악 → 즉시 작업 시작** 가능하도록 설계됨. 자세한 history는 11번 참조.
