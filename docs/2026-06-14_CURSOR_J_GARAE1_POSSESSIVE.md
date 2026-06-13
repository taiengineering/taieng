# CURSOR 작업지시서 J — 갈래1 보정 2회차: 소유격 "A의 B+주격조사" (B 추출)

작성일: 2026-06-14
발행: Claude 기획창 / 수행: Cursor (로컬/railway, kiwipiepy + Supabase)
근거: docs/2026-06-14_EXECUTOR_FIX_STRATEGY.md, _EXECUTOR_FIX_ROUND1_DONE.md(1회차)

---

## 1회차 이후 — 이번엔 소유격 케이스 (갈래1 잔여 806건)

1회차: "명사+주격조사 직결" 1,280건 보정 완료(사전등재, 임시테이블 APPLIED).
이번: 갈래1 잔여 중 원문 맨앞이 **"A의 B"**(소유격)로 시작하는 806건.

Claude 표본 글읽기(25건) 결과:
- 다수가 "A의 **장은/위원은/관계인은/소유자는**" 구조 → **B(의 다음 명사)가 진짜 주어.**
  (1회차에서 A만 뽑아 틀렸던 것 → 이번엔 B를 뽑으면 정확)
  예: "관리기관의 장은…" → 장 / "지정위원회의 위원이…" → 위원 / "특정소방대상물의 관계인은…" → 관계인
- 함정 2종(미뤄야):
  · 나열형: "법인의 대표자나 법인…종업원이" → 진짜 주어는 나열 끝(종업원). B(대표자)≠주어.
  · B가 목적어/수식: "산업시설구역등의 산업용지 또는…", "하나의 공동주택단지를" → 을/를·또는 끼면 미룸.
  · 부정: "외국의 제작자가 아닌 자로부터…" → 제작자 뒤 "아닌"으로 부정 → 미룸.

## "완벽" 정의 (변함없음, 둘 다 충족)
1. 수정 후 Kiwi 재검증 작동 (명사로 바뀌어 OK)
2. 바꿀 주어가 원문에서 확정 (A의 **B**, B 직후 주격조사 직결 = 원문이 직접 말한 주어)

## 성격 / 안전 경계 (1회차와 동일)
- 원본 semantic_clause 수정 금지. semantic_clause_fix(임시)에서만. executor_text는 STEP까지 보존.
- 분해기·Kiwi사전 무변경. 동사어간 사전등록 금지.
- Kiwi 사전 = 자가생산 1,348 NNP (동일).

---

## STEP 1 — 소유격 B 추출 (Kiwi, "A의 B+주격조사"만)

대상: fix_flag='GARAE1_VERB_STEM' AND fix_status<>'APPLIED' AND 원문 맨앞이 "단어의 …".
각 source_part_text 맨앞을 Kiwi 분석:
```
패턴: [명사덩어리 A] + 관형격조사 '의'(JKG) + [명사덩어리 B] + 주격조사(JKS 이/가 또는 JX 은/는)
  → 주어 = B (의 다음 명사덩어리)
제외(미룸):
  - B 직후가 주격조사 아님(목적격 을/를, 접속 나/또는/및, 기타조사) → SKIP_B_NOT_SUBJECT
  - A의 B의 C … 처럼 '의'가 연속(중첩 소유격) → SKIP_NESTED (B 확정 모호)
  - B 다음에 '아닌/아니'(부정) → SKIP_NEGATION
  - 나열 신호(B 또는 직후에 나/와/과/및/또는 + 추가 명사) → SKIP_ENUM
신뢰: 추출 B가 자가생산 사전(1,348) 등재면 PERFECT_POSSESSIVE (1회차처럼 사전등재만 보정대상)
```
분류 집계: PERFECT_POSSESSIVE / SKIP_B_NOT_SUBJECT / SKIP_NESTED / SKIP_NEGATION / SKIP_ENUM / B_NOT_IN_DICT.

## STEP 2 — executor_fixed 채움 (PERFECT_POSSESSIVE만, executor_text 보존)
```sql
UPDATE semantic_clause_fix
SET executor_fixed = '<추출된 B>', fix_status='FIXED_POSS'
WHERE id = <id>;   -- executor_text 안 건드림
```

## STEP 3 — Kiwi 재색출 검증 (조건1) ★
채운 executor_fixed를 Kiwi 색출 규칙으로 재판정 → 전부 OK(명사끝)인지.
REFIX_FAIL(명사 아님) 나오면 그 건+형태소 보고. 0 기대.
+ 사물 차단 확인: executor_fixed가 사전 미등재인데 사물접미(설비/장치/함/용지 등)면 별도 표기.

## STEP 4 — 표본 글읽기 (Claude 판정용)
FIXED_POSS 중 무작위 25건:
```
법령·조문 | 원문 source_part_text 앞 90자 | executor_text(기존 동사어간) | executor_fixed(=B) | content_type
```
특히 "A의 장은" 류가 정확히 "장"으로 뽑혔는지, 나열/목적어 함정이 안 섞였는지 확인.

## 보고 형식
```
[선별]    소유격 대상 총 / PERFECT_POSSESSIVE / SKIP_* 각 건수 / B_NOT_IN_DICT
[채움]    executor_fixed 채운 건수(FIXED_POSS)
[재색출]  OK 수 / REFIX_FAIL(+샘플) — 0 기대 / 사물 의심 별도
[표본]    25건: 법령·조문 | 원문앞 | 기존exec | 보정exec(B) | content_type
[비고]    특이점 (수정 말고 기록만, executor_text 미변경 확인)
```

표본·재색출 통과 시 → 임시테이블 executor_text 반영은 Claude가 이 창에서(1회차처럼). 원본 복사는 보정 다 끝낸 뒤 한 번에(대표 결정).
금지: 원본 수정 / executor_text 변경(이번엔 추출·채움·표본만) / 나열·목적어·중첩·부정 보정 /
      분해기·사전 변경 / 동사어간 등록. 끝나면 정지.
