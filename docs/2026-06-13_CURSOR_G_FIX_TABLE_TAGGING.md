# CURSOR 작업지시서 G — 의미절 보정 1단계: 임시테이블 색출 태깅 + 원본 비교

작성일: 2026-06-13
발행: Claude 기획창 / 수행: Cursor (로컬/railway, kiwipiepy + Supabase)
근거: docs/2026-06-13_CURSOR_F_KIWI_RESCAN_V3.md (3회차 색출 확정),
      docs/2026-06-13_LEGAL_ENGINE_ROOTCAUSE_PIPELINE_SWAP.md 10장

---

## 절차 (대표 확정) — 임시테이블 → 비교분석 → 이상없으면 원본복사

이번 단계는 **태깅만**. 보정(주어 교체)은 태깅 검증 통과 후 다음 단계.
원본 semantic_clause는 절대 건드리지 않는다. 모든 작업은 semantic_clause_fix(임시)에서.

```
[이번] 임시테이블에 색출 태그 기록 → 원본과 비교분석 → 이상없음 확인
[다음] 갈래1 보정(작은 표본) → 검증 → 확대 → 원본 복사
```

## 이미 준비됨 (Claude가 생성)
`semantic_clause_fix` 테이블 = semantic_clause 1:1 복사(58,495) + 보정 컬럼:
- fix_flag (text): OK / GARAE1_VERB_STEM / GARAE2_SUBJECT_VERB / NONSUBJ / SAMUL / NULLEXEC
- fix_last_tag (text): Kiwi 마지막 형태소 품사
- executor_original (text): 원래 executor 박제됨(되돌리기용)
- executor_fixed (text): 보정될 주어 (이번엔 안 채움, NULL 유지)
- fix_status (text): PENDING(현재) → TAGGED

## 성격 / 안전 경계
- **원본 semantic_clause 수정 금지.** semantic_clause_fix(임시)에만 UPDATE.
- **executor_text 자체도 이번엔 안 바꿈.** fix_flag/fix_last_tag만 기록(태깅).
- 분해기·Kiwi 사전: 2회차와 동일(자가생산 1,348 NNP). 동사어간 사전등록 금지.
- 태깅만. 보정(executor 교체)은 다음 단계. 색출·태깅·비교·보고.

---

## STEP 1 — 임시테이블에 색출 태그 기록 (semantic_clause_fix UPDATE)

3회차 확정 규칙으로 의무류(OBLIGATION/PROHIBITION/AUTHORITY) 각 행을 분류해
fix_flag, fix_last_tag 기록:
```
NOUN=("NNG","NNP","NNB","NP","XSN")
VERBISH=("XSV","VV","VA","VX","EC","EF","EP")
NONSUBJ=("JKB","JKS","JKO","JKC","JX","MAG","SSC","SSO","SW","XSA","ETN","ETM","JC","XPN","IC","SN","Z_CODA")

executor NULL → fix_flag='NULLEXEC'
마지막 명사(NOUN) → fix_flag='OK'
마지막 동사류(VERBISH):
   EC/EF로 끝 또는 값이 '려'/'받'으로 끝 → 'GARAE2_SUBJECT_VERB'
   그 외(XSV/VV) → 'GARAE1_VERB_STEM'
마지막 비주어(NONSUBJ) → 'NONSUBJ'
```
- 의무류 아닌 행(DEFINITION/DELEGATION 등)은 fix_flag='OK'(또는 'NON_OBLIG')로 두고 보정 대상 제외.
- UPDATE 후 fix_status='TAGGED'.
- semantic_clause_fix 에만 쓴다. (Supabase service_role)

```python
# scripts/_probe_tag_fix_table.py — 임시테이블 색출 태깅 (semantic_clause_fix UPDATE only)
import os
from supabase import create_client
from kiwipiepy import Kiwi
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
kiwi = Kiwi()
# 자가생산 사전 주입 (2회차 STEP1 동일 집합 1,348)
# ... add_user_word(w,"NNP",5.0) ...

NOUN=("NNG","NNP","NNB","NP","XSN"); VERBISH=("XSV","VV","VA","VX","EC","EF","EP")
NONSUBJ=("JKB","JKS","JKO","JKC","JX","MAG","SSC","SSO","SW","XSA","ETN","ETM","JC","XPN","IC","SN","Z_CODA")
OBLIG=("OBLIGATION","PROHIBITION","AUTHORITY")

def tag(ex):
    if not ex: return "NULLEXEC", None
    toks=kiwi.tokenize(ex); lt=toks[-1].tag if toks else None; base=(lt or "").split("-")[0]
    if base in NOUN: return "OK", lt
    if base in VERBISH or lt in VERBISH:
        if base in ("EC","EF") or ex.endswith(("려","받")): return "GARAE2_SUBJECT_VERB", lt
        return "GARAE1_VERB_STEM", lt
    if base in NONSUBJ or lt in NONSUBJ: return "NONSUBJ", lt
    return "REVIEW", lt

# 의무류 전수 페이지네이션 → 각 행 태깅 → fix 테이블 UPDATE (배치)
# (id 기준 UPDATE. executor_text는 건드리지 않음)
```
대량 UPDATE는 배치(예: id 묶음 100~500개씩)로. 완료 후 분포 출력.

## STEP 2 — 원본과 비교 분석 (이상 없는지)

```sql
-- (1) 행수·executor 무변경 확인 (태깅이 원본 데이터를 훼손 안 했나)
SELECT count(*) FROM semantic_clause_fix f JOIN semantic_clause o ON o.id=f.id
  WHERE f.executor_text IS DISTINCT FROM o.executor_text;   -- 0 이어야
SELECT count(*) FROM semantic_clause_fix f JOIN semantic_clause o ON o.id=f.id
  WHERE f.source_text IS DISTINCT FROM o.source_text;       -- 0 이어야

-- (2) fix_flag 분포 (3회차 색출과 일치하나)
SELECT fix_flag, count(*) FROM semantic_clause_fix
  WHERE content_type IN ('OBLIGATION','PROHIBITION','AUTHORITY')
  GROUP BY fix_flag ORDER BY 2 DESC;
-- 기대: OK 29,519 / GARAE1 7,065 / GARAE2 4,464 / NONSUBJ 408 / NULLEXEC 421 근사

-- (3) 산안법 17조 선임 의미절이 어떻게 태깅됐나 (글읽기 검증)
SELECT source_text, executor_text, content_type, fix_flag, fix_last_tag
FROM semantic_clause_fix f
JOIN law_article a ON a.id=f.source_article_id
JOIN law_master m ON m.id=a.law_id
WHERE m.law_name='산업안전보건법' AND a.article_no='17';
```

## 보고 형식
```
[태깅]    semantic_clause_fix UPDATE 완료 건수 / fix_status=TAGGED 수
[무결성]  executor 변경 0 / source_text 변경 0 (원본 데이터 훼손 없음)
[분포]    fix_flag별 건수 (3회차 색출과 일치하는지)
[17조]    산안법 17조 의미절들의 (source_text·executor·fix_flag) — "두어야 한다"가 GARAE1인지
[비고]    이상·불일치 (수정 말고 기록만)
```

이 결과로 Claude가 태깅 정확성을 글로 판정 → 통과 시 갈래1 보정 단계 설계.
금지: 원본 semantic_clause 수정 / executor 교체(이번엔 태깅만) / 분해기·Kiwi사전 변경 /
      동사어간 사전등록. semantic_clause_fix 태깅·비교·보고만. 끝나면 정지.
