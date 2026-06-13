# CURSOR 작업지시서 I — 갈래1 보정 1회차 실행: 주격조사 직결만 (executor_fixed 채움 + 재색출 검증)

작성일: 2026-06-14
발행: Claude 기획창 / 수행: Cursor (로컬/railway, kiwipiepy + Supabase)
근거: docs/2026-06-14_EXECUTOR_FIX_STRATEGY.md, 지시서 H 표본검증 결과(Claude 판정)

---

## H 표본 판정 결과 (이 지시의 근거)

H의 PERFECT 1,676건 표본 25건을 Claude가 글로 검증한 결과:
- 16/25 정확. 단 두 종류 오차 발견:
  · "A의 B" 소유격: "위원회의 위원이"인데 "위원회"만 추출(진짜 주어=위원). 명사라 재검증도 통과 → 위험.
  · 맨앞 사물: "건설공사에 관한…당사자는"인데 "건설공사" 추출.
- 결론: PERFECT 전체는 아직 못 씀. **"명사+주격조사(은/는/이/가) 직결"만** 1회차 대상.
  소유격 "의", 기타조사, 조사없음은 전부 다음 회차로 미룸.
- 규모(SQL 거친 집계): 주격조사 직결 ~1,525 / 소유격 의 920 / 기타조사 1,527 / 조사없음 3,093.

## "완벽" 재확인 (대표 정의 — 둘 다 충족해야)
1. 수정 후 Kiwi 재검증 작동 (명사로 바뀌어 OK/FLAG 판정 가능)
2. 바꿀 주어가 원문에서 확정 (맨앞 명사 **직후** 주격조사 = 원문이 직접 말한 주어, 추측 아님)

## 성격 / 안전 경계
- 원본 semantic_clause 수정 금지. semantic_clause_fix(임시)에서만.
- executor_text 아직 안 바꿈. **executor_fixed에만 채움.** executor_text 반영은 검증 통과 후 별도.
- 분해기·Kiwi사전 무변경. 동사어간 사전등록 금지.

---

## STEP 1 — 1회차 대상 선별 (Kiwi 정밀, 주격조사 직결만)

대상: fix_flag='GARAE1_VERB_STEM' (7,065).
각 의미절 source_part_text 맨앞을 Kiwi 분석 → **명사덩어리 직후 바로 주격조사**인 것만 PERFECT_V2:
```
조건: 맨앞 토큰이 NNG/NNP (또는 연속 명사덩어리) 이고,
      그 명사덩어리 바로 다음 토큰이 주격조사 JKS(이/가) 또는 보조사 JX 중 은/는.
      ★ 명사덩어리 다음이 관형격 '의'(JKG)면 제외 (A의 B 케이스 → 미룸)
      ★ 명사덩어리 다음이 기타조사(에/를/로 등)면 제외
주어 = 그 명사덩어리. 단 추출 주어가 자가생산 사전(1,348) 등재면 신뢰 ↑(우선),
      미등재라도 "명사+주격조사 직결"이면 1회차 포함 가능(원문이 직접 말한 주어이므로).
```
분류 집계: PERFECT_V2(주격직결) / 소유격제외 / 기타조사제외 / 조사없음제외.

## STEP 2 — executor_fixed 채움 (semantic_clause_fix, executor_text는 그대로)

PERFECT_V2 각 행:
```sql
UPDATE semantic_clause_fix
SET executor_fixed = '<추출된 맨앞주어>', fix_status='FIXED'
WHERE id = <id>;
-- executor_text 는 절대 건드리지 않음 (원본 보존, 비교용)
```
배치로. 완료 후 executor_fixed 채워진 건수 보고.

## STEP 3 — Kiwi 재색출 검증 (조건1: 고친 게 검증을 통과하는가) ★

채운 executor_fixed를 다시 Kiwi로 색출 규칙에 넣어, **전부 OK(명사끝)인지** 확인:
```
for each FIXED row:
    재판정 = classify(executor_fixed)   # H의 색출 규칙과 동일
    재판정이 OK 아니면 → 'REFIX_FAIL' 로 표시 (잘못 채운 것 = 색출됨)
```
- 기대: PERFECT_V2 전부 OK (명사+주격조사에서 뽑았으니 명사여야).
- REFIX_FAIL이 나오면 그 건 + 형태소 보고 (규칙 구멍). 0이어야 정상.

## STEP 4 — 표본 글읽기 (Claude 판정용)

executor_fixed 채운 것 중 무작위 25건:
```
법령·조문 | 원문 source_part_text 앞 90자 | executor_text(기존 틀림) | executor_fixed(보정) | content_type
```
+ 산안법 17·18·19조가 PERFECT_V2에 포함됐는지, 포함됐다면 그 보정 결과 별도 표기
  (안전관리자 선임 의무 executor가 '사업주'로 보정됐는지 — 핵심 목표).

## 보고 형식
```
[선별]    PERFECT_V2(주격직결) 건수 / 소유격·기타조사·조사없음 제외 각 건수
[채움]    executor_fixed 채운 건수 / fix_status=FIXED 수
[재색출]  FIXED 중 재판정 OK 수 / REFIX_FAIL 수(+샘플) — 0이어야
[표본]    25건: 법령·조문 | 원문앞 | 기존executor | 보정executor | content_type
[17조]    산안법 15~19조 선임 보정 결과 (있으면)
[비고]    특이점 (수정 말고 기록만, executor_text 미변경 확인)
```

표본·재색출 통과 시 → executor_text 반영 + 원본 복사는 별도 지시(대표 승인 후).
금지: 원본 수정 / executor_text 변경 / 소유격·기타조사 케이스 보정(이번엔 주격직결만) /
      분해기·사전 변경 / 동사어간 등록. 끝나면 정지.
