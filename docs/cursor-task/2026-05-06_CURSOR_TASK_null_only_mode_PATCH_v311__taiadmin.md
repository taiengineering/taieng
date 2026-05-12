# Cursor 작업지시서 PATCH — v3.1.1 fetch ORDER BY 보강 (2026-05-06 dry-run 결과 반영)

> 이전 doc: `docs/extraction/CURSOR_TASK_2026-05-06_null_only_mode.md` (§2-2 패치 후 dry-run에서 추가 문제 발견)
> 적용 대상: `docs/extraction/scripts/classify_articles_v1.py`

---

## 1. dry-run에서 발견된 추가 문제

| 카운터 | 값 |
|---|---|
| DB의 NULL parts | 39,960 |
| 스크립트 `[INFO] 전체 fetch:` | **67,495** (DB의 1.7배) |
| `target parts:` (필터 후) | 39,290 |
| `final_classification` (unique id) | 24,773 |
| CRITICAL `expected vs actual` | 39,290 vs 24,773 |
| CRITICAL `missing` | 0 |

**원인**: PostgREST의 `is_(NULL)` 필터 + `range(offset, offset+999)` 페이지네이션이 **ORDER BY 없이** 호출되어 페이지 간 결과 일관성이 깨짐.
- 같은 row가 여러 페이지에 중복 출현 → fetch 67K (실제 NULL 40K의 1.7배)
- 일부 row는 어느 페이지에도 안 잡힘 → fetch unique 39,290 (실제 NULL 39,960보다 670건 누락)
- target_parts 리스트에 중복 id 다수 → dict로 덮어쓰며 final_classification = 24,773으로 수렴
- missing=0인 이유: 모든 unique id는 dict에 들어감 (단지 한 번씩만)

**v3.0 본 실행의 ~3K fetch 누락도 같은 원인**으로 추정됨 (NULL 필터 없을 때도 ORDER BY 누락).

---

## 2. 수정 사항 (v3.1.1)

### 2-1. general 분기 fetch에 `.order('id')` 추가

**위치**: 이전 doc §2-2의 fetch 패치 코드 안

**변경**: `_fetch()` 내부의 다음 줄
```python
return q.range(offset, offset + 999).execute().data
```

다음으로 교체:
```python
return q.order('id').range(offset, offset + 999).execute().data
```

(즉 `.range(...)` 앞에 `.order('id')` 추가)

### 2-2. bonchik 분기 fetch도 동일

bonchik 분기의 같은 위치에도 `.order('id')` 추가.

### 2-3. fetch 직후 dedup 안전장치 (general/bonchik 둘 다)

**위치**: 이전 doc §2-2 패치의 마지막 줄 `print(f"[INFO] 전체 fetch: {len(all_parts)} parts")` 직후

**추가**:
```python
# dedup 안전장치 (PostgREST 페이지네이션 일관성 보강)
seen_ids = set()
deduped = []
for p in all_parts:
    if p['id'] not in seen_ids:
        seen_ids.add(p['id'])
        deduped.append(p)
if len(deduped) != len(all_parts):
    print(f"[WARN] fetch 중복 제거: {len(all_parts)} → {len(deduped)} "
          f"({len(all_parts) - len(deduped)} 중복)")
all_parts = deduped
```

### 2-4. (선택) kec 분기에도 `.order('id')` 추가

kec 분기는 `in_('article_id', chunk)` 방식이라 페이지네이션은 없지만, 향후 일관성 보장 위해 추가 권장:

**위치**: kec 분기 내 `_fetch()` 함수
```python
return supabase.from_('law_article_part').select(
    'id,article_id,parent_id,part_text,part_type,depth'
).in_('article_id', chunk).execute().data
```

다음으로 교체:
```python
return supabase.from_('law_article_part').select(
    'id,article_id,parent_id,part_text,part_type,depth'
).in_('article_id', chunk).order('id').execute().data
```

---

## 3. 재실행 절차

### Step A — Cursor에 patch 적용

Cursor 컴포저에 다음 그대로 붙여넣기:

```
docs/extraction/CURSOR_TASK_2026-05-06_null_only_mode_PATCH_v311.md를 읽고
§2의 4개 변경(2-1, 2-2, 2-3, 2-4)을 docs/extraction/scripts/classify_articles_v1.py에
정확히 적용해줘.

규칙:
- doc에 명시된 위치/코드 정확히 따름
- RULES, classify_text, classify_nftc_kds는 일절 건드리지 않음
- 새 룰/판단 기준 추가 금지
- 끝나면 git diff 결과의 변경 라인 수만 알려줘
```

### Step B — 변경 확인 + dry-run 재실행

```bash
cd ~/Desktop/tai-engineering/tai-admin
git diff docs/extraction/scripts/classify_articles_v1.py | head -80

railway run python3 docs/extraction/scripts/classify_articles_v1.py \
  --target part_general --null-only --dry-run 2>&1 | tee /tmp/null_only_dry2.log

cat /tmp/null_only_dry2.log
```

### Step C — 결과 chat 보고

`cat /tmp/null_only_dry2.log` 결과 통째로 chat에 붙여주시면 GO/NO-GO 판단합니다.

---

## 4. 기대 결과 (Step B의 dry-run)

| 항목 | 기대값 |
|---|---|
| `[INFO] 전체 fetch:` | **약 39,960** (DB NULL과 일치, 중복 없음) |
| `[WARN] fetch 중복 제거` | **표시 안 됨** (또는 0건) |
| `[INFO] target parts:` | **약 39,960** |
| `[CRITICAL]` 메시지 | **없음** |
| `[RESULT] 총 분류` | **≈ 39,960** |
| direct + inherited 합 | **≥ 80%** |
| `null_internal` + `null_needs_review` | 명사구 enumeration 잔여, 합리적 수준 (수천 건 이내) |

**기대값 미달 시 본 실행 진행 금지** — 추가 진단 필요.

---

## 5. 보고 — chat에 다음 항목 그대로 붙여주세요

```bash
cat /tmp/null_only_dry2.log
```

전체 결과 (또는 길면 `tail -150 /tmp/null_only_dry2.log`).

---

## 6. 메모

- 이 patch가 통과하면 v3.0 본 실행의 fetch 누락 ~3K도 자동 해결되는 것으로 보임
- bonchik/kec 본 실행 시 같은 ORDER BY 보강 효과 적용됨
- 향후 다른 페이지네이션 함수(`fetch_all_paged` 등)도 같은 원리로 보강 필요할 수 있음 — 별도 작업
