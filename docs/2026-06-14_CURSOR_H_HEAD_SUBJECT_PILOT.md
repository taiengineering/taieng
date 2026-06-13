# CURSOR 작업지시서 H — 갈래1 보정 1회차: 원문 맨앞주어 추출 + 표본검증 (보정 아직 안 함)

작성일: 2026-06-14
발행: Claude 기획창 / 수행: Cursor (로컬/railway, kiwipiepy + Supabase)
근거: docs/2026-06-14_EXECUTOR_FIX_STRATEGY.md ("완벽" 2조건),
      docs/2026-06-13_SESSION_END_EXECUTOR_FIX_STATUS.md (어제 멈춘 지점)

---

## 이번 단계 = 완벽 후보 추출 + 표본검증까지. 실제 보정은 표본 통과 후.

어제 "조문에서 OK주어 빌리기"가 표본 절반 틀림(소방관/출구 오선택)으로 폐기됨.
이번엔 **원문(source_part_text) 맨 앞 주어 추출**로 "완벽 후보"만 골라 표본 검증한다.
표본이 통과해야 executor_fixed 채우고 재색출로 넘어간다.

## 성격 / 안전 경계
- 원본 semantic_clause 수정 금지. semantic_clause_fix(임시)에서만.
- 이번 STEP 1~2는 **읽기/표본추출만**. executor_fixed 채우기(STEP3)는 표본 통과 후 별도 지시.
- 분해기·Kiwi사전 무변경. 동사어간 사전등록 금지.
- Kiwi 사전 = 자가생산 1,348개 NNP (2회차 동일).

---

## STEP 1 — 갈래1 의미절의 원문 맨앞 주어 추출 → "완벽 후보" 표시

대상: semantic_clause_fix 의무류 중 fix_flag='GARAE1_VERB_STEM' (7,065건).
각 의미절의 source_part_text(원문 전체) 맨 앞을 Kiwi로 분석해 주어 추출:

```python
# scripts/_probe_head_subject_extract.py — 맨앞주어 추출 (읽기/판정만, executor_text 안 건드림)
import os
from supabase import create_client
from kiwipiepy import Kiwi
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
kiwi = Kiwi()
# 자가생산 사전 주입 (1,348 NNP) — 2회차 STEP1 동일 집합
subject_set = set(...)   # 사전 목록(아래 SQL 결과)
for w in subject_set: kiwi.add_user_word(w,"NNP",5.0)

NOUN=("NNG","NNP")
SUBJ_JOSA=("은","는","이","가")  # 주격/보조사

def head_subject(part_text):
    """원문 맨 앞에서 [명사+ 주격조사] 주어를 추출. 없으면 None."""
    if not part_text: return None, "EMPTY"
    toks = kiwi.tokenize(part_text)
    # 맨 앞부터 스캔: 첫 명사덩어리(연속 NN*) 직후에 주격조사가 오면 그게 주어
    i = 0; n = len(toks)
    # 조건절/부사 선행 처리: 맨 앞이 명사가 아니면(제3항/다음/이/그 등) 주어 확정 불가로 본다(보수적)
    if n==0: return None, "EMPTY"
    if toks[0].tag not in ("NNG","NNP","XPN"):  # 맨 앞이 명사가 아니면 미확정
        return None, f"HEAD_NOT_NOUN:{toks[0].tag}"
    # 연속 명사덩어리 모으기
    buf=[]; j=0
    while j<n and (toks[j].tag.startswith("NN") or toks[j].tag in ("XPN","XSN","SW")):
        buf.append(toks[j].form); j+=1
    if j<n and toks[j].tag.startswith("JK") or (j<n and toks[j].form in SUBJ_JOSA):
        cand = "".join(buf)
        return cand, "OK_HEAD_SUBJECT"
    if j<n and toks[j].form in SUBJ_JOSA:
        return "".join(buf), "OK_HEAD_SUBJECT"
    return "".join(buf) if buf else None, "NO_JOSA_AFTER_NOUN"

# 갈래1 전수 → head_subject 추출 → 완벽 후보 판정
# 완벽후보 = status=OK_HEAD_SUBJECT AND 추출주어 in subject_set(사전 등재 검증주체)
```

판정 분류(각 건수 집계):
- **PERFECT**: 맨앞 [명사+주격조사] 추출됨 AND 그 명사가 자가생산 사전에 등재 (조건1∧2 충족)
- NOUN_NOT_IN_DICT: 맨앞 주어는 뽑혔으나 사전에 없음 (검증 약함 → 미룸)
- HEAD_NOT_NOUN: 맨앞이 조건절/부사/지시어 (제3항/다음/이 등 → 주어 미확정 → 미룸)
- NO_JOSA / EMPTY: 주격조사 없음/원문 없음 → 미룸

## STEP 2 — PERFECT 후보 표본 검증 (글읽기, 보정 안 함)

PERFECT로 분류된 것 중 무작위 25건 출력:
```
원문 source_part_text 앞 90자 | 현재 executor(틀림) | 추출된 맨앞주어(PERFECT) | 법령·조문
```
→ Claude가 글로 읽어 "추출된 맨앞주어가 이 의무의 진짜 주어인지" 원문 대조 판정.
   (어제처럼 표본에서 틀린 게 섞이는지 확인. 통과해야 STEP3 보정 진행.)

## 보고 형식
```
[분류]    갈래1 7,065 중 PERFECT / NOUN_NOT_IN_DICT / HEAD_NOT_NOUN / NO_JOSA / EMPTY 각 건수
[표본]    PERFECT 25건: 원문앞부분 | 현executor | 추출주어 | 법령·조문
[빈도]    PERFECT 추출주어 상위 20 (사업주 n, 장관 n …)
[비고]    특이점 (수정 말고 기록만)
```

표본 통과 시 STEP3(executor_fixed 채움 → Kiwi 재색출 검증 → executor_text 반영) 별도 지시.
금지: 원본 수정 / executor_text 변경(이번엔 추출·표본만) / 분해기·사전 변경 / 동사어간 등록.
읽기·표본·보고만. 끝나면 정지.

---
### 참고: 자가생산 사전 SQL (STEP1 subject_set)
```sql
SELECT DISTINCT executor_text FROM semantic_clause_fix
WHERE fix_flag='OK' AND executor_text IS NOT NULL
  AND executor_text ~ '(자|인|장|관|회|주|사|원|청|부|국|단|소|처|책임자|권자|업자|기관|공단|협회|정부|위원|공무원|근로자|대통령|도지사|군수|구청장|시장)$'
  AND length(executor_text) BETWEEN 2 AND 40;
```
