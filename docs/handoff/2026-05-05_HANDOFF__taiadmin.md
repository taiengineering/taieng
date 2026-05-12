# 법령파싱 작업 핸드오프 (2026-05-05 → 2026-05-06)

## 0. 오늘 최종 결과 (2026-05-05 마감)

| Phase | articles 처리됨 / 대상 | parts | 상태 |
|---|---|---:|:---:|
| 일반 법령 (조문) | 20,711 / 22,642 (KEC 제외 100%, 남44=짧음) | 116,014 | ✅ 완료 |
| KEC | 1,931 / 1,931 | 7,518 | ✅ 완료 |
| **Phase 1: NFTC/KDS** | **4,887 / 5,331** (444 미처리) | **5,387** | ✅ 완료 |
| **Phase 2: 본칙** | **5,155 / 5,444** (289 미처리) | **21,216** | ✅ 완료 |
| **합계** | **32,684** | **150,135** | — |

### 미처리 분석 (오늘 추가)
- Phase 1 NFTC/KDS 444 = article_text 짧음 또는 article_title 번호 추출 실패
- Phase 2 본칙 289 = article_text 짧음 또는 마커 없는 단일 문단 + duplicate key 1건 (ENG.N.002.0030-000, 무시 가능)
- 모두 본질적 한계 — 추가 처리 가치 낮음

## 1. 어제(2026-05-05) 완료 작업 종합

### 일반 법령 (조문 type)
- 미처리 517 articles 중 473 처리 완료 (parts 3,173 신규 적재)
- 남은 44 = `article_text ≤ 10자` (분해 불가능한 짧은 article)
- v8 RPC `get_unprocessed_articles_for_parser` 도입 — fetch_all_paged 페이징 누락/중복 우회

### KEC (한국전기설비규정) 통합
| 단계 | 결과 |
|---|---|
| 본문 INSERT | 1,931 leaf articles (5자리 1,485 / 4자리 420 / 3자리 26) |
| 본문 분리 | 7,518 parts (paragraph 1,931 + clause 3,043 + subclause 2,121 + proviso 423) |
| drafts 매핑 | 572/575 (99.5%) — 5자리 393 / 4자리 부모 157 / 3자리 부모 22 |
| 매핑 실패 3개 | `231.3.3.다`, `표 232.2-2 주석`, `표 645.8.5-1` (manual 검토 필요) |

### Phase 1: NFTC/KDS parser
- 처리: 4,887 articles → 5,387 parts (대부분 single paragraph, 평균 1.1 parts/article)
- 미처리: 444 (article_title 시작 번호 추출 실패 + article_text < 5자)
- script: `docs/extraction/scripts/parse_nftc_kds_parts.py` (commit `3cab5a9f`)

### Phase 2: 본칙 parser
- 처리: 5,155 articles → 21,216 parts (호·항·목 다수 분리)
- 미처리: 289 (단일 문장, 마커 없음)
- script: `docs/extraction/scripts/parse_bonchik_parts.py` (commit `1778d419`)
- 본칙 5,444 분포 분석:
  - 일반법령형 (제N조): 3,699 (68%) → 마커 부착 후 정상 분리
  - NFTC/KDS형 (N.N): 1,140 (21%) → single paragraph 처리
  - 기타: 605 (11%)

### 코드 변경 이력
| commit | 파일 | 내용 |
|---|---|---|
| `f25521a` | `import_kec_articles.py` v1 | KEC 텍스트 → law_article INSERT |
| `625d60c` | `import_kec_articles.py` v2 | law_version_id NOT NULL fix |
| `315a3790` | `parse_article_parts.py` v6 | KEC 제외 EXCLUDED_LAW_NAMES |
| `90a1d7d4` | `parse_kec_parts.py` 신규 | KEC 전용 parser |
| `4cf91810` | `parse_article_parts.py` v7 | article_type='조문' filter + distinct |
| `9e5b2b76` | `parse_article_parts.py` v7.1 | proviso typo fix |
| `0c19d2c8` | `parse_article_parts.py` v8 | --unprocessed-only RPC 옵션 |
| `3cab5a9f` | `parse_nftc_kds_parts.py` 신규 | Phase 1 — NFTC/KDS parser |
| `1778d419` | `parse_bonchik_parts.py` 신규 | Phase 2 — 본칙 parser |
| `c2df86bf` | `HANDOFF_2026-05-05.md` 신규 | 핸드오프 문서 |

### Supabase RPC 추가
- `get_unprocessed_articles_for_parser(excluded_law_names text[])` — 미처리 조문 article 직접 fetch
- `map_kec_article(law_article text)` — KEC drafts.law_article → KEC article.id 매핑

## 2. 현재 DB 상태 (2026-05-05 마감)

### law_article 분포
| article_type | count | 처리 상태 |
|---|---:|:---:|
| 조문 (일반 법령) | 22,642 | ✅ 본질완료 (20,711 + KEC 1,931) |
| 본칙 (행정고시류) | 5,444 | ✅ 5,155 처리 (289 미처리, 한계) |
| 장/절/조/항/목 (NFTC/KDS) | 5,331 | ✅ 4,887 처리 (444 미처리, 한계) |
| 전문 (placeholder) | 1,766 | — 처리 불필요 |

### law_article_part
- 총 parts: **150,135**
- distinct articles: 32,684

### drafts 매핑 대기 현황 (placeholder 가리킴)
| 카테고리 | drafts 수 | Phase 3 처리 |
|---|---:|---|
| NFTC/기술기준 계열 | 1,335 | Phase 1 article (NFTC/KDS 4,887개) |
| 일반 법령 | 674 | 이미 처리된 조문 article 매핑 |
| 고시/지침/규정 | 141 | Phase 2 article (본칙 5,155개) |
| 기타 | 281 | 분석 필요 |
| **합계** | **2,431** | — |

## 3. 내일(2026-05-06) Phase 3 진행 — drafts 매핑

### ⚠️ 매핑 logic 복잡성 — 진행 전 결정 필요

article 구조가 type별로 달라 매핑 함수 단일화 어려움:

| article 종류 | 매핑 키 | 매핑 함수 |
|---|---|---|
| 일반 법령 | `article_no` (예: 5조 = `article_no=5`) | 신규 작성 |
| KEC | `article_sub_no` 인코딩 (예: 113.2.1 = 113002001) | ✅ `map_kec_article` |
| **NFTC/KDS** | **`article_title` 시작 번호** (예: "1.7.1.2 ...") | 신규 — string LIKE 매칭 + 부모 fallback |
| **본칙** | `article_no` 또는 `article_title` 혼재 | 신규 — 형식 자동 판단 |

### 진행 옵션 (내일 선택)

#### 옵션 A: drafts 매핑 보류 ⭐ 가장 보수적
- 매핑 함수 안 만들고, 진단 엔진 검색 시 `drafts.law_name + drafts.law_article` 직접 조회
- drafts는 정량 추출 데이터로만 사용 (매핑 테이블 X)
- ⚠️ 단점: drafts 역할 변경 결정과 충돌 — 재논의 필요

#### 옵션 B: NFTC/KDS만 시도 ⭐ 권장 시작점
- 1,335개에 대한 매핑 함수 1개만 만들고 정확도 sample 검증
- 잘 작동하면 본칙·일반 법령·기타로 단계적 확장
- 정확도 낮으면 옵션 A로 회귀
- 작업량: RPC 함수 1개 + 매핑 dry-run + 매핑 UPDATE + sample 검증

#### 옵션 C: 4가지 매핑 함수 동시 작성
- map_general / map_nftc_kds / map_bonchik / map_etc
- 큰 작업, 검증 분산되어 정확도 보장 어려움
- 비추천

### 옵션 B 진행 시 작업 plan (NFTC/KDS 매핑)

#### 1단계: drafts.law_article 형식 sample 분석
```sql
-- placeholder 가리키는 NFTC drafts sample 30개 (다양한 패턴)
SELECT d.law_name, d.law_article, COUNT(*) AS cnt
FROM law_rule_drafts d
JOIN law_article a ON a.id = d.article_id
WHERE a.article_no = 1
  AND (d.law_name LIKE '%NFTC%' OR d.law_name LIKE '%기술기준%' 
       OR d.law_name LIKE '%설계기준%')
GROUP BY 1, 2
ORDER BY cnt DESC, d.law_name, d.law_article
LIMIT 30;
```

#### 2단계: NFTC article의 article_title 형식 검증
```sql
-- NFTC article의 article_title 시작 번호 추출 패턴
SELECT 
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE article_title ~ '^\s*\d+(\.\d+)*') AS title_num_match,
  COUNT(*) FILTER (WHERE article_title !~ '^\s*\d+') AS title_no_num
FROM law_article 
WHERE article_type IN ('장','절','조','항','목');
```

#### 3단계: map_nftc_kds_article RPC 함수 작성

```sql
CREATE OR REPLACE FUNCTION map_nftc_kds_article(
    law_name_str text, 
    law_article_str text
) RETURNS uuid AS $$
DECLARE
    found_id uuid;
    parts text[];
    parent_pattern text;
    i int;
BEGIN
    IF law_article_str IS NULL OR law_name_str IS NULL THEN
        RETURN NULL;
    END IF;
    
    -- 1단계: 정확 매칭 - article_title이 law_article_str로 시작
    SELECT a.id INTO found_id
    FROM law_article a 
    JOIN law_master m ON m.id = a.law_id
    WHERE m.law_name = law_name_str
      AND a.article_type IN ('장','절','조','항','목')
      AND a.article_title ~ ('^\s*' || regexp_replace(law_article_str, '\.', '\.', 'g') || '(\s|$)')
    LIMIT 1;
    
    IF found_id IS NOT NULL THEN RETURN found_id; END IF;
    
    -- 2단계 ~ N단계: 부모 fallback (점 분리 단계적 축소)
    parts := regexp_split_to_array(law_article_str, '\.');
    FOR i IN REVERSE (array_length(parts, 1) - 1)..1 LOOP
        parent_pattern := array_to_string(parts[1:i], '.');
        
        SELECT a.id INTO found_id
        FROM law_article a 
        JOIN law_master m ON m.id = a.law_id
        WHERE m.law_name = law_name_str
          AND a.article_type IN ('장','절','조','항','목')
          AND a.article_title ~ ('^\s*' || regexp_replace(parent_pattern, '\.', '\.', 'g') || '(\s|\.|$)')
        LIMIT 1;
        
        IF found_id IS NOT NULL THEN RETURN found_id; END IF;
    END LOOP;
    
    RETURN NULL;  -- 매칭 실패
END;
$$ LANGUAGE plpgsql STABLE;
```

#### 4단계: dry-run + 정확도 검증 (sample 20개)
```sql
WITH mapped AS (
    SELECT d.id, d.law_name, d.law_article,
           map_nftc_kds_article(d.law_name, d.law_article) AS new_article_id
    FROM law_rule_drafts d
    JOIN law_article a ON a.id = d.article_id
    WHERE a.article_no = 1
      AND (d.law_name LIKE '%NFTC%' OR d.law_name LIKE '%기술기준%' 
           OR d.law_name LIKE '%설계기준%')
)
SELECT 
    COUNT(*) AS total,
    COUNT(new_article_id) AS mapped,
    COUNT(*) - COUNT(new_article_id) AS unmapped,
    ROUND(100.0 * COUNT(new_article_id) / COUNT(*), 1) AS mapping_pct
FROM mapped;

-- sample 검증 — 매핑된 article의 article_title이 정말 drafts.law_article과 일치하는지
SELECT d.law_name, d.law_article AS draft_article,
       LEFT(a2.article_title, 80) AS mapped_to_title
FROM law_rule_drafts d
JOIN law_article a ON a.id = d.article_id
JOIN law_article a2 ON a2.id = map_nftc_kds_article(d.law_name, d.law_article)
WHERE a.article_no = 1
  AND (d.law_name LIKE '%NFTC%' OR d.law_name LIKE '%기술기준%')
ORDER BY RANDOM()
LIMIT 20;
```

#### 5단계: 정확도 OK 시 UPDATE
```sql
UPDATE law_rule_drafts d
SET article_id = map_nftc_kds_article(d.law_name, d.law_article),
    updated_at = NOW()
FROM law_article a
WHERE a.id = d.article_id
  AND a.article_no = 1
  AND (d.law_name LIKE '%NFTC%' OR d.law_name LIKE '%기술기준%' 
       OR d.law_name LIKE '%설계기준%')
  AND map_nftc_kds_article(d.law_name, d.law_article) IS NOT NULL;
```

## 4. 미해결 사항

### A. 일반 법령 NN의M parser 버그 (메모리 #25)
- 561 articles 잠재 영향
- `process_clauses`가 `[N.]` 마커만 보고 clause_no 결정 → `1의2`, `17의2` 같은 패턴을 같은 호로 인식
- 표기 통일 방안: `NN의M` → `.N.M` (예: `1의2` → `.1.2`)
- 우선순위: Phase 3 완료 후

### B. KEC 매핑 실패 3개
- `231.3.3.다` — 5자리/부모 모두 본문 없음
- `표 232.2-2 주석` — 표 형식
- `표 645.8.5-1` — 표 형식
- 조치: manual 검토 또는 placeholder 유지

### C. Phase 1, 2 미처리 733개
- Phase 1: 444 (NFTC/KDS — article_title 번호 추출 실패)
- Phase 2: 289 (본칙 — 마커 없는 단일 문장)
- 본질적 한계 — 추가 시도 가치 낮음

### D. parse_bonchik_parts.py SyntaxWarning
- docstring 안 `\s` 표기 (`^N.\s`) → raw string으로 fix 필요
- 동작에 영향 없음 — 다음 commit에서 정정

## 5. 중요 컨텍스트

### drafts 역할 변경 (대표 결정 2026-05-05)
- drafts는 더 이상 정량 추출 데이터 보관소가 아님
- 정량 추출(주체·시기·조건 등)은 법령 영역에서 직접 관리
- drafts는 **article_id ↔ master_rule_id 매핑 테이블** 역할

### 작업 진행 원칙 (메모리 #7)
- "진행률·건수 쌓기보다 옳은 방식 자체 찾기"
- 100% 완료 선언 금지 (검증 없이)
- 패턴 발견 → 룰 보강 → 재반복
- ⭐ Phase 3 들어가기 전 매핑 정확도 sample 검증 필수

### TAI API 배포 규칙 (메모리 #1)
- main push → Railway 자동배포
- 200줄+ 파일 MCP 수정 금지 → Cursor

## 6. 핵심 검증 SQL

```sql
-- 전체 진행률 한눈에
SELECT 
  '조문 (일반)' AS category, COUNT(*) AS articles 
  FROM law_article a JOIN law_master m ON m.id = a.law_id
  WHERE a.article_type = '조문' AND m.is_active = true 
    AND m.law_name != '한국전기설비규정'
UNION ALL SELECT 'KEC', COUNT(*) FROM law_article 
  WHERE law_id = '64209405-1a40-4f0a-aa8a-6f3e55917001' AND article_no != 1
UNION ALL SELECT '본칙', COUNT(DISTINCT a.id) FROM law_article a 
  JOIN law_master m ON m.id = a.law_id
  JOIN law_article_part p ON p.article_id = a.id
  WHERE a.article_type = '본칙' AND m.is_active = true
UNION ALL SELECT 'NFTC/KDS', COUNT(DISTINCT a.id) FROM law_article a 
  JOIN law_master m ON m.id = a.law_id
  JOIN law_article_part p ON p.article_id = a.id
  WHERE a.article_type IN ('장','절','조','항','목') AND m.is_active = true;

-- 전체 parts 분포
SELECT 
  CASE 
    WHEN a.law_id = '64209405-1a40-4f0a-aa8a-6f3e55917001' THEN 'KEC'
    WHEN a.article_type = '조문' THEN '조문'
    WHEN a.article_type IN ('장','절','조','항','목') THEN 'NFTC/KDS'
    WHEN a.article_type = '본칙' THEN '본칙'
    ELSE '기타'
  END AS category,
  COUNT(*) AS parts,
  COUNT(DISTINCT a.id) AS articles
FROM law_article_part p JOIN law_article a ON a.id = p.article_id
GROUP BY 1
ORDER BY parts DESC;

-- drafts 매핑 상태
SELECT 
  CASE
    WHEN d.law_name LIKE '%NFTC%' OR d.law_name LIKE '%기술기준%' 
         OR d.law_name LIKE '%설계기준%' THEN 'NFTC/기술기준'
    WHEN d.law_name LIKE '%고시%' OR d.law_name LIKE '%지침%' THEN '고시/지침'
    WHEN d.law_name LIKE '%법%' OR d.law_name LIKE '%령%' OR d.law_name LIKE '%규칙%' THEN '일반 법령'
    ELSE '기타'
  END AS category,
  COUNT(*) FILTER (WHERE a.article_no = 1) AS placeholder_pointing,
  COUNT(*) FILTER (WHERE a.article_no != 1) AS mapped,
  COUNT(*) AS total
FROM law_rule_drafts d
JOIN law_article a ON a.id = d.article_id
GROUP BY 1
ORDER BY placeholder_pointing DESC;
```
