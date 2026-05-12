# SECTOR CODE IMPACT 2026-05-07

> sector 표준화 (4 sector + sectors[] 다중 매핑)에 따른 코드/DB 전역변수 영향 분석

## 핵심 결론

**현재 sector 코드는 7가지 표기로 무질서**. 단순 INDUSTRY → INDUSTRIAL 변경이 아니라 **전체 표준화 마이그레이션**이 필요함.

---

## 영향 범위 종합

| 영역 | 매칭 | 위험도 | 비고 |
|---|---|---|---|
| **DB 테이블** | 29개 (운영 15개 + archive 14개) | **HIGH** | 7가지 표기 무질서 |
| **tai-api 백엔드** | 65건 (sector+INDUSTRY) | **HIGH** | VALID_SECTORS 하드코딩 3 파일 |
| **tai-admin 프론트** | 37건 (sector+INDUSTRY) | MEDIUM | 진단 입력 페이지, feature-flags |
| **taieng 마케팅** | 0건 | NONE | 정적 사이트, 영향 없음 |

---

## 1. DB 영향 — 7가지 무질서 표기

### 운영 테이블 sector 값 분포

| 테이블 | 값 분포 (count) | 표준화 필요 |
|---|---|---|
| `factories` | BUILDING(10) **INDUSTRIAL**(15, 정비완료) CONSTRUCTION(5) | ✓ 정비완료 |
| `agent_service` | construction(12) industrial(7) facility(6) | **소문자 → 대문자**, facility → SPECIAL_FACILITY |
| `diagnosis_input_fields` | BUILDING(44) **INDUSTRY**(43) CONSTRUCTION(31) | INDUSTRY → INDUSTRIAL |
| `diagnosis_purchases` | BUILDING(2) **INDUSTRY**(12) CONSTRUCTION(2) | INDUSTRY → INDUSTRIAL |
| `document_form_master` | BUILDING(38) CONSTRUCTION(18) **MANUFACTURING**(7) | MANUFACTURING → INDUSTRIAL |
| `document_forms` | **건물**(81) **공통**(77) **건설**(71) **산업**(31) | 한글 → 영어 (또는 한글 유지 결정) |
| `factory_features` | **ALL**(12) **INDUSTRY**(7) CONSTRUCTION(6) BUILDING(3) | INDUSTRY → INDUSTRIAL, ALL → ? |
| `form_templates` | BUILDING(11) | 그대로 |
| `industrial_accident_precedents` | NULL(849) | 채워야 함 |
| `inspection_master` | **공통**(407) **건설**(365) **건물**(349) **산업**(125) | 한글 → 영어 (또는 유지) |
| `inspection_requests` | (확인 필요) | - |
| **`kosha_safety_materials`** | **COMMON**(21,162) CONSTRUCTION(4,338) **MANUFACTURING**(3,727) **SERVICE**(1,320) | **MANUFACTURING → INDUSTRIAL, SERVICE → ?** (가장 큰 영향) |
| `price_policy` | facility(11) industrial(8) construction(7) **industry**(3) | **소문자 → 대문자** + industry/industrial 충돌 |
| `public_diagnosis_requests` | BUILDING(6) **INDUSTRY**(4) CONSTRUCTION(2) SPECIAL_FACILITY(1) **building**(1) | INDUSTRY → INDUSTRIAL, building → BUILDING |
| `users` | **INDUSTRY**(14) CONSTRUCTION(3) BUILDING(2) | INDUSTRY → INDUSTRIAL |

### Archive 테이블 (변경 불필요)

`master_building_legal_rules`, `master_legal_rules_archive`, `master_legal_rules_pending_review`, `master_legal_rules_preserved`, `master_rules_archive_20260422`, `law_rule_drafts`, `law_rule_drafts_preswitch_20260423`, `diagnosis_results_backup_20260416`, `inspection_master_backup_20260501`, `reparse_job_log`, `semantic_clause_iter1`, `v_drafts_with_code`

---

## 2. tai-api 백엔드 영향

### `VALID_SECTORS` 하드코딩 (3 파일)

```python
VALID_SECTORS = {"BUILDING", "INDUSTRY", "CONSTRUCTION"}
```

발견 위치:
- `routers/feature_flags.py`
- `routers/diagnosis_fields.py` (8KB, sector + tier 매핑 핵심)
- `routers/precedent_api.py`

이 패턴은 **API parameter validation**으로 사용. 즉 외부에서 'INDUSTRY'로 호출해야 통과. 'INDUSTRIAL'로 호출하면 400 에러.

### sector + INDUSTRY 둘 다 사용하는 파일 (20개)

```
routers/diagnosis_fields.py        — 진단 입력 필드 API (핵심)
routers/public_pricing.py          — 공개 가격 API
routers/precedent_api.py           — 산재판례 API
routers/diagnosis_proposal.py      — 진단 제안서
routers/auth.py                    — 인증
routers/price_setting.py           — 가격 설정 (관리자)
routers/quotes.py                  — 견적
routers/diagnosis_plan_recommend.py — 플랜 추천
routers/diagnosis_result_web.py    — 진단 결과 웹
routers/connect_registration.py    — 연결 등록
routers/diagnosis_integrated.py    — 통합 진단
routers/kosha_collect.py           — KOSHA 수집

services/diagnosis_integrated_svc.py
services/diagnosis_helpers.py
services/roi_calculator.py

app/models/diagnosis_result.py
schemas/diagnosis_integrated.py
schemas/diagnosis_result_v2026_04.json

templates/proposal_pdf.html
templates/diagnosis_report_paid.html
```

### `INDUSTRY_V2`, `BUILDING_V2`, `CONSTRUCTION_V2`

facility_type_code (가격 코드)로 사용 — sector와 별개. 변경 불필요. 단 헷갈리지 않게 코드 리뷰 시 주의.

---

## 3. tai-admin 프론트엔드 영향

### 핵심 파일 (37개 중 docs/data 제외)

```
tadmin/full-version/assets/js/feature-flags.js
tadmin/full-version/assets/js/tai/plan-gate.js
tadmin/full-version/assets/js/tai/menu-tadmin.js
tadmin/full-version/app/inspect.html
tadmin/full-version/app/index.html
tadmin/full-version/app/i18n.js              ← 다국어, sector 한글 매핑
tadmin/full-version/html/horizontal-menu-template/
  ├─ diagnosis-input-industry-paid1.html     ← URL/path에 industry 포함!
  ├─ diagnosis-input-industry-paid2.html
  ├─ diagnosis-input-industry-paid3.html
  ├─ auth-login-cover.html
  └─ my-company.html

admin/full-version/assets/js/tai/pages/price-setting.page.js
admin/full-version/html/horizontal-menu-template/
  ├─ price-setting.html
  ├─ engine-qa.html
  ├─ diagram-gallery.html
  └─ diagnosis-step1.html

site/full-version/assets/js/tai/menu-tadmin.js
site/full-version/html/horizontal-menu-template/index.html

scripts/capture-app.js
scripts/capture-light.js
```

**파일명에 'industry' 포함** — `diagnosis-input-industry-paid1.html` 등 3개 페이지. URL 라우팅 변경 = 사용자 북마크 깨짐.

---

## 핵심 의사결정 필요 — 5가지

### 결정 1. **kosha_safety_materials.sector 처리** (30,547건)

가장 큰 영향. KOSHA 안전자료 메타.

| 현재 값 | 의미 | 권고 |
|---|---|---|
| COMMON (21,162) | 공통 | 다중 sector로 변환? 또는 별도 'COMMON' 유지? |
| CONSTRUCTION (4,338) | 건설 | CONSTRUCTION 그대로 |
| **MANUFACTURING** (3,727) | 제조 | INDUSTRIAL로 변경 |
| SERVICE (1,320) | 서비스업 | SPECIAL_FACILITY 또는 별도? |

KOSHA 분류는 우리 표준과 다른 자료원. **별도 정책 필요**:
- 옵션 A: kosha_safety_materials는 KOSHA 분류 그대로 두고 매핑 view 제공
- 옵션 B: 우리 표준으로 일괄 변환 (MANUFACTURING → INDUSTRIAL, SERVICE → SPECIAL_FACILITY, COMMON → 다중 sector)

권고: **옵션 A** (출처가 다름, 변환 시 의미 손실)

### 결정 2. **document_forms / inspection_master 한글 sector** (260 + 1,246건)

한글 표기(건물/공장/건설/공통)를 영어로 통일?

- 옵션 A: DB는 영어 표준 (BUILDING/INDUSTRIAL/CONSTRUCTION), UI에서 한글 변환
- 옵션 B: 별도 한글 컬럼 추가 (sector_korean), 영어/한글 병행
- 옵션 C: 한글 그대로 유지 (단 코드 영향 추적 불가)

권고: **옵션 A** + system_codes에 한글 라벨 추가

### 결정 3. **agent_service / price_policy 소문자 + facility/industry**

소문자 영어 + 'facility' 별도 + 'industry' 사용. 두 테이블 모두 30건 미만으로 작음.

권고: **일괄 UPDATE** (소문자 → 대문자, facility → SPECIAL_FACILITY)

### 결정 4. **factory_features.sector = 'ALL' (12건)**

'ALL' = 모든 sector 의미. 

- 옵션 A: NULL로 변환 (모든 sector 자동 적용)
- 옵션 B: ['BUILDING','INDUSTRIAL','CONSTRUCTION'] 다중 (sectors[] 컬럼으로 변경)
- 옵션 C: 'ALL' 그대로 유지 + 별도 처리

권고: **옵션 B** — 다른 테이블도 향후 sectors[] 다중 지원하려면 일관성 있게

### 결정 5. **마이그레이션 방식**

- 옵션 A: **일괄 SQL UPDATE** (모든 테이블 한 번에) — 빠름, 위험
- 옵션 B: **단계별** (DB → 백엔드 → 프론트) — 안전, 시간
- 옵션 C: **호환성 레이어** (백엔드에 양방향 변환 함수) — 점진, 코드 늘어남

권고: **옵션 B 단계별**:
1. DB UPDATE (가장 먼저, 운영 테이블 11개)
2. 백엔드 VALID_SECTORS + 하드코딩 INDUSTRY 변경
3. 프론트엔드 plan-gate.js, feature-flags.js, 페이지 라우트
4. URL 라우트 변경 (diagnosis-input-industry-* → diagnosis-input-industrial-*) — 사용자 영향 있음 (북마크), redirect 추가

---

## 작업 단계 (단계별 권고)

### Phase 1 — DB 운영 테이블 일괄 UPDATE (즉시)

```sql
BEGIN;

-- 영어 대문자 표준 (4 sector)
UPDATE diagnosis_input_fields SET sector='INDUSTRIAL' WHERE sector='INDUSTRY';
UPDATE diagnosis_purchases SET sector='INDUSTRIAL' WHERE sector='INDUSTRY';
UPDATE document_form_master SET sector='INDUSTRIAL' WHERE sector='MANUFACTURING';
UPDATE factory_features SET sector='INDUSTRIAL' WHERE sector='INDUSTRY';
UPDATE public_diagnosis_requests SET sector='INDUSTRIAL' WHERE sector='INDUSTRY';
UPDATE public_diagnosis_requests SET sector='BUILDING' WHERE sector='building';
UPDATE users SET sector='INDUSTRIAL' WHERE sector='INDUSTRY';

-- 소문자 → 대문자 (agent_service, price_policy)
UPDATE agent_service SET sector=CASE 
  WHEN sector='construction' THEN 'CONSTRUCTION'
  WHEN sector='industrial' THEN 'INDUSTRIAL'
  WHEN sector='facility' THEN 'SPECIAL_FACILITY'
  ELSE sector END;

UPDATE price_policy SET sector=CASE 
  WHEN sector='construction' THEN 'CONSTRUCTION'
  WHEN sector='industrial' OR sector='industry' THEN 'INDUSTRIAL'
  WHEN sector='facility' THEN 'SPECIAL_FACILITY'
  ELSE sector END;

-- factory_features.sector='ALL' → 별도 처리 (사용자 결정 후)

-- CHECK 제약 추가 (NULL 허용 + 4 enum)
ALTER TABLE diagnosis_input_fields ADD CONSTRAINT diagnosis_input_fields_sector_check
  CHECK (sector IS NULL OR sector IN ('BUILDING','INDUSTRIAL','CONSTRUCTION','SPECIAL_FACILITY'));
-- (각 테이블에 동일하게 추가)

COMMIT;
```

### Phase 2 — 백엔드 (tai-api)

```python
# 모든 VALID_SECTORS 일괄 변경
VALID_SECTORS = {"BUILDING", "INDUSTRIAL", "CONSTRUCTION", "SPECIAL_FACILITY"}

# 모든 'INDUSTRY' 문자열 비교 → 'INDUSTRIAL'
if sector == "INDUSTRY":  →  if sector == "INDUSTRIAL":
```

영향 파일 (Cursor 작업지시서로):
- `routers/diagnosis_fields.py`
- `routers/feature_flags.py`
- `routers/precedent_api.py`
- 기타 17개 파일

### Phase 3 — 프론트엔드 (tai-admin)

JS 파일:
- `tadmin/full-version/assets/js/feature-flags.js`
- `tadmin/full-version/assets/js/tai/plan-gate.js`
- `tadmin/full-version/assets/js/tai/menu-tadmin.js`
- `tadmin/full-version/app/i18n.js`

HTML 페이지:
- `diagnosis-input-industry-paid1/2/3.html` → 3 옵션 중 결정 필요:
  - A. 파일명 그대로 두고 내부 sector 값만 변경
  - B. 파일명도 industrial로 변경 + redirect 추가
  - C. 새 파일 추가 + 기존 파일은 deprecated

권고: **A** (파일명 변경 비용 > 효익. URL 영향 최소화)

### Phase 4 — UI 한글 라벨 정비

```sql
-- system_codes에 sector 한글 라벨 추가
INSERT INTO system_codes (category, category_name, code, code_name, code_value, sort_order, is_active) VALUES
('sector_label', 'sector한글라벨', 'BUILDING', '건물', NULL, 1, TRUE),
('sector_label', 'sector한글라벨', 'INDUSTRIAL', '공장', NULL, 2, TRUE),
('sector_label', 'sector한글라벨', 'CONSTRUCTION', '건설', NULL, 3, TRUE),
('sector_label', 'sector한글라벨', 'SPECIAL_FACILITY', '특수시설', NULL, 4, TRUE);
```

document_forms와 inspection_master의 한글 sector 컬럼은 유지하거나 별도 view 제공 (옵션 A 권고대로 처리).

---

## 위험 평가

| 위험 | 가능성 | 영향 | 완화 |
|---|---|---|---|
| 운영 중단 (오픈 전이라 무관) | 낮음 | 낮음 | 미오픈, 사용자 0명 |
| 데이터 일관성 깨짐 | 높음 | 높음 | 단계별 + 검증 SQL |
| 코드 deploy 실패 | 중간 | 중간 | Cursor 작업지시서 + 테스트 |
| 검색/CHECK 제약 누락 | 중간 | 낮음 | Phase 1 완료 후 일괄 검증 |
| facility_type_code (INDUSTRY_V2) 혼동 | 낮음 | 낮음 | sector와 별개 명시 |

→ **현재 미오픈 단계라 일괄 변경 위험 작음**. 단계별 진행 시 검증 가능.

---

## 다음 단계

사용자 결정 필요:
1. **결정 1~5에 대한 답변**
2. **Phase 1 (DB UPDATE) 즉시 실행 동의 여부**
3. **Phase 2~4 작업지시서 작성 진행 여부**

---

## 관련 문서

- `docs/extraction/HANDOFF_2026-05-06_evening.md` — 의미절 v1.7.1 본 적용
- `docs/extraction/LAW_SECTOR_MAPPING_2026-05-07.md` — 366 법령 sector 매핑
- `docs/extraction/SECTOR_CODE_IMPACT_2026-05-07.md` — **본 문서** (코드 영향 분석)
