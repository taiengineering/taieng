# CURSOR TASK 2026-05-09 — fetch_clauses 중복 제거 + INSERT 멱등성

## § 0 절대 금지

1. AI/LLM 호출 0% (이번 변경에 추가 금지)
2. 사전·정규식·로직 수정 금지 (이번 작업은 멱등성·중복 제거만)
3. process_clause 로직 변경 금지
4. scope_code 생성 규칙 변경 금지 (`SCOPE_{clause_id 앞 8자}` 유지)
5. 검증 없는 완료 선언 금지

---

## § 1 배경 (원칙: PRINCIPLE_RECALL_FIRST)

본 적용 시 매번 같은 `SCOPE_2ae21184`에서 UNIQUE 위반:

```
postgrest.exceptions.APIError: {'code': '23505',
  'details': 'Key (scope_code)=(SCOPE_2ae21184) already exists.'}
```

진단 (DB 직접 조회):

| 검증 | 결과 |
|---|---|
| `2ae21184` prefix 보유 의미절 (semantic_clause) | **단 1건** |
| 9,635 INSERT 후 SCOPE_2ae21184 row | 1건 INSERT됨 |
| 첫 줄 출력 `[RETRY 1/5] RemoteProtocolError` | YES |

→ 같은 clause가 두 번 처리됨. `fetch_clauses`의 `with_retry`가 partial success(서버 송신 성공 + client 수신 실패) 후 retry 시 같은 batch를 재수집한 결과로 추정.

---

## § 2 수정 사항 (두 곳)

### 수정 1: `fetch_clauses` 끝부분 — 중복 제거 (root cause fix)

**위치**: `docs/extraction/scripts/extract_scope_from_clauses.py`, 함수 `fetch_clauses` 마지막 `return` 직전.

**변경 전**:

```python
    return all_clauses[:sample_size]
```

**변경 후**:

```python
    # 중복 제거 (with_retry partial success 시 같은 batch 재수집 방지)
    seen_ids = set()
    deduped: List[Dict[str, Any]] = []
    for c in all_clauses:
        cid = c.get("id")
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            deduped.append(c)
    if len(deduped) < len(all_clauses):
        print(
            f"[DEDUPE] fetch_clauses: {len(all_clauses)} → {len(deduped)} "
            f"({len(all_clauses) - len(deduped)}건 중복 제거)",
            file=sys.stderr,
        )
    return deduped[:sample_size]
```

### 수정 2: `insert_scope_and_thresholds` — INSERT 멱등성 (안전망)

**위치**: 같은 파일, 함수 `insert_scope_and_thresholds` 첫 줄.

**변경 전**:

```python
def insert_scope_and_thresholds(scope: Dict[str, Any], thresholds: List[Dict[str, Any]]) -> str:
    res = with_retry(lambda: supabase.table("master_rule_scope").insert(scope).execute())
    scope_id = (res.data or [{}])[0].get("id")
    if not scope_id:
        raise RuntimeError("master_rule_scope insert 결과에서 id를 받지 못했습니다.")
```

**변경 후**:

```python
def insert_scope_and_thresholds(scope: Dict[str, Any], thresholds: List[Dict[str, Any]]) -> str:
    # upsert(on_conflict=scope_code): retry로 인한 중복 INSERT 시 update로 멱등성 보장
    res = with_retry(
        lambda: supabase.table("master_rule_scope")
        .upsert(scope, on_conflict="scope_code")
        .execute()
    )
    scope_id = (res.data or [{}])[0].get("id")
    if not scope_id:
        # upsert가 결과를 반환하지 않으면 scope_code로 조회
        sel = with_retry(
            lambda: supabase.table("master_rule_scope")
            .select("id")
            .eq("scope_code", scope.get("scope_code"))
            .single()
            .execute()
        )
        scope_id = (sel.data or {}).get("id")
    if not scope_id:
        raise RuntimeError("master_rule_scope upsert 결과에서 id를 받지 못했습니다.")
```

---

## § 3 검증 절차

### 3.1 자가 검증 (PR 전)

```bash
# 문법 / lint
python3 -c "import ast; ast.parse(open('docs/extraction/scripts/extract_scope_from_clauses.py').read())"

# AI 호출 import 0
grep -E "openai|anthropic|gpt|claude" docs/extraction/scripts/extract_scope_from_clauses.py
# (출력 0줄이어야 함)
```

### 3.2 dry-run 검증

```bash
cd docs/extraction/scripts
railway run python3 extract_scope_from_clauses.py --dry-run --sample-size 1000
```

기대:
- `[DEDUPE]` 메시지 없거나 (정상) 또는 약간의 중복 제거 (네트워크 retry 시)
- INSERT 대상 ~990~996건 (이전 결과와 동일)
- needs_review 99%대

### 3.3 본 적용

```bash
railway run python3 extract_scope_from_clauses.py --apply --truncate-first --sample-size 100000 2>&1 | tee /tmp/extract_scope_recall_first.log
```

체크포인트:
- 첫 라인 `fetched semantic_clause: 58495 rows`
- 만약 RETRY 발생 후 `[DEDUPE]` 출력되면 root cause fix 작동
- 만약 RETRY 미발생이라도 upsert가 멱등성 보장 (다른 path에서 INSERT 두 번 시도해도 안전)
- 정상 완료: `[DONE] inserted scopes=~58300 thresholds=~175`

### 3.4 사후 DB 검증 (이건 기획자 SQL로 진행)

| 검증 | 기대 |
|---|---|
| master_rule_scope row 수 | ~58,300 |
| scope_code 중복 | 0 (UNIQUE 제약) |
| 4 FK broken | 0 |
| sectors 보유 의미절 누락 | 0 (PRINCIPLE_RECALL_FIRST 보강 검증) |
| needs_review='sectors만 보유' | ~53,000 |
| needs_review='분류형만 추출' | ~5,000 |

---

## § 4 commit / push

```bash
git add docs/extraction/scripts/extract_scope_from_clauses.py
git commit -m "fix(scope): fetch_clauses 중복 제거 + insert→upsert (멱등성)"
git pull --rebase origin main  # remote 변경 통합
git push origin main
```

---

## § 5 작업 후 핸드오프

작업 완료 후 기획자에게 보고:
- dry-run 출력 (sample 1,000)
- 본 적용 출력 (전체 58,495 처리)

기획자가 사후 DB 검증 SQL로 4 FK 누락 0 / needs_review 분포 확인 후 Phase E 종결.
