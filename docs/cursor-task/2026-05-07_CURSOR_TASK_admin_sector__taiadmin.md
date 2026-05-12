# CURSOR TASK 2026-05-07: tai-admin sector 표준화 마이그레이션

> 백엔드 sector 표준화에 따른 프론트엔드 코드 동시 변경.

## 변경 요약

| 변경 전 | 변경 후 |
|---|---|
| `'INDUSTRY'` | `'INDUSTRIAL'` |
| `'industry'` (소문자) | `'INDUSTRIAL'` |
| `'MANUFACTURING'` | `'INDUSTRIAL'` |
| 한글 sector 비교 (`'건물'`, `'공장'` 등) | UI 표시는 system_codes.sector_label 사용 |

**제외**: facility_type_code (`INDUSTRY_V2`, `BUILDING_V2`) 변경 금지.

**페이지 파일명**: `diagnosis-input-industry-paid1/2/3.html` 그대로 유지 (URL 영향 최소화). 내부 sector 값만 변경.

---

## 작업 원칙

1. AI/LLM 호출 0%
2. main 브랜치만 (dev 없음)
3. 200줄+ 파일은 GitHub MCP 직접 수정 금지 → 로컬 편집
4. 변경 후 브라우저 콘솔 에러 없는지 확인
5. 사용자 영향 최소화 (URL 변경 X, 호환성 유지)

---

## 변경 대상 파일 (37개 매칭, 핵심 15개)

### 1순위: feature flag + plan gate (전역 영향)

#### `tadmin/full-version/assets/js/feature-flags.js`

```javascript
// 변경 전
const VALID_SECTORS = ['BUILDING', 'INDUSTRY', 'CONSTRUCTION'];
function isValidSector(s) { return VALID_SECTORS.includes(s.toUpperCase()); }

// 변경 후 (4 sector 표준)
const VALID_SECTORS = ['BUILDING', 'INDUSTRIAL', 'CONSTRUCTION', 'SPECIAL_FACILITY'];
// 참고: COMMON은 다중 매핑 임시 표기 (단일 컬럼 한계, 추후 sectors[]로 정리)
```

#### `tadmin/full-version/assets/js/tai/plan-gate.js`

`sector` 비교 로직 모두 INDUSTRY → INDUSTRIAL.

#### `tadmin/full-version/assets/js/tai/menu-tadmin.js`

메뉴 항목별 sector 필터링 로직 변경.

### 2순위: i18n + UI 표시

#### `tadmin/full-version/app/i18n.js`

sector 한글 라벨 통일:

```javascript
// 변경 전
const SECTOR_LABELS = {
  building: '건물',
  industry: '공장',
  construction: '건설',
};

// 변경 후 (대문자 표준 + 4 sector + COMMON)
const SECTOR_LABELS = {
  BUILDING: '건물',
  INDUSTRIAL: '공장',
  CONSTRUCTION: '건설',
  SPECIAL_FACILITY: '특수시설',
  COMMON: '공통',
};

function sectorLabel(sector) {
  if (!sector) return '';
  return SECTOR_LABELS[sector.toUpperCase()] || sector;
}
```

### 3순위: 진단 입력 페이지 (3 파일)

```
tadmin/full-version/html/horizontal-menu-template/diagnosis-input-industry-paid1.html
tadmin/full-version/html/horizontal-menu-template/diagnosis-input-industry-paid2.html
tadmin/full-version/html/horizontal-menu-template/diagnosis-input-industry-paid3.html
```

**파일명 유지**. 내부 JS만 변경:

```javascript
// 변경 전
const SECTOR = 'INDUSTRY';
fetch(`/diagnosis/fields?sector=INDUSTRY&tier=PAID1`)

// 변경 후
const SECTOR = 'INDUSTRIAL';
fetch(`/diagnosis/fields?sector=INDUSTRIAL&tier=PAID1`)
```

### 4순위: 기타 페이지

```
tadmin/full-version/app/inspect.html
tadmin/full-version/app/index.html
tadmin/full-version/html/horizontal-menu-template/auth-login-cover.html
tadmin/full-version/html/horizontal-menu-template/my-company.html

admin/full-version/assets/js/tai/pages/price-setting.page.js
admin/full-version/html/horizontal-menu-template/price-setting.html
admin/full-version/html/horizontal-menu-template/engine-qa.html
admin/full-version/html/horizontal-menu-template/diagram-gallery.html
admin/full-version/html/horizontal-menu-template/diagnosis-step1.html

site/full-version/assets/js/tai/menu-tadmin.js
site/full-version/html/horizontal-menu-template/index.html

scripts/capture-app.js
scripts/capture-light.js
```

각 파일에서 sector 비교/할당 패턴만 변경:

```javascript
// 패턴 1: 문자열 비교
if (sector === 'INDUSTRY')  →  if (sector === 'INDUSTRIAL')
if (sector == 'INDUSTRY')   →  if (sector == 'INDUSTRIAL')

// 패턴 2: 할당
let sector = 'INDUSTRY';    →  let sector = 'INDUSTRIAL';
sector: 'INDUSTRY'          →  sector: 'INDUSTRIAL'

// 패턴 3: 배열
['BUILDING', 'INDUSTRY', 'CONSTRUCTION']  
  →  ['BUILDING', 'INDUSTRIAL', 'CONSTRUCTION', 'SPECIAL_FACILITY']

// 패턴 4: 한글 비교 (있다면)
if (sector === '공장')  →  if (sector === 'INDUSTRIAL')
if (sector === '건물')  →  if (sector === 'BUILDING')

// 패턴 5: 변경 금지 (facility_type_code)
'INDUSTRY_V2'      →  유지
'INDUSTRY_PAID1'   →  유지
```

---

## 작업 순서

### Step 1: 검색으로 영향 정확히 파악

```bash
# 로컬 tai-admin에서
grep -rn '"INDUSTRY"' --include="*.html" --include="*.js" .
grep -rn "'INDUSTRY'" --include="*.html" --include="*.js" .
grep -rn 'industry'   --include="*.js" . | grep -v 'INDUSTRY_'  # 소문자
grep -rn '"공장"\|"건물"\|"건설"\|"공통"' --include="*.html" --include="*.js" .

# 변경 금지 패턴
grep -rn 'INDUSTRY_V2\|INDUSTRY_PAID' --include="*.html" --include="*.js" .
```

### Step 2: 자동 변환 + 수동 검증

`facility_type_code` 패턴(INDUSTRY_V2, INDUSTRY_PAID*)은 제외하고 sector 값만 변경.

### Step 3: 검증

```bash
# HTML/JS syntax (eslint, prettier)
npx eslint .
npx prettier --check .

# 변경 후 INDUSTRY 잔존 검색 (facility_type_code만 남아야)
grep -rn '"INDUSTRY"\|'\''INDUSTRY'\''' --include="*.js" --include="*.html" .

# 브라우저에서 실제 페이지 로드 + 콘솔 에러 확인
```

### Step 4: 배포

```bash
git add -A
git commit -m "refactor: sector 표준화 INDUSTRY → INDUSTRIAL (4 sector 표준)"
git push origin main  # Cloudflare Pages 자동 배포
```

배포 후 페이지 동작 확인:
- `/html/horizontal-menu-template/diagnosis-input-industry-paid1.html` 로드 OK
- 진단 폼 sector=INDUSTRIAL로 API 호출 OK
- plan-gate.js 정상 동작 OK
- inspection_anchor 페이지 sector 필터 정상 OK

---

## URL 호환성 (옵션)

미오픈 단계라 불필요. 단 외부 링크/북마크 보호 위해:

```javascript
// 페이지 상단에 sector legacy 매핑 (안전망)
const SECTOR_LEGACY_MAP = {
  INDUSTRY: 'INDUSTRIAL',
  MANUFACTURING: 'INDUSTRIAL',
};

function normalizeSector(s) {
  if (!s) return s;
  s = s.toUpperCase();
  return SECTOR_LEGACY_MAP[s] || s;
}

// 사용
const sector = normalizeSector(urlParams.get('sector'));
```

---

## 한글 라벨 — system_codes 활용 (권고)

UI에서 sector 한글 표시 시 system_codes.sector_label 활용:

```javascript
// API: GET /api/system-codes?category=sector_label
// Response:
[
  { code: 'BUILDING', code_name: 'BUILDING', code_value: '건물' },
  { code: 'INDUSTRIAL', code_name: 'INDUSTRIAL', code_value: '공장' },
  ...
]

// JS에서 사용
async function getSectorLabels() {
  const res = await fetch('/api/system-codes?category=sector_label');
  const data = await res.json();
  return Object.fromEntries(data.map(c => [c.code, c.code_value]));
}

// 또는 i18n.js에 하드코딩 (오프라인 지원)
const SECTOR_LABELS = {
  BUILDING: '건물',
  INDUSTRIAL: '공장',
  CONSTRUCTION: '건설',
  SPECIAL_FACILITY: '특수시설',
  COMMON: '공통',
};
```

권고: **하드코딩 + system_codes는 fallback** (페이지 로드 속도 우선).

---

## 검증 체크리스트

- [ ] 모든 `'INDUSTRY'` 문자열 비교 → `'INDUSTRIAL'`
- [ ] 모든 `'industry'` (소문자) → `'INDUSTRIAL'`
- [ ] `'MANUFACTURING'` → `'INDUSTRIAL'`
- [ ] 한글 sector 비교 → 영어로 변경 (또는 system_codes 활용)
- [ ] `VALID_SECTORS` 배열 4 sector + SPECIAL_FACILITY 추가
- [ ] facility_type_code (INDUSTRY_V2 등) 변경 안 됨
- [ ] 진단 입력 3 페이지 정상 로드 + API 호출 OK
- [ ] plan-gate.js 정상 동작
- [ ] 한글 라벨 표시 정상 (system_codes 또는 i18n.js)
- [ ] 브라우저 콘솔 에러 0
- [ ] `/api/diagnosis/fields?sector=INDUSTRIAL&tier=PAID1` 정상 응답

---

## 관련 문서

- `docs/extraction/SECTOR_CODE_IMPACT_2026-05-07.md` — 영향 분석
- `docs/extraction/CURSOR_TASK_2026-05-07_api_sector.md` — 백엔드 작업 (먼저 진행)
- `docs/extraction/LAW_SECTOR_MAPPING_2026-05-07.md` — 366 법령 sector 매핑
