# SEMANTIC CLAUSE SECTORS[] 다중매핑 완료 2026-05-07

> 의미절 자체에 sectors text[] 컬럼 추가 + law_sector_mapping에서 다중매핑 복사 완료

## 작업 완료 종합

| 단계 | 상태 |
|---|---|
| 1. 의미절 분리 | ✅ 완료 (58,495 clauses) |
| 2. 법령 단위 다중매핑 | ✅ 완료 (`law_sector_mapping.sectors text[]`) |
| 3. 매핑 무결성 | ✅ 완료 (MISMATCH 0) |
| **4. 의미절 자체 다중매핑** | **✅ 완료** (`semantic_clause.sectors text[]`) |

→ 이제 master_rule_v2 설계 진입 가능.

---

## 변경 내용

### 1. 컬럼 추가

```sql
ALTER TABLE semantic_clause 
  ADD COLUMN sectors text[];

-- CHECK 제약 (4 활성 sector만 허용, INACTIVE는 NULL)
ALTER TABLE semantic_clause ADD CONSTRAINT semantic_clause_sectors_valid
  CHECK (sectors IS NULL OR sectors <@ ARRAY['BUILDING','INDUSTRIAL','CONSTRUCTION','SPECIAL_FACILITY']::text[]);

-- 빈 배열 방지
ALTER TABLE semantic_clause ADD CONSTRAINT semantic_clause_sectors_nonempty
  CHECK (sectors IS NULL OR array_length(sectors, 1) >= 1);

-- GIN 인덱스 (다중 sector 검색 최적화)
CREATE INDEX idx_semantic_clause_sectors ON semantic_clause USING GIN(sectors);
```

semantic_clause_iter1 백업도 동일 처리.

### 2. 다중매핑 복사

```sql
UPDATE semantic_clause sci
SET sectors = lsm.sectors
FROM law_article la, law_sector_mapping lsm
WHERE sci.source_article_id = la.id
  AND la.law_id = lsm.law_id
  AND lsm.sectors IS NOT NULL;
```

### 3. 기존 sector 단일 컬럼 처리

호환성 위해 **임시 유지** (deprecated 표시). 추후 코드 정리 후 drop 예정.

```sql
COMMENT ON COLUMN semantic_clause.sector IS 
  'DEPRECATED: 단일 sector 호환성 컬럼. 신규 코드는 sectors text[] 사용. 추후 drop 예정.';

COMMENT ON COLUMN semantic_clause.sectors IS 
  'TAI 사업장 sector 다중 매핑 (BUILDING/INDUSTRIAL/CONSTRUCTION/SPECIAL_FACILITY). NULL = INACTIVE. 다중 값 = "공용".';
```

---

## 결과 통계

### 의미절 sector 매핑 분포 (58,495)

| 매핑 패턴 | 의미절 수 | 비율 |
|---|---|---|
| 단일 sector (단독 적용) | 25,809 | 44.1% |
| 2 sectors (공용) | 21,309 | 36.4% |
| 3 sectors (공용) | 11,216 | 19.2% |
| NULL (INACTIVE) | 161 | 0.3% |
| **합계** | **58,495** | **100%** |

다중 매핑("공용") 의미절: **32,525건 (55.6%)**

### sector별 적용 의미절 수 (unnest)

| sector | 적용 의미절 | 비율 |
|---|---|---|
| BUILDING | 30,314 | 52.0% |
| INDUSTRIAL | 29,955 | 51.4% |
| CONSTRUCTION | 28,302 | 48.5% |
| SPECIAL_FACILITY (비활성) | 13,504 | 23.1% |

3 활성 sector가 48~52%로 균형. 산업안전보건법 등 다중 매핑 법령이 3 sector 모두에 카운트되기 때문.

### 일관성 검증 (sector vs sectors[])

| 상태 | 건수 |
|---|---|
| ✅ CONSISTENT (sector ∈ sectors) | 28,960 (49.5%) |
| ✅ COMMON 단일컬럼 한계 (sectors가 진짜 다중) | 29,374 (50.2%) |
| ✅ NULL (INACTIVE) | 161 (0.3%) |
| ❌ INCONSISTENT | **0** |

---

## 사용 예제

### 정확한 sector별 의미절 조회

```sql
-- BUILDING 사업장에 적용되는 모든 의미절 (정확)
SELECT * FROM semantic_clause WHERE 'BUILDING' = ANY(sectors);
-- 결과: 30,314건 (단독 BUILDING + 다중 BUILDING 포함)
```

### 다중 적용("공용") 의미절만

```sql
SELECT * FROM semantic_clause 
WHERE array_length(sectors, 1) >= 2;
-- 결과: 32,525건
```

### 단일 sector 전용 의미절

```sql
SELECT * FROM semantic_clause 
WHERE array_length(sectors, 1) = 1
  AND sectors[1] = 'INDUSTRIAL';
-- 결과: INDUSTRIAL 단독 적용
```

### INACTIVE (사업장 의무 아님)

```sql
SELECT * FROM semantic_clause WHERE sectors IS NULL;
-- 결과: 161건 (자연재난구호/농어촌전기/정부조직 등)
```

### sector 교집합 (예: BUILDING + INDUSTRIAL 공용)

```sql
SELECT * FROM semantic_clause 
WHERE sectors @> ARRAY['BUILDING','INDUSTRIAL']::text[];
```

---

## 기존 단일 sector 컬럼 deprecation 일정

### 현재 (2026-05-07)
- `semantic_clause.sector` (단일) — 유지, deprecated 표시
- `semantic_clause.sectors[]` — 신규, 정확

### 다음 작업 (master_rule_v2 후)
- 모든 신규 코드는 `sectors[]` 사용
- 기존 코드는 `sector` 사용 (호환성 유지)

### 미래 (코드 정리 완료 후)
- `sector` 컬럼 drop
- `sectors[]`만 유지

---

## master_rule_v2 설계 준비도

```
✅ 의미절 분해 (58,495)            — base data
✅ 법령 → sectors[] 매핑 (366)     — sector 결정
✅ 의미절 → sectors[] 매핑 (58,334) — 정확한 다중매핑
✅ 매핑 무결성 (MISMATCH 0)         — 데이터 신뢰
✅ CHECK 제약 (13 테이블)           — 미래 보호
```

→ master_rule_v2 자동 변환 알고리즘에서 `semantic_clause.sectors[]`를 그대로 `master_rule.sectors[]`로 복사 가능.

---

## 검증 SQL (재실행 가능)

```sql
-- 1. sectors[] 분포
SELECT 
  CASE 
    WHEN sectors IS NULL THEN 'NULL (INACTIVE)'
    WHEN array_length(sectors, 1) = 1 THEN 'SINGLE'
    WHEN array_length(sectors, 1) = 2 THEN 'DOUBLE (공용)'
    WHEN array_length(sectors, 1) >= 3 THEN 'TRIPLE+ (공용)'
  END AS pattern,
  COUNT(*) AS cnt
FROM semantic_clause
GROUP BY pattern
ORDER BY cnt DESC;

-- 2. 일관성 검증 (sector vs sectors[])
SELECT 
  CASE
    WHEN sectors IS NULL THEN 'INACTIVE'
    WHEN sector = ANY(sectors) THEN 'CONSISTENT'
    WHEN sector = 'COMMON' AND array_length(sectors, 1) >= 2 THEN 'COMMON 다중매핑 (정상)'
    ELSE 'INCONSISTENT'
  END AS status,
  COUNT(*) AS cnt
FROM semantic_clause
GROUP BY status;
-- INCONSISTENT 0건이어야 함
```

---

## 관련 문서

- `docs/extraction/HANDOFF_2026-05-06_evening.md` — 의미절 v1.7.1 본 적용
- `docs/extraction/LAW_SECTOR_MAPPING_2026-05-07.md` — 366 법령 매핑
- `docs/extraction/SECTOR_INTEGRITY_VERIFICATION_2026-05-07.md` — 무결성 전수검사
- `docs/extraction/SEMANTIC_CLAUSE_SECTORS_ARRAY_2026-05-07.md` — **본 문서** (의미절 다중매핑 완료)
