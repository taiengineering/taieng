# CURSOR 작업지시서 A — 의미절 전체 복원(--apply) + 전체 엔진 역검증

작성일: 2026-06-13
발행: Claude 기획창 / 수행: Cursor (railway run)
근거: docs/2026-06-13_LEGAL_ENGINE_ROOTCAUSE_PIPELINE_SWAP.md (방향·격리),
      docs/2026-06-13_CURSOR_TEST_DECOMPOSE_DRYRUN.md (시험 통과·2단계 전략)
대표 확정: 전체 복원 + 전체 검증. 그때(5/8)는 LLM 샘플검증, 지금은 엔진 전수 역검증.

---

## 이 작업의 성격 / 안전 경계

- **decompose_v1.py를 한 글자도 수정하지 않는다.** 정해진 명령으로 실행만 한다.
- 쓰기 대상은 **semantic_clause_iter1 단 하나.** 본 테이블(semantic_clause)·기존 자산
  (constraint/evidence/rule_candidate/executable_draft 등) 전부 **무영향.**
- iter1은 격리된 작업 공간. **사고 나도 truncate 후 재실행하면 됨.** 과감하게 진행.
- 분해 규칙 재발명 금지. executor 보정 시도 금지(2단계 별도 트랙). 이번은 "복원 + 검증"만.

---

## STEP A1 — 의미절 전체 복원 (--apply, iter1에만 쓰기)

5/8 문서의 본 실행 명령 그대로. `--sample-size` 큰 값 필수(누락 시 50건만 처리되는 사고 이력).

```bash
cd docs/extraction/scripts/
railway run python3 decompose_v1.py --apply --truncate-first \
  --sample-size 100000 --sampling random 2>&1 | tee /tmp/decompose_apply_full.log
```

정상 출력 패턴(없으면 사고):
- `[TRUNCATE] semantic_clause_iter1 비움 완료`
- `[INFO] 모집단: ~49,997 paragraphs from ~366 laws` (수치는 현 DB 기준 다를 수 있음)
- `[DECOMPOSE] ~48,000 parts → ~58,000 clauses` ← 이 라인 반드시 확인
- `[DONE] inserted ~58,000 clauses into semantic_clause_iter1`

종료 후 즉시 행수 확인(쓰기 검증):
```sql
SELECT count(*) FROM semantic_clause_iter1;
SELECT content_type, count(*) FROM semantic_clause_iter1 GROUP BY 1 ORDER BY 2 DESC;
```
- 기대: 총 ~58,000건. content_type 분포에 OBLIGATION이 최다(약 5만 중 2.9만 수준).
- **본 테이블은 건드리지 않았는지 확인**: `SELECT count(*) FROM semantic_clause;` → 여전히 0이어야
  (아직 본 동기화 전. iter1에만 들어가야 정상).

---

## STEP A2 — 전체 엔진 역검증 (check_engine 활용, LLM 아님)

복원된 iter1 의미절 전체를, 기존 범용 체크엔진(services/check_engine.py)으로 역검증한다.
**사람이 읽지 않는다. 엔진이 결과를 룰과 거꾸로 대조해 MISMATCH/NO_RULE을 사실로 드러낸다.**

check_engine 계약: `CheckItem(id, values)` 를 `expected` 와 대조 → MATCH / MISMATCH / NO_RULE.
의미절 검증용 어댑터를 **새 1회용 스크립트로** 만든다(check_engine.py·decompose_v1.py 수정 금지).

검증 항목 2가지(각각 어댑터로 변환):

### (가) content_type 종결어미 일관성 역검증
의미절의 `source_text` 종결어미가 분류된 `content_type`과 일관되는가.
- expected = 의미절의 content_type (예: "OBLIGATION")
- values   = source_text 종결어미를 분해기 룰로 재판정한 결과(들)
- MISMATCH = 종결어미는 OBLIGATION인데 content_type이 다르게 저장됨(또는 반대) → 오분류 후보
- NO_RULE  = 종결어미가 어느 룰에도 안 걸림 → 미분류(None) 후보

### (나) executor 타당성 역검증 (2단계 트랙의 시작 — 색출만, 수정 안 함)
의무 의미절(OBLIGATION/PROHIBITION/AUTHORITY)의 executor가 타당한가.
- expected = "유효주체"
- values   = executor_text를 is_fake_executor / is_object_subject 로 판정한 결과
  (예: 사물주어·종속어·잘림이면 values에서 "유효주체" 빠짐 → MISMATCH)
- MISMATCH = executor가 사물/잘림/종속어(예: 17조①항 "지도ㆍ조언하") → 보정 대상 색출
- 여기서는 **색출만 한다. 고치지 않는다.** 목록을 카운트+샘플로 보고.

어댑터 스크립트 예(읽기 전용, _probe_ 접두로 보존/삭제):
```python
# scripts/_probe_verify_clauses.py — iter1 의미절 전수 역검증 (수정 없음)
import os
from supabase import create_client
import check_engine as CE
import decompose_v1 as D

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

# iter1 전수 페이지네이션 (range 1000씩)
rows, off = [], 0
while True:
    r = sb.table("semantic_clause_iter1").select(
        "id,source_text,content_type,executor_text").range(off, off+999).execute().data
    if not r: break
    rows.extend(r);  off += 1000
    if len(r) < 1000: break

# (가) content_type 역검증
ct_items, ct_expected = [], {}
mismatch_ct, norule_ct = [], []
for c in rows:
    ctype, rule_id = D.classify_content_type_priority((c.get("source_text") or "").strip())
    exp = (c.get("content_type") or "").upper()
    got = (ctype or "").upper()
    if not got:
        norule_ct.append(c)
    elif exp and exp != got:
        mismatch_ct.append((c, exp, got))

# (나) executor 역검증 (의무류만)
TARGET = {"OBLIGATION","PROHIBITION","AUTHORITY"}
bad_exec = []
for c in rows:
    if (c.get("content_type") or "").upper() not in TARGET: continue
    ex = c.get("executor_text")
    if not ex or D.is_fake_executor(ex) or D.is_object_subject(ex):
        bad_exec.append(c)

print("iter1 총:", len(rows))
print("(가) content_type MISMATCH:", len(mismatch_ct), " / NO_RULE(미분류):", len(norule_ct))
print("(나) executor 의심(의무류):", len(bad_exec))
print("--- content_type MISMATCH 샘플 10 ---")
for c, exp, got in mismatch_ct[:10]:
    print(f"  저장={exp} 재판정={got} :: {(c['source_text'] or '')[:70]}")
print("--- executor 의심 샘플 10 ---")
for c in bad_exec[:10]:
    print(f"  exec={c.get('executor_text')!r} :: {(c['source_text'] or '')[:70]}")
```
```bash
railway run python3 scripts/_probe_verify_clauses.py 2>&1 | tee /tmp/verify_clauses.log
```

---

## STEP A3 — 산안법 17·18조 집중 글읽기 (전체 검증의 핵심 표본)

전수 엔진 검증과 별개로, 선임 누락의 진원지인 산안법 17·18조가 iter1에서 어떻게 들어갔는지
DB에서 직접 글로 확인(Claude가 판정할 근거):
```sql
SELECT sc.source_text, sc.content_type, sc.executor_text, sc.needs_review
FROM semantic_clause_iter1 sc
JOIN law_article a ON a.id = sc.source_article_id
JOIN law_master m ON m.id = a.law_id
WHERE m.law_name='산업안전보건법' AND a.article_no IN ('15','16','17','18','19')
ORDER BY a.article_no, sc.clause_seq;
```

---

## 보고 형식 (이 형식 그대로 기획창에 제출)

```
[A1 복원] [DECOMPOSE]·[DONE] 라인 / iter1 총 행수 / content_type 분포 /
          본 테이블 semantic_clause는 여전히 0인지
[A2 역검증] iter1 총 / content_type MISMATCH 수+샘플10 / NO_RULE 수 / executor 의심 수+샘플10
[A3 산안법] 15~19조 의미절 (source_text·content_type·executor·needs_review) 전체 붙여넣기
[비고]    에러·예상과 다른 점 (수정하지 말고 기록만)
```

금지: decompose_v1.py·check_engine.py 수정 / executor 보정 / 본 테이블 동기화 /
      분해규칙 변경 / 자가패치. 복원·검증·보고만. 끝나면 정지.
대표 승인 후에만 다음(본 테이블 동기화·룰 변환)으로 진행.
