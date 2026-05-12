# HANDOFF 2026-05-07 — sector 표준화 + 의미절 다중매핑 + master_rule_v2 설계

> 의미절 분해 → sector 표준화 → 다중매핑 → master_rule_v2 설계까지 완료한 큰 마일스톤.

---

## 오늘 작업 종합

### ✅ 완료 (DB 변경)

| # | 작업 | 결과 |
|---|---|---|
| 1 | 366 법령 → sectors[] 자동 매핑 | HIGH 331 / MEDIUM 28 / INACTIVE 7 |
| 2 | 외부 검색 검증 | 다중이용업소·재난구호·농어촌전기 등 5 그룹 |
| 3 | sector 표준 통일 (system_codes) | 4 sector 표준 + 한글 라벨 (sector_label) |
| 4 | factories.sector 통일 | INDUSTRY → INDUSTRIAL (15 rows) |
| 5 | law_sector_mapping 테이블 생성 | 366 법령 INSERT |
| 6 | DB 운영 테이블 일괄 마이그레이션 | 15 테이블, 한글/소문자/MANUFACTURING/INDUSTRY/ALL 모두 표준화 |
| 7 | KOSHA industry_category 분리 | sector → industry_category (의미 차원 분리) |
| 8 | sector 무결성 전수검사 | INVALID 0건, MISMATCH 0건 |
| 9 | semantic_clause COMMON 17,191건 정확한 sector로 갱신 | SPECIAL_FACILITY 13,504 + INDUSTRIAL 3,402 + BUILDING 285 |
| 10 | industrial_accident_precedents 849건 sector 자동 분류 | NULL → 100% 채움 |
| 11 | CHECK 제약 13 테이블 추가 | 미래 invalid 차단 |
| 12 | **semantic_clause.sectors text[] 컬럼 추가** | **다중매핑 완료, 32,525건 공용 의미절** |
| 13 | semantic_clause_iter1 동기화 | 본 + 백업 일치 |

### ✅ 작업지시서 push (Cursor 실행 대기)

| 파일 | 대상 |
|---|---|
| `CURSOR_TASK_2026-05-07_api_sector.md` | tai-api 20 파일 (INDUSTRY → INDUSTRIAL) |
| `CURSOR_TASK_2026-05-07_admin_sector.md` | tai-admin 15 파일 |
| `CURSOR_TASK_2026-05-07_kosha_industry_category.md` | kosha_collect.py 1 파일 |

### ✅ 설계 doc push

| 파일 | 내용 |
|---|---|
| `DESIGN_master_rule_v2_2026-05-07.md` | master_rule_v2 스키마 + 변환 알고리즘 + 4계층 흐름 |

---

## 핵심 결과 — 의미절 sectors[] 다중매핑

| 매핑 패턴 | 의미절 수 | 비율 |
|---|---|---|
| 단일 sector (단독 적용) | 25,809 | 44.1% |
| 2 sectors (공용) | 21,309 | 36.4% |
| 3 sectors (공용) | 11,216 | 19.2% |
| NULL (INACTIVE) | 161 | 0.3% |
| **합계** | **58,495** | **100%** |

다중 매핑("공용") 의미절: **32,525건 (55.6%)**

### sector별 적용 의미절 수 (다중 unnest)

| sector | 적용 의미절 |
|---|---|
| BUILDING | 30,314 |
| INDUSTRIAL | 29,955 |
| CONSTRUCTION | 28,302 |
| SPECIAL_FACILITY (비활성) | 13,504 |

---

## sector 표준 (확정)

### 4 활성 sector

| 코드 | 한글 | 의미 |
|---|---|---|
| BUILDING | 건물 | 건축법, 화재안전, 시설안전 |
| INDUSTRIAL | 공장 | 제조업, 화학물질, 위험물 |
| CONSTRUCTION | 건설 | 건설안전법, KCSC |
| SPECIAL_FACILITY | 특수시설 | 의료/학교/철도 등 (비활성, 고도화 예정) |

### 임시 표기

| 코드 | 의미 |
|---|---|
| COMMON | 단일 컬럼 한계로 임시 표기. `sectors[]` 컬럼 도입 후에는 다중 매핑으로 정리됨 |
| NULL | 사업장 의무 아님 (INACTIVE: 자연재난구호/농어촌전기/정부조직) |

---

## 단일 sector 컬럼 vs 다중 sectors[] 컬럼

### 현재 (호환성 유지)

```sql
-- 단일 컬럼 (DEPRECATED, 호환성 위해 유지)
semantic_clause.sector text  -- 'COMMON' or 'BUILDING' 등

-- 다중 컬럼 (NEW, 정확)
semantic_clause.sectors text[]  -- ['BUILDING','INDUSTRIAL','CONSTRUCTION'] 등
```

### 미래 (코드 정리 후)
- 모든 신규 코드는 `sectors[]` 사용
- `sector` 단일 컬럼 drop
- 동일하게 `factories`, `inspection_master` 등도 `sectors[]` 도입 가능

---

## master_rule_v2 설계 요약

### 4계층 흐름

```
[Layer 1] semantic_clause (58,495)        ← ✓ 완료
              │ 자동 변환 (정규식+키워드)
              ▼
[Layer 2] master_rule_v2 (신규)            ← 다음 단계
              │ 법령엔진 (사업장 매칭)
              ▼
[Layer 3] inspection_sets (기존, 보강)     ← 점검항목 (4가지 세팅)
              │ 안전관리자 세팅 완료
              ▼
[Layer 4] work_schedules (기존)           ← 자동 일정
```

### master_rule_v2 핵심 컬럼 (요약)

```sql
-- 식별 + 출처
id, rule_code, source_clause_id (FK), source_article_id, source_law_id, legacy_mblr_id

-- 6하원칙
when_*: cycle_type, cycle_value, cycle_unit, due_days, base_event, text_raw
who_executor, who_executor_text_raw
what_action, what_target, what_action_text_raw
how_method, how_form
sectors text[] (의미절 그대로 복사)
why_obligation_summary, why_law_citation

-- 범위 (사업장 매칭)
scope_industry_codes[], scope_facility_types[], scope_construction_types[],
scope_process_codes[], scope_equipment_types[], scope_building_use_codes[],
scope_min_area_sqm, scope_min_employees, scope_min_construction_amount,
scope_extra (jsonb)

-- 분류 (이미지 탭)
obligation_category: 점검 / 작업_전 / 보고 / 서류 / 신고 / 선임 / 조치 / 기타

-- 검증 메타
generation_method (AUTO_REGEX/MANUAL/HYBRID), generation_confidence (0~1)
status (DRAFT/VALIDATED/ACTIVE/DEPRECATED)
needs_review, review_reason
```

### 변환 알고리즘 (AI 0%)

```
1. is_rule_candidate() — DEFINITION/DELEGATION/STATEMENT skip
2. extract_who_what_how() — 의미절 5요소 직접 매핑
3. extract_when() — cycle_text 정밀 파싱
4. extract_scope() — 키워드 사전 매칭
5. classify_obligation_category() — 8 분류 자동
6. calculate_confidence() — 5W1H 채움률
7. needs_review() — 신뢰도 < 0.7 OR scope 비어있음
```

예상 결과:
- 변환 가능: ~46,000건
- VALIDATED: ~30,000건
- DRAFT (needs_review): ~16,000건

---

## 내일 (또는 다음 작업) 우선순위

### Phase A — master_rule_v2 테이블 생성

```sql
-- DESIGN_master_rule_v2_2026-05-07.md의 DDL 실행
-- Supabase migration: create_master_rule_v2_table
```

### Phase B — 변환 스크립트 작성

`docs/extraction/scripts/convert_clause_to_rule.py`:
- semantic_clause 읽기
- 7단계 알고리즘 적용
- master_rule_v2 INSERT
- 변환 로그

예상 시간: 2~3일 (정규식 사전 정확성 검증 포함)

### Phase C — Cursor 작업 3개 실행

| 파일 | 영향 |
|---|---|
| `CURSOR_TASK_2026-05-07_kosha_industry_category.md` | kosha_collect.py 1 파일 (가장 작음) |
| `CURSOR_TASK_2026-05-07_api_sector.md` | tai-api 20 파일 |
| `CURSOR_TASK_2026-05-07_admin_sector.md` | tai-admin 15 파일 |

권장 순서: kosha → api → admin (작은 것부터, 백엔드 → 프론트)

### Phase D — inspection_sets 4가지 세팅 컬럼 추가

```sql
ALTER TABLE inspection_sets ADD COLUMN is_when_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN is_who_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN is_what_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN is_how_set BOOLEAN DEFAULT FALSE;
ALTER TABLE inspection_sets ADD COLUMN is_schedule_ready BOOLEAN 
  GENERATED ALWAYS AS (is_when_set AND is_who_set AND is_what_set AND is_how_set) STORED;
```

### Phase E — 법령엔진 API v2 작성

`tai-api/routers/legal_engine_v2.py`:
- POST `/legal-engine/evaluate?factory_id=X` — 적용 룰 추출
- POST `/legal-engine/sync-inspection-sets?factory_id=X` — 룰 → inspection_sets

### Phase F — 프론트엔드 점검항목관리 페이지 연동

`safe.taieng.co.kr/html/horizontal-menu-template/inspection-anchor` — master_rule_v2 기반 갱신

---

## 사용 예제 (참고)

```sql
-- BUILDING 사업장 적용 의미절 (정확)
SELECT * FROM semantic_clause WHERE 'BUILDING' = ANY(sectors);
-- → 30,314건

-- 다중 적용("공용") 의미절
SELECT * FROM semantic_clause WHERE array_length(sectors, 1) >= 2;
-- → 32,525건

-- INACTIVE
SELECT * FROM semantic_clause WHERE sectors IS NULL;
-- → 161건

-- 사업장 X 적용 룰 (master_rule_v2 생성 후)
SELECT mr.* FROM master_rule_v2 mr, factories f
WHERE f.id = $1 
  AND f.sector = ANY(mr.sectors)
  AND mr.status = 'ACTIVE';
```

---

## 작업 원칙 (불변)

1. AI/LLM 호출 0% (정규식/키워드 사전 기반만)
2. 검증 없는 완료 선언 금지
3. 패턴 발견 → 룰 보강 → 재반복 (iterative refinement)
4. 정확함이 건수/비율보다 중요
5. ask_user_input_v0 사용 금지 (텍스트로 직접)
6. 200줄+ 파일은 GitHub MCP 직접 수정 금지 → Cursor 로컬
7. 비-OBLIGATION inherit는 needs_review로 마크 (silent failure 방지)
8. 의미절 출처 추적 가능 (FK), AI 임의판단 추적/차단

---

## 핵심 인프라 메모

- Project ID: `vwlahtguyggrhvslabax` (서울)
- Repo: `taiengineering/tai-admin`, `taiengineering/tai-api` (모두 main only)
- 의미절: `semantic_clause` (58,495 rows, sectors[] 다중매핑 완료)
- 백업: `semantic_clause_iter1` (동기화 완료)
- sector 표준: `system_codes.sector` (4개) + `system_codes.sector_label` (한글)
- 매핑: `law_sector_mapping` (366 법령)
- 신규 설계: `master_rule_v2` (DDL 준비됨, 미생성)

---

## 오늘 push된 모든 문서 (한 번에 보기)

```
docs/extraction/
├── HANDOFF_2026-05-06_evening.md           ← 어제 핸드오프
├── LAW_SECTOR_MAPPING_2026-05-07.md        ← 366 법령 sector 매핑
├── SECTOR_CODE_IMPACT_2026-05-07.md        ← 코드 영향 분석
├── CURSOR_TASK_2026-05-07_api_sector.md    ← tai-api 작업지시서
├── CURSOR_TASK_2026-05-07_admin_sector.md  ← tai-admin 작업지시서
├── CURSOR_TASK_2026-05-07_kosha_industry_category.md  ← KOSHA rename
├── SECTOR_INTEGRITY_VERIFICATION_2026-05-07.md  ← 무결성 전수검사
├── SEMANTIC_CLAUSE_SECTORS_ARRAY_2026-05-07.md  ← 의미절 sectors[] 다중매핑
├── DESIGN_master_rule_v2_2026-05-07.md     ← master_rule_v2 설계
└── HANDOFF_2026-05-07.md                   ← 본 핸드오프 문서
```

---

## 이전 핸드오프 시리즈

- `HANDOFF_2026-05-05.md` — 분해기 v1.0~v1.4, KEC 완료, Phase1/2 완료
- `HANDOFF_2026-05-06_evening.md` — 의미절 v1.7.1 본 적용 + sector 표준화 분석 시작
- `HANDOFF_2026-05-07.md` — **본 문서** (sector 표준화 완료 + 다중매핑 + master_rule_v2 설계)
