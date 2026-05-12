# CURSOR TASK 2026-05-07: tai-api sector 표준화 마이그레이션

> DB는 이미 표준화 완료. 백엔드 코드의 sector 값 통일 작업.

## 변경 요약

| 변경 전 | 변경 후 |
|---|---|
| `'INDUSTRY'` | `'INDUSTRIAL'` |
| `'MANUFACTURING'` | `'INDUSTRIAL'` |
| `{"BUILDING", "INDUSTRY", "CONSTRUCTION"}` | `{"BUILDING", "INDUSTRIAL", "CONSTRUCTION", "SPECIAL_FACILITY"}` |

**제외**: `INDUSTRY_V2`, `BUILDING_V2`, `CONSTRUCTION_V2` 같은 facility_type_code는 sector와 별개. **변경 금지**.

---

## 작업 원칙

1. AI/LLM 호출 0% — 사용자 사전 + 정규식만
2. 검증 없는 완료 선언 금지
3. 200줄+ 파일은 GitHub MCP 직접 수정 금지 → 로컬 편집 후 git push
4. 변경 후 `python -m py_compile` 또는 `ruff check`로 syntax 검증
5. main push → Railway 자동 배포 (staging 없음). `/health` 절대 503 금지

---

## 변경 대상 파일 (20개)

### 1순위: VALID_SECTORS 하드코딩 (3 파일) — 가장 위험

**`routers/diagnosis_fields.py`** (8KB, 핵심 진단 필드 API):

```python
# 변경 전
VALID_SECTORS = {"BUILDING", "INDUSTRY", "CONSTRUCTION"}
INDUSTRY_TIER_ORDER = ["PAID1", "PAID2", "PAID3"]

# 변경 후 (SPECIAL_FACILITY 추가는 비활성이지만 일관성 위해 포함)
VALID_SECTORS = {"BUILDING", "INDUSTRIAL", "CONSTRUCTION", "SPECIAL_FACILITY"}
INDUSTRIAL_TIER_ORDER = ["PAID1", "PAID2", "PAID3"]  # 변수명도 변경
```

```python
# 변경 전
if sector == "INDUSTRY" and tier in INDUSTRY_TIER_ORDER:
    idx = INDUSTRY_TIER_ORDER.index(tier)
    tiers_to_fetch = ["FREE"] + INDUSTRY_TIER_ORDER[:idx + 1]

# 변경 후
if sector == "INDUSTRIAL" and tier in INDUSTRIAL_TIER_ORDER:
    idx = INDUSTRIAL_TIER_ORDER.index(tier)
    tiers_to_fetch = ["FREE"] + INDUSTRIAL_TIER_ORDER[:idx + 1]
```

```python
# 변경 전: query 비교
elif sector == "INDUSTRY":
    if not tier:
        raise HTTPException(status_code=400, detail="INDUSTRY 섭터는 tier...")
    ...
    return {"data": {"sector": sector, "determined_type": f"INDUSTRY_{tier}_V2", ...}}

# 변경 후
elif sector == "INDUSTRIAL":
    if not tier:
        raise HTTPException(status_code=400, detail="INDUSTRIAL 섭터는 tier...")
    ...
    # ⚠️ INDUSTRY_V2 facility_type_code는 변경 금지! determined_type 그대로
    return {"data": {"sector": sector, "determined_type": f"INDUSTRY_{tier}_V2", ...}}
```

### `routers/feature_flags.py`

```python
# 변경 전
VALID_SECTORS = {"BUILDING", "INDUSTRY", "CONSTRUCTION"}

# 변경 후
VALID_SECTORS = {"BUILDING", "INDUSTRIAL", "CONSTRUCTION", "SPECIAL_FACILITY"}
```

모든 `if sector == "INDUSTRY"` → `if sector == "INDUSTRIAL"` 변경.

### `routers/precedent_api.py`

동일하게 VALID_SECTORS + 모든 'INDUSTRY' 비교문 변경.

### 2순위: sector + INDUSTRY 둘 다 사용하는 17개 파일

```
routers/public_pricing.py
routers/diagnosis_proposal.py
routers/auth.py
routers/price_setting.py
routers/quotes.py
routers/diagnosis_plan_recommend.py
routers/diagnosis_result_web.py
routers/connect_registration.py
routers/diagnosis_integrated.py
routers/kosha_collect.py
routers/industry.py            ← 파일명에 industry, sector 외 의미 가능 — 신중
routers/ksic_engine.py
routers/process_management.py
routers/diagnosis_report.py

services/diagnosis_integrated_svc.py
services/diagnosis_helpers.py
services/roi_calculator.py

app/models/diagnosis_result.py
schemas/diagnosis_integrated.py
schemas/diagnosis_result_v2026_04.json

templates/proposal_pdf.html
templates/diagnosis_report_paid.html
```

각 파일에서 다음 패턴만 변경:

```python
# 변경 대상
"INDUSTRY"        →  "INDUSTRIAL"      (sector 값일 때만)
'INDUSTRY'        →  'INDUSTRIAL'      
sector == "INDUSTRY"  →  sector == "INDUSTRIAL"
sector = "INDUSTRY"   →  sector = "INDUSTRIAL"
"MANUFACTURING"   →  "INDUSTRIAL"

# 변경 금지 (facility_type_code)
"INDUSTRY_V2"        →  유지
"INDUSTRY_PAID1"     →  유지
"INDUSTRY_PAID2_V2"  →  유지
f"INDUSTRY_{tier}_V2"  →  유지
```

### SQL 파일 (1개)

`sql/20260419_diagnosis_input_fields_industry_paid2_paid3_saas.sql`

파일명 그대로 두고 내부 sector 값만 변경:
```sql
-- 변경 전
INSERT INTO diagnosis_input_fields (sector, ...) VALUES ('INDUSTRY', ...)

-- 변경 후
INSERT INTO diagnosis_input_fields (sector, ...) VALUES ('INDUSTRY' /* TODO: INDUSTRIAL */, ...)
-- 또는 그대로 유지 (이미 DB 적용 완료된 SQL이므로)
```

⚠️ 이 SQL은 이미 적용 완료된 마이그레이션. **재실행 안 됨** → 변경 안 해도 무방.

---

## 작업 순서 (권고)

### Step 1: 검색으로 영향 정확히 파악 (Cursor)

```bash
# 로컬 tai-api에서
grep -rn '"INDUSTRY"' --include="*.py" .
grep -rn "'INDUSTRY'" --include="*.py" .
grep -rn '"MANUFACTURING"' --include="*.py" .
grep -rn 'VALID_SECTORS' --include="*.py" .
grep -rn 'INDUSTRY_TIER' --include="*.py" .

# 변경 금지 패턴 (facility_type_code) 식별
grep -rn 'INDUSTRY_V2\|INDUSTRY_PAID\|INDUSTRY_{' --include="*.py" .
```

### Step 2: 자동 변환 + 수동 검증

`facility_type_code` 패턴은 제외하고 sector 값만 일괄 변경.

각 파일별로:
1. `"INDUSTRY"` → `"INDUSTRIAL"` (단, facility_type 제외)
2. `"MANUFACTURING"` → `"INDUSTRIAL"`
3. `VALID_SECTORS = {...}` 업데이트
4. 한글 변수명 (예: `INDUSTRY_TIER_ORDER` → `INDUSTRIAL_TIER_ORDER`) 변경

### Step 3: 검증

```bash
# Python syntax 검증
python -m compileall -q routers services schemas

# 변경 후 INDUSTRY 잔존 검색 (facility_type_code만 남아야)
grep -rn '"INDUSTRY"' --include="*.py" .
# 결과: facility_type_code만 매칭되어야 함

# pytest 실행 (있다면)
pytest tests/
```

### Step 4: 배포

```bash
git add -A
git commit -m "refactor: sector 표준화 INDUSTRY → INDUSTRIAL (4 sector 표준)"
git push origin main  # Railway 자동 배포
```

`/health` 200 OK 확인.

---

## 변경 후 클라이언트 영향

### Breaking Change — API parameter 변경

이전: `GET /diagnosis/fields?sector=INDUSTRY&tier=PAID1`
이후: `GET /diagnosis/fields?sector=INDUSTRIAL&tier=PAID1`

**프론트엔드도 동시 변경 필수** (별도 작업지시서 — `CURSOR_TASK_2026-05-07_admin_sector.md`).

### 호환성 레이어 (옵션)

미오픈 단계라 불필요. 단 외부 통합 있다면 추가:

```python
# routers/diagnosis_fields.py 상단에 호환성 매핑 추가
SECTOR_LEGACY_MAP = {
    "INDUSTRY": "INDUSTRIAL",
    "MANUFACTURING": "INDUSTRIAL",
}

def _normalize_sector(s: str) -> str:
    s = s.upper()
    return SECTOR_LEGACY_MAP.get(s, s)

# 사용
sector = _normalize_sector(sector)
if sector not in VALID_SECTORS:
    raise HTTPException(...)
```

→ 미오픈이라 호환성 레이어 권고 안 함. 단순 교체.

---

## 검증 SQL (배포 후)

```sql
-- 백엔드 변경 후 운영 테이블 sector가 표준에 맞는지 확인
SELECT 'INVALID_SECTORS_FOUND' AS status, table_name, sector, COUNT(*)
FROM (
  SELECT 'agent_service' AS table_name, sector FROM agent_service
  UNION ALL SELECT 'diagnosis_input_fields', sector FROM diagnosis_input_fields
  UNION ALL SELECT 'diagnosis_purchases', sector FROM diagnosis_purchases
  UNION ALL SELECT 'document_form_master', sector FROM document_form_master
  UNION ALL SELECT 'document_forms', sector FROM document_forms
  UNION ALL SELECT 'factories', sector FROM factories
  UNION ALL SELECT 'factory_features', sector FROM factory_features
  UNION ALL SELECT 'inspection_master', sector FROM inspection_master
  UNION ALL SELECT 'price_policy', sector FROM price_policy
  UNION ALL SELECT 'public_diagnosis_requests', sector FROM public_diagnosis_requests
  UNION ALL SELECT 'users', sector FROM users
) t
WHERE sector IS NOT NULL 
  AND sector NOT IN ('BUILDING','INDUSTRIAL','CONSTRUCTION','SPECIAL_FACILITY','COMMON')
GROUP BY table_name, sector
ORDER BY table_name, sector;

-- 결과: 0 rows 이어야 함
```

---

## 관련 문서

- `docs/extraction/SECTOR_CODE_IMPACT_2026-05-07.md` — 영향 분석
- `docs/extraction/LAW_SECTOR_MAPPING_2026-05-07.md` — 366 법령 sector 매핑
- `docs/extraction/CURSOR_TASK_2026-05-07_admin_sector.md` — 프론트엔드 작업 (별도)
