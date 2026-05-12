# [Cursor 위탁] Phase 2.2 — 정확도 보강 + sub_type 구조 확장

**작성일**: 2026-05-10  
**작성자**: PM 창 (Claude 기획창)  
**위탁 대상**: Cursor (TAI Backend / Railway)  
**선행**: 
- `Track_E_20260510_Phase2_1.md` (Cursor Phase 2.1 보고서)
- `Track_E_20260510_Phase2_1_Reverse_Validation.md` (PM 정확도 진단)
- 사용자 PM 결정: "정확도를 올리는 방향으로 진행"

---

## 0. 본 명세의 본질

Phase 2.1은 분류율 55.10% 도달했으나 PM 진단 결과 **정확도 ~50%만**:
- AS_본다 보조 룰 3종 → 모두 FP (3,267건)
- DELEGATION_ETRAHADA → ~80% FP (~977건)
- OBLIGATION_DETAIL_GWAN_SAHANG → 모두 FP (2,389건)
- WEAK_JUNYONG_HADA → sub_type 부정확 (1,080건)
- UC 명사 종결 단편 → 분류 가능 (~59,000건)

**본 명세 본질**: 정확도 ~50% → ~90%+ 도달.

---

## 1. 절대 원칙 (마스터 §2 — 100% 정합 필수)

### 1.1 LLM 미사용 (마스터 §2.1)
- 룰 작성·sample 분석 모두 LLM 호출 X
- Kiwi + 정규식 + DB 빈도만

### 1.2 법령 보전 (마스터 §2.2)
- source_text / tokenization_json 변경 X

### 1.3 누락 0건 (마스터 §2.3)
- row 수 변동 X (151,751 동일)
- 룰 매칭 X → UNCLASSIFIED 유지 (강제 분류 X)

### 1.4 100% 매핑 (마스터 §2.4)
- UPDATE만 (sub_type 재매핑 + 신규 분류)
- INSERT/DELETE X (단 신규 룰 INSERT는 허용)

### 1.5 오염 = 폐기 (마스터 §2.5)
- 본 작업의 sub_type 재매핑은 "오염 정정"이 아니라 **룰 정의 정정**으로 진행
- row 수 보전, source_text 보전 → 마스터 §2.5 폐기 트리거 미해당

### 1.6 Phase 1/2.1 보전 (마스터 §2.7)
- Phase 1 분류 8,303건 (Phase 1 +94 포함) — **절대 변경 X**
- Phase 2.1 분류 75,318건 (Phase 1 외 분류) — **재매핑 가능 (FP 정정)**

### 1.7 DB가 ground truth (마스터 §2.7 v1.4)
- 진입 시 DB 사실 재확인
- PM 진단(`Phase2_1_Reverse_Validation.md`)은 reference만, sample 점검으로 직접 검증

### 1.8 검증 부담 0 (마스터 §2.6)
- 사용자 sample 검증 요청 X

---

## 2. 작업 환경

| 항목 | 값 |
|---|---|
| Supabase Project ID | `vwlahtguyggrhvslabax` |
| 환경 | `railway run python3 ...` |
| 코드 base | `taiengineering/tai-api` (engine/subtype_rule_match.py / scripts/track_e_phase2_run.py) |
| 룰 DB | `rule_classify_subtype` (현재 35: 활성 34 / 비활성 1) |

### 2.1 진입 점검 SQL (필수)

```sql
-- 1. row 수 + sub_type 분포
SELECT 
  (SELECT COUNT(*) FROM stage_2_elements) AS total,
  (SELECT COUNT(*) FROM stage_2_elements WHERE sub_type='UNCLASSIFIED') AS uc,
  (SELECT COUNT(*) FROM rule_classify_subtype WHERE enabled=true) AS active_rules;
-- 예상: 151,751 / 68,130 / 34

-- 2. CHECK enum 확인
SELECT cc.check_clause 
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc ON tc.constraint_name = cc.constraint_name
WHERE tc.table_name='stage_2_elements' AND tc.constraint_type='CHECK' AND cc.check_clause LIKE '%sub_type%';
-- 예상: 25 enum (ENUMERATION_ITEM 포함, ENUMERATION_LIST_INTRO/REFERENCE_TO_ATTACHMENT/REFERENCE_INVOCATION 미포함)
```

→ 결과가 명세와 다르면 즉시 정지 + PM 회신.

---

## 3. 백업 (필수)

```sql
CREATE TABLE rule_classify_subtype_backup_20260510_pre_phase2_2 AS 
  SELECT * FROM rule_classify_subtype;

CREATE TABLE stage_2_elements_backup_20260510_pre_phase2_2 AS 
  SELECT * FROM stage_2_elements;

-- 검증
SELECT 
  (SELECT COUNT(*) FROM rule_classify_subtype_backup_20260510_pre_phase2_2) AS rules,
  (SELECT COUNT(*) FROM stage_2_elements_backup_20260510_pre_phase2_2) AS elems;
-- 예상: 35 / 151,751
```

---

## 4. DB CHECK enum 확장 (마이그레이션)

### 4.1 신규 sub_type 3개 추가

기존 25 enum + **신규 3개**:
- ENUMERATION_LIST_INTRO
- REFERENCE_TO_ATTACHMENT
- REFERENCE_INVOCATION

### 4.2 마이그레이션 SQL

```sql
-- (1) 기존 CHECK 제약 DROP
ALTER TABLE stage_2_elements DROP CONSTRAINT stage_2_elements_sub_type_check;
ALTER TABLE rule_classify_subtype DROP CONSTRAINT rule_classify_subtype_sub_type_check;

-- (2) 신규 CHECK 제약 추가 (28 enum)
ALTER TABLE stage_2_elements ADD CONSTRAINT stage_2_elements_sub_type_check
CHECK (sub_type = ANY (ARRAY[
  'OBLIGATION_HEADER', 'PROHIBITION_HEADER', 'PENALTY_HEADER', 'AUTHORITY_HEADER',
  'EXEMPTION_HEADER', 'DEFINITION_HEADER', 'DELEGATION_ACTIVE', 'AS_본다',
  'OBLIGATION_DETAIL_ITEM', 'PENALTY_VIOLATOR_ITEM', 'AUTHORITY_TARGET_ITEM',
  'EXEMPTION_TARGET_ITEM', 'DEFINITION_TARGET_ITEM', 'PROHIBITION_TARGET_ITEM',
  'DELETED', 'DEFINITION_INTRO', 'TITLE_HEADER', 'DATE_EFFECTIVE',
  'PARSE_FRAGMENT', 'DELEGATED_WAIVER', 'ENUMERATION_ITEM', 'EXCEPTION_CLAUSE',
  'WEAK_한다단순', 'WEAK_있다단순', 'UNCLASSIFIED',
  -- 신규 3개
  'ENUMERATION_LIST_INTRO', 'REFERENCE_TO_ATTACHMENT', 'REFERENCE_INVOCATION'
]));

ALTER TABLE rule_classify_subtype ADD CONSTRAINT rule_classify_subtype_sub_type_check
CHECK (sub_type = ANY (ARRAY[
  -- 위와 동일 28 enum
  'OBLIGATION_HEADER', 'PROHIBITION_HEADER', 'PENALTY_HEADER', 'AUTHORITY_HEADER',
  'EXEMPTION_HEADER', 'DEFINITION_HEADER', 'DELEGATION_ACTIVE', 'AS_본다',
  'OBLIGATION_DETAIL_ITEM', 'PENALTY_VIOLATOR_ITEM', 'AUTHORITY_TARGET_ITEM',
  'EXEMPTION_TARGET_ITEM', 'DEFINITION_TARGET_ITEM', 'PROHIBITION_TARGET_ITEM',
  'DELETED', 'DEFINITION_INTRO', 'TITLE_HEADER', 'DATE_EFFECTIVE',
  'PARSE_FRAGMENT', 'DELEGATED_WAIVER', 'ENUMERATION_ITEM', 'EXCEPTION_CLAUSE',
  'WEAK_한다단순', 'WEAK_있다단순', 'UNCLASSIFIED',
  'ENUMERATION_LIST_INTRO', 'REFERENCE_TO_ATTACHMENT', 'REFERENCE_INVOCATION'
]));

-- (3) 검증
SELECT cc.check_clause FROM information_schema.check_constraints cc
WHERE cc.constraint_name IN ('stage_2_elements_sub_type_check', 'rule_classify_subtype_sub_type_check');
-- 28 enum 확인
```

→ Cursor가 `Supabase:apply_migration` 또는 `apply_migration` 도구로 진행. migration name: `phase_2_2_subtype_enum_extension`.

---

## 5. 룰 sub_type 재매핑 (FP 정정)

### 5.1 AS_본다 보조 룰 3종 분할

기존 룰을 폐기하지 않고 **`pattern_position` 또는 추가 조건으로 분할**. 가장 명확한 방법: **신규 룰 INSERT (높은 priority) + 기존 룰 sub_type 변경 (낮은 priority fallback)**.

```sql
-- (1) 신규 룰: ENUMERATION_LIST_INTRO_DAUM (다음 각 호와 같다 / 다음과 같다)
INSERT INTO rule_classify_subtype 
  (rule_name, sub_type, match_strategy, pattern, pattern_position, priority, enabled, description)
VALUES (
  'ENUMERATION_LIST_INTRO_DAUM_GACHO',
  'ENUMERATION_LIST_INTRO',
  'COMPOSITE',
  '"다음\s*각\s*호와\s*같다\.?$"'::jsonb,  -- 정규식
  'TAIL_REGEX',
  85,  -- AS_본다_TAIL3 (80) 다음, AS_본다 보조 (81-83) 앞
  true,
  '다음 각 호와 같다 종결 — enumeration 도입'
),
(
  'ENUMERATION_LIST_INTRO_DAUMGWA',
  'ENUMERATION_LIST_INTRO',
  'COMPOSITE',
  '"다음과\s*같다\.?$"'::jsonb,
  'TAIL_REGEX',
  86,
  true,
  '다음과 같다 종결 — enumeration 도입'
);

-- (2) 신규 룰: REFERENCE_TO_ATTACHMENT (별표/별지)
INSERT INTO rule_classify_subtype VALUES (
  'REFERENCE_TO_ATTACHMENT_BYPYO_GATDA',
  'REFERENCE_TO_ATTACHMENT',
  'COMPOSITE',
  '"별표\s*\d+(?:의\d+)?와?\s*같다\.?$"'::jsonb,
  'TAIL_REGEX',
  87,
  true,
  '별표 N과 같다 종결 — 별표 참조'
), (
  'REFERENCE_TO_ATTACHMENT_BYPYO_TTAREUNDA',
  'REFERENCE_TO_ATTACHMENT',
  'COMPOSITE',
  '"별표\s*\d+(?:의\d+)?(?:의\s*기준)?에\s*따른다\.?$"'::jsonb,
  'TAIL_REGEX',
  72,  -- DELEGATION_ETRAHADA (71) 앞
  true,
  '별표 N에 따른다 종결 — 별표 참조'
), (
  'REFERENCE_TO_ATTACHMENT_BYJI_GATDA',
  'REFERENCE_TO_ATTACHMENT',
  'COMPOSITE',
  '"별지\s*제\d+호\s*서식과?\s*같다\.?$"'::jsonb,
  'TAIL_REGEX',
  88,
  true,
  '별지 제N호 서식과 같다 종결'
), (
  'REFERENCE_TO_ATTACHMENT_BYJI_TTAREUNDA',
  'REFERENCE_TO_ATTACHMENT',
  'COMPOSITE',
  '"별지\s*제\d+호\s*서식에\s*따른다\.?$"'::jsonb,
  'TAIL_REGEX',
  73,
  true,
  '별지 제N호 서식에 따른다 종결'
);

-- (3) 신규 룰: REFERENCE_INVOCATION (준용)
INSERT INTO rule_classify_subtype VALUES (
  'REFERENCE_INVOCATION_JUNYONG',
  'REFERENCE_INVOCATION',
  'TAIL_POS',
  '{"tokens": [{"form":"준용","tag":"NNG"},{"form":"하","tag":"XSV"},{"form":"ᆫ다","tag":"EF"}]}'::jsonb,
  'TAIL_3',
  198,  -- WEAK_JUNYONG_HADA (199) 앞
  true,
  '준용한다 종결 — 다른 조항 적용'
);
```

→ Cursor는 `pattern_position` 컬럼이 'TAIL_REGEX' 값을 받는지 DB CHECK 또는 코드 정합 확인 후 적용. 'COMPOSITE' match_strategy 룰의 패턴 처리 로직은 기존 코드(`engine/subtype_rule_match.py`)에서 정규식 fallback 가능 여부 확인.

### 5.2 OBLIGATION_DETAIL_GWAN_SAHANG sub_type 변경

```sql
UPDATE rule_classify_subtype
SET sub_type = 'ENUMERATION_ITEM',
    description = '관한 사항 종결 — enumeration 항목 (이전 OBLIGATION_DETAIL_ITEM 오분류 정정)',
    updated_at = NOW()
WHERE rule_name = 'OBLIGATION_DETAIL_GWAN_SAHANG';
```

### 5.3 WEAK_JUNYONG_HADA sub_type 변경

```sql
UPDATE rule_classify_subtype
SET sub_type = 'REFERENCE_INVOCATION',
    description = '준용한다 종결 — REFERENCE_INVOCATION 본질 매핑',
    updated_at = NOW()
WHERE rule_name = 'WEAK_JUNYONG_HADA';
```

### 5.4 AS_본다 보조 룰 3종 처리

신규 ENUMERATION_LIST_INTRO / REFERENCE_TO_ATTACHMENT 룰이 **higher priority**로 매칭되므로 기존 AS_본다 보조 룰은:

**옵션 A — 비활성** (권고):
```sql
UPDATE rule_classify_subtype
SET enabled = false,
    description = description || ' [DEPRECATED Phase 2.2 — FP 95%+, 신규 룰로 대체]',
    updated_at = NOW()
WHERE rule_name IN ('AS_본다_WA_GATDA', 'AS_본다_GWA_GATDA', 'AS_본다_TTOHAN_GATDA');
```

**옵션 B — sub_type을 ENUMERATION_LIST_INTRO fallback으로 변경**:
- 너무 광범위해서 비활성 권고

---

## 6. 신규 룰 INSERT (FN 보강)

### 6.1 OBLIGATION 변형

```sql
-- 어야 → 야 변형 (Kiwi 축약 출력)
INSERT INTO rule_classify_subtype VALUES (
  'OBLIGATION_HEADER_YA_TAIL3',
  'OBLIGATION_HEADER',
  'TAIL_POS',
  '{"tokens": [{"form":"야","tag":"EC"},{"form":"하","tag":"VX"},{"form":"ᆫ다","tag":"EF"}]}'::jsonb,
  'TAIL_3',
  11,  -- OBLIGATION_HEADER_TAIL3 (10) 다음
  true,
  '야/EC + 하/VX + ᆫ다/EF — 어야 축약 변형'
),
-- 의무가 있다
(
  'OBLIGATION_HAS_DUTY',
  'OBLIGATION_HEADER',
  'TAIL_POS',
  '{"tokens": [{"form":"의무","tag":"NNG"},{"form":"가","tag":"JKS"},{"form":"있","tag":"VV"},{"form":"다","tag":"EF"}]}'::jsonb,
  'TAIL_4',
  12,
  true,
  '의무가 있다 — 명시적 의무 표현'
);
```

### 6.2 PROHIBITION 변형

```sql
-- 안 된다 (아니의 축약)
INSERT INTO rule_classify_subtype VALUES (
  'PROHIBITION_HEADER_AN_DOEN',
  'PROHIBITION_HEADER',
  'TAIL_POS',
  '{"tokens": [{"form":"안","tag":"MAG"},{"form":"되","tag":"VV"},{"form":"ᆫ다","tag":"EF"}]}'::jsonb,
  'TAIL_3',
  18,  -- PROHIBITION_HEADER_MAG_DOEI (19) 앞
  true,
  '안 + 되 + ᆫ다 — 아니 축약 변형'
),
-- 못한다
(
  'PROHIBITION_HEADER_MOTHANDA',
  'PROHIBITION_HEADER',
  'TAIL_POS',
  '{"tokens": [{"form":"못하","tag":"VX"},{"form":"ᆫ다","tag":"EF"}]}'::jsonb,
  'TAIL_2',
  23,
  true,
  '못한다 — 불가능 표현'
);
```

### 6.3 ENUMERATION_ITEM 룰 (단편 분류, 핵심)

UC 명사 종결 ~59,000건 분류용. **TAIL_POS 룰**: 마지막 토큰이 `NNG/NNB/NNP` 이고 길이 < 80자.

```sql
-- 명사 종결 단편 (parent 컨텍스트 고려 X — 단순 패턴 매칭)
INSERT INTO rule_classify_subtype VALUES (
  'ENUMERATION_ITEM_NOMINAL_TAIL',
  'ENUMERATION_ITEM',
  'TAIL_POS',
  '{"tokens": [{"form":"*","tag":"NNG|NNB|NNP"}], "max_text_length": 80}'::jsonb,
  'TAIL_1',
  250,  -- WEAK fallback (200, 201) 다음 — 마지막 매칭
  true,
  '명사 종결 단편 — enumeration 자식 항목'
);
```

→ Cursor는 `engine/subtype_rule_match.py`에서 `tag` 필드의 `|` 구분자 (NNG|NNB|NNP) 처리 로직을 확인. 또는 **3개 룰로 분리**:

```sql
-- 분리 버전
INSERT INTO rule_classify_subtype VALUES 
('ENUMERATION_ITEM_TAIL_NNG', 'ENUMERATION_ITEM', 'TAIL_POS', '{"tokens": [{"form":"*","tag":"NNG"}]}'::jsonb, 'TAIL_1', 251, true, '명사(NNG) 종결'),
('ENUMERATION_ITEM_TAIL_NNB', 'ENUMERATION_ITEM', 'TAIL_POS', '{"tokens": [{"form":"*","tag":"NNB"}]}'::jsonb, 'TAIL_1', 252, true, '의존명사(NNB) 종결'),
('ENUMERATION_ITEM_TAIL_NNP', 'ENUMERATION_ITEM', 'TAIL_POS', '{"tokens": [{"form":"*","tag":"NNP"}]}'::jsonb, 'TAIL_1', 253, true, '고유명사(NNP) 종결');
```

→ `form: "*"` 의 wildcard 처리 가능 여부 확인. 불가 시 `engine/subtype_rule_match.py`에서 form match 생략 옵션 추가.

---

## 7. Phase 2 재실행

### 7.1 대상

- UC 68,130 (UNCLASSIFIED)
- AS_본다 보조 룰 매칭 3,267 (재매핑)
- OBLIGATION_DETAIL_GWAN_SAHANG 매칭 2,389 (sub_type 변경 후 재검증)
- DELEGATION_ETRAHADA 매칭 1,188 (별표/별지 분할)
- WEAK_JUNYONG_HADA 매칭 1,080 (sub_type 변경)
- 합계: **76,054건 재실행 대상**

### 7.2 실행 명령

```bash
railway run python3 scripts/track_e_phase2_run.py --phase22
# 또는 Cursor가 신규 옵션 추가 후 실행
```

### 7.3 보전 검증 (필수)

```sql
-- Phase 1 보전 검증 (절대 불변)
SELECT sub_type, COUNT(*) FROM stage_2_elements
WHERE sub_type IN ('DELETED', 'DEFINITION_INTRO', 'TITLE_HEADER', 'DATE_EFFECTIVE')
  -- EXCEPTION_CLAUSE는 Phase 2.1에서 +57 증가 — Phase 2.2도 증가 가능 (누락 보강)
GROUP BY sub_type;
-- 예상: DELETED 1,768, DEFINITION_INTRO 142, TITLE_HEADER 127, DATE_EFFECTIVE 92 (Phase 2.1과 동일)
```

---

## 8. 검증 (정확도 우선)

### 8.1 검증 SQL

```sql
-- (1) 신규 sub_type 분포
SELECT sub_type, COUNT(*) FROM stage_2_elements 
WHERE sub_type IN ('ENUMERATION_ITEM', 'ENUMERATION_LIST_INTRO', 'REFERENCE_TO_ATTACHMENT', 'REFERENCE_INVOCATION')
GROUP BY sub_type;

-- (2) FP 정정 검증
SELECT 
  -- AS_본다는 TAIL3 (으로 본다) 만 남아야 함
  (SELECT COUNT(*) FROM stage_2_elements WHERE sub_type='AS_본다') AS as_bonda_after,
  -- DELEGATION_ACTIVE는 진짜 위임만 남아야 함
  (SELECT COUNT(*) FROM stage_2_elements WHERE sub_type='DELEGATION_ACTIVE') AS delegation_after,
  -- OBLIGATION_DETAIL_ITEM은 GWAN_SAHANG 제외돼야 함 (4,355건 예상)
  (SELECT COUNT(*) FROM stage_2_elements WHERE sub_type='OBLIGATION_DETAIL_ITEM') AS oblig_detail_after,
  -- ENUMERATION_ITEM 신규 분류 (수만건 예상)
  (SELECT COUNT(*) FROM stage_2_elements WHERE sub_type='ENUMERATION_ITEM') AS enum_item_after,
  -- UC 감소 (10K~ 수준 예상)
  (SELECT COUNT(*) FROM stage_2_elements WHERE sub_type='UNCLASSIFIED') AS uc_after;

-- (3) 100조문 sample 정확도
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
```

### 8.2 임계 (정확도 우선)

| check | 임계 (1차) | 임계 (이상적) |
|---|---|---|
| 분류율 | ≥ 70% | ≥ 90% |
| **AS_본다 (TAIL3만)** | ≤ 1,000 (이전 4,188 → 754 정도) | ≤ 800 |
| **OBLIGATION_DETAIL_ITEM** | ≤ 5,000 (이전 6,748 → 4,355 정도) | ≤ 4,500 |
| **ENUMERATION_ITEM** | ≥ 50,000 (UC 단편 흡수) | ≥ 55,000 |
| **0건 매칭 룰** | ≤ 2 | 0 |
| Phase 1 보전 (5종 row 수) | 동일 | 동일 |
| **정확도 (sample 100건)** | **≥ 80%** | ≥ 95% |

### 8.3 sample 정확도 검증 (자동화)

본 검증은 PM 창에서 진행 (Cursor 위탁 X):
- AS_본다 sub_type → 100% TAIL3 (으로 본다) 정합 확인
- DELEGATION_ACTIVE → 100% TAIL3 + 정하는 바/령/규칙/고시 정합
- ENUMERATION_LIST_INTRO → 100% "다음 각 호/다음과 같다" 정합
- REFERENCE_TO_ATTACHMENT → 100% 별표/별지 정합

→ Cursor는 sub_type 분포 + 0건 매칭 룰 검증만 진행. 정확도 sample은 PM 창.

---

## 9. verification_log INSERT

```sql
INSERT INTO verification_log (stage, check_name, check_type, result_status, expected_value, actual_value, threshold, error_count, error_examples, verified_by, notes) VALUES
  (2, 'phase_2_2_classify_pct', 'AUTO_HOOK', 'PASS_OR_FAIL', '>=70%', '실측%', '70', 0, '[]'::jsonb, 'Cursor_Phase_2_2_2026-05-XX', '분류율'),
  (2, 'phase_2_2_zero_match_rules', 'AUTO_HOOK', 'PASS_OR_FAIL', '<=2', '실측', '2', 0, '[]'::jsonb, 'Cursor_Phase_2_2', '0건 매칭 룰'),
  (2, 'phase_2_2_phase1_preserved', 'AUTO_HOOK', 'PASS_OR_FAIL', '5종 동일', '실측', '0', 0, '[]'::jsonb, 'Cursor_Phase_2_2', 'Phase 1 보전'),
  (2, 'phase_2_2_enumeration_item_count', 'AUTO_HOOK', 'PASS_OR_FAIL', '>=50000', '실측', '50000', 0, '[]'::jsonb, 'Cursor_Phase_2_2', 'ENUMERATION_ITEM 분류'),
  (2, 'phase_2_2_as_bonda_count', 'AUTO_HOOK', 'PASS_OR_FAIL', '<=1000', '실측', '1000', 0, '[]'::jsonb, 'Cursor_Phase_2_2', 'AS_본다 정확화'),
  (2, 'phase_2_2_subtype_enum_count', 'AUTO_HOOK', 'PASS_OR_FAIL', '28', '실측', '28', 0, '[]'::jsonb, 'Cursor_Phase_2_2', 'CHECK enum 확장');
```

---

## 10. 임의판단 금지 규칙 (Cursor 자체 판단 X)

| 영역 | 금지 | 허용 |
|---|---|---|
| LLM 호출 | 어떤 형태든 X | Kiwi + 정규식 + 빈도 분석 |
| sub_type 추가 | 본 명세 외 신규 enum | 본 명세 정의 3개만 |
| 룰 sub_type 변경 | 임의 판단 변경 | 본 명세 §5 정의대로만 |
| Phase 1 결과 | 변경 / 덮어쓰기 | 100% 보전 |
| 룰 매칭 실패 | 강제 분류 | UNCLASSIFIED 유지 |
| 임계 미달 | 룰 임의 추가 | 즉시 정지 + PM 회신 |
| sample 검증 | 사용자에게 요청 | 자동 검증만 |

---

## 11. 중단 트리거 (즉시 정지 + PM 회신)

1. 진입 점검 SQL 결과 명세와 다름
2. 백업 row 수 ≠ 본체
3. CHECK enum 마이그레이션 실패
4. row 수 변동 (151,751 ≠)
5. Phase 1 분류 (DELETED/DEFINITION_INTRO/TITLE_HEADER/DATE_EFFECTIVE) row 변경 발견
6. 분류율 < 70% (1차 임계 미달)
7. 0건 매칭 룰 ≥ 3
8. 신규 sub_type 분포가 명세 추정과 큰 차이 (예: ENUMERATION_ITEM < 30,000)

---

## 12. 본 명세 외 작업 절대 X

- ❌ Stage 3 진입
- ❌ v3.0 마스터 객체 테이블 마이그레이션
- ❌ Tier 2 본법 수집
- ❌ Kiwi 사전 보강 (Track C 별도)
- ❌ 6하원칙 보강 (별도 명세)
- ❌ 신규 sub_type 추가 (본 명세 3개 외)
- ❌ Phase 1 결과 변경

---

## 13. 보고서 양식

```markdown
# [Track E] Phase 2.2 — 정확도 보강 + sub_type 구조 확장

## 1. 사전 점검
## 2. 백업
## 3. CHECK enum 확장 결과 (28 enum)
## 4. 룰 변경 사항 (재매핑 + 신규 INSERT 12+개)
## 5. Phase 2 재실행 결과 — sub_type 분포
| sub_type | Phase 2.1 | Phase 2.2 | 변화 |
|---|---|---|---|
| AS_본다 | 4,188 | ___ | -___ |
| OBLIGATION_DETAIL_ITEM | 6,748 | ___ | -___ |
| ENUMERATION_ITEM | 0 | ___ | +___ |
| ENUMERATION_LIST_INTRO | 0 | ___ | +___ |
| REFERENCE_TO_ATTACHMENT | 0 | ___ | +___ |
| REFERENCE_INVOCATION | 0 | ___ | +___ |
| UNCLASSIFIED | 68,130 | ___ | -___ |

**총 분류율: ___% (Phase 2.1 55.10% 대비 +___%p)**

## 6. 검증 결과
## 7. 절대 원칙 점검
## 8. 다음 단계 (PM 진단 후 Stage 3 진입 또는 추가 보강)
```

---

## 14. 환경 정보

| 항목 | 값 |
|---|---|
| 코드 base | `taiengineering/tai-api` (engine/subtype_rule_match.py 보강 가능, scripts/track_e_phase2_run.py에 --phase22 옵션 추가) |
| 마이그레이션 | Cursor가 `apply_migration` 도구로 진행 (name: phase_2_2_subtype_enum_extension) |
| 보고서 commit | `taiengineering/tai-admin`, `docs/extraction/v3/log/Track_E_20260510_Phase2_2.md` |
| 코드 commit | `taiengineering/tai-api`, `dev` 브랜치 |
| push | tai-admin main / tai-api dev (PR 또는 rebase 별도) |

---

**END — Phase 2.1 정확도 ~50% → Phase 2.2 ~90%+ 도달 + sub_type 구조 확장 (28 enum).**
