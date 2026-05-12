# Cursor 작업지시서 — classify_articles_v1.py에 `--null-only` 모드 추가 (v3.1)

> 생성일: 2026-05-06
> 대상 파일: `docs/extraction/scripts/classify_articles_v1.py` (32KB, 700+줄 → Cursor 로컬 작업)
> 관련 핸드오프: `docs/extraction/HANDOFF_2026-05-06_classify_v3_bug.md`

---

## 0. 목적

v3.0 본 실행(2026-05-06 15:54) 결과:

| 단계 | 카운트 |
|---|---|
| DB 실측 target_parts | 116,014 |
| 스크립트 fetch (`target parts`) | 113,024 (① **fetch에서 ~3K 누락**) |
| `leaf_parts` | 100,081 |
| leaf 처리 합 (45,388 + 28,388 + 15,575 + 19) | 89,370 (② leaf loop ~11K 누락) |
| `final_classification` 최종 | **76,054** (③ internal까지 합쳐 ~37K 누락) |
| DB applied + NONE | 75,402 + 652 = 76,054 ✓ |
| **DB null_both (버그)** | **39,960** |

코드 로직만 보면 모든 target_parts가 final_classification에 들어가야 정상인데 ~37K 누락. 원인 미상이나 재현 가능. 적용된 75K는 손실 risk 있어 reset 회피하고, **NULL 40K만 재처리**하는 우회 모드 추가.

---

## 1. 원칙 (불변)

- 적용된 75K는 건드리지 않음 (data 손실 0)
- 검증된 RULES + classify_text + update_chunked 그대로 재사용
- fetch 안전장치 (empty batch retry + 정기 재연결)
- 누락 assert로 final_classification 카운트 검증
- 검증 없는 완료 선언 금지 — dry-run 필수
- `--null-only`와 `--reset` 동시 사용 금지

---

## 2. 변경 사항

### 2-1. CLI 인자 추가

**위치**: `def main()` 함수 내 argparse 부분

**추가**:
```python
parser.add_argument('--null-only', action='store_true',
    help='NULL parts(content_types IS NULL AND classification_confidence IS NULL)만 '
         '재처리. 이미 적용된 분류는 건드리지 않음. v3.0 누락 fix용 우회 모드.')
```

argparse 직후 검증:
```python
if args.null_only and args.reset:
    print("[ERROR] --null-only와 --reset은 동시 사용 불가", file=sys.stderr)
    sys.exit(1)
```

---

### 2-2. classify_parts() — fetch 단계 패치 (general/bonchik 두 분기 동일 적용)

**기존 코드** (target_filter == 'general' 분기):
```python
all_parts = []
offset = 0
while True:
    def _fetch():
        return supabase.from_('law_article_part').select(
            'id,article_id,parent_id,part_text,part_type,depth'
        ).range(offset, offset + 999).execute().data
    batch = with_retry(_fetch)
    if not batch:
        break
    all_parts.extend(batch)
    if len(batch) < 1000:
        break
    offset += 1000
```

**변경**:
```python
all_parts = []
offset = 0
empty_retry_used = False  # 빈 batch 1회 retry (false-negative 방지)
fetched_since_reset = 0
RESET_THRESHOLD = 10000  # 10K fetch마다 supabase 재연결
while True:
    def _fetch():
        q = supabase.from_('law_article_part').select(
            'id,article_id,parent_id,part_text,part_type,depth'
        )
        if getattr(args, 'null_only', False):
            q = q.is_('content_types', 'null').is_('classification_confidence', 'null')
        return q.range(offset, offset + 999).execute().data
    batch = with_retry(_fetch)
    if not batch:
        if empty_retry_used:
            break
        empty_retry_used = True
        print(f"  [WARN] empty batch at offset={offset}, 재연결 후 한 번 더 시도")
        reset_supabase()
        time.sleep(2)
        continue
    empty_retry_used = False
    all_parts.extend(batch)
    fetched_since_reset += len(batch)
    if len(batch) < 1000:
        break
    offset += 1000
    if fetched_since_reset >= RESET_THRESHOLD:
        print(f"  [FETCH-RECONNECT] {len(all_parts)} fetched, 재연결")
        reset_supabase()
        time.sleep(1)
        fetched_since_reset = 0
print(f"[INFO] 전체 fetch: {len(all_parts)} parts")
```

`bonchik` 분기도 동일 변경 (`is_` 필터 줄만 추가). `kec` 분기는 in_chunk 방식이라 변경 불필요(원본 유지).

---

### 2-3. null-only 모드용 applied parent 분류 DB 조회

`--null-only` 모드에서는 `part_by_id`에 NULL parts만 있어, parent가 이미 적용된 part(75K 중 하나)이면 lookup 실패 → article_text fallback으로만 감. 정확한 inherit 위해 applied parent 분류를 DB에서 별도 조회.

**위치**: `leaf_parts = [...]` 직후, `final_classification = {}` 직전

**추가**:
```python
# null-only 모드: parent가 이미 적용된 part일 수 있어 별도 DB 조회
applied_parent_class = {}
if getattr(args, 'null_only', False):
    needed_parent_ids = list({
        p['parent_id'] for p in target_parts
        if p.get('parent_id') and p['parent_id'] not in part_by_id
    })
    print(f"[INFO] null-only: applied parent 조회 대상 {len(needed_parent_ids)}건")
    for i in range(0, len(needed_parent_ids), 200):
        chunk = needed_parent_ids[i:i + 200]
        def _fetch_pp():
            return supabase.from_('law_article_part').select(
                'id,content_types,primary_content_type,classification_confidence,classified_by_rules'
            ).in_('id', chunk).execute().data
        res = with_retry(_fetch_pp)
        for r in res:
            if r.get('content_types') and r.get('primary_content_type') and r.get('classification_confidence') in ('HIGH','MEDIUM','LOW'):
                applied_parent_class[r['id']] = (r['content_types'], r.get('classified_by_rules') or [])
    print(f"[INFO] null-only: applied parent 분류 확보 {len(applied_parent_class)}건")
```

---

### 2-4. leaf inherit traversal에 applied_parent 시도 추가

**기존 코드** (leaf_parts loop 내 while):
```python
while cur and cur.get('parent_id') and depth < 10:
    parent = part_by_id.get(cur['parent_id'])
    if not parent:
        break
    ptypes, prules = direct_classification[parent['id']]
    if ptypes:
        inherited_types = ptypes
        inherited_rules = prules + ['inherited:from_part_' + parent['id'][:8]]
        break
    cur = parent
    depth += 1
```

**변경**:
```python
while cur and cur.get('parent_id') and depth < 10:
    parent = part_by_id.get(cur['parent_id'])
    if not parent:
        # null-only 모드: 이미 적용된 parent 시도
        if getattr(args, 'null_only', False):
            ap = applied_parent_class.get(cur['parent_id'])
            if ap:
                inherited_types = ap[0]
                inherited_rules = ap[1] + ['inherited:from_applied_parent_' + cur['parent_id'][:8]]
        break
    ptypes, prules = direct_classification[parent['id']]
    if ptypes:
        inherited_types = ptypes
        inherited_rules = prules + ['inherited:from_part_' + parent['id'][:8]]
        break
    cur = parent
    depth += 1
```

---

### 2-5. 누락 안전장치 — assert

**위치**: classify_parts() 안에서 `print(f"\n[RESULT]")` 바로 직전

**추가**:
```python
# 안전장치: 모든 target_parts가 final_classification에 들어갔는지 검증
expected_count = len(target_parts)
actual_count = len(final_classification)
if expected_count != actual_count:
    missing = [p for p in target_parts if p['id'] not in final_classification]
    print(f"\n[CRITICAL] final_classification 누락 발견!")
    print(f"  expected: {expected_count}, actual: {actual_count}, missing: {len(missing)}")
    print(f"  missing sample (5):")
    for m in missing[:5]:
        text = (m.get('part_text') or '')[:100].replace('\n', ' ')
        print(f"    [{m.get('part_type')} d={m.get('depth')}] {text}")
    if not args.dry_run:
        print(f"[CRITICAL] DB update 중단. dry-run으로 원인 진단 필요.")
        sys.exit(1)
```

---

## 3. 실행 순서

### Step A — 패치 적용

```bash
cd ~/Desktop/tai-engineering/tai-admin
git pull origin main
# Cursor에서 docs/extraction/scripts/classify_articles_v1.py 열고 위 5개 변경 적용
git diff docs/extraction/scripts/classify_articles_v1.py | head -200  # 변경 확인
```

### Step B — dry-run

```bash
railway run python3 docs/extraction/scripts/classify_articles_v1.py \
  --target part_general --null-only --dry-run 2>&1 | tee /tmp/null_only_dry.log
```

**dry-run 검증 기준** (모두 통과해야 본 실행):
- `target parts:` 약 39,960 (±수십)
- `[CRITICAL] final_classification 누락 발견!` 메시지 **없어야 함**
- `[DRY-RUN 분포]`에서 `direct` + `inherited` 합 ≥ 70% (paragraph root + proviso는 직접 매칭 가능)
- `[DRY-RUN NULL leaf sample]`이 명사구 enumeration("조사 목적", "선발 예정 인원" 등) 위주면 정상

### Step C — 본 실행

dry-run 모든 검증 통과 후:
```bash
nohup railway run python3 docs/extraction/scripts/classify_articles_v1.py \
  --target part_general --null-only > /tmp/null_only_apply.log 2>&1 &
tail -f /tmp/null_only_apply.log
```

예상 소요: 약 30~40분 (40K parts × ~0.05s + 80회 재연결).

### Step D — 적용 후 검증 (Supabase SQL)

```sql
WITH KEC_LAW AS (SELECT '64209405-1a40-4f0a-aa8a-6f3e55917001'::uuid AS id),
target AS (
  SELECT p.* FROM law_article_part p
  JOIN law_article a ON a.id = p.article_id
  WHERE a.article_type = '조문' AND a.law_id != (SELECT id FROM KEC_LAW)
)
SELECT
  CASE
    WHEN content_types IS NOT NULL AND classification_confidence IS NOT NULL THEN 'applied'
    WHEN content_types IS NULL AND classification_confidence IS NULL THEN 'null_both (BUG)'
    WHEN content_types IS NULL AND classification_confidence = 'NONE' THEN 'null_none (정상)'
    ELSE 'other'
  END AS status,
  classification_confidence AS conf,
  COUNT(*) AS cnt,
  MAX(classified_at) AS last_at
FROM target
GROUP BY 1, 2
ORDER BY 1, 3 DESC;
```

**기대 결과**:
- `null_both (BUG)`: **0** (assert 덕분에)
- `applied`: 약 110K+ (75K 기존 + ~35K 신규)
- `null_none (정상)`: 명사구 enumeration 잔여 (수천 건 이내가 합리적)

핸드오프 doc의 Layer 0~3 검증 SQL도 추가 실행 권장.

### Step E — 커밋 + push

```bash
git add docs/extraction/scripts/classify_articles_v1.py
git commit -m "feat(classify): v3.1 — add --null-only mode + safety asserts

- v3.0 본 실행에서 target 113K 중 76K만 final_classification에 들어가
  NULL 40K가 update 누락된 버그 fix용 우회 모드 추가
- --null-only: NULL parts만 fetch + 처리 + update (적용된 75K 미터치)
- fetch: empty batch 1회 retry + 10K마다 재연결 (false-negative 제거)
- inherit 보강: null-only 모드에서 applied parent 분류 DB 조회
- 안전장치: target vs final_classification 카운트 assert로 누락 감지

검증: docs/extraction/CURSOR_TASK_2026-05-06_null_only_mode.md 참조"
git push origin main
```

---

## 4. 보고 항목 (작업 완료 후 chat에서)

다음 3가지를 chat에 그대로 붙여주세요:

1. **dry-run 로그 핵심 부분**:
   - `target parts:` 줄
   - `[INFO] null-only: applied parent ...` 줄
   - `[RESULT]` 블록 전체
   - `[CRITICAL]` 메시지 유무
   - `[DRY-RUN 분포]` 상위 10줄
   - `[DRY-RUN NULL leaf sample]` 첫 10줄

2. **본 실행 결과 요약**:
   - 최종 `[DONE] N/M parts updated`
   - 소요 시간

3. **Step D 검증 SQL 결과**

---

## 5. 후속 작업 (이번 작업 완료 후)

- `part_bonchik` 분류 (~19,822 parts) — 동일 코드로 `--target part_bonchik` 실행
- `part_kec` 분류 (~7,521 parts) — `--target part_kec`
- 핸드오프 doc 업데이트: `HANDOFF_2026-05-06_classify_v3_bug.md`에 v3.1 결과 추가

---

## 6. 주의

- assert 실패 시 본 실행 진행 **금지** → dry-run 추가 진단 필요
- 본 실행 도중 끊기면 idempotent하므로 재실행 안전 (`--null-only`는 NULL만 fetch하니 자동 retry 가능)
- bonchik/kec은 별도 `--target`으로 진행 (한 번에 다 안 함)
