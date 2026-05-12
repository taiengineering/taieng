# CURSOR_TASK 2026-05-08 — extract_scope_from_clauses.py

> 의미절에서 적용 범위 (scope) 추출 → master_rule_scope + master_rule_scope_threshold INSERT.
>
> ⚠️ **이 작업의 가장 중요한 원칙은 의미해석 0%**.

---

## 0. 위반 시 작업 폐기 — 절대 금지 사항

이 5개 중 하나라도 발견되면 **작업 폐기 + 알고리즘 보강**:

1. ❌ **키워드 사전에 없는 단어를 추정으로 매핑** (예: "아파트"가 사전에 있으면 매핑, 없으면 NULL. "비슷한 단어"는 절대 매핑 금지)
2. ❌ **정규식에 안 잡히는 표현을 추정으로 채움** (예: "큰 사업장" → 임계값 NULL)
3. ❌ **numeric_value를 default 0/1/-1로 채움** (없으면 INSERT skip)
4. ❌ **needs_review=false로 마크하면서 실제로는 해석 필요** (해석 필요 = 무조건 needs_review=true)
5. ❌ **AI/LLM API 호출** (정규식·키워드 사전만)

---

## 1. 입력 / 출력

### 입력
- `semantic_clause` 58,495행
- `law_master`, `law_article` (layer 분류용)
- `unit_conversion` 74행 (단위 환산)

### 출력 1: `master_rule_scope` (예상 ~4,000~5,000행)
- 분류형 차원 (sectors/industry/building_use/facility/construction/equipment/process) 추출
- scope_text = source_text 원문 보존

### 출력 2: `master_rule_scope_threshold` (예상 ~500~1,500행)
- 임계값 4값 (criterion + numeric_value + unit + operator)

---

## 2. 알고리즘 — 5단계

### Step 1. semantic_clause SELECT (페이지네이션 — Supabase 1000 limit 우회)

```python
def fetch_clauses(start_from=0, sample_size=100000):
    all_clauses = []
    offset = start_from
    while len(all_clauses) < sample_size:
        chunk_size = min(1000, sample_size - len(all_clauses))
        def _do():
            return supabase.from_("semantic_clause").select(
                "id, source_part_id, source_article_id, "
                "source_text, content_type, action_text, executor_text, "
                "sectors, condition_text, exception_text"
            ).order("id").range(offset, offset + chunk_size - 1).execute()
        res = with_retry(_do)
        batch = res.data or []
        if not batch:
            break
        all_clauses.extend(batch)
        if len(batch) < chunk_size:
            break
        offset += chunk_size
    return all_clauses[:sample_size]
```

⚠️ **필수**: argparse `--sample-size` default=100000, 명시적 값 누락 시 stderr 경고 (이전 사고 학습).

### Step 2. layer 분류 (law_master.law_name 기반)

```python
def determine_layer(law_name):
    """ONLY 명시된 패턴만. 이외는 '본법령'."""
    if not law_name:
        return '본법령'
    if '시행령' in law_name:
        return '시행령'
    if '시행규칙' in law_name:
        return '시행규칙'
    if '고시' in law_name:
        return '고시'
    if '기준' in law_name or '규정' in law_name:
        return '기준규정'
    return '본법령'
```

### Step 3. 분류형 차원 추출 — 키워드 사전만

#### 3-1. building_use_codes (건축법 시행령 별표 1 — 29개 표준)

⚠️ **이 사전 외 매핑 절대 금지**. 사전에 없는 한글 단어 → 빈 배열.

```python
BUILDING_USE_DICT = {
    # 01 단독주택
    '단독주택': '01_단독주택',
    
    # 02 공동주택
    '공동주택': '02_공동주택',
    '아파트': '02_공동주택',
    '연립주택': '02_공동주택',
    '다세대주택': '02_공동주택',
    '기숙사': '02_공동주택',
    
    # 03 제1종근린생활시설
    '제1종근린생활시설': '03_제1종근린생활시설',
    '근린생활시설': '03_제1종근린생활시설',  # 종 미명시 시 1종
    
    # 04 제2종근린생활시설
    '제2종근린생활시설': '04_제2종근린생활시설',
    
    # 05 문화및집회시설
    '문화및집회시설': '05_문화및집회시설',
    '문화시설': '05_문화및집회시설',
    '집회시설': '05_문화및집회시설',
    '공연장': '05_문화및집회시설',
    '관람장': '05_문화및집회시설',
    '전시장': '05_문화및집회시설',
    
    # 06 종교시설
    '종교시설': '06_종교시설',
    
    # 07 판매시설
    '판매시설': '07_판매시설',
    '대형마트': '07_판매시설',
    '백화점': '07_판매시설',
    '쇼핑센터': '07_판매시설',
    
    # 08 운수시설
    '운수시설': '08_운수시설',
    
    # 09 의료시설
    '의료시설': '09_의료시설',
    '병원': '09_의료시설',
    '종합병원': '09_의료시설',
    '의원': '09_의료시설',
    '요양병원': '09_의료시설',
    
    # 10 교육연구시설
    '교육연구시설': '10_교육연구시설',
    '학교': '10_교육연구시설',
    '대학교': '10_교육연구시설',
    '연구소': '10_교육연구시설',
    
    # 11 노유자시설
    '노유자시설': '11_노유자시설',
    '아동관련시설': '11_노유자시설',
    '노인복지시설': '11_노유자시설',
    
    # 12 수련시설
    '수련시설': '12_수련시설',
    
    # 13 운동시설
    '운동시설': '13_운동시설',
    '체육관': '13_운동시설',
    '경기장': '13_운동시설',
    
    # 14 업무시설
    '업무시설': '14_업무시설',
    '오피스텔': '14_업무시설',
    
    # 15 숙박시설
    '숙박시설': '15_숙박시설',
    '호텔': '15_숙박시설',
    '여관': '15_숙박시설',
    
    # 16 위락시설
    '위락시설': '16_위락시설',
    
    # 17 공장
    '공장': '17_공장',
    
    # 18 창고시설
    '창고시설': '18_창고시설',
    '창고': '18_창고시설',
    
    # 19 위험물저장및처리시설
    '위험물저장및처리시설': '19_위험물저장및처리시설',
    '위험물시설': '19_위험물저장및처리시설',
    '주유소': '19_위험물저장및처리시설',
    '가스충전소': '19_위험물저장및처리시설',
    
    # 20 자동차관련시설
    '자동차관련시설': '20_자동차관련시설',
    '주차장': '20_자동차관련시설',
    '세차장': '20_자동차관련시설',
    
    # 21 동물및식물관련시설
    '동물및식물관련시설': '21_동물및식물관련시설',
    '축사': '21_동물및식물관련시설',
    
    # 22 자원순환관련시설
    '자원순환관련시설': '22_자원순환관련시설',
    '폐기물처리시설': '22_자원순환관련시설',
    
    # 23 교정및군사시설
    '교정및군사시설': '23_교정및군사시설',
    '교정시설': '23_교정및군사시설',
    '군사시설': '23_교정및군사시설',
    
    # 24 방송통신시설
    '방송통신시설': '24_방송통신시설',
    '방송국': '24_방송통신시설',
    '전신전화국': '24_방송통신시설',
    
    # 25 발전시설
    '발전시설': '25_발전시설',
    '발전소': '25_발전시설',
    
    # 26 묘지관련시설
    '묘지관련시설': '26_묘지관련시설',
    '봉안당': '26_묘지관련시설',
    
    # 27 관광휴게시설
    '관광휴게시설': '27_관광휴게시설',
    
    # 28 장례시설
    '장례시설': '28_장례시설',
    
    # 29 야영장시설
    '야영장시설': '29_야영장시설',
    '야영장': '29_야영장시설',
}

def extract_building_use(text):
    """사전에 명시된 키워드만 매핑. 사전 외 단어는 매핑 안 함."""
    if not text:
        return []
    found = set()
    for kw, code in BUILDING_USE_DICT.items():
        if kw in text:
            found.add(code)
    return sorted(list(found))
```

⚠️ **금지**: `if '주택' in text` 같은 부분 매칭으로 추정 금지. 사전 키 그대로 매칭만.

#### 3-2. industry_codes (KSIC 대분류 — 한글 그대로 + KSIC 코드)

KSIC 표준 사전이 마련되지 않았으므로 **한글 원문 그대로 보존** + 알려진 대분류만 코드 매핑.

```python
INDUSTRY_DICT = {
    # KSIC 대분류 매핑
    '제조업': 'C',         # KSIC C 대분류
    '건설업': 'F',         # KSIC F 대분류 (41-43)
    '농업': 'A',           # KSIC A
    '임업': 'A',
    '어업': 'A',
    '광업': 'B',
    '도매업': 'G',
    '소매업': 'G',
    '판매업': 'G',
    '운수업': 'H',         # KSIC H (49-52)
    '운수창고업': 'H',
    '숙박업': 'I',
    '음식점업': 'I',
    '정보통신업': 'J',
    '금융업': 'K',
    '보험업': 'K',
    '부동산업': 'L',
    '교육서비스업': 'P',
    '보건업': 'Q',
    '사회복지서비스업': 'Q',
    '예술스포츠업': 'R',
    # 사전에 없는 산업 표현 → 빈 배열
}

def extract_industry(text):
    if not text:
        return []
    found = set()
    for kw, code in INDUSTRY_DICT.items():
        if kw in text:
            found.add(code)
    return sorted(list(found))
```

#### 3-3. construction_types (공사 종류)

```python
CONSTRUCTION_TYPE_DICT = {
    '토목공사': 'civil',
    '건축공사': 'building',
    '전기공사': 'electrical',
    '통신공사': 'communication',
    '소방공사': 'firefighting',
    '소방시설공사': 'firefighting',
    '정보통신공사': 'information',
    '문화재수리공사': 'cultural_heritage',
    '조경공사': 'landscaping',
}

def extract_construction_type(text):
    if not text:
        return []
    found = set()
    for kw, code in CONSTRUCTION_TYPE_DICT.items():
        if kw in text:
            found.add(code)
    return sorted(list(found))
```

#### 3-4. facility_types (시설 종류 — 한글 키워드 그대로)

표준 코드 없음. **한글 키워드 그대로 array에 저장**.

```python
FACILITY_KEYWORDS = [
    '공장', '창고', '사업장', '작업장', '공사장',
    '발전시설', '변전소', '송전탑',
    '저장시설', '저장탱크', '가스시설',
    '폐수처리시설', '대기오염방지시설',
    '소각시설', '매립시설',
    '가축사육시설', '도축시설',
    '항만시설', '공항시설', '철도시설',
]

def extract_facility(text):
    if not text:
        return []
    found = set()
    for kw in FACILITY_KEYWORDS:
        if kw in text:
            found.add(kw)  # 한글 그대로
    return sorted(list(found))
```

⚠️ 표준화는 후속 단계. 지금은 한글 보존.

#### 3-5. equipment_types (설비/장비 — 한글 키워드 그대로)

```python
EQUIPMENT_KEYWORDS = [
    '압력용기', '보일러', '냉동기',
    '크레인', '리프트', '곤돌라', '승강기', '에스컬레이터',
    '지게차', '굴착기', '포크레인',
    '고압가스용기', '고압가스저장탱크',
    '전기설비', '전기시설',
    '용접기', '연마기', '프레스',
    '컨베이어', '호이스트',
]

def extract_equipment(text):
    if not text:
        return []
    found = set()
    for kw in EQUIPMENT_KEYWORDS:
        if kw in text:
            found.add(kw)
    return sorted(list(found))
```

#### 3-6. process_codes (공정 — 한글 키워드 그대로)

```python
PROCESS_KEYWORDS = [
    '용접', '용단', '도장',
    '열처리', '주조', '단조',
    '연마', '절단',
    '도금', '표면처리',
    '화학반응', '증류',
    '발효', '건조',
]

def extract_process(text):
    if not text:
        return []
    found = set()
    for kw in PROCESS_KEYWORDS:
        if kw in text:
            found.add(kw)
    return sorted(list(found))
```

#### 3-7. sectors (semantic_clause.sectors 그대로 복사)

```python
def get_sectors(clause):
    s = clause.get('sectors')
    return s if isinstance(s, list) else []
```

### Step 4. 임계값 추출 (4값) — 정규식 패턴만

⚠️ 명시된 정규식 외 추정 금지.

```python
# 4값 추출 정규식 — 한국 법령 임계값 표현
THRESHOLD_PATTERNS = [
    # 패턴 1: "근로자 N명 이상" / "상시근로자 N인 이상"
    {
        'name': 'employee',
        'pattern': r'(?P<criterion>상시근로자|근로자)\s*(?P<value>\d+(?:,\d{3})*)\s*(?P<unit>명|인)\s*(?P<op>이상|이하|초과|미만)',
        'criterion_code': 'employee',
    },
    # 패턴 2: "면적 N㎡ 이상" / "연면적 N제곱미터 이상"
    {
        'name': 'area',
        'pattern': r'(?P<criterion>연면적|대지면적|건축면적|면적)\s*(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>㎡|제곱미터|m²|m2|평)\s*(?P<op>이상|이하|초과|미만)',
        'criterion_code': 'area_floor',
    },
    # 패턴 3: "공사금액 N억원 이상"
    {
        'name': 'construction_amount',
        'pattern': r'(?P<criterion>공사금액|총공사금액|도급금액|계약금액)\s*(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>억원|억|만원|천만원|백만원|원)\s*(?P<op>이상|이하|초과|미만)',
        'criterion_code': 'construction_amount',
    },
    # 패턴 4: "용량 NkW 이상"
    {
        'name': 'capacity_power',
        'pattern': r'(?P<criterion>용량|정격용량|발전용량|수전용량|설비용량)\s*(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>kW|MW|kVA)\s*(?P<op>이상|이하|초과|미만)',
        'criterion_code': 'capacity_power',
    },
    # 패턴 5: "높이 Nm 이상"
    {
        'name': 'height',
        'pattern': r'(?P<criterion>높이|건축물높이)\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>m|미터|층)\s*(?P<op>이상|이하|초과|미만)',
        'criterion_code': 'height',
    },
    # 패턴 6: "저장량 N톤 이상" / "처리량 NL/일 이상"
    {
        'name': 'capacity_weight',
        'pattern': r'(?P<criterion>저장량|처리량|보관량|반입량)\s*(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>톤|t|kg|㎏)\s*(?P<op>이상|이하|초과|미만)',
        'criterion_code': 'capacity_weight',
    },
    # 패턴 7: "압력 NMPa 이상"
    {
        'name': 'pressure',
        'pattern': r'(?P<criterion>압력|작업압력|설계압력)\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>MPa|kPa|bar|kgf/cm²)\s*(?P<op>이상|이하|초과|미만)',
        'criterion_code': 'capacity_pressure',
    },
    # 패턴 8: "세대수 N세대 이상"
    {
        'name': 'count_unit',
        'pattern': r'(?P<criterion>세대수|호수|동수)\s*(?P<value>\d+(?:,\d{3})*)\s*(?P<unit>세대|호|동|실)\s*(?P<op>이상|이하|초과|미만)',
        'criterion_code': 'count_unit',
    },
]

OPERATOR_MAP = {
    '이상': 'GTE',
    '이하': 'LTE',
    '초과': 'GT',
    '미만': 'LT',
}

def extract_thresholds(text):
    """4값 분해. 매핑 안 되면 NULL 반환 (추정 금지)."""
    if not text:
        return []
    
    thresholds = []
    for pattern_def in THRESHOLD_PATTERNS:
        for m in re.finditer(pattern_def['pattern'], text):
            criterion = m.group('criterion')
            value_str = m.group('value').replace(',', '')
            unit = m.group('unit')
            op_kr = m.group('op')
            
            try:
                numeric_value = float(value_str)
            except ValueError:
                continue  # 숫자 변환 실패 시 skip
            
            operator = OPERATOR_MAP.get(op_kr)
            if not operator:
                continue
            
            thresholds.append({
                'criterion': criterion,
                'criterion_code': pattern_def['criterion_code'],
                'numeric_value': numeric_value,
                'unit': unit,
                'operator': operator,
                'normalized_value': None,  # 환산은 후속 단계 (의미해석 회피)
                'normalized_unit': None,
                'source_text': m.group(0),
            })
    
    return thresholds
```

⚠️ **정규식이 안 잡으면 thresholds = []**. 절대 추정 채움 금지.

### Step 5. master_rule_scope + threshold INSERT

```python
def process_clause(clause, article_meta):
    """
    의미절 1개 → master_rule_scope 0~1개 + threshold 0~N개
    
    master_rule_scope에 INSERT하는 조건:
    - 분류형 추출 결과 1개 이상 비지 않음, OR
    - 임계값 추출 결과 1개 이상
    """
    sectors = clause.get('sectors') or []
    industry = extract_industry(clause['source_text'])
    building = extract_building_use(clause['source_text'])
    facility = extract_facility(clause['source_text'])
    construction = extract_construction_type(clause['source_text'])
    equipment = extract_equipment(clause['source_text'])
    process = extract_process(clause['source_text'])
    thresholds = extract_thresholds(clause['source_text'])
    
    # scope 데이터가 없으면 INSERT 안 함
    has_classification = any([industry, building, facility, construction, equipment, process])
    has_threshold = len(thresholds) > 0
    has_sectors = len(sectors) > 0
    
    if not (has_classification or has_threshold or has_sectors):
        return None, []
    
    layer = determine_layer(article_meta.get('law_name'))
    
    # scope_code: SCOPE_{clause_id 앞 8자}
    scope_code = f"SCOPE_{str(clause['id'])[:8]}"
    
    scope = {
        'scope_code': scope_code,
        'source_clause_id': clause['id'],
        'source_part_id': clause['source_part_id'],
        'source_article_id': clause['source_article_id'],
        'source_law_id': article_meta['source_law_id'],
        'layer': layer,
        'sectors': sectors,
        'industry_codes': industry,
        'building_use_codes': building,
        'facility_types': facility,
        'construction_types': construction,
        'equipment_types': equipment,
        'process_codes': process,
        'scope_text': clause['source_text'][:1000],  # 길이 제한
        'generation_method': 'AUTO_REGEX',
        'generation_confidence': calculate_confidence(has_classification, has_threshold, has_sectors),
        'needs_review': not (has_classification and has_threshold),  # 둘 다 있어야 검토 불필요
        'review_reason': '분류형/임계값 둘 다 추출됨' if (has_classification and has_threshold) 
                         else '분류형만 추출' if has_classification 
                         else '임계값만 추출' if has_threshold
                         else 'sectors만 보유',
    }
    
    return scope, thresholds


def calculate_confidence(has_classification, has_threshold, has_sectors):
    """신뢰도. AI 유추 없음. 추출된 차원 수만 카운트."""
    score = 0.0
    if has_sectors: score += 0.3
    if has_classification: score += 0.4
    if has_threshold: score += 0.3
    return score


def insert_scope_and_thresholds(scope, thresholds):
    """1 scope + N thresholds INSERT (트랜잭션)"""
    res = supabase.table('master_rule_scope').insert(scope).execute()
    scope_id = res.data[0]['id']
    
    if thresholds:
        for t in thresholds:
            t['scope_id'] = scope_id
        supabase.table('master_rule_scope_threshold').insert(thresholds).execute()
    
    return scope_id
```

---

## 3. argparse + 명령

```python
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--apply', action='store_true')
parser.add_argument('--truncate-first', action='store_true',
                    help='적용 전 master_rule_scope* 비움')
parser.add_argument('--sample-size', type=int, default=100000,
                    help='처리할 의미절 수. 전체 처리는 100000+ 명시.')
```

⚠️ `--apply`인데 `--sample-size` 명시 안 하면 stderr 경고 (이전 사고 학습).

```bash
cd docs/extraction/scripts

# dry-run sample 100
railway run python3 extract_scope_from_clauses.py --dry-run --sample-size 100

# 전체 실행
railway run python3 extract_scope_from_clauses.py --apply --sample-size 100000 2>&1 | tee /tmp/extract_scope.log
```

---

## 4. 출력 검증 SQL (실행 후 즉시 점검)

```sql
-- 1. master_rule_scope row 수
SELECT 
  layer,
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE array_length(industry_codes,1)>0) AS has_industry,
  COUNT(*) FILTER (WHERE array_length(building_use_codes,1)>0) AS has_building,
  COUNT(*) FILTER (WHERE array_length(facility_types,1)>0) AS has_facility,
  COUNT(*) FILTER (WHERE array_length(equipment_types,1)>0) AS has_equipment,
  COUNT(*) FILTER (WHERE needs_review) AS needs_review_cnt
FROM master_rule_scope
GROUP BY layer
ORDER BY total DESC;

-- 2. master_rule_scope_threshold 4값 채움률
SELECT 
  context_inferred AS bucket,
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE numeric_value IS NOT NULL) AS has_value,
  COUNT(*) FILTER (WHERE unit IS NOT NULL) AS has_unit,
  COUNT(*) FILTER (WHERE operator IS NOT NULL) AS has_op,
  COUNT(*) FILTER (WHERE normalized_value IS NULL) AS need_normalize
FROM (
  SELECT *, criterion_code AS context_inferred FROM master_rule_scope_threshold
) sub
GROUP BY bucket
ORDER BY total DESC;

-- 3. FK 무결성
SELECT 
  'scope FK 끊김' AS check_, 
  COUNT(*) AS broken
FROM master_rule_scope mrs
LEFT JOIN semantic_clause sc ON mrs.source_clause_id = sc.id
WHERE sc.id IS NULL

UNION ALL

SELECT 'threshold FK 끊김', COUNT(*)
FROM master_rule_scope_threshold mrst
LEFT JOIN master_rule_scope mrs ON mrst.scope_id = mrs.id
WHERE mrs.id IS NULL;

-- 4. 의미해석 검증 — operator NULL이거나 numeric_value NULL인 행은 needs_review=true 인지
SELECT COUNT(*) AS suspicious
FROM master_rule_scope_threshold
WHERE (numeric_value IS NULL OR unit IS NULL OR operator IS NULL);
-- 예상: 0 (모두 채워져 있어야)
```

---

## 5. 자가 검증 — 의심스러운 결과 발견 시

INSERT 후 다음 확인:

```sql
-- A. building_use_codes에 사전 외 값이 들어있는지
SELECT DISTINCT unnest(building_use_codes) AS code 
FROM master_rule_scope
WHERE NOT (unnest(building_use_codes) ~ '^(0[1-9]|[12][0-9])_');
-- 예상: 0 rows (사전 코드 외 매핑은 0)

-- B. industry_codes에 KSIC 알파벳(A-U) 외 값이 있는지
-- 예상: 0 (사전 외 매핑 없음)

-- C. operator가 5값 외인지
SELECT operator, COUNT(*) FROM master_rule_scope_threshold
WHERE operator NOT IN ('GTE','GT','LTE','LT','EQ');
-- 예상: 0
```

⚠️ 위 검증에서 1행이라도 발견되면 **알고리즘 결함**. 작업 폐기 + 패턴 보강.

---

## 6. 절대 금지 패턴 — Cursor 자가 점검

코드 작성 후 자기 검증:

```
□ regex pattern에 ".*" (greedy) 사용 안 함
□ 키워드 사전 매칭 시 부분 문자열 매칭 안 함 (in 연산자 OK, 그러나 단어 경계 고려)
□ NULL 채우는 default 값 0/1/-1 안 사용
□ "추정", "유추", "비슷한" 같은 주석/로직 안 사용
□ AI/LLM API 호출 코드 (openai/anthropic 등) import 안 함
```

---

## 7. 완료 기준

- [ ] master_rule_scope ~4,000~5,000행
- [ ] master_rule_scope_threshold ~500~1,500행
- [ ] FK 무결성 통과 (끊김 0)
- [ ] 사전 외 코드 0개
- [ ] operator/criterion_code CHECK 위반 0개
- [ ] sample 5건 사용자 검토 통과 (의미해석 흔적 없음 확인)

---

## 8. 200줄+ 파일 처리

이 스크립트는 ~600줄 예상. **GitHub MCP 직접 수정 금지**, Cursor 로컬 + git push.

```bash
cd ~/Cursor/tai-admin/docs/extraction/scripts/
# Cursor agent에 작업지시서 첨부 + 작성 요청 (이 문서)

git add extract_scope_from_clauses.py
git commit -m "feat(extraction): extract_scope_from_clauses v1.0 — 4값 분해 + 키워드 사전 (의미해석 0%)"
git push origin main
```

---

## 9. 진행 흐름

```
1. 본 문서를 Cursor에 첨부 + 스크립트 작성 요청
2. dry-run sample 100 실행 → 사용자 검토
3. 의미해석 흔적 없음 확인 → 전체 실행
4. 검증 SQL 4개 통과 → 다음 단계 (매핑 작업)
```
