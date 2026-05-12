# law_rule_drafts 무결성 확보 통합 작업 계획 (S13)

**작성일**: 2026-05-04
**선행 문서**: `AUDIT_law_rule_drafts_20260504.md`
**총 데이터**: 3,158 row / 139 법령 / 713 조항
**목적**: 한 번에 실행 가능한 무결성 확보 마이그레이션 + 운영 정합성 회복

---

## 0. 답: "4가지로 끝나는가?"

**아니요.** 직전 보고의 4가지는 **결정 포인트**였고, 실제 작업은 **15개 변경 그룹**.
다만 단일 트랜잭션 + Python 스크립트 1개로 **한 번에 실행 가능**.

---

## 1. 추가 분석 결과 (S13 보강)

### 1.1 P1 15건 의미 확정

| 유형 | 건수 | 의미 |
|---|---:|---|
| registered 있는데 status≠APPROVED | 8 | **운영 적재 후 사후 강등** (전기사업법 5건 NEEDS_REVIEW + 다중이용업소법 3건 REJECTED). active 테이블에서 비활성화 됐는지 확인 필요 |
| APPROVED인데 registered NULL | 1 | NFTC 103B 2.1.1.1 — 운영 적재 누락 |
| law_changed_at > created_at | 6 | 모두 전기사업법. created=4/3 / changed=4/17. **논리 오류 아님**. "drafts row 만든 후 법령이 개정됨" 표시 |

### 1.2 AND 5건 = 다중 조건 의도 컨벤션 (정상)
- `condition_code` = `["floor_count","building_area"]` (배열)
- `condition_operator` = `AND`
- `condition_value` = JSON 객체

→ 5건 중 일부는 단순 문자열, 일부는 구조화 JSON. **value 구조만 통일 필요**.

### 1.3 article_id 1,352건 자동 매칭 시뮬레이션 (★ 핵심 발견)

| 매칭 전략 | 매칭 건수 | 비율 |
|---|---:|---:|
| 정확 매칭 (article_no_sort) | 0 | 0% |
| article_internal_key 매칭 | 0 | 0% |
| **정규식 article_no 매칭** (`제N조` → article_no=N) | **1,278** | **94.5%** |
| article_title 부분 매칭 | 1,192 | 88% |

→ **정규식 매칭으로 1,278건 즉시 자동 UPDATE 가능**.
→ 매칭 안 되는 74건은 별도 검수 큐.
→ master 없는 3건은 추가 적재.

### 1.4 master 미적재 3건
1. 이동용 음식판매 화물자동차 내 LPG 사용시설 특례기준 (산자부 고시 2024-61)
2. 캠핑용자동차 내 LPG 사용시설 안전기준 (산자부 고시 2024-62)
3. 항공위험물운송기술기준 (국토부)

→ 각 1조항짜리 작은 법령. master + version + article 적재만 하면 됨.

### 1.5 reviewed_at 1,413건 vs reviewed_by NULL = 일괄 자동 검수
- 2026-04-25 단일 날짜에 1,307건 집중
- → 일괄 마이그레이션. 이슈 아님. 다만 reviewed_by에 'SYSTEM_AUTO_BATCH' 등 식별자 채우면 더 명확

### 1.6 APPROVED but condition_code NULL 1,017건 = 정상 다수
- 소방시설법 시행규칙(75), 화재예방법 시행규칙(57), 작업환경측정 고시(52) 등
- 행정 절차/관리 의무 — 조건 없이 항상 적용 (예: "검사결과 보존 의무"는 모든 사업장 적용)
- → 사후 검토 큐로 두되 즉시 수정 대상은 아님

### 1.7 draft_rule_id 명명 = 의도된 그룹 키
- FIREACT 245 / HAZMAT 118 / HPGASACT 107 / LPGACT 101 / OSHACT 80 / CHEMACT 74 / HOUSINGACT 55 / MECHACT 41
- 체계적: `{법령코드}-{조항번호}-{용도/섹터}`
- → 식별자가 아닌 그룹 키 의도. 컬럼명만 명문화 필요 (`rule_group_code`로 변경 검토)

---

## 2. 통합 작업 계획 (총 5단계 / 15개 변경 그룹)

### Phase 0 — 안전장치 (소요 ~1분)

```sql
-- 0-1. 진단 시점 백업
CREATE TABLE law_rule_drafts_audit_20260504 AS
SELECT * FROM law_rule_drafts;

-- 0-2. 무결성 검증 SQL 스위트 (재실행 가능) → docs/sql/audit_law_rule_drafts.sql 로 저장
```

### Phase 1 — 컨벤션 결정 (대표님 결정 4개, 소요 ~10분)

| # | 항목 | 옵션 | 권장 |
|---|---|---|---|
| 1 | `condition_operator` 표기 | (a) `gte/eq/gt/lt` (단축형) / (b) `>=/==/>/<` (수학기호) | **(a)** 기존 다수 (gte 784 vs >= 25) |
| 2 | AND 룰 `condition_value` 구조 | (a) 단순 `{key: '>=N'}` / (b) 구조화 `{key: {operator, value, unit}}` | **(b)** 구조화 — unit/note 정보 보존 |
| 3 | `ai_flags` 컨벤션 | (a) object 통일 (`{notes: [...], ...}`) / (b) `review_notes` 컬럼 분리 | **(a)** object 통일 — 스키마 변경 없음 |
| 4 | `INSTALL` 1건 | (a) `ACTION`으로 통합 / (b) `INSTALL` enum 유지 | **(a)** ACTION 통합 — 단 1건이라 enum 분리 의미 없음 |

### Phase 2 — 자동 일괄 정리 마이그레이션 (소요 ~5분)

단일 트랜잭션 / `apply_migration` 한 번에 실행:

#### 2-A. P1 즉시수정 (15건)

```sql
-- (a) registered 있는데 status≠APPROVED 8건
--     → 먼저 active 테이블(legal_obligations)에서 해당 registered_rule_id 비활성화 여부 확인 후 결정
--     → 권장: status='APPROVED' 환원하지 말고 reviewer_note에 사유 기록 + active 측 정리
UPDATE law_rule_drafts
SET reviewer_note = COALESCE(reviewer_note,'') || ' [S13 audit: 운영적재 후 강등됨, active 정리 필요]',
    updated_at = NOW()
WHERE registered_rule_id IS NOT NULL AND TRIM(registered_rule_id)<>''
  AND status<>'APPROVED';

-- (b) APPROVED 1건 NFTC 103B 2.1.1.1 — active 등록 또는 status 환원 (수동 결정)
-- → 일괄 마이그레이션에서 제외, 별도 row 검토

-- (c) law_changed_at > created_at 6건 — 논리오류 아님
UPDATE law_rule_drafts
SET review_reason = COALESCE(review_reason,'') || ' [법령 개정 예정 row]',
    updated_at = NOW()
WHERE law_changed_at > created_at;
```

#### 2-B. P2-1 condition_operator 표기 통일 (87건)

```sql
UPDATE law_rule_drafts SET condition_operator = 'gte' WHERE condition_operator = '>=';
UPDATE law_rule_drafts SET condition_operator = 'eq'  WHERE condition_operator = '==';
UPDATE law_rule_drafts SET condition_operator = 'gt'  WHERE condition_operator = '>';
UPDATE law_rule_drafts SET condition_operator = 'lt'  WHERE condition_operator = '<';
-- AND 5건은 그대로 유지 (다중조건 표기, value 구조만 통일)
```

#### 2-C. P2-2 AND 룰 condition_value 구조 통일 (5건)

```sql
-- 단순 문자열 → 구조화 JSON (Python에서 처리 권장 — 정규식 파싱 필요)
-- 예: '{"floor_count": ">=7"}' → '{"floor_count": {"operator": "gte", "value": 7}}'
```

#### 2-D. P5 완전중복 제거 (22건 DELETE, 18 → 18 그룹)

```sql
WITH ranked AS (
  SELECT id, ROW_NUMBER() OVER (
    PARTITION BY law_name, law_article, obligation_summary,
                 condition_code, condition_operator, condition_value
    ORDER BY created_at, id
  ) AS rn
  FROM law_rule_drafts
)
DELETE FROM law_rule_drafts
WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
-- 예상: 40 - 18 = 22건 DELETE
```

#### 2-E. P6 양끝 공백/특수문자 정리 (21건)

```sql
UPDATE law_rule_drafts SET law_article = TRIM(law_article) 
WHERE law_article <> TRIM(law_article);
```

#### 2-F. P6 INSTALL → ACTION (1건, 결정 4번 (a) 채택 시)

```sql
UPDATE law_rule_drafts SET obligation_type = 'ACTION' WHERE obligation_type = 'INSTALL';
```

#### 2-G. P3 article_id 자동 매칭 (1,278건 UPDATE)

```sql
WITH matched AS (
  SELECT 
    n.id AS draft_id,
    a.id AS article_id
  FROM law_rule_drafts n
  JOIN law_master m ON m.law_name = n.law_name AND m.is_active = true
  JOIN law_article a ON a.law_version_id = m.current_version_id 
    AND a.article_no = (REGEXP_MATCH(n.law_article, '제\s*(\d+)조'))[1]::int
    AND COALESCE(a.article_sub_no, 0) = COALESCE(
      NULLIF((REGEXP_MATCH(n.law_article, '제\s*\d+조의\s*(\d+)'))[1], '')::int, 0
    )
  WHERE n.article_id IS NULL
)
UPDATE law_rule_drafts d
SET article_id = m.article_id, updated_at = NOW()
FROM matched m
WHERE d.id = m.draft_id;
-- 예상: 1,278건 (단, JOIN 결과 중복 가능 — 1:1 보장 검증 필수)
```

⚠️ **주의**: 위 매칭 결과 중 같은 (law_name, article_no, sub_no)에 매칭되는 article이 여러 version에 걸쳐 존재할 수 있음.
→ Python 스크립트로 dry-run + conflict 처리 후 실행 권장.

#### 2-H. P2-3 ai_flags object 통일 (2,583건 변환)

```sql
-- array → {notes: [...]}
UPDATE law_rule_drafts
SET ai_flags = jsonb_build_object('notes', ai_flags)
WHERE jsonb_typeof(ai_flags) = 'array';
-- 예상: 2,276건

-- null → 빈 객체
UPDATE law_rule_drafts
SET ai_flags = '{}'::jsonb
WHERE ai_flags IS NULL;
-- 예상: 307건

-- KEC 575건 object는 그대로
```

#### 2-I. reviewed_by 채우기 (1,413건)

```sql
UPDATE law_rule_drafts
SET reviewed_by = 'SYSTEM_AUTO_BATCH', updated_at = NOW()
WHERE reviewed_at IS NOT NULL AND reviewed_by IS NULL;
```

### Phase 3 — master 추가 적재 (3건, 소요 ~10분)

수동 또는 스크립트로 law_master + law_version + law_article 적재:

| 법령 | 부처 | 비고 |
|---|---|---|
| 이동용 음식판매 화물자동차 내 LPG 사용시설 특례기준 | 산자부 고시 2024-61 | 1조항 |
| 캠핑용자동차 내 LPG 사용시설 안전기준 | 산자부 고시 2024-62 | 1조항 |
| 항공위험물운송기술기준 | 국토부 | 1조항 |

적재 후 해당 3건 row의 article_id 매칭 추가 UPDATE.

### Phase 4 — 미해결 큐 운영 (74건)

article_id 자동 매칭 실패한 74건 → 검수 큐:
- `reviewer_note = '[S13 audit: article_id 자동매칭 실패, 수동 매핑 필요]'`
- 추후 수동 또는 LLM 보강 매칭

### Phase 5 — 정규화 트랙 (별도, 향후)

- KEC 575건 정규화 (sector / condition_code / obligation_type 채우기) — 핸드오프 § 6 자동 정규화 알고리즘 결정 후
- APPROVED but condition_code NULL 1,017건 검토 — 진짜 조건 없는 룰인지 확정

---

## 3. 실행 형태 — Python 스크립트 1개로 통합

```
~/dev/tai-poc-kec/audit_drafts_phase2.py
├─ 0. 백업 테이블 생성
├─ 1. dry-run 모드 (각 단계별 영향 row 카운트만 출력)
├─ 2. 사용자 확인 (y/n)
├─ 3. 단일 트랜잭션으로 2-A ~ 2-I 순차 실행
│   ├─ 2-A: P1 reviewer_note 보강 (8건)
│   ├─ 2-B: condition_operator 통일 (87건)
│   ├─ 2-C: AND value 구조 통일 (5건, JSON 파싱 필요)
│   ├─ 2-D: 완전중복 DELETE (22건)
│   ├─ 2-E: law_article TRIM (21건)
│   ├─ 2-F: INSTALL → ACTION (1건)
│   ├─ 2-G: article_id 자동매칭 (1,278건, conflict 처리 포함)
│   ├─ 2-H: ai_flags object 통일 (2,583건)
│   └─ 2-I: reviewed_by 채우기 (1,413건)
├─ 4. 검증 — 무결성 진단 SQL 재실행 → 깨끗해진 항목 확인
└─ 5. 결과 리포트 출력
```

장점:
- dry-run으로 사전 검증
- 단일 트랜잭션 → 실패 시 ROLLBACK
- conflict / 예외 row를 CSV로 출력 (수동 검토용)

---

## 4. 변경 그룹 요약표

| # | 단계 | 영향 row | 단계명 | 자동/수동 |
|---:|---|---:|---|---|
| 1 | 0 | 3,158 | 백업 테이블 생성 | 자동 |
| 2 | 1 | — | 컨벤션 4개 결정 | **수동 (대표님)** |
| 3 | 2-A | 8+6=14 | P1 reviewer_note 보강 | 자동 |
| 4 | 2-A(b) | 1 | NFTC 103B 1건 | **수동 검토** |
| 5 | 2-B | 87 | condition_operator 표기 통일 | 자동 |
| 6 | 2-C | 5 | AND 룰 value 구조 통일 | 자동 (Python) |
| 7 | 2-D | 22 | 완전중복 DELETE | 자동 |
| 8 | 2-E | 21 | law_article TRIM | 자동 |
| 9 | 2-F | 1 | INSTALL → ACTION | 자동 |
| 10 | 2-G | 1,278 | article_id 자동 매칭 | 자동 (Python) |
| 11 | 2-H | 2,583 | ai_flags object 통일 | 자동 |
| 12 | 2-I | 1,413 | reviewed_by 채우기 | 자동 |
| 13 | 3 | 3 | master 추가 적재 | **수동 + 자동** |
| 14 | 4 | 74 | 미해결 큐 운영 | **수동 보강 필요** |
| 15 | 5 | 575+1,017 | 정규화 트랙 | 별도 트랙 |

**총 자동 처리 row**: 약 5,418 (중복 영향 포함)
**수동 검토 필요**: 약 78 (NFTC 1 + 미해결 74 + master 추가 3)
**별도 트랙**: 1,592 (정규화)

---

## 5. 다음 단계 의사결정

대표님 결정 필요:

1. **Phase 1 컨벤션 4개 결정** (10분)
2. **Phase 2 Python 스크립트 작성 시작** — 직접 작성 (Cursor) vs 본 핸드오프에 SQL 그대로 두고 분할 실행
3. **Phase 3 master 3건 적재 우선순위** — 지금 vs 별도 트랙
4. **Phase 4 미해결 74건** — 자동 보강 시도 (LLM 매칭) vs 수동 검수 큐로만

이 4개 답이 나오면 한 번에 실행 가능.
