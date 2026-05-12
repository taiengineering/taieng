# [Cursor 위탁] Track E Stage 1/2 Phase 2 — Kiwi 정밀화 작업 명세

**작성일**: 2026-05-10  
**작성자**: PM 창 (Claude 기획창)  
**위탁 대상**: Cursor (TAI Backend / Railway 환경)  
**선행 인계**: 마스터 핸드오프 v1.6 (`docs/extraction/v3/MASTER_HANDOFF.md`) §19.10 우선순위 1+2  
**선행 보고서**: `docs/extraction/v3/log/Track_E_20260510_Stage1_Phase1.md` + `Stage2_Phase1.md` (PM 창 본 창)

---

## 0. 본 명세의 위치

본 명세는 PM 창에서 SQL-only 환경으로 완료한 **Stage 1 Phase 1 + Stage 2 Phase 1**의 후속 단계. **Phase 1은 정규식만으로 가능한 영역만 처리**했고, **Phase 2는 Kiwi 형태소 분석기 필수 영역**을 Cursor에게 위탁.

**Phase 1 도달 상태 (DB ground truth)**:
- `stage_1_clauses`: **151,751 row** (5/5 검증 PASS)
- `stage_2_elements`: **151,751 row** (1:1, 6/6 검증)
- sub_type 정확 분류: **5.41%** (8,209건) — 정규식만으로 가능한 단편 5종
- if_pattern 명시 분류: **17.58%** (26,675건)
- **UNCLASSIFIED 143,542건 (94.59%) — 본 작업 대상**

---

## 1. 절대 원칙 (마스터 §2 — 본 작업 100% 정합 필수)

### 1.1 LLM 사용 X (마스터 §2.1)
- GPT/Claude/Gemini API 호출 금지
- "검증용/참고용"도 X (예외 없음)
- **허용**: Kiwi 형태소 분석기, 정규식, dict_legal_terms, rule_classify_subtype 룰

### 1.2 법령 보전 (마스터 §2.2)
- `stage_1_clauses.source_text`는 절대 변경 X
- 본 작업은 메타데이터 채우기만 (UPDATE — INSERT 후 채워지는 NULL 컬럼들)

### 1.3 누락 0건 (마스터 §2.3)
- 분해/분류 어려운 row는 **UNCLASSIFIED 유지** (본 룰로 분류 안 되면 그대로 둠)
- "어려우니 제외"는 절대 금지

### 1.4 100% 매핑 (마스터 §2.4)
- stage_1_clauses 151,751 = 작업 후에도 151,751 (row 수 변동 X)
- stage_2_elements 151,751 = 작업 후에도 151,751 (row 수 변동 X)
- 본 작업은 UPDATE만, INSERT/DELETE X

### 1.5 오염 = 데이터셋 단위 폐기 (마스터 §2.5)
- 룰 적용 도중 오염 발견 시 → 백업으로 롤백 → 룰 수정 → 재실행
- 부분 polish (오염된 row만 수정) **금지**

### 1.6 검증 부담 0 (마스터 §2.6)
- 사용자에게 sample 검증 요청 X (100조문 sample 검증은 본 명세 §6.4 자동화 절차로 진행)

### 1.7 Ground Truth 우선 (마스터 §2.7)
- Phase 1에서 분류된 5.41% 결과는 **그대로 보전** (덮어쓰기 X)
- Phase 2는 **UNCLASSIFIED 143,542건만 대상**으로 분류 시도

### 1.8 DB가 ground truth (마스터 §2.7 v1.4)
- 진입 시 1차 작업 = DB 사실 재확인
- 본 명세의 행 수, 룰 수, sub_type 분포 모두 **DB 직접 점검 후 작업 시작**

---

## 2. 작업 환경

| 항목 | 값 |
|---|---|
| Supabase Project ID | `vwlahtguyggrhvslabax` (서울) |
| 작업 환경 | `railway run python3 ...` (Railway, Track A 인프라) |
| 코드 base | `taiengineering/tai-api` (engine/morpheme.py + engine/stage_1.py + engine/stage_2.py) |
| Kiwi 자동 로드 | `engine.user_dict_size == 1725` (Track C v1.2 ground truth) |
| 룰 DB 테이블 | `rule_clause_split` (11), `rule_classify_subtype` (23), `rule_classify_if_pattern` (8) — 모두 적재 완료 |

**진입 점검 SQL** (작업 시작 전 1차 실행 필수, 마스터 §2.7):

```sql
-- 1. row 수 ground truth 확인
SELECT 'stage_1_clauses' AS tbl, COUNT(*) AS rows FROM stage_1_clauses
UNION ALL SELECT 'stage_2_elements', COUNT(*) FROM stage_2_elements
UNION ALL SELECT 'rule_classify_subtype enabled', COUNT(*) FROM rule_classify_subtype WHERE enabled = true
UNION ALL SELECT 'rule_classify_if_pattern enabled', COUNT(*) FROM rule_classify_if_pattern WHERE enabled = true;

-- 예상: 151751 / 151751 / 23 / 8

-- 2. UNCLASSIFIED 정확한 수
SELECT sub_type, COUNT(*) FROM stage_2_elements GROUP BY sub_type ORDER BY COUNT(*) DESC;
-- UNCLASSIFIED 143,542 정합 확인

-- 3. NULL 컬럼 정확한 수 (Phase 2 작업 영역)
SELECT 
  COUNT(*) FILTER (WHERE tokenization_json IS NULL) AS s1_tokenization_null,
  COUNT(*) FILTER (WHERE split_rule_id IS NULL) AS s1_split_rule_null,
  COUNT(*) FILTER (WHERE char_start IS NULL) AS s1_char_start_null
FROM stage_1_clauses;
-- 예상: 151,751 / 151,751 / 151,751 (모두 NULL)
```

작업 시작 전 위 결과가 명세와 다르면 **즉시 정지** + PM 창 회신 (DB 변동 발생 가능성 검토).

---

## 3. 백업 (마스터 §3.2 정합, 작업 시작 전 필수)

```sql
CREATE TABLE stage_1_clauses_backup_20260510_pre_phase2 AS SELECT * FROM stage_1_clauses;
CREATE TABLE stage_2_elements_backup_20260510_pre_phase2 AS SELECT * FROM stage_2_elements;

-- 검증
SELECT 
  (SELECT COUNT(*) FROM stage_1_clauses_backup_20260510_pre_phase2) AS s1_backup,
  (SELECT COUNT(*) FROM stage_2_elements_backup_20260510_pre_phase2) AS s2_backup;
-- 예상: 151,751 / 151,751
```

백업 row 수가 본체와 다르면 즉시 정지.

---

## 4. Stage 1 Phase 2 — 메타데이터 보강 (UPDATE)

### 4.1 작업 본질

Stage 1 Phase 1에서 NULL로 둔 3 컬럼을 채움. 의미적 효과 X (Stage 3 진입에 필수 X), 추적성·재현성 보강용.

### 4.2 채울 컬럼

| 컬럼 | 정체 | 채움 방식 |
|---|---|---|
| `tokenization_json` | Kiwi 토큰화 결과 jsonb | 각 source_text를 Kiwi로 분석 → `[{"form":"...", "tag":"NNG", "start":0, "len":2}, ...]` |
| `split_rule_id` | 어느 rule_clause_split 매칭 | DELIMITER_HANDA 등 11개 룰 중 적용된 룰 ID. 매칭 안 된 fallback row는 NULL 유지 |
| `char_start` / `char_end` | part_text 내 start/end (정수) | 본 row의 source_text가 part_text의 어느 위치에서 추출됐는지 |

### 4.3 임의판단 금지 규칙

| 항목 | 금지 사항 | 허용 |
|---|---|---|
| 토큰화 결과 | 토큰을 임의로 합치거나 자르기 | Kiwi 결과 그대로 jsonb 적재 |
| split_rule_id | "비슷해 보이는 룰 매칭" 추정 | 정확히 종결어 substring 매칭만 |
| char_start | source_text 발견 위치 추정 | `part_text.find(source_text)` 정확 매칭만 |
| 매칭 실패 row | 강제 매칭 | NULL 유지 (마스터 §2.7) |

### 4.4 적용 SQL (배치 1,000 row 단위)

Cursor 코드 (`engine/stage_1.py` 활용):

```python
from engine.morpheme import MorphemeEngine
from db.supabase_client import get_supabase
import json

engine = MorphemeEngine()  # 자동 로드 (1,725 verified terms)
sb = get_supabase()

BATCH_SIZE = 1000
total = 151751

for offset in range(0, total, BATCH_SIZE):
    batch = sb.table('stage_1_clauses').select(
        'id, source_text, part_id'
    ).range(offset, offset + BATCH_SIZE - 1).execute().data
    
    updates = []
    for row in batch:
        # 1. Kiwi 토큰화
        tokens = engine.tokenize(row['source_text'])  # [(form, tag, start, len), ...]
        tok_json = [{"form": t[0], "tag": t[1], "start": t[2], "len": t[3]} for t in tokens]
        
        # 2. split_rule_id 매칭 (종결어 정확 매칭)
        split_rule_id = match_split_rule(row['source_text'])  # 11 룰 중 1개 또는 None
        
        # 3. char_start/char_end (part_text 내 위치)
        part_text = sb.table('law_article_part').select('part_text').eq('id', row['part_id']).single().execute().data['part_text']
        char_start = part_text.find(row['source_text'])
        char_end = char_start + len(row['source_text']) if char_start >= 0 else None
        
        updates.append({
            'id': row['id'],
            'tokenization_json': tok_json,
            'split_rule_id': split_rule_id,
            'char_start': char_start if char_start >= 0 else None,
            'char_end': char_end
        })
    
    # batch UPDATE
    for u in updates:
        sb.table('stage_1_clauses').update({
            'tokenization_json': u['tokenization_json'],
            'split_rule_id': u['split_rule_id'],
            'char_start': u['char_start'],
            'char_end': u['char_end']
        }).eq('id', u['id']).execute()
```

### 4.5 검증

```sql
-- 4.5.1 NULL 비율
SELECT 
  100.0 * COUNT(*) FILTER (WHERE tokenization_json IS NULL) / COUNT(*) AS tokenization_null_pct,
  100.0 * COUNT(*) FILTER (WHERE char_start IS NULL) / COUNT(*) AS char_start_null_pct,
  100.0 * COUNT(*) FILTER (WHERE split_rule_id IS NULL) / COUNT(*) AS split_rule_null_pct
FROM stage_1_clauses;
-- 예상: tokenization_json 0%, char_start 0%, split_rule_id ~5% (fallback row, 정규식 매칭 안 된 경우)

-- 4.5.2 char_start 범위 정합
SELECT COUNT(*) FROM stage_1_clauses 
WHERE char_start IS NOT NULL AND char_start < 0;
-- 예상: 0 (음수 char_start 없어야 함)
```

검증 임계:
- tokenization_json NULL ≤ 0.1% (kiwi 토큰화 실패 케이스)
- char_start NULL ≤ 5% (part_text와 source_text 불일치 케이스 — 본 작업 한계)
- split_rule_id NULL ≤ 95% (대부분 fallback row, 정상)

---

## 5. Stage 2 Phase 2 — Kiwi 기반 sub_type 정밀 분류 (UPDATE)

### 5.1 작업 본질

UNCLASSIFIED 143,542건을 23 sub_type 룰 (rule_classify_subtype)을 적용하여 정확 분류.

**중요**: rule_classify_subtype의 match_strategy ∈ {TAIL_POS, HEAD_TOKEN, POS_SEQUENCE, COMPOSITE} — **REGEX 없음**. Kiwi 토큰화 필수.

### 5.2 적용 대상 룰 (DB에서 SELECT)

```sql
-- 활성화된 23 룰 모두 (priority 순)
SELECT id, rule_name, sub_type, match_strategy, pattern_definition, priority
FROM rule_classify_subtype
WHERE enabled = true
ORDER BY priority ASC;
```

각 룰의 `pattern_definition` jsonb 구조 (룰별로 다름):
- TAIL_POS 룰 (예: OBLIGATION_HEADER): 마지막 N 토큰의 (form, tag) 시퀀스 매칭
- HEAD_TOKEN 룰 (예: DEFINITION_INTRO): 첫 N 토큰 매칭
- POS_SEQUENCE 룰: 임의 위치의 POS 시퀀스 매칭
- COMPOSITE 룰: 여러 시그니처 조합

### 5.3 적용 우선순위 (priority ASC)

priority가 작은 룰부터 적용 (작은 priority = 더 정확/우선). 한 row가 여러 룰 매칭 시 **첫 번째 priority 룰의 sub_type 적용**.

priority 분포 (예상):
- 10-99: HEADER 8 (OBLIGATION/PROHIBITION/PENALTY/AUTHORITY/EXEMPTION/DEFINITION/DELEGATION_ACTIVE/AS_본다)
- 100-199: ITEM 2 (OBLIGATION_DETAIL_ITEM / PENALTY_VIOLATOR_ITEM)
- 200-299: 단편 5 (Phase 1에서 직접 적용했으므로 본 단계에서 재적용 X)
- 300-399: 단서 1 (Phase 1 적용)
- 400-499: 약함 2 (WEAK_한다단순/WEAK_있다단순 — fallback)

### 5.4 임의판단 금지 규칙

| 항목 | 금지 사항 | 허용 |
|---|---|---|
| sub_type 분류 | DB CHECK 외 새 sub_type 생성 | rule_classify_subtype.sub_type 25개 enum만 |
| pattern_definition 해석 | 패턴 외 추가 조건 임의 추가 | 룰 정의된 패턴만 |
| priority 무시 | 사람이 보기 좋아 보이는 룰 선택 | priority ASC 첫 매칭 룰 |
| Phase 1 결과 덮어쓰기 | sub_type ≠ UNCLASSIFIED인 row 재분류 | UNCLASSIFIED만 대상 |
| WEAK fallback | 강제 분류 | 어느 룰도 매칭 안 되면 UNCLASSIFIED 유지 또는 WEAK_* (룰 정의대로) |
| 다중 매칭 | 임의 선택 | priority 가장 작은 룰 선택 |
| Phase 1 분류 결과 | 변경 X | DELETED 1,768 + EXCEPTION_CLAUSE 6,117 + DEFINITION_INTRO 142 + TITLE_HEADER 94 + DATE_EFFECTIVE 88 보전 |

### 5.5 적용 코드 패턴 (`engine/stage_2.py` 활용)

```python
from engine.morpheme import MorphemeEngine
from engine.stage_2 import Stage2Decomposer
from db.supabase_client import get_supabase

engine = MorphemeEngine()
decomposer = Stage2Decomposer(engine)
sb = get_supabase()

# 1. 활성화 룰 로드 (priority ASC)
rules = sb.table('rule_classify_subtype').select('*').eq('enabled', True).order('priority').execute().data
print(f"Loaded {len(rules)} sub_type rules")
assert len(rules) == 23, "rule_classify_subtype 23개 정합 깨짐 — 즉시 정지"

# 2. UNCLASSIFIED 대상만 (Phase 1 분류 보전)
BATCH_SIZE = 500  # tokenization 비용 고려
total_unclassified = 143542

offset = 0
while offset < total_unclassified:
    batch = sb.table('stage_2_elements').select(
        'id, clause_id, sub_type'
    ).eq('sub_type', 'UNCLASSIFIED').range(offset, offset + BATCH_SIZE - 1).execute().data
    
    if not batch:
        break
    
    # 3. clause_id로 source_text + tokenization_json 가져오기 (Phase 1 결과 활용)
    clause_ids = [r['clause_id'] for r in batch]
    clauses = sb.table('stage_1_clauses').select(
        'id, source_text, tokenization_json'
    ).in_('id', clause_ids).execute().data
    clause_map = {c['id']: c for c in clauses}
    
    # 4. 룰 priority ASC 순으로 매칭 시도
    updates = []
    for elem in batch:
        clause = clause_map.get(elem['clause_id'])
        if not clause or not clause['tokenization_json']:
            continue  # tokenization 없으면 분류 불가, UNCLASSIFIED 유지
        
        tokens = clause['tokenization_json']
        matched_rule = None
        for rule in rules:  # priority ASC
            if decomposer.match_rule(rule, tokens, clause['source_text']):
                matched_rule = rule
                break  # 첫 매칭 적용
        
        if matched_rule:
            updates.append({
                'id': elem['id'],
                'sub_type': matched_rule['sub_type'],
                'classify_rule_id': matched_rule['id'],
                'confidence_score': 0.85  # 룰 정확 매칭 시 base
            })
    
    # 5. UPDATE batch
    for u in updates:
        sb.table('stage_2_elements').update({
            'sub_type': u['sub_type'],
            'classify_rule_id': u['classify_rule_id'],
            'confidence_score': u['confidence_score']
        }).eq('id', u['id']).execute()
    
    offset += BATCH_SIZE
    print(f"Processed {offset}/{total_unclassified} (matched in batch: {len(updates)})")
```

### 5.6 6하원칙 분해 (executor / recipient / what / when_value / where_value / how / condition)

**적용 대상**: Phase 2 분류 후 sub_type ≠ UNCLASSIFIED 인 row만 (분류된 의미가 있는 것만 분해).

**임의판단 금지**:
- LLM 추론 X
- Kiwi POS 태그 시그니처 + dict_legal_terms 매칭만 사용
- 발견 안 되면 NULL 유지 (강제 채움 X)

**POS 시그니처 룰** (engine/stage_2.py에 정의 또는 신규 추가):

| 필드 | 시그니처 |
|---|---|
| executor | 주격 조사 (이/가/은/는) 앞 NNG/NNP — 행위자 |
| recipient | 여격 조사 (에게/한테) 앞 NNG/NNP — 수혜자 |
| what | VV (동사) 또는 NNG (행위 명사) — 행위/목적어 |
| when_value | 날짜/기간 표현 (NNB + 명사) — 시점 |
| where_value | 처격 조사 (에/에서) 앞 NNG/NNP — 장소/대상 |
| how | 부사절 (MAG) 또는 도구격 (로/으로) — 방법 |
| condition | 조건 표현 (~경우, ~때) — 조건 |

각 필드는 **첫 매칭만** 추출 (다중 매칭 무시). 발견 안 되면 NULL.

### 5.7 검증 (마스터 §3.4 정합)

```sql
-- 5.7.1 sub_type 정확 분류율 (UNCLASSIFIED 외)
SELECT 
  100.0 * COUNT(*) FILTER (WHERE sub_type != 'UNCLASSIFIED') / COUNT(*) AS classified_pct
FROM stage_2_elements;
-- 임계: ≥ 70% (Phase 2 목표), 이상적 ≥ 90%

-- 5.7.2 sub_type 분포
SELECT sub_type, COUNT(*) FROM stage_2_elements GROUP BY sub_type ORDER BY COUNT(*) DESC;

-- 5.7.3 6하원칙 채움률 (sub_type 분류된 row만)
SELECT 
  100.0 * COUNT(*) FILTER (WHERE executor IS NOT NULL) / COUNT(*) AS executor_pct,
  100.0 * COUNT(*) FILTER (WHERE recipient IS NOT NULL) / COUNT(*) AS recipient_pct,
  100.0 * COUNT(*) FILTER (WHERE what IS NOT NULL) / COUNT(*) AS what_pct
FROM stage_2_elements WHERE sub_type != 'UNCLASSIFIED';
-- 임계: 각 필드 ≥ 50% (HEADER/ITEM은 더 높을 것)

-- 5.7.4 100조문 sample 자동 검증 (마스터 §3.4)
-- 무작위 100 article 추출 → 해당 article의 stage_2_elements 분류 결과 → 룰 패턴 정합 자동 확인
WITH sample_articles AS (
  SELECT id FROM law_article ORDER BY random() LIMIT 100
)
SELECT 
  COUNT(*) AS total_clauses,
  COUNT(*) FILTER (WHERE s2.sub_type != 'UNCLASSIFIED') AS classified,
  100.0 * COUNT(*) FILTER (WHERE s2.sub_type != 'UNCLASSIFIED') / NULLIF(COUNT(*), 0) AS sample_classify_pct
FROM stage_2_elements s2
JOIN stage_1_clauses s1 ON s1.id = s2.clause_id
JOIN law_article_part lap ON lap.id = s1.part_id
JOIN sample_articles sa ON sa.id = lap.article_id;
-- 임계: ≥ 70% (sample 정확도)
```

### 5.8 verification_log 적재 (Track A validator.py 정합)

```sql
INSERT INTO verification_log (stage, check_name, check_type, result_status, expected_value, actual_value, threshold, error_count, error_examples, verified_by, notes) VALUES
  (2, 'phase_2_classify_pct', 'AUTO_HOOK', 'PASS_OR_FAIL', '≥70%', '실측%', '70', 0, '[]'::jsonb, 'Cursor_Phase_2_2026-05-XX', 'UNCLASSIFIED 143,542 → 정밀 분류'),
  (2, 'phase_2_six_w_executor', 'AUTO_HOOK', 'PASS_OR_FAIL', '≥50%', '실측%', '50', 0, '[]'::jsonb, 'Cursor_Phase_2', '6하원칙 executor 채움률'),
  (2, 'phase_2_six_w_what', 'AUTO_HOOK', 'PASS_OR_FAIL', '≥50%', '실측%', '50', 0, '[]'::jsonb, 'Cursor_Phase_2', '6하원칙 what 채움률'),
  (2, 'phase_2_sample_100', 'AUTO_HOOK', 'PASS_OR_FAIL', '≥70%', '실측%', '70', 0, '[]'::jsonb, 'Cursor_Phase_2', '100조문 sample 자동 검증'),
  (1, 'phase_2_tokenization_filled', 'AUTO_HOOK', 'PASS_OR_FAIL', '≥99.9%', '실측%', '99.9', 0, '[]'::jsonb, 'Cursor_Phase_2', 'Stage 1 tokenization_json 채움'),
  (1, 'phase_2_split_rule_filled', 'AUTO_HOOK', 'INFO', '~5% null (fallback)', '실측%', '95', 0, '[]'::jsonb, 'Cursor_Phase_2', 'Stage 1 split_rule_id 매칭 (fallback row null 정상)');
```

verification_log stage CHECK ∈ {1, 2, 3}, result_status ∈ {PASS, FAIL, INFO} — DB 점검 후 정확한 enum 사용.

---

## 6. 작업 절차 (체크리스트)

### 6.1 사전 점검 (필수, 마스터 §2.7)
- [ ] §2 진입 점검 SQL 실행, 모든 row 수 정합 확인
- [ ] 결과가 명세와 다르면 즉시 정지 + PM 회신

### 6.2 백업 (필수, 마스터 §2.5)
- [ ] §3 백업 SQL 실행, row 수 정합 확인

### 6.3 Stage 1 Phase 2 (메타데이터 보강)
- [ ] §4.4 Python 코드 실행 (151,751 row, BATCH_SIZE=1000)
- [ ] §4.5 검증 SQL 실행, 임계 통과 확인

### 6.4 Stage 2 Phase 2 (sub_type 정밀 분류)
- [ ] §5.5 Python 코드 실행 (UNCLASSIFIED 143,542 row, BATCH_SIZE=500)
- [ ] sub_type 정확 분류율 ≥ 70% 확인 (§5.7.1)
- [ ] 임계 미달 시 정지 + PM 회신 (룰 정밀화 필요 가능성)

### 6.5 Stage 2 Phase 2 (6하원칙 분해)
- [ ] §5.6 시그니처 룰 적용 (sub_type ≠ UNCLASSIFIED 대상만)
- [ ] §5.7.3 채움률 검증 (≥ 50%)

### 6.6 검증 + verification_log
- [ ] §5.7 모든 검증 SQL 실행
- [ ] §5.8 verification_log INSERT
- [ ] 100조문 sample 정확도 ≥ 70% 확인

### 6.7 보고서 작성 + GitHub commit
- [ ] `docs/extraction/v3/log/Track_E_20260510_Phase2.md` 작성 (§7 양식)
- [ ] commit message: `docs(v3): Track E Stage 1/2 Phase 2 — Kiwi 정밀화 + 6하원칙 분해`

---

## 7. 보고서 양식 (필수)

```markdown
# [Track E] Phase 2 — Kiwi 정밀화 + 6하원칙 분해

## 1. 사전 점검 결과
- (진입 점검 SQL 결과 표)

## 2. 백업
- stage_1_clauses_backup_20260510_pre_phase2 row: ___
- stage_2_elements_backup_20260510_pre_phase2 row: ___

## 3. Stage 1 Phase 2 결과
| 컬럼 | NULL 전 | NULL 후 | 채움률 |
|---|---|---|---|
| tokenization_json | 151,751 | ___ | ___% |
| split_rule_id | 151,751 | ___ | ___% |
| char_start | 151,751 | ___ | ___% |

## 4. Stage 2 Phase 2 결과 — sub_type 분류
| sub_type | Phase 1 | Phase 2 추가 | 누계 | 비율 |
|---|---|---|---|---|
| OBLIGATION_HEADER | 0 | ___ | ___ | __% |
| ... |
| **UNCLASSIFIED** | 143,542 | (-___) | ___ | __% |

**총 정확 분류율: ___%**

## 5. Stage 2 Phase 2 결과 — 6하원칙 채움률
| 필드 | 채움 row | 채움률 |
|---|---|---|
| executor | ___ | ___% |
| recipient | ___ | ___% |
| what | ___ | ___% |
| when_value | ___ | ___% |
| where_value | ___ | ___% |
| how | ___ | ___% |
| condition | ___ | ___% |

## 6. 검증 결과
| check_name | expected | actual | status |
|---|---|---|---|
| phase_2_classify_pct | ≥ 70% | ___% | PASS/FAIL |
| ... |

## 7. 절대 원칙 점검 (마스터 §2)
| 원칙 | 적용 |
|---|---|
| ① LLM X | ✅ |
| ② 법령 보전 | ✅ source_text 변경 X |
| ... |

## 8. 다음 단계
- Stage 3 진입 가능 여부: (분류율 ≥ 70% 도달 시 가능)
- v3.0 마스터 객체 테이블 결정 (사용자 결정 펜딩)
```

---

## 8. 중단/회신 트리거 (Cursor 자체 판단 X)

다음 중 하나라도 발생 시 **즉시 작업 정지** + PM 창 회신:

1. 진입 점검 SQL 결과가 명세와 다름 (DB row 수 변동 등)
2. Kiwi 토큰화 실패율 > 1% (1,517 row 이상)
3. sub_type 정확 분류율 < 60% (Phase 2 목표 70% 미달이 너무 큼 — 룰 정밀화 필요)
4. 룰 적용 결과 기존 분류 (DELETED/EXCEPTION_CLAUSE/DEFINITION_INTRO/TITLE_HEADER/DATE_EFFECTIVE) 덮어쓰는 row 발견
5. 백업 row 수 ≠ 본체 row 수 (백업 실패)
6. UNCLASSIFIED → DELETED/PARSE_FRAGMENT 로 분류된 row 발생 (Phase 1에서 처리됐어야 함, 룰 충돌 의심)
7. row 수 변동 (151,751 → 다른 수) — INSERT/DELETE 발생 의심

---

## 9. 본 명세 외 작업 (절대 X)

다음 작업은 **본 명세에 포함되지 않음**. Cursor 임의 추가 X:

- ❌ Stage 3 진입 (rule_objectify 적용) — 본 PM 결정 후 별도 명세
- ❌ v3.0 마스터 객체 테이블 마이그레이션 — 사용자 결정 펜딩
- ❌ Tier 2 본법 13건 수집 — 별도 명세
- ❌ rule_classify_subtype 룰 신규 추가 — 본 명세는 23 룰만 적용
- ❌ Phase 1 결과 (5.41% 분류된 row) 변경
- ❌ stage_3_objects 적재
- ❌ object_* 마스터 테이블 CREATE

---

## 10. 산출물 commit 위치

- 보고서: `docs/extraction/v3/log/Track_E_20260510_Phase2.md`
- 백업 테이블: DB에 보전 (별도 commit 없음)

---

**END — 본 명세를 따라 임의판단 없이 진행. 검증 임계 통과 + 보고서 commit + PM 회신.**
