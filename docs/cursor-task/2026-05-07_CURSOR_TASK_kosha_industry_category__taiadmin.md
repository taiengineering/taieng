# CURSOR TASK 2026-05-07: kosha_safety_materials.sector → industry_category rename

> KOSHA 자료의 sector 분류는 사업장 sector(BUILDING/INDUSTRIAL/...)와 다른 차원이라 컬럼명 분리.
> DB rename은 이미 완료. 코드 변경만 남음.

## 의미 분리

| 차원 | 컬럼 | 값 |
|---|---|---|
| **사업장 분류** (TAI 표준) | `factories.sector`, `master_rule.sectors[]` | BUILDING / INDUSTRIAL / CONSTRUCTION / SPECIAL_FACILITY |
| **KOSHA 산업분류** (자체 규칙) | `kosha_safety_materials.industry_category` | COMMON / MANUFACTURING / CONSTRUCTION / SERVICE |

같은 'CONSTRUCTION'이라도 의미 다름:
- TAI 사업장: 건설현장 등록자
- KOSHA: 건설업종 직무용 자료

## DB 변경 (이미 완료)

```sql
ALTER TABLE kosha_safety_materials RENAME COLUMN sector TO industry_category;
```

## 코드 변경 — 1 파일만

### `routers/kosha_collect.py`

**변경 1: `_classify_material()` 함수 — 변수명 + 반환값 명확화**

```python
# 변경 전 (현재)
_SECTOR_RULES: list[Tuple[str, str]] = [
    (r'(건설|건설업|건설현장|콘크리트|타워크레인|비계|거푸집|굴착|항타|갱폼|공사)', 'CONSTRUCTION'),
    (r'(제조|제조업|프레스|선반|절단기|용접|사출|전단기|절곡기|컨베이어|크레인|지게차|보일러|압력용기)', 'MANUFACTURING'),
    (r'(서비스|배달|이륜차|물류|운반|운송|택배|청소|조리)', 'SERVICE'),
]

def _classify_material(title: str) -> Tuple[str, str]:
    """
    제목 기반 카테고리 + 업종 자동 분류.
    Returns (category, sector)
    """
    t = title or ""
    category = "OTHER"
    sector = "COMMON"
    for pattern, cat in _CATEGORY_RULES:
        if re.search(pattern, t):
            category = cat
            break
    for pattern, sec in _SECTOR_RULES:
        if re.search(pattern, t):
            sector = sec
            break
    return category, sector
```

```python
# 변경 후
# 변수명: _SECTOR_RULES → _INDUSTRY_CATEGORY_RULES
_INDUSTRY_CATEGORY_RULES: list[Tuple[str, str]] = [
    (r'(건설|건설업|건설현장|콘크리트|타워크레인|비계|거푸집|굴착|항타|갱폼|공사)', 'CONSTRUCTION'),
    (r'(제조|제조업|프레스|선반|절단기|용접|사출|전단기|절곡기|컨베이어|크레인|지게차|보일러|압력용기)', 'MANUFACTURING'),
    (r'(서비스|배달|이륜차|물류|운반|운송|택배|청소|조리)', 'SERVICE'),
]


def _classify_material(title: str) -> Tuple[str, str]:
    """
    제목 기반 카테고리 + KOSHA 산업분류 자동 분류.
    
    참고: industry_category는 TAI의 사업장 sector(BUILDING/INDUSTRIAL/...)와 다른 차원.
          KOSHA 자료의 직무 영역 분류(COMMON/MANUFACTURING/CONSTRUCTION/SERVICE).
    
    Returns (category, industry_category)
    """
    t = title or ""
    category = "OTHER"
    industry_category = "COMMON"
    for pattern, cat in _CATEGORY_RULES:
        if re.search(pattern, t):
            category = cat
            break
    for pattern, ic in _INDUSTRY_CATEGORY_RULES:
        if re.search(pattern, t):
            industry_category = ic
            break
    return category, industry_category
```

**변경 2: `_collect_safety_materials()` 함수 내 INSERT 부분**

```python
# 변경 전 (line 200 근처)
        for i, it in enumerate(items):
            title = it.get("MED_SJ_NM") or it.get("title") or it.get("mediaTitle") or ""
            url   = it.get("MED_URL") or it.get("url") or it.get("mediaUrl") or ""
            rid   = it.get("mediaId") or it.get("MED_SEQ") or _make_id("mat", url, title)
            category, sector = _classify_material(title)
            rows.append({
                "id": str(rid),
                "title": title,
                "product_type": it.get("productType") or it.get("MED_CL_NM") or "",
                "industry": it.get("industry") or "",
                "accident_type": it.get("accidentType") or "",
                "url": url,
                "category": category,
                "sector": sector,                # ← 컬럼명 변경 필요
                "raw_json": it,
            })
```

```python
# 변경 후
        for i, it in enumerate(items):
            title = it.get("MED_SJ_NM") or it.get("title") or it.get("mediaTitle") or ""
            url   = it.get("MED_URL") or it.get("url") or it.get("mediaUrl") or ""
            rid   = it.get("mediaId") or it.get("MED_SEQ") or _make_id("mat", url, title)
            category, industry_category = _classify_material(title)
            rows.append({
                "id": str(rid),
                "title": title,
                "product_type": it.get("productType") or it.get("MED_CL_NM") or "",
                "industry": it.get("industry") or "",
                "accident_type": it.get("accidentType") or "",
                "url": url,
                "category": category,
                "industry_category": industry_category,    # ← 컬럼명 변경
                "raw_json": it,
            })
```

**변경 3: 모듈 docstring 버전 추가** (선택)

```python
"""
KOSHA 데이터 수집 — DB 저장 + 크론 갱신
prefix: /kosha-collect

v1.7.0 (2026-05-07):
  [REFACTOR] _SECTOR_RULES → _INDUSTRY_CATEGORY_RULES (의미 명확화)
  [REFACTOR] kosha_safety_materials.sector → industry_category (DB 컬럼 rename)
  [DOC] industry_category는 TAI 사업장 sector(BUILDING/INDUSTRIAL/...)와 다른 차원

v1.6.0 (2026-05-02):
  [FIX] MAX_PAGES 100→500 (10,000건 한도 해제)
  [ADD] _collect_safety_materials()에 start_page 파라미터 추가
  [ADD] /run 엔드포인트에 start_page 쿼리 파라미터 추가 (이어받기 가능)

...
"""
```

---

## 작업 순서

### Step 1: 로컬 검색

```bash
# tai-api 로컬에서
grep -rn '_SECTOR_RULES\|"sector": sector\|category, sector = _classify_material\|kosha.*sector' \
  --include="*.py" .
```

예상 결과: `routers/kosha_collect.py` 단일 파일 (3~4 위치)

### Step 2: 정확히 3 곳 수정

1. `_SECTOR_RULES` → `_INDUSTRY_CATEGORY_RULES` (변수 정의)
2. `_classify_material()` 함수 내부 변수명 + docstring + return tuple 변수명
3. `_collect_safety_materials()` 함수 내 `category, sector = ...` → `category, industry_category = ...` 및 dict key 변경

### Step 3: 검증

```bash
# Python syntax
python -m py_compile routers/kosha_collect.py

# 잔존 'sector' 검색 (kosha_collect.py에는 0이어야 함, 다른 파일은 무관)
grep -n 'sector' routers/kosha_collect.py
# 결과: 0 (industry_category로 모두 변경)

# 정상 응답 확인
# (배포 후) curl https://api.taieng.co.kr/kosha-collect/status
```

### Step 4: 배포

```bash
git add routers/kosha_collect.py
git commit -m "refactor(kosha): sector → industry_category (KOSHA 산업분류와 사업장 sector 분리)"
git push origin main
```

---

## 검증 SQL (배포 후)

```sql
-- 신규 수집 시 industry_category가 채워지는지 확인
-- (cron 실행 후 또는 수동 /kosha-collect/run?target=safety-materials 호출 후)
SELECT industry_category, COUNT(*) AS cnt, MAX(collected_at) AS latest_collect
FROM kosha_safety_materials
WHERE collected_at > NOW() - INTERVAL '1 hour'
GROUP BY industry_category
ORDER BY cnt DESC;

-- 기존 데이터 분포 (rename 후 그대로 유지되어야 함)
SELECT industry_category, COUNT(*) AS cnt
FROM kosha_safety_materials
GROUP BY industry_category
ORDER BY cnt DESC;
-- 예상: COMMON 21162 / CONSTRUCTION 4338 / MANUFACTURING 3727 / SERVICE 1320
```

---

## 미래 확장 — TAI sectors[]와의 연결

`industry_category`는 KOSHA 분류 그대로 두고, 추후 `master_rule_v2`에서 KOSHA 자료를 추천할 때 **매핑 함수**로 변환:

```python
# 가상의 매핑 (master_rule_v2 설계 시 결정)
def kosha_industry_to_tai_sectors(industry_category: str) -> list[str]:
    """KOSHA 산업분류 → TAI 사업장 sectors[] 매핑"""
    return {
        'CONSTRUCTION':   ['CONSTRUCTION'],
        'MANUFACTURING':  ['INDUSTRIAL'],
        'SERVICE':        ['BUILDING', 'SPECIAL_FACILITY'],  # 배달/청소/조리 등
        'COMMON':         ['BUILDING', 'INDUSTRIAL', 'CONSTRUCTION', 'SPECIAL_FACILITY'],  # 다중
    }.get(industry_category, [])
```

→ 이 매핑은 master_rule_v2 설계 시 본격 적용. 지금은 컬럼 분리만.

---

## 관련 문서

- `docs/extraction/SECTOR_CODE_IMPACT_2026-05-07.md` — 영향 분석
- `docs/extraction/CURSOR_TASK_2026-05-07_api_sector.md` — 사업장 sector 표준화 (별도 작업)
- `docs/extraction/CURSOR_TASK_2026-05-07_admin_sector.md` — 프론트엔드 작업 (별도)
