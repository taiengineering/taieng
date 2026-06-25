# WO-CHECK-LAYER-TRACE-CLEANUP-001 — 역추적 필드 정제

**작성일:** 2026-06-26 | **상태:** 완료 (Check Layer 내부 품질 작업, 계약 무변경)
**선행:** WO-CHECK-LAYER-LEGAL-TRACE-001
**대상:** factory `e9c56af6-…`, batch `WO-MVP-001-LIVE`, 171건

> 이 작업은 "더 많은 값을 만드는" 작업이 아니다. 이미 trace된 값을 **원문 근거가 있을 때만**
> 신뢰 가능한 형태로 정리하는 Check Layer 내부 품질 정리다. 원본은 수정하지 않는다.

---

## Boundary Check

```
Applicability 내부 작업인가?   NO
Boundary 변경 필요한가?        NO
Data Contract 변경 필요한가?   NO
Breaking Change인가?           NO
→ Check Layer 내부 품질 작업. 새 산출 필드만 추가. 원본/계약 무변경.
```

**금지 (전부 준수):** Check Engine·Applicability 수정 금지 / semantic_clause 원본 UPDATE 금지 /
master_rule_v2 생성 금지 / LLM 의미 재분해 금지 / WHERE·WHAT·HOW 생성 금지 / 증빙 생성 금지 / Data Contract 변경 금지.

---

## TASK-001 — 노이즈 후보 (171건 실측 분포)

```
executor_text:  사업주 166 · 관계수급인 1 · 건설공사도급인 1 · 도급인 1   → 정상 169
                사업장 1 · 해당하 1                                      → 노이즈 2
cycle_text:     null 153 · 즉시 4 · 정기적으로 4 · 60일이내/30일이내/15일이내/수시로/지체없이 각1
                                                                        → 정상 13
                상시 5                                                  → 후보 5
recipient_text: null 155 · 선행오염 fragment 16                          → 후보 16
```

> 정정(정직): WO는 recipient 노이즈를 "조사/어미 조각으로 끝나는 경우"로 정의했으나,
> 실측은 **꼬리가 아니라 선행(주어·동사) 오염**이 대부분이다 (예 "사업주는 근로자"). 꼬리는 대개 실제 대상.

---

## TASK-002 — 노이즈 유형 분류 (실제 사례)

```
A. executor 파싱 오류
   "해당하"  ← "다음 각 호의 어느 하나에 해당하는 사업의 사업주는…" 에서 '해당하' 절취
   "사업장"  ← "…산업보건의를 두어야 하는 사업의 종류와 사업장은…으로 한다"(정의조문)

B. recipient 선행 오염 (꼬리는 유효 대상)
   "사업주는 근로자" → 근로자 / "정하는 바에 따라 고용노동부장관" → 고용노동부장관
   "첨부하여 관할 지방고용노동관서의 장" → 관할 지방고용노동관서의 장

C. cycle '상시' — 원문에 따라 두 갈래 (★ 핵심)
   C-1 조건값: "상시근로자 20명/50명…" → 주기 아님 (제거)
   C-2 지속값: "상시 게시"·"상시 점검" → 常時(지속) = 유효 주기 (유지)

D. 정상값 (정제 불필요)
   executor: 사업주/도급인/관계수급인/건설공사도급인
   cycle: 즉시 · 정기적으로 · 60일 이내 · 30일 이내 · 15일 이내 · 수시로 · 지체 없이
```

---

## TASK-003 — 정제 원칙

**허용:** 원문(action_text/source_text)에 명시된 값을 그대로 복원.

```
executor "해당하" + 원문 "…사업주는…"  → traced_executor = "사업주"
recipient "사업주는 근로자"             → 꼬리 폐쇄집합 대상 = "근로자"
cycle "상시" + 원문 "상시근로자"        → 조건값 → traced_cycle = NULL
cycle "상시" + 원문 "상시 게시/점검"    → 지속 → traced_cycle = "상시" 유지
```

**금지:** 원문에 없는 주체 생성 · 추론으로 주기 생성 · 카테고리 기반 보정.

```
executor "사업장"(정의조문): 원문에 행위주체 명시 없음 → 복원 거부 → unresolved
recipient "호에 해당하는 사람"/"있는 능력을 갖춘 사업주": 모호 → unresolved
```

폐쇄집합(closed-set)만 사용: 주체 = {사업주, 도급인, 관계수급인, 건설공사도급인} /
대상 = {근로자, 소속 근로자, 해당 근로자, 고용노동부장관, 관할 지방고용노동관서의 장, 산업안전보건위원회의 위원}.
집합 밖이면 만들지 않고 unresolved.

---

## TASK-004 — 새 산출 필드 (원본 무수정)

semantic_clause 원본 컬럼은 그대로 둔다. Check Layer 출력에 새 필드만 추가:

```
traced_executor      정제된 주체 (없으면 null)
traced_recipient     정제된 대상 (없으면 null)
traced_cycle         정제된 주기 (조건값이면 null)
trace_cleanup_reason 정제/제거/불가 사유
```

---

## TASK-005 — 171건 적용 결과 (before → after, 실측)

```
[executor] 171
  clean        169   (그대로)
  cleanup        1   "해당하" → "사업주"  (원문 "…사업주는…" 근거)
  unresolved     1   "사업장" (정의조문, 원문 주체 없음)
  → 유효 주체 170 / 미해결 1

[cycle] 비null 18
  clean         13   (즉시·정기적으로·N일 이내·수시로·지체 없이)
  keep(상시)     2   "상시 게시"·"상시 점검" = 지속 → 유지
  drop(상시)     3   "상시근로자" 조건값 → null 정정 (가짜 주기 제거)
  → 유효 주기 15 (더 정확) / 제거 3

[recipient] 비null 16
  cleanup       12   선행오염 제거 → 폐쇄집합 대상 복원
  unresolved     4   "보건관리자 등이 사업주" · "실질적으로 총괄하여 관리하는 사람"
                     · "있는 능력을 갖춘 사업주" · "호에 해당하는 사람"
  → 유효 대상 12 / 미해결 4
```

**recipient 정제 매핑 (전수):**
```
정하는 바에 따라 고용노동부장관            → 고용노동부장관
이내에 관할 지방고용노동관서의 장          → 관할 지방고용노동관서의 장
첨부하여 관할 지방고용노동관서의 장        → 관할 지방고용노동관서의 장
사업주는 산업안전보건위원회의 위원         → 산업안전보건위원회의 위원
사업주는 소속 근로자                       → 소속 근로자
조치 외에 해당 근로자                      → 해당 근로자
사업주는 근로자(×2)·호의 사항을 근로자·위험을 방지하기 위하여 근로자
  ·방식의 지게차를 운전하는 근로자·관리대상 유해물질을 취급하는 근로자 → 근로자
```

---

## TASK-006 — Check Layer trace 출력 v1.1 (내부 보강, 계약 무변경)

기존 출력(traced_fields / trace_source / unresolved_fields / unresolved_reason)에 보강 추가:

```jsonc
"cleanup": {
  "cleanup_applied": ["WHO", "WHEN", "RECIPIENT"],   // 정제 적용 필드
  "cleanup_source":  "action_text|source_text",      // 원문 근거 위치
  "cleanup_reason":  "executor '해당하' → 원문 '사업주는' 복원"
}
```

> Data Contract 변경이 아니라 Check Layer 내부 필드 보강으로 문서화한다.
> traced_executor/recipient/cycle는 기존 traced_fields의 WHO/RECIPIENT/WHEN을 **대체하지 않고 병기**한다
> (원본 trace값 보존 + 정제값 추가). 화면 레이어가 정제값 우선 사용.

---

## TASK-007 — 보고서 요약

```
A. 노이즈 후보 수        executor 2 · cycle(상시) 5 · recipient 16  = 23
B. 정제 가능 수          executor 1 · cycle 3(drop)+2(keep재분류) · recipient 12 = 18
C. 정제 불가 수          executor 1 · recipient 4 = 5
D. 대표 사례             해당하→사업주 / 상시(조건)→제거·상시(지속)→유지 / 사업주는 근로자→근로자
E. 정제 원칙             원문 명시값만 복원, 폐쇄집합, 추론·카테고리·LLM 금지
F. Data Contract 무변경  원본 UPDATE 0 · 신규테이블 0 · DDL 0 · 읽기전용 SELECT만
```

---

## 재현 가능한 정제 로직 (결정적, LLM 없음)

```sql
-- executor
CASE
  WHEN ex IN ('사업주','도급인','관계수급인','건설공사도급인','사업주등','발주자') THEN ex
  WHEN ex IS NOT NULL AND src ~ '사업주는' THEN '사업주'
  ELSE NULL END AS traced_executor
-- cycle
CASE
  WHEN cy IS NULL OR cy='' THEN NULL
  WHEN cy='상시' AND src ~ '상시근로자' THEN NULL          -- 조건값 제거
  ELSE cy END AS traced_cycle                              -- 상시(지속) 포함 유지
-- recipient (폐쇄집합 꼬리)
CASE
  WHEN rc ~ '고용노동부장관$'            THEN '고용노동부장관'
  WHEN rc ~ '지방고용노동관서의 장$'     THEN '관할 지방고용노동관서의 장'
  WHEN rc ~ '위원$'                      THEN '산업안전보건위원회의 위원'
  WHEN rc ~ '소속 근로자$'               THEN '소속 근로자'
  WHEN rc ~ '해당 근로자$'               THEN '해당 근로자'
  WHEN rc ~ '근로자$'                    THEN '근로자'
  ELSE NULL END AS traced_recipient
-- src = COALESCE(action_text, source_text)
```

---

## 성공 기준 충족

```
✓ WHO/RECIPIENT/WHEN의 명백한 파싱 노이즈가 원문 근거가 있는 경우에만 정제됨
✓ 원문에 근거 없는 값(사업장·모호 recipient 4)은 생성하지 않고 unresolved 유지
✓ "상시" 양분(조건값 제거 3 / 지속 유지 2) — 글읽기로 유효값 파괴 방지
✓ 원본 데이터 무수정 · Data Contract 무변경
```

---

## 경계 준수 / 다음 단계

```
✓ semantic_clause 원본 UPDATE 0 · master_rule_v2 생성 0 · LLM 재분해 0
✓ WHERE/WHAT/HOW·증빙 생성 0 (이 WO 범위 아님)

다음 후보:
  - traced_fields(정제값 포함) → 화면용 실행가이드 표현 (Refinement, 별도 WO)
  - (B 상류) WHERE/WHAT/HOW 분해·별표·master_rule_v2 적재 (GPT/Architecture 경계)
```

---

*WO-CHECK-LAYER-TRACE-CLEANUP-001 완료. 만든 게 아니라 정리했다.*
*정제 18 / 미해결 5 / 원본·계약 무변경. 원문에 있는 값만 복원했다.*
