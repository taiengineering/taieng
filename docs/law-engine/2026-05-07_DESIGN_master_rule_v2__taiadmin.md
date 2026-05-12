# DESIGN: master_rule_v2 스키마 (의미절 기반)

> 의미절 → master_rule_v2 → inspection_sets → work_schedules 4계층 설계
>
> 핵심 원칙: AI 임의판단 0%, 출처 추적 가능, sectors[] 다중매핑 활용

---

## 1. 큰 그림 — 4계층 흐름

```
[Layer 1] semantic_clause (58,495)        ← 의미절 base data ✓ 완료
              │
              │ 자동 변환 (정규식+키워드 사전, AI 0%)
              ▼
[Layer 2] master_rule_v2 (신규)            ← 마스터 룰 (전국 공통, 6하원칙 + 범위)
              │
              │ 법령엔진 (사업장 조건 매칭)
              ▼
[Layer 3] inspection_sets (기존 활용)      ← 사업장별 점검항목 (이미지 화면)
              │
              │ 안전관리자 4가지 세팅 (언제/누가/무엇을/어떻게)
              ▼
[Layer 4] work_schedules (기존 활용)       ← 자동 생성 일정
```

### 기존 인프라 발견 — 새 테이블 최소화

| 기존 테이블 | 역할 | 변경 필요? |
|---|---|---|
| `semantic_clause` (58,495) | 의미절 + sectors[] | ✓ 완료 |
| `inspection_sets` (324) | 점검항목 (이미지 화면 데이터) | ⚠️ 일부 컬럼 보강 |
| `work_schedules` (0) | 일정 | 그대로 사용 |
| `work_assignments` (0) | 작업 할당 | 그대로 사용 |
| `inspection_rule_mapping` (0) | 점검 ↔ 룰 매핑 | 그대로 사용 |

→ 신규 테이블은 **`master_rule_v2`** 1개만.

---

## 2. master_rule_v2 스키마

### 핵심 설계 원칙

1. **출처 추적 가능** — `source_clause_id` (FK semantic_clause)로 항상 의미절까지 역추적
2. **6하원칙 6요소** — 의미절 5요소 + 범위 1요소
3. **sectors[] 다중매핑** — 의미절에서 그대로 복사
4. **AI 임의판단 추적** — `generation_method` + `generation_confidence` 명시
5. **needs_review 기본 정책** — silent failure 0

### DDL

```sql
CREATE TABLE master_rule_v2 (
  -- ============ 식별 + 출처 ============
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_code TEXT UNIQUE NOT NULL,                     -- 사람 읽기 쉬운 코드 (예: SAFE-CONS-001)
  
  -- 의미절 출처 (필수, 추적 가능)
  source_clause_id UUID NOT NULL REFERENCES semantic_clause(id) ON DELETE RESTRICT,
  source_article_id UUID NOT NULL REFERENCES law_article(id) ON DELETE RESTRICT,
  source_law_id UUID NOT NULL REFERENCES law_master(id) ON DELETE RESTRICT,
  
  -- 참고용 매핑 (있으면, 점진 폐기 예정)
  legacy_mblr_id UUID REFERENCES master_building_legal_rules(id) ON DELETE SET NULL,
  
  -- ============ 6하원칙 (행위 본질) ============
  
  -- 언제 (When)
  when_cycle_type TEXT,                                -- ONCE / DAILY / WEEKLY / MONTHLY / YEARLY / ON_EVENT
  when_cycle_value INTEGER,                            -- 주기 값 (예: 3 = 3개월)
  when_cycle_unit TEXT,                                -- DAY / WEEK / MONTH / YEAR
  when_due_days INTEGER,                               -- 기한 일수 (예: 30 = 30일 이내)
  when_base_event TEXT,                                -- 기준 이벤트 (예: "작업 시작 전", "선임 후")
  when_text_raw TEXT,                                  -- 의미절 cycle_text 원문 (디버깅)
  
  -- 누가 (Who)
  who_executor TEXT,                                   -- 안전관리자 / 사업주 / 작업자 / ...
  who_executor_text_raw TEXT,                          -- 의미절 executor_text 원문
  
  -- 무엇을 (What)
  what_action TEXT NOT NULL,                           -- 점검 / 보고 / 신고 / 제출 / 선임 / 조치 / 작성 / ...
  what_target TEXT,                                    -- 무엇에 대해 (예: "압력용기", "작업환경")
  what_action_text_raw TEXT,                           -- 의미절 action_text 원문
  
  -- 어떻게 (How)
  how_method TEXT,                                     -- 육안 / 측정 / 서류 / 디지털 / ...
  how_form TEXT,                                       -- 양식 코드 (예: "별지 23호")
  
  -- 어디서 (Where) = 범위 (scope)
  sectors TEXT[] NOT NULL,                             -- 의미절 sectors[] 그대로 복사 (필수)
  scope_industry_codes TEXT[],                         -- KSIC 산업 코드 (선택)
  scope_facility_types TEXT[],                         -- FACTORY / WAREHOUSE / OFFICE 등
  scope_construction_types TEXT[],                     -- KCSC 공사 종류
  scope_process_codes TEXT[],                          -- KCSC 공정 코드
  scope_equipment_types TEXT[],                        -- 설비 종류
  scope_building_use_codes TEXT[],                     -- 건축물 용도 (건축물대장)
  scope_min_area_sqm NUMERIC,                          -- 면적 임계 (예: 5000 m²)
  scope_min_employees INTEGER,                         -- 인원 임계 (예: 50명)
  scope_min_construction_amount NUMERIC,               -- 공사금액 임계 (예: 5억)
  scope_extra JSONB,                                   -- 기타 조건 (확장용)
  
  -- 왜 (Why) = 법령 출처 + 의무 요약
  why_obligation_summary TEXT NOT NULL,                -- 의미절 action_text를 사람 읽기 좋게
  why_law_citation TEXT,                               -- 법령 인용 (예: "산업안전보건법 제42조 제1항")
  
  -- ============ 분류 (이미지의 점검항목관리 탭) ============
  obligation_category TEXT NOT NULL,                   -- 점검 / 작업_전 / 보고 / 서류 / 신고 / 선임 / 조치 / 기타
  
  -- ============ 추가 정보 ============
  penalty_summary TEXT,                                -- 과태료 정보 (선택)
  online_system_url TEXT,                              -- 신고 시스템 URL (선택)
  reference_links JSONB,                               -- 참고 링크 (선택)
  
  -- ============ 검증 메타 ============
  generation_method TEXT NOT NULL DEFAULT 'AUTO_REGEX'  -- AUTO_REGEX / MANUAL / HYBRID
    CHECK (generation_method IN ('AUTO_REGEX','MANUAL','HYBRID')),
  generation_confidence NUMERIC(3,2)                   -- 0.00 ~ 1.00
    CHECK (generation_confidence IS NULL OR (generation_confidence >= 0 AND generation_confidence <= 1)),
  
  status TEXT NOT NULL DEFAULT 'DRAFT'                 -- DRAFT / VALIDATED / ACTIVE / DEPRECATED
    CHECK (status IN ('DRAFT','VALIDATED','ACTIVE','DEPRECATED')),
  
  needs_review BOOLEAN NOT NULL DEFAULT TRUE,          -- 사람 검증 필요
  review_reason TEXT,                                  -- review 이유
  
  validated_at TIMESTAMPTZ,
  validated_by UUID,                                   -- FK users.id (선택)
  
  -- ============ 시스템 ============
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- ============ 제약 ============
  CONSTRAINT master_rule_v2_sectors_valid 
    CHECK (sectors <@ ARRAY['BUILDING','INDUSTRIAL','CONSTRUCTION','SPECIAL_FACILITY']::text[]),
  CONSTRAINT master_rule_v2_sectors_nonempty 
    CHECK (array_length(sectors, 1) >= 1),
  CONSTRAINT master_rule_v2_obligation_category_valid
    CHECK (obligation_category IN ('점검','작업_전','보고','서류','신고','선임','조치','기타')),
  CONSTRAINT master_rule_v2_cycle_consistency
    CHECK (
      (when_cycle_type IS NULL) OR
      (when_cycle_type = 'ONCE') OR
      (when_cycle_type = 'ON_EVENT' AND when_base_event IS NOT NULL) OR
      (when_cycle_type IN ('DAILY','WEEKLY','MONTHLY','YEARLY') 
        AND when_cycle_value IS NOT NULL AND when_cycle_unit IS NOT NULL)
    )
);

-- ============ 인덱스 ============

CREATE INDEX idx_master_rule_v2_sectors ON master_rule_v2 USING GIN(sectors);
CREATE INDEX idx_master_rule_v2_source_clause ON master_rule_v2(source_clause_id);
CREATE INDEX idx_master_rule_v2_source_law ON master_rule_v2(source_law_id);
CREATE INDEX idx_master_rule_v2_obligation_category ON master_rule_v2(obligation_category);
CREATE INDEX idx_master_rule_v2_status ON master_rule_v2(status);
CREATE INDEX idx_master_rule_v2_needs_review ON master_rule_v2(needs_review) 
  WHERE needs_review = TRUE;
CREATE INDEX idx_master_rule_v2_when_cycle ON master_rule_v2(when_cycle_type, when_cycle_value);
CREATE INDEX idx_master_rule_v2_industry ON master_rule_v2 USING GIN(scope_industry_codes);
CREATE INDEX idx_master_rule_v2_equipment ON master_rule_v2 USING GIN(scope_equipment_types);

-- ============ 트리거 ============

CREATE OR REPLACE FUNCTION update_master_rule_v2_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_master_rule_v2_updated_at
  BEFORE UPDATE ON master_rule_v2
  FOR EACH ROW
  EXECUTE FUNCTION update_master_rule_v2_updated_at();

-- ============ 코멘트 ============

COMMENT ON TABLE master_rule_v2 IS 
  'TAI Safe 법령엔진 마스터 룰 (의미절 기반). semantic_clause → master_rule_v2 → inspection_sets → work_schedules.';
COMMENT ON COLUMN master_rule_v2.source_clause_id IS '의미절 출처 (FK 필수). AI 임의판단 추적/차단.';
COMMENT ON COLUMN master_rule_v2.sectors IS '의미절 sectors[] 그대로 복사. 다중 = 공용.';
COMMENT ON COLUMN master_rule_v2.generation_method IS 'AUTO_REGEX (정규식자동) / MANUAL (수동) / HYBRID. AI 호출 0%.';
COMMENT ON COLUMN master_rule_v2.needs_review IS '신뢰도 < 0.7 OR scope 비어있으면 TRUE. silent failure 0 정책.';
```

---

## 3. 의미절 → master_rule_v2 자동 변환 알고리즘

### 입력
- `semantic_clause` (58,495)

### 처리 (정규식 + 키워드 사전, AI 0%)

```python
# Phase 1: 의미절 필터 (룰이 될 수 있는 것만)
def is_rule_candidate(clause):
    """DEFINITION/DELEGATION/STATEMENT는 룰 아님"""
    if clause.content_type in ['DEFINITION', 'DELEGATION', 'STATEMENT']:
        return False
    if clause.sectors is None:  # INACTIVE
        return False
    return True

# Phase 2: 6하원칙 5요소 직접 매핑 (의미절에 이미 있음)
def extract_who_what_how(clause):
    return {
        'who_executor': clause.executor_text,
        'what_action_text_raw': clause.action_text,
        'what_action': classify_action(clause.action_text),
        'what_target': extract_target(clause.action_text),
        'how_form': clause.form_token,
        'why_obligation_summary': summarize_obligation(clause.action_text),
    }

# Phase 3: 언제 (cycle) 정밀 추출
def extract_when(clause):
    """의미절 cycle_text + action_text에서 정확히 파싱"""
    if clause.cycle_text:
        # 예: "매년 1회" → cycle_type=YEARLY, cycle_value=1, cycle_unit=YEAR
        # 예: "30일 이내" → due_days=30
        # 예: "작업 시작 전" → cycle_type=ON_EVENT, base_event="작업 시작 전"
        return parse_cycle_text(clause.cycle_text)
    
    # cycle_text 없으면 action_text에서 키워드 검색
    if any(kw in clause.action_text for kw in ['작업 시작 전', '작업 전']):
        return {'cycle_type': 'ON_EVENT', 'base_event': '작업 시작 전'}
    
    return {'cycle_type': None}  # cycle 없음 → 일회성 또는 이벤트성

# Phase 4: 범위 (scope) 추출 — 키워드 사전
def extract_scope(clause):
    """clause text에서 키워드 검색하여 scope 채움"""
    return {
        'sectors': clause.sectors,  # 의미절에서 그대로 (다중매핑 완료)
        'scope_equipment_types': match_equipment_keywords(clause),  # 압력용기/보일러/...
        'scope_facility_types': match_facility_keywords(clause),
        'scope_min_employees': extract_employee_threshold(clause),
        'scope_min_construction_amount': extract_amount_threshold(clause),
        # ...
    }

# Phase 5: 의무구분 분류 (이미지 탭)
def classify_obligation_category(clause):
    """action_text 키워드 기반"""
    text = clause.action_text
    
    # cycle 있으면 점검 가능성 높음
    if clause.cycle_text and clause.content_type == 'OBLIGATION':
        if '점검' in text or '확인' in text:
            return '점검'
    
    # 키워드 매칭
    if '작업 시작 전' in text or '작업 전' in text:
        return '작업_전'
    if '보고' in text:
        return '보고'
    if '신고' in text:
        return '신고'
    if '선임' in text:
        return '선임'
    if '조치' in text or '시정' in text:
        return '조치'
    if '작성' in text or '비치' in text or '보존' in text:
        return '서류'
    
    return '기타'

# Phase 6: 신뢰도 계산
def calculate_confidence(rule):
    """5W1H 채움률 기반"""
    fields = [
        rule['who_executor'],
        rule['what_action'],
        rule['when_cycle_type'] or rule['when_base_event'],
        rule['how_form'] or rule['how_method'],
        rule['sectors'],
        rule['why_obligation_summary'],
    ]
    filled = sum(1 for f in fields if f)
    return filled / len(fields)

# Phase 7: needs_review 판정
def needs_review(rule):
    if rule['generation_confidence'] < 0.7:
        return True, "신뢰도 부족"
    if not rule['sectors']:
        return True, "scope 비어있음"
    if not rule['what_action'] or not rule['who_executor']:
        return True, "필수 요소 누락"
    return False, None

# 메인 변환
def convert_clause_to_rule(clause):
    if not is_rule_candidate(clause):
        return None
    
    rule = {
        'source_clause_id': clause.id,
        'source_article_id': clause.source_article_id,
        'source_law_id': clause.law_id,
        **extract_who_what_how(clause),
        **extract_when(clause),
        **extract_scope(clause),
        'obligation_category': classify_obligation_category(clause),
        'generation_method': 'AUTO_REGEX',
    }
    rule['generation_confidence'] = calculate_confidence(rule)
    rule['needs_review'], rule['review_reason'] = needs_review(rule)
    rule['status'] = 'VALIDATED' if not rule['needs_review'] else 'DRAFT'
    rule['rule_code'] = generate_rule_code(rule)  # 예: SAFE-IND-CONS-MNTH-1234
    
    return rule
```

### 출력
- `master_rule_v2` 자동 생성 룰 (예상 35,000~45,000건)
- DEFINITION/DELEGATION/STATEMENT 11,498건 skip
- INACTIVE 161 skip
- needs_review TRUE: ~30~50% (신뢰도 < 0.7)

---

## 4. 사업장 정보 → 적용 룰 매칭 (법령엔진)

### 입력 (사업장 인풋)

```
산업 구분    → factories.industry_type_code (KSIC)
시설         → factories.* + buildings.*
공사장       → construction_sites.*
공정         → factory_process.* (KCSC 코드)
설비         → equipment_assets.*
사업장 sector → factories.sector
면적/인원    → factories.building_area, employee_count
공사금액     → construction_sites.contract_amount, factories.construction_amount
건축물대장   → factories.bdmgtsn, main_purpose_code
```

### 매칭 알고리즘 (SQL 기반)

```sql
-- 사업장 X에 적용되는 master_rule_v2 룰 추출
WITH factory_context AS (
  SELECT 
    f.id, f.sector, f.industry_type_code, f.building_area, 
    f.employee_count, f.construction_amount,
    array_agg(DISTINCT fp.process_id) FILTER (WHERE fp.process_id IS NOT NULL) AS process_codes,
    array_agg(DISTINCT ea.equipment_type_code) FILTER (WHERE ea.equipment_type_code IS NOT NULL) AS equipment_types,
    array_agg(DISTINCT f.main_purpose_code) FILTER (WHERE f.main_purpose_code IS NOT NULL) AS building_use_codes
  FROM factories f
  LEFT JOIN factory_process fp ON fp.factory_id = f.id
  LEFT JOIN equipment_assets ea ON ea.factory_id = f.id
  WHERE f.id = $1
  GROUP BY f.id
)
SELECT mr.*
FROM master_rule_v2 mr, factory_context fc
WHERE mr.status = 'ACTIVE'
  -- 1. sector 매칭 (필수)
  AND fc.sector = ANY(mr.sectors)
  -- 2. 면적 임계 (있으면)
  AND (mr.scope_min_area_sqm IS NULL OR fc.building_area >= mr.scope_min_area_sqm)
  -- 3. 인원 임계 (있으면)
  AND (mr.scope_min_employees IS NULL OR fc.employee_count >= mr.scope_min_employees)
  -- 4. 공사금액 임계 (있으면)
  AND (mr.scope_min_construction_amount IS NULL 
       OR fc.construction_amount >= mr.scope_min_construction_amount)
  -- 5. 산업 코드 (있으면)
  AND (mr.scope_industry_codes IS NULL 
       OR fc.industry_type_code = ANY(mr.scope_industry_codes))
  -- 6. 공정 (있으면)
  AND (mr.scope_process_codes IS NULL 
       OR mr.scope_process_codes && fc.process_codes)  -- 교집합
  -- 7. 설비 (있으면)
  AND (mr.scope_equipment_types IS NULL 
       OR mr.scope_equipment_types && fc.equipment_types)
  -- 8. 건축물 용도 (있으면)
  AND (mr.scope_building_use_codes IS NULL 
       OR mr.scope_building_use_codes && fc.building_use_codes);
```

→ 결과: 사업장 X에 적용되는 룰 목록 (예상 50~500건)

---

## 5. master_rule_v2 → inspection_sets 흐름

기존 `inspection_sets` 테이블 활용. 적용 룰을 inspection_sets로 변환:

```sql
-- 사업장 X에 적용 룰 → inspection_sets에 자동 INSERT
INSERT INTO inspection_sets (
  company_id, factory_id,
  inspection_set_name,           -- master_rule_v2.why_obligation_summary
  inspection_category_code,       -- master_rule_v2.obligation_category
  cycle_unit, cycle_value,        -- when_cycle_unit, when_cycle_value
  cycle_base_type,                -- when_cycle_type
  cycle_base_guide,               -- 안내 텍스트
  obligation_type,                -- obligation_category
  obligation_summary,             -- why_obligation_summary
  legal_rule_id,                  -- master_rule_v2.id
  legal_rule_code,                -- master_rule_v2.rule_code
  law_name, law_article,          -- 법령 출처
  source,                         -- 'AUTO_FROM_RULE'
  status_code,                    -- 'PENDING_SETUP' (4가지 세팅 대기)
  ...
)
SELECT 
  $company_id, $factory_id,
  mr.why_obligation_summary,
  mr.obligation_category,
  ...
FROM master_rule_v2 mr
WHERE mr.id = ANY($applied_rule_ids);
```

### 4가지 세팅 상태 (이미지의 ✓언제 ✗누가 ✗무엇을 ✗어떻게)

`inspection_sets`에 4 boolean 컬럼 추가 권고:

```sql
ALTER TABLE inspection_sets ADD COLUMN IF NOT EXISTS is_when_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN IF NOT EXISTS is_who_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN IF NOT EXISTS is_what_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN IF NOT EXISTS is_how_set BOOLEAN DEFAULT FALSE;

-- computed: 4가지 모두 충족 시 스케줄 생성 가능
ALTER TABLE inspection_sets ADD COLUMN IF NOT EXISTS is_schedule_ready BOOLEAN 
  GENERATED ALWAYS AS (is_when_set AND is_who_set AND is_what_set AND is_how_set) STORED;
```

→ 안전관리자가 각 세팅 완료 시 boolean true로 변경. `is_schedule_ready=TRUE`인 row만 스케줄 생성.

---

## 6. inspection_sets → work_schedules 자동 생성

```sql
-- is_schedule_ready=TRUE인 점검항목으로 work_schedules INSERT
INSERT INTO work_schedules (
  inspection_set_id, asset_id, assigned_user_id,
  repeat_type, repeat_interval, repeat_weekday,
  start_date, planned_date,
  obligation_type, cycle_base_guide,
  rule_code, law_name, law_article, form_code,
  source_type, status_code
)
SELECT 
  is_.id, is_.equipment_set_id, is_.assignee_user_id,
  is_.cycle_unit, is_.cycle_value, is_.cycle_weekday,
  is_.schedule_anchor_date, is_.next_planned_date,
  is_.obligation_type, is_.cycle_base_guide,
  is_.legal_rule_code, is_.law_name, is_.law_article, ...,
  'AUTO_FROM_INSPECTION_SET', 'PENDING'
FROM inspection_sets is_
WHERE is_.is_schedule_ready = TRUE
  AND is_.factory_id = $factory_id;
```

---

## 7. 작업 단계 (실행 순서)

### Phase A — master_rule_v2 테이블 생성 (즉시 가능)

```sql
-- 위 DDL 실행 (Supabase migration)
```

### Phase B — 의미절 → master_rule_v2 자동 변환 스크립트 작성

`docs/extraction/scripts/convert_clause_to_rule.py` 작성:
- semantic_clause 읽기
- Phase 1~7 알고리즘 적용
- master_rule_v2에 INSERT
- 신뢰도/needs_review 자동 계산
- 변환 로그 (master_rule_extraction_log 테이블, 선택)

예상 결과:
- 변환 가능: ~46,000건 (DEFINITION/DELEGATION/STATEMENT/INACTIVE 제외)
- VALIDATED: ~30,000건 (신뢰도 ≥ 0.7)
- DRAFT (needs_review): ~16,000건 (신뢰도 < 0.7 또는 scope 비어있음)

### Phase C — 사용자 검증

신뢰도 < 0.7 룰 (~16,000건) 중 자주 적용될 핵심 룰부터 사용자 검증:
- 산업안전보건법 룰 우선
- 화학물질관리법 우선
- 건축법 / 건설기술진흥법 등

### Phase D — inspection_sets 4가지 세팅 컬럼 추가

```sql
ALTER TABLE inspection_sets ADD COLUMN is_when_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN is_who_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN is_what_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN is_how_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN is_schedule_ready BOOLEAN 
  GENERATED ALWAYS AS (is_when_set AND is_who_set AND is_what_set AND is_how_set) STORED;
```

### Phase E — 법령엔진 API 작성

`tai-api/routers/legal_engine_v2.py`:
- POST `/legal-engine/evaluate?factory_id=X` — 사업장 X에 적용 룰 추출
- POST `/legal-engine/sync-inspection-sets?factory_id=X` — 적용 룰 → inspection_sets

### Phase F — 프론트엔드 점검항목관리 페이지 연동

기존 `/html/horizontal-menu-template/inspection-anchor` 페이지를 master_rule_v2 기반으로 갱신.

---

## 8. 검증 SQL

```sql
-- 변환 결과 종합
SELECT 
  status,
  generation_method,
  needs_review,
  COUNT(*) AS cnt,
  AVG(generation_confidence) AS avg_conf
FROM master_rule_v2
GROUP BY status, generation_method, needs_review
ORDER BY cnt DESC;

-- sector별 룰 수
SELECT unnest(sectors) AS sector, COUNT(*) AS cnt
FROM master_rule_v2 WHERE status = 'ACTIVE'
GROUP BY sector ORDER BY cnt DESC;

-- 의무구분별 룰 수
SELECT obligation_category, COUNT(*) AS cnt
FROM master_rule_v2 WHERE status = 'ACTIVE'
GROUP BY obligation_category ORDER BY cnt DESC;

-- 사업장 X 적용 룰 수
SELECT COUNT(*) FROM master_rule_v2 mr, factories f
WHERE f.id = $1 AND f.sector = ANY(mr.sectors) AND mr.status = 'ACTIVE';
```

---

## 9. 미구현 / 추후 결정 필요

| 항목 | 결정 필요 |
|---|---|
| `master_rule_extraction_log` 테이블 | 변환 추적 별도 테이블 필요? |
| `master_rule_application` 테이블 | 사업장×룰 매트릭스 캐시 필요? (성능 이슈 시) |
| 룰 코드 명명 규칙 (`rule_code`) | 예: SAFE-{sector}-{cat}-{seq} 충분? |
| 키워드 사전 정확도 | scope_equipment_types 매칭 룰 정확성 검증 필요 |
| 시행령 / 시행규칙 중복 처리 | 같은 의무가 법/시행령/시행규칙에 분산 — 통합 룰 vs 별개 룰? |
| 외부 시스템 연동 | online_system_url 자동 추출 가능? |

---

## 10. 관련 자산

```
✅ semantic_clause (58,495)            ← Layer 1, sectors[] 다중매핑 완료
✅ law_sector_mapping (366)            ← sector 결정 매핑
✅ system_codes (sector + sector_label) ← 표준
🟡 master_rule_v2 (신규, 본 문서)      ← Layer 2, 본 문서 설계
✅ inspection_sets (324)               ← Layer 3, 일부 컬럼 보강 필요
✅ work_schedules (0)                  ← Layer 4, 그대로 사용
✅ inspection_rule_mapping (0)         ← 점검 ↔ 룰 매핑 (Layer 2~3 연결)
```

---

## 관련 문서

- `HANDOFF_2026-05-06_evening.md` — 의미절 v1.7.1 본 적용
- `LAW_SECTOR_MAPPING_2026-05-07.md` — 366 법령 sector 매핑
- `SECTOR_INTEGRITY_VERIFICATION_2026-05-07.md` — 무결성 전수검사
- `SEMANTIC_CLAUSE_SECTORS_ARRAY_2026-05-07.md` — 의미절 sectors[] 다중매핑 완료
- `DESIGN_master_rule_v2_2026-05-07.md` — **본 문서** (master_rule_v2 설계)
