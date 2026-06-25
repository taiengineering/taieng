# WO-CHECK-LAYER-LEGAL-TRACE-001 — 법령 역추적 Check Layer

**작성일:** 2026-06-26 | **상태:** 완료 (Path A — 실데이터 기반 trace 범위 확정)
**선행:** WO-CHECKENGINE-API-CONTRACT-001, HANDOFF_EXISTS입력활성화완료
**대상:** factory `e9c56af6-5de7-487d-bd2e-0d452291a562` (INDUSTRIAL, worker 280), batch `WO-MVP-001-LIVE`, obligation 171건

> 이 WO는 "실패"가 아니라 **Check Layer가 현재 데이터로 실제 추적 가능한 범위를 확정**하는 작업이다.
> Check Layer = 생성기가 아니라 역추적기(Legal Trace). 없는 값은 만들지 않는다. unresolved는 정직하게 남긴다.

---

## 0. 한 문단 요약

171개 obligation 전부에 대해 의무→조문→법령 추적 골격이 100% 살아있고, 그 위에서
**WHO·WHY·원문(trace_source)은 100%, WHEN은 18건(부분)** 채워진다.
**WHERE/WHAT/HOW·required_evidence·required_data는 현재 데이터로 추적 불가**이며,
그 원인(semantic_clause 미분해 / master_rule_v2 0건 / law_appendix 1건 / delegation·citation 희박)을
의무마다 `unresolved_reason`으로 구조화한다. 규칙·카테고리로 빈 칸을 만들지 않았다.

---

## 1. Boundary Check (헌법 TASK-007)

```
Applicability 내부 작업인가?   NO
Boundary 변경 필요한가?        NO
Data Contract 변경 필요한가?   NO
Breaking Change인가?           NO
→ 전부 NO. 기존 Contract 그대로. 신규 테이블/DDL 없음. 읽기 전용 SELECT만.
```

**확정 원칙 (대표 승인, Path A):**
- 없는 값을 만들지 않는다.
- WHERE/WHAT/HOW를 규칙으로 생성하지 않는다.
- category 기반 evidence를 만들지 않는다.
- action_text/article_text 원문 인용은 허용하되, "분해된 6W"가 아니라 **trace_source**로 분리한다.

---

## 2. TASK-001 — Check Layer 입력 Contract 확정 (정정 포함)

입력은 **obligation_adapter의 obligations 배열 + obligation_instance + semantic_clause**다.
**Track-A CheckResult(facility_applicability 경로, GPT 소관)는 사용하지 않는다.**

확정된 실제 조인 체인 (전 구간 실측 연결):

```
obligation_instance.source_clause_id
  → semantic_clause.id          (executor/cycle/recipient/condition/source/action 텍스트)
    → source_article_id → law_article.id   (article_no / article_title / article_text)
      → law_id → law_master.id             (law_name)
```

> 정정: 이전 WO(평면 8필드 CheckResult)는 Track-A 스키마였음. 우리 171은 그 경로가 아니라
> obligation 경로를 타므로 per-의무 check_method/draft_id가 없고, verdict는 adapter 통과값(불변),
> reason은 obligation_instance.reason(불변)을 인용한다.

---

## 3. Trace Skeleton — 실측 100%

```
의무 → semantic_clause       171/171  (clause_missing 0)
clause → law_article         171/171  (article_ok 171)
article → law_master(법령명)  171/171
distinct 조문 135개 / distinct 법령 7개
```

추적 골격에는 끊김이 없다. 모든 의무가 근거 조문과 법령까지 닿는다.

---

## 4. Check Layer 출력 구조 (의무 1건당 레코드)

```jsonc
{
  // ── 불변 carry-through (수정 금지) ──
  "obligation_id":  "<obligation_instance.id>",
  "trigger_type":   "<UNIVERSAL(NONE)/THRESHOLD/EQUIPMENT_ACT/MATERIAL_ACT/WORK_ACT>",
  "input_field":    "<has_crane 등 | null>",
  "verdict":        "<adapter 통과값, 불변>",
  "reason":         "<obligation_instance.reason, 재생성 금지>",
  "law_reference":  { "law_name": "...", "article_no": 0, "article_title": "..." },

  // ── 1. traced_fields (있을 때만 채움, 없으면 키 생략) ──
  "traced_fields": {
    "WHO":       "<semantic_clause.executor_text>",          // 100%
    "WHY":       "<law_name + 제{article_no}조 + article_title>", // 100%
    "WHEN":      "<semantic_clause.cycle_text>",             // cycle_text 있을 때만
    "RECIPIENT": "<semantic_clause.recipient_text>",         // 있을 때만
    "CONDITION": "<semantic_clause.condition_text>"          // 있을 때만
  },

  // ── 2. trace_source (원문, 분해 아님 — 인용) ──
  "trace_source": {
    "source_text":  "<semantic_clause.source_text>",   // 100%
    "action_text":  "<semantic_clause.action_text>",   // 100%
    "article_text": "<law_article.article_text>"       // 100%
  },

  // ── 3. unresolved_fields (현재 데이터로 추적 불가) ──
  "unresolved_fields": ["WHERE", "WHAT", "HOW", "required_evidence", "required_data"],

  // ── 4. unresolved_reason ──
  "unresolved_reason": [
    "semantic_clause WHERE/WHAT/HOW 미분해 (where_text/what_text/how_text 0%)",
    "master_rule_v2 0건 (구조화 규칙 미적재)",
    "law_appendix 1건 (별표 미적재 → 선임기준·증빙 추적 불가)",
    "delegation 21% / citation 6% (상위 위임·정의조문 연결 희박)"
  ]
}
```

**필드 출처(provenance) 고정:** traced_fields와 trace_source의 모든 값은 위 컬럼에서 **직독**한다.
값이 없으면 키를 생성하지 않는다(WHEN/RECIPIENT/CONDITION). 합성·추론·규칙 매핑 없음.

---

## 5. 실측 Coverage (171건, trigger_type별)

```
trigger          n    skeleton  WHO  WHY  WHEN  RECIP  COND  trace_source
EQUIPMENT_ACT    25     25      25   25    0     0     16     25
MATERIAL_ACT     32     32      32   32    2     2     16     32
UNIVERSAL(NONE)  93     93      93   93   13    12      0     93
THRESHOLD         3      3       3    3    3     0      0      3
WORK_ACT         18     18      18   18    0     2     14     18
─────────────────────────────────────────────────────────────────────
TOTAL           171    171     171  171   18    16     46    171

비율:  skeleton 100% · WHO 100% · WHY 100% · trace_source 100%
       WHEN 10.5% · RECIPIENT 9% · CONDITION 27%
       WHERE/WHAT/HOW(구조화) 0% · required_evidence/required_data 0%
```

**성공 기준 충족:** 171건 모두 skeleton 100% / WHO·WHY 100% / WHEN 일부 / source 100% / unresolved 명시. ✓

---

## 6. 실제 Trace 표본 (trigger별 1건, 직독)

```
[EQUIPMENT_ACT · has_crane]
  WHO 사업주 | WHY 산업안전보건기준에 관한 규칙 제139조(크레인의 수리 등의 작업)
  WHEN — | trace_source 보유(action/article 원문) | unresolved WHERE/WHAT/HOW…

[MATERIAL_ACT · has_chemical_substance]
  WHO 사업주 | WHY 산업안전보건기준에 관한 규칙 제449조(유해성 등의 주지)
  CONDITION "…관리대상 유해물질을 취급하는 작업에 근로자를 종사하도록 하는 경우"
  RECIPIENT(노이즈) "호의 사항을 근로자" | trace_source 보유

[UNIVERSAL(NONE)]
  WHO 사업주 | WHY 산업안전보건법 시행규칙 제197조(일반건강진단의 주기 등)
  WHEN "정기적으로" | trace_source 보유

[THRESHOLD · worker_count]
  WHO "해당하"(파싱 노이즈, 실제 의무는 유효 — 안전보건관리담당자 선임)
  WHY 산업안전보건법 시행령 제24조(안전보건관리담당자의 선임 등)
  WHEN "상시"(상시근로자 조각, 주기 아님 — 노이즈) | trace_source 보유

[WORK_ACT · has_welding]
  WHO 사업주 | WHY 산업안전보건기준에 관한 규칙 제236조(화재 위험이 있는 작업의 장소 등)
  CONDITION "화기를 사용하는 작업…불꽃이 발생될 우려가 있는 작업(화재위험작업)…경우"
  trace_source 보유
```

---

## 7. 안정화된 추출 방식 (진짜 산출물 — 재현 가능 SQL)

```sql
WITH oi AS (
  SELECT o.id AS obligation_id, o.trigger_type, o.input_field,
         o.reason AS oi_reason, o.source_clause_id
  FROM obligation_instance o
  WHERE o.factory_id = :factory_id
    AND o.generation_batch = :batch
)
SELECT
  oi.obligation_id, oi.trigger_type, oi.input_field, oi.oi_reason,
  -- traced_fields
  sc.executor_text                                   AS who,
  lm.law_name, la.article_no, la.article_title,      -- why
  NULLIF(sc.cycle_text,'')      AS when_,
  NULLIF(sc.recipient_text,'')  AS recipient,
  NULLIF(sc.condition_text,'')  AS condition_,
  -- trace_source
  sc.source_text, sc.action_text, la.article_text
FROM oi
JOIN semantic_clause sc ON sc.id = oi.source_clause_id
LEFT JOIN law_article  la ON la.id = sc.source_article_id
LEFT JOIN law_master   lm ON lm.id = la.law_id;
-- unresolved_fields / unresolved_reason 는 고정 상수로 부여 (위 §4)
```

이 추출식이 곧 Check Layer의 trace 로직이다. 건수가 아니라 이 추출 방식이 산출물이다.

---

## 8. Unresolved 지도 = 상류 적재 작업목록 (Path B, GPT/Architecture 경계)

현재 비어 추적 불가인 항목과 그 원인. **이 WO 범위 밖이며, 파싱·법령데이터 적재 영역이라 GPT 전담·Architecture Review 선행.**

```
WHERE / WHAT / HOW (구조화)
  원인: semantic_clause.where_text/what_text/how_text = 0/171
  필요: semantic_clause 6W 분해 파이프라인 (또는 master_rule_v2 적재)
        ※ 원문은 article_text/action_text에 100% 존재 — 분해만 미완

required_evidence
  원인: law_appendix 전체 1건 (별표 미적재) → 선임기준·신고서식 추적 불가
  필요: 별표(law_appendix) 적재 + article_refs 연결

required_data
  원인: 구조화 scope(master_rule_v2.scope_*) 0건
  필요: scope_min_employees/area/equipment 등 구조화 규칙 적재
  ※ 부분 대안: obligation_instance.input_field(has_crane 등)로 일부 역산 가능 — 별도 검토

상위 정의·시행령 trace
  delegation 28/135(21%) · citation 8/135(6%) — 연결 희박
```

---

## 9. 알려진 노이즈 (정제는 별도 과제 — 이 WO는 trace 범위 확정)

```
- executor_text "해당하" : 제24조 등 파싱 노이즈. 실제 의무 유효 → 거르지 않음(핸드오프 함정 #2).
- executor_text "관계수급인" : 도급 조문의 주체. 유효하나 사업주 의무와 구분 필요.
- recipient_text "호의 사항을 근로자"/"사업주는 근로자" : 조각. 신고대상 아님.
- cycle_text "상시" : 상시근로자 조각이 WHEN에 섞임. 주기 아님.
→ WHO는 100% 존재하나 정제율은 별도 측정 과제. 본 WO는 "무엇이 추적되는가"의 범위만 확정.
```

---

## 10. 메모리 정정 (다음 창 반드시 반영)

```
★ master_rule_v2 = 0행 (빈 테이블). 메모리의 "master_rule_v2 (58,495건)"은 STALE.
  스키마는 풍부(what_action/how_method/scope_*/penalty_summary/online_system_url 등)하나
  데이터 미적재. semantic_clause(58,495)와 동일 카운트로 오인된 것으로 보임.
```

---

## 11. 경계 준수 확인

```
✓ Applicability Engine / Generator / Trigger / Check Engine 무수정
✓ verdict 변경 없음 · reason 재생성 없음 · obligation 수정 없음
✓ Data Contract 변경 없음 · Boundary 변경 없음 · 신규 테이블/DDL 없음 (읽기 전용 SELECT만)
✓ 규칙 기반 6W 생성 없음 · category 기반 evidence 생성 없음
✓ 원문 인용은 traced_fields가 아닌 trace_source로 분리
```

---

## 다음 단계

```
이 WO (A) — 완료. Check Layer의 trace 가능 범위 확정.
다음 후보:
  - (정제) executor/recipient/cycle 노이즈 정제율 측정 + 정제 규칙 (trace 범위 내, Claude 영역)
  - (B 상류) semantic_clause WHERE/WHAT/HOW 분해 / 별표 적재 / master_rule_v2 적재
    → GPT/Architecture 경계. Review 선행. 완료 후 unresolved_fields가 traced_fields로 승격.
  - (Refinement) traced_fields → 화면용 실행가이드 표현 (정제레이어, 별도 WO)
```

---

*WO-CHECK-LAYER-LEGAL-TRACE-001 완료. Check Layer는 역추적기다.*
*171건: skeleton 100% / WHO·WHY·source 100% / WHEN 18 / unresolved 명시.*
*없는 값은 만들지 않았다. unresolved는 상류 적재(Path B)의 지도로 남긴다.*
