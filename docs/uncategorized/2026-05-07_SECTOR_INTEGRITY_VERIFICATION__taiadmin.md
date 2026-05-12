# SECTOR INTEGRITY VERIFICATION 2026-05-07

> 모든 운영 테이블 sector 컬럼 전수검사 + 무결성 복구 + CHECK 제약 추가

## 작업 결과 종합

### ✅ 무결성 100% 달성

| 상태 | 행수 | 테이블 수 |
|---|---|---|
| **INVALID** (비표준 값) | **0** | 0 |
| **NULL** (정상) | 0 | 0 |
| STANDARD (4 sector 표준) | 31,172 | 14 |
| COMMON_TEMP (단일 컬럼 한계) | 30,031 | 4 |

### sector 컬럼 표준 (확정)

```
NULL                   — 미분류
BUILDING               — 건물
INDUSTRIAL             — 공장
CONSTRUCTION           — 건설
SPECIAL_FACILITY       — 특수시설 (비활성)
COMMON                 — 다중 적용 임시 표기 (단일 컬럼 한계, 추후 sectors[] 컬럼 도입 시 정리)
```

---

## 1. 매핑 무결성 — semantic_clause vs law_sector_mapping

### 변경 전
```
COMMON으로 분류된 의미절: 46,726건 (80%)
  - 진짜 다중 매핑(공용)이 필요한 것: 29,374건
  - 잘못 분류된 것 (단일 sector여야 함): 17,191건  ← 무결성 깨짐
NO_MAPPING: 161건 (INACTIVE 의도)
```

### 변경 후
```
무결성 매트릭스 (58,495 의미절):
  ✅ MATCH (clause sector ∈ 매핑)         : 28,960 (49.5%)
  ✅ COMMON for 다중매핑 (정상)           : 29,374 (50.2%)
  ✅ NO_MAPPING (INACTIVE 의도)           : 161 (0.3%)
  ❌ MISMATCH (검토 필요)                  : 0
```

**MISMATCH 0건 — 완벽한 무결성** 달성.

### semantic_clause sector 분포 변화

| sector | 변경 전 | 변경 후 | 변화 |
|---|---|---|---|
| COMMON | 46,726 | 29,535 | **-17,191** |
| **SPECIAL_FACILITY** | 0 | **13,504** | **+13,504** |
| INDUSTRIAL | 3,151 | 6,553 | +3,402 |
| BUILDING | 4,539 | 4,824 | +285 |
| CONSTRUCTION | 4,079 | 4,079 | 0 |

**의미**: 의료법/장애인복지법 등 SPECIAL_FACILITY 13,504건이 그동안 COMMON으로 잘못 묻혀있었음. 화학물질관리법 등 INDUSTRIAL 3,402건도 마찬가지.

---

## 2. industrial_accident_precedents (산재판례 849건) sector 자동 분류

### 변경 전
```
sector NULL: 849건 (100%) — 분류 안 됨
```

### 변경 후 (keywords 기반 자동 매칭)
```
BUILDING        : 770 (90.7%)
CONSTRUCTION    :  64 (7.5%)
INDUSTRIAL      :  11 (1.3%)
SPECIAL_FACILITY:   4 (0.5%)
NULL            :   0 (0%)
```

**알고리즘**: `keywords` 배열의 법령명 → `law_sector_mapping.sectors[]` → 빈도 최다 sector 채택

**한계**: 근로기준법(300건)이 BUILDING+INDUSTRIAL+CONSTRUCTION 다중이라 알파벳 순(BUILDING)으로 reduce. 단일 컬럼 한계. 정확한 다중 매핑은 추후 `sectors[]` 컬럼 도입 시.

---

## 3. CHECK 제약 추가 (13 테이블)

미래 invalid 값 차단:

```sql
ALTER TABLE <tbl> ADD CONSTRAINT <tbl>_sector_check
  CHECK (sector IS NULL OR sector IN 
    ('BUILDING','INDUSTRIAL','CONSTRUCTION','SPECIAL_FACILITY','COMMON'));
```

적용 테이블:
```
agent_service                       (25)
diagnosis_input_fields              (118)
diagnosis_purchases                 (16)
document_form_master                (63)
document_forms                      (260)
factories                           (30)
factory_features                    (28)
form_templates                      (11)
industrial_accident_precedents      (849)
inspection_master                   (1,246)
price_policy                        (29)
public_diagnosis_requests           (14)
users                               (19)

# semantic_clause, semantic_clause_iter1는 이미 추가됨
```

---

## 4. 빈 운영 테이블 (참고)

| 테이블 | 행수 | 비고 |
|---|---|---|
| `factory_diagnosis_results` | 0 | 운영 시작 전 |
| `inspection_requests` | 0 | 운영 시작 전 |

→ 데이터 0건이라 무결성 X. 향후 데이터 입력 시 CHECK 제약은 추가됨.

---

## 5. 백업/Archive 테이블 (변경 안 함)

다음 테이블은 archive 또는 backup으로 그대로 유지:
- `master_building_legal_rules` (2,002) — 참고용
- `law_rule_drafts` (87,099) — AI 초안 archive 예정
- `master_legal_rules_pending_review` (1,454)
- `master_legal_rules_preserved` (321)
- `master_legal_rules_archive` (44)
- `master_rules_archive_20260422`
- `diagnosis_results_backup_20260416`
- `inspection_master_backup_20260501`
- `law_rule_drafts_preswitch_20260423`
- `reparse_job_log`
- `semantic_clause_iter1` (58,495) — 본 테이블과 동기화 완료
- `v_drafts_with_code` — view

---

## 6. 잔여 작업 (Cursor 실행 대기)

| 파일 | 영향 |
|---|---|
| `CURSOR_TASK_2026-05-07_api_sector.md` | tai-api 20 파일 (INDUSTRY → INDUSTRIAL) |
| `CURSOR_TASK_2026-05-07_admin_sector.md` | tai-admin 15 파일 |
| `CURSOR_TASK_2026-05-07_kosha_industry_category.md` | kosha_collect.py 1 파일 |

---

## 검증 SQL (재실행 가능)

```sql
-- 1. 모든 운영 테이블 invalid sector 검색 (0이어야 함)
SELECT 'INVALID_FOUND' AS status, table_name, sector, COUNT(*)
FROM (
  SELECT 'agent_service' AS table_name, sector FROM agent_service
  UNION ALL SELECT 'diagnosis_input_fields', sector FROM diagnosis_input_fields
  UNION ALL SELECT 'diagnosis_purchases', sector FROM diagnosis_purchases
  UNION ALL SELECT 'document_form_master', sector FROM document_form_master
  UNION ALL SELECT 'document_forms', sector FROM document_forms
  UNION ALL SELECT 'factories', sector FROM factories
  UNION ALL SELECT 'factory_features', sector FROM factory_features
  UNION ALL SELECT 'form_templates', sector FROM form_templates
  UNION ALL SELECT 'industrial_accident_precedents', sector FROM industrial_accident_precedents
  UNION ALL SELECT 'inspection_master', sector FROM inspection_master
  UNION ALL SELECT 'price_policy', sector FROM price_policy
  UNION ALL SELECT 'public_diagnosis_requests', sector FROM public_diagnosis_requests
  UNION ALL SELECT 'semantic_clause', sector FROM semantic_clause
  UNION ALL SELECT 'users', sector FROM users
) t
WHERE sector IS NOT NULL 
  AND sector NOT IN ('BUILDING','INDUSTRIAL','CONSTRUCTION','SPECIAL_FACILITY','COMMON')
GROUP BY table_name, sector;

-- 2. semantic_clause vs law_sector_mapping 일관성
SELECT 
  CASE
    WHEN lsm.sectors IS NULL THEN 'NO_MAPPING (INACTIVE)'
    WHEN sci.sector = ANY(lsm.sectors) THEN 'MATCH'
    WHEN sci.sector = 'COMMON' AND array_length(lsm.sectors, 1) >= 2 THEN 'COMMON for 다중매핑'
    ELSE 'MISMATCH'
  END AS status,
  COUNT(*) AS cnt
FROM semantic_clause sci
JOIN law_article la ON la.id = sci.source_article_id
JOIN law_master lm ON lm.id = la.law_id
LEFT JOIN law_sector_mapping lsm ON lsm.law_id = lm.id
GROUP BY status
ORDER BY cnt DESC;
-- 기대: MISMATCH 0건
```

---

## 관련 문서

- `docs/extraction/SECTOR_CODE_IMPACT_2026-05-07.md` — 영향 분석
- `docs/extraction/LAW_SECTOR_MAPPING_2026-05-07.md` — 366 법령 매핑
- `docs/extraction/CURSOR_TASK_2026-05-07_api_sector.md` — 백엔드 작업
- `docs/extraction/CURSOR_TASK_2026-05-07_admin_sector.md` — 프론트 작업
- `docs/extraction/CURSOR_TASK_2026-05-07_kosha_industry_category.md` — KOSHA rename
- `docs/extraction/SECTOR_INTEGRITY_VERIFICATION_2026-05-07.md` — **본 문서** (전수검사)
