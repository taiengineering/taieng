# HANDOFF — content_type 분류 v3.0 적용 후 버그 진단 (2026-05-06)

> 다음 chat은 이 문서 + 시작 프롬프트만 보고 동일하게 작업 이어가야 함.
> 컨텍스트 절약을 위해 최소한의 정보로 압축.

---

## 0. 시작 프롬프트 (새 chat 첫 메시지)

```
TAI Engineering 산업안전 SaaS의 법령엔진 content_type 분류 작업 핸드오프.

작업 위치: ~/Desktop/tai-engineering/tai-admin
Repo: github.com/taiengineering/tai-admin (branch: main)
Supabase project_id: vwlahtguyggrhvslabax (서울)

작업 시작 전 반드시:
1. 이 핸드오프 doc 전체 읽기:
   docs/extraction/HANDOFF_2026-05-06_classify_v3_bug.md
2. DB 스키마 SQL로 직접 확인 (law_article, law_article_part)
3. 현재 적용 상태 확인 (NULL 카운트, 적용 카운트)

원칙 (불변):
- 누락 0, AI 임의해석 0, 룰 기반만
- 100% 커버 + 정확성 (정확성 > 갯수)
- 검증 없는 완료 선언 금지 ("100% PASS" 등)
- 패턴 발견 → 룰 보강 → 재반복 (옳은 방식 안정화)
- ask_user_input_v0 사용 금지 (텍스트로 직접)
- 수정 가능 → push, 수정 불가 → 광범으로 둠
- 스키마 변경/대량 쿼리 전 의존성 확인 먼저
- 대량 UPDATE 시 중간에 supabase 재연결 (오버쿼리 방지)
- 200줄+ 파일은 GitHub MCP 직접 수정 금지 → Cursor 로컬

다음 액션은 doc의 "다음 단계" 섹션 참조.
```

---

## 1. DB 스키마 (반드시 먼저 SQL로 확인)

### `law_article` (조문 단위)
| 컬럼 | 타입 | 비고 |
|---|---|---|
| id | uuid PK | gen_random_uuid() |
| law_id | uuid FK | NOT NULL |
| law_version_id | uuid FK | NOT NULL |
| parent_article_id | uuid FK | nullable (계층) |
| article_internal_key | text | NFTC%/KDS%/일반 |
| article_no, article_sub_no | int | 조 번호 |
| article_no_sort | text | 정렬용 |
| **article_type** | text | '조문' / '본칙' / NFTC/KDS 별도 |
| article_title | text | 조 제목 |
| **article_text** | text | 조 본문 |
| article_text_normalized | text | 정규화 본문 |
| article_status_code | text | DEFAULT 'ACTIVE' |
| **content_type** | text | (legacy 단일) |
| **content_types** | text[] | **다중 분류 (v2.x)** |
| **primary_content_type** | text | 대표 type |
| **classification_confidence** | text | HIGH/MEDIUM/LOW/NONE |
| **classified_by_rules** | text[] | 매칭된 룰 ID 배열 |
| classified_by, classified_at | text/ts | 분류 메타 |

### `law_article_part` (항/호/목/단서 단위)
| 컬럼 | 타입 | 비고 |
|---|---|---|
| id | uuid PK | gen_random_uuid() |
| article_id | uuid FK | NOT NULL → law_article.id |
| **part_type** | text | NOT NULL ('paragraph'/'clause'/'subclause'/'proviso') |
| paragraph_no, clause_no | int | 번호 |
| subclause_code | text | 가/나/다 |
| **depth** | int | NOT NULL (1=항, 2=호, 3=목) |
| parent_id | uuid FK | nullable → law_article_part.id |
| sort_order | int | NOT NULL |
| **part_text** | text | NOT NULL (본문) |
| has_proviso, proviso_text | bool/text | 단서 |
| part_code | text | NOT NULL (식별 코드) |
| amended_dates | text[] | 개정일 |
| **content_types**, **primary_content_type**, **classification_confidence**, **classified_by_rules** | (분류 컬럼, 동일) |

### 기타 의존 정보
- KEC_LAW_ID = `64209405-1a40-4f0a-aa8a-6f3e55917001` (한국전기설비규정 — 별도 처리)
- NFTC/KDS는 article_internal_key prefix로 식별 (target=nftc_kds)
- 일반 조문 = `article_type = '조문' AND law_id != KEC_LAW_ID` (target=part_general)
- 본칙 = `article_type = '본칙'` (target=part_bonchik)
- KEC = `law_id = KEC_LAW_ID` (target=part_kec)

---

## 2. 진행 현황 (2026-05-06 기준)

### NFTC/KDS articles ✅ 완료
- 3,560건 분류 + 검증 통과 + 45건 SQL fix
- 백업: `_backup_content_type_20260506` (112,838건)

### part_general (일반 조문 parts) ⚠️ **부분 완료 + 버그**
- target_parts: 115,354건 (DB 실측)
- **적용**: 76,054건 (66%)
- **NULL (미적용)**: **39,960건 (35%) ← 코드 버그**
- + null_internal/null_needs_review 정상 NULL: 652건

### part_bonchik ⏳ 대기 (~19,822 parts)
### part_kec ⏳ 대기 (~7,521 parts)

---

## 3. 룰 진화 (v2.1 → v3.0)

**파일**: `docs/extraction/scripts/classify_articles_v1.py`

| 버전 | commit | 핵심 변경 |
|---|---|---|
| v2.1 | be8eed5 | PROHIBITION_cannot (?<!초과), AUXILIARY_old_law_cite 후처리 |
| v2.2 | b6dd233 | 6개 룰 (정한다/고시한다, 에 의한다, 위탁/지원/지급/징수, 하지 못한다, 광범 RIGHT, 삭제) |
| v2.3 | 7764681 | DEFINITION_colon, OBLIGATION_eoya_handa, OBLIGATION_haeng_handa 6개 |
| v2.4 | 87e2eb6 | OBLIGATION_ya_handa 광범, handa_general 광범, badaya 보강 |
| v2.5 | 6a8b925 | parts에 article 본문 fallback traversal + RIGHT_have + article_types 3-tuple |
| v2.6 | 9932b62 | EXCEPTION_haji_anihanda 광범 + AUTHORITY_general_can 광범 |
| v2.7 | 7c23be3 | EXCEPTION_haji_anihanda 종결 조건 fix + RIGHT_have 보강 |
| v2.8 | 3d46937 | OBLIGATION dunda/handa_space/doeenda 3개 보강 |
| v2.9 | b8db22d | 5개 룰 (PROHIBITION_cannot_general, seoneun_anhdoenda, OBLIGATION_handa_after_paren, jinda, doeenda_space) |
| **v3.0** | **b3384540** | **update_chunked 정기 재연결 (reset_every=500) — 오버쿼리 방지** |

### NULL 진척 (dry-run 기준)
30.5% → 24% → 16.8% → 8.4% → 0.16% → 0.092% → 0.16% → 0.06% → **0.012% (12건)**

---

## 4. 광범 룰 정확성 검증 결과

| 룰 | sample 정확도 | 평가 |
|---|---|---|
| PROHIBITION_cannot_general | 100% (25/25) | ✅ |
| AUTHORITY_general_can | 100% (25/25) | ✅ |
| OBLIGATION_ya_handa | 100% (15/15) | ✅ |
| DEFINITION_colon | 96% (24/25) | ✅ |
| EXCEPTION_haji_anihanda | 90%+ (v2.7 fix 후) | ✅ |
| OBLIGATION_doeenda_space | ~85% | ⚠️ 일부 DEFINITION 흡수 |
| OBLIGATION_handa_general | ~80% | ⚠️ 광범, 우선순위 자동 fix |
| RIGHT_general_can | 20% (대부분 AUTHORITY) | → AUTHORITY_general_can으로 fix됨 |

---

## 5. ⚠️ CRITICAL BUG (현재 미해결)

### 증상
- dry-run에서 `final_classification` 크기 = 76,054 (target_parts 117K 중 41K 누락)
- 결과: NULL 39,960건 (적용 안 됨)

### 진단 결과
- **NULL 본문 sample 10건 모두 룰 매칭 가능** (DEFINITION/OBLIGATION/RIGHT)
- 룰은 정상, **코드 버그**

### NULL 분포 (39,960건)
| part_type | depth | root_status | cnt |
|---|---|---|---|
| clause | 2 | has_parent | 17,808 |
| paragraph | 1 | root | 17,438 |
| proviso | 1 | has_parent | 2,275 |
| subclause | 3 | has_parent | 1,826 |
| proviso | 2 | has_parent | 613 |

### 의심 위치
- `classify_articles_v1.py` `classify_parts()` 함수
- leaf_parts loop 또는 internal loop에서 일부 누락
- 또는 `final_classification` dict에 안 들어가는 케이스

코드 로직상 모든 target_parts가 들어가야 하는데 41K 누락. 직접 시뮬레이션 필요.

---

## 6. 검증 SQL (Layer 0~3)

### L0 분포 + L1 일관성 + L2 광범 룰 + L3 coverage

```sql
WITH KEC_LAW AS (SELECT '64209405-1a40-4f0a-aa8a-6f3e55917001'::uuid AS id),
target AS (
  SELECT p.* FROM law_article_part p
  JOIN law_article a ON a.id = p.article_id
  WHERE a.article_type = '조문' AND a.law_id != (SELECT id FROM KEC_LAW)
),
results AS (
  SELECT 'L0_distribution' AS layer, primary_content_type AS k1, classification_confidence AS k2, COUNT(*) AS cnt
  FROM target GROUP BY primary_content_type, classification_confidence
  UNION ALL
  SELECT 'L1_primary_consistency',
         CASE WHEN primary_content_type = content_types[1] THEN 'match' ELSE 'mismatch' END,
         'count', COUNT(*) FROM target WHERE primary_content_type IS NOT NULL GROUP BY 2
  UNION ALL
  SELECT 'L3_coverage',
    CASE
      WHEN primary_content_type IS NULL THEN 'NULL'
      WHEN EXISTS (SELECT 1 FROM unnest(classified_by_rules) r WHERE r LIKE 'inherited:from_article_%') THEN 'article_fallback'
      WHEN EXISTS (SELECT 1 FROM unnest(classified_by_rules) r WHERE r LIKE 'inherited:from_part_%') THEN 'part_chain'
      ELSE 'direct'
    END, 'count', COUNT(*) FROM target GROUP BY 2
)
SELECT layer, k1, k2, cnt FROM results ORDER BY layer, cnt DESC;
```

### NULL 본문 sample 진단

```sql
WITH KEC_LAW AS (SELECT '64209405-1a40-4f0a-aa8a-6f3e55917001'::uuid AS id)
SELECT LEFT(part_text, 250) AS text, part_type, depth, parent_id IS NULL AS is_root
FROM law_article_part p
JOIN law_article a ON a.id = p.article_id
WHERE a.article_type = '조문' AND a.law_id != (SELECT id FROM KEC_LAW)
  AND p.content_types IS NULL AND p.classification_confidence IS NULL
ORDER BY RANDOM() LIMIT 25;
```

---

## 7. 다음 단계 (다음 chat이 진행)

### 옵션 A — NULL-only 빠른 fix (즉시, 추천)

별도 스크립트 `classify_null_only.py` 작성:
1. `content_types IS NULL AND classification_confidence IS NULL`인 parts만 fetch
2. 동일한 RULES + classify_text 적용
3. update (정기 재연결 포함)

**장점**: 빠름 (~30분), 적용된 76K 데이터 손실 X
**단점**: 코드 버그 자체는 향후 진단 필요

### 옵션 B — 코드 버그 진단 + 재실행

1. `classify_articles_v1.py` `classify_parts()` 직접 시뮬레이션 (Cursor)
2. final_classification에 누락되는 케이스 찾기 (paragraph root 17,438 + clause depth=2 17,808 단서)
3. fix 후 `--reset --target part_general` + 재실행
4. **부작용**: 76K 데이터 reset됨, 재적용 1시간+

### 옵션 C — A + B 병행 (가장 안전)

1. 옵션 A로 즉시 NULL 메꿈
2. 코드 fix → part_bonchik/part_kec는 정확 코드로 진행

**추천: 옵션 C**

---

## 8. 후속 작업

### part_bonchik (~19,822 parts)
- 코드 fix 후 진행
- 실행: `railway run python3 docs/extraction/scripts/classify_articles_v1.py --target part_bonchik`

### part_kec (~7,521 parts)
- 마지막 진행
- 실행: `railway run python3 docs/extraction/scripts/classify_articles_v1.py --target part_kec`

### 검증 (각 단계 후 필수)
- L0~L3 SQL 실행
- NULL sample 25건 spot-check
- 광범 룰 단독 매칭 sample 검증

---

## 9. 주요 명령

```bash
# dry-run
cd ~/Desktop/tai-engineering/tai-admin && git pull origin main && \
  railway run python3 docs/extraction/scripts/classify_articles_v1.py \
  --target part_general --dry-run

# 적용 (백그라운드)
cd ~/Desktop/tai-engineering/tai-admin && git pull origin main && \
  nohup railway run python3 docs/extraction/scripts/classify_articles_v1.py \
  --target part_general > classify_v3_part_general.log 2>&1 &

# 모니터링
tail -f classify_v3_part_general.log

# reset (주의 — 기존 분류 모두 NULL)
railway run python3 docs/extraction/scripts/classify_articles_v1.py \
  --reset --target part_general
```

---

## 10. 백업 정보

- NFTC/KDS articles 백업: `_backup_content_type_20260506` (112,838건)
- parts 백업: 없음 (대표님 지시)
- 적용 76K 손실 방지 위해 **reset 신중히** — 옵션 A 먼저 시도

---

## 11. 환경

- Backend: Railway 싱가포르
- DB: Supabase 서울 (project_id: `vwlahtguyggrhvslabax`)
- 로컬: `~/Desktop/tai-engineering/tai-admin`
- 실행: `railway run python3 ...` (env vars 자동)

---

## 12. 핵심 원칙 (반복)

1. **누락 0, AI 임의해석 0, 룰 기반만**
2. **100% 커버 + 정확성 우선** (정확성 > 갯수)
3. **검증 없는 완료 선언 금지** ("PASS" 같은 단정 X)
4. **패턴 발견 → 룰 보강 → 재반복**
5. **수정 가능 → push, 수정 불가 → 광범**
6. **대량 UPDATE 중간 supabase 재연결** (오버쿼리 방지)
7. **200줄+ 파일 GitHub MCP 직접 수정 금지** → Cursor 로컬
8. **ask_user_input_v0 사용 금지** (텍스트 직접)
9. **스키마 변경/대량 쿼리 전 의존성 확인**

---

## 13. 이전 핸드오프 (참조)

- `docs/extraction/HANDOFF_2026-05-05.md` — 법령파싱 종료 시점
- `docs/extraction/HANDOFF_2026-05-06.md` — content_type 분류 시작 시점

이 문서는 `HANDOFF_2026-05-06_classify_v3_bug.md` (현재 시점, v3.0 적용 후 버그 발견).
