# WO-E2E-OPERATIONAL-001 — 사용자 진단 → 결과화면 운영 최종 E2E 검증

**작성일:** 2026-06-27 | **성격:** 읽기·실행 검증(코드/엔진/DB/프론트 변경 0).
**판정: ⚠️ 보류 (NOT CLOSED) — 신규 obligation 파이프 기준 E2E 미연결.**
**대상 factory:** `e9c56af6-5de7-487d-bd2e-0d452291a562` (INDUSTRIAL)

> 결론 요약: 실제 "진단하기" 버튼은 **레거시 legal_engine 경로**로 동작하며 자체적으로 결과화면까지 닫혀 있다. 그러나 이번 세션에 구축·검증한 **171→169 obligation 파이프(adapter→transform→v2)는 실 UI 어디에도 배선돼 있지 않다.** 따라서 "사용자 버튼 → obligation → persist → transform → v2 결과화면" E2E는 **단일 실행으로 닫히지 않는다.** "검증 없는 100% 완료 금지" 원칙에 따라 PASS 보류.

---

## 핵심 발견 — 운영 흐름에 두 개의 분리된 결과 시스템이 공존

```
[A] 레거시(실제 사용자 버튼이 타는 경로) — 라이브
  diagnosis-step1.html  btnDiagnose
    → POST /legal-engine/diagnose/step1  {factory_id, sector, input}   (v510 엔진)
    → 반환 data(diagnosis_id, rules[], result_data) → sessionStorage 'tai_diagnosis_step1'
    → 이동: 비건설 → diagnosis-result.html / 건설 → construction-diagnosis-step2.html
  diagnosis-result.html
    → sessionStorage 우선, 없으면 GET /legal-engine/diagnose/{factory_id}/latest
    → result_data.rules[] {law_name, law_article, obligation}, applicable_count, risk_level
    → "주요 룰 최대 30건" 표 렌더
  ※ /diagnosis/transform 미호출, obligations[]·169·trigger_sources 미사용, created_by 없음

[B] 신규(이번 세션 구축·검증) — 라이브 미배선
  obligation_instance → adapter(/obligation-adapter/from-instances?persist=true)
    → factory_diagnosis_results.result_data.obligations[] (created_by 포함)
    → GET /diagnosis/transform/{diagnosis_id} → 169 dedup + trigger_sources
    → diagnosis-result-v2.html
  ※ 실 UI 어디서도 v2로 이동/링크하지 않음(코드 검색: 자기 자신·docs·darkmode script만)
```

---

## TASK-001 — 진단 실행 버튼 실제 호출 (실파일 직독)
```
파일:   tadmin/.../diagnosis-step1.html  버튼 id=btnDiagnose ("1단계 진단 실행")
URL:    POST https://api.taieng.co.kr/legal-engine/diagnose/step1
Method: POST
Auth:   apiCall() = Authorization: Bearer <localStorage.access_token>
Payload:{ factory_id, sector, input:{...} }
persist=true:  없음 (쿼리 파라미터 미사용)
이동:    비건설 → diagnosis-result.html?factory_id&sector&diagnosis_id
         건설   → construction-diagnosis-step2.html?...
```
→ **실 버튼은 obligation-adapter가 아니라 legal_engine v510을 호출.** 결과화면도 v2가 아님.

## TASK-002 — obligation 생성 확인
- 실 버튼 경로(legal_engine/step1)는 `rules[]` 형태를 산출 — **obligation_instance→candidate→adapter(171) 파이프를 타지 않음.**
- 171 obligation·persist는 **obligation-adapter 경로에서만** 생성됨(지난 WO 실호출 검증):
```
diagnosis_id      0238b7fd-690c-4965-9c7f-5d0c35498345
source            FROM_INSTANCES_OBLIGATION_INSTANCE
raw_obligations   171
(이 행은 어댑터 호출로 생성 — 사용자 버튼이 만든 행 아님)
```

## TASK-003 — Persist 확인 (DB 직독, adapter 경로)
```
factory_diagnosis_results  id=0238b7fd-690c-4965-9c7f-5d0c35498345
created_by        있음(admin 251c81a1-…)  → has_created_by=true
is_latest         true
input_source      FROM_INSTANCES_OBLIGATION_INSTANCE
result_data       obligations[] (raw 171)
```
→ persist 자체는 정상. 단 트리거가 **사용자 버튼이 아니라 어댑터 직접 호출**.

## TASK-004 — diagnosis_transform 확인 (검증본, 지난 WO 실호출)
```
GET /diagnosis/transform/{0238b7fd}  (Bearer)
HTTP 200          ✓ (403 아님 — created_by FIX 반영)
schema_version    "unknown" (result_data 미기록 — v2가 "재진단 권장" 배너 노출)
headline          {summary, severity}
obligations       169 (raw 171 → 병합키 distinct 169)  ✓
trigger_sources   포함 ✓  (병합 2건: [NONE:UNIVERSAL], [MATERIAL_ACT:HAZMAT])
```
by-id 엔드포인트 = `_build_transform`(latest와 동일 빌더) → dedup 169 동일.

## TASK-005 — 결과 화면 확인 (diagnosis-result-v2.html)
**실 운영 흐름에서 도달 불가.** 사용자 버튼은 diagnosis-result.html(레거시, rules[] 표)로 이동하며, v2로 navigate/link하는 코드가 존재하지 않음(검색 확정).
→ Headline/169/Category/Description/Evidence/Law/ROI/Schedule를 **사용자 단일 실행으로** 화면에서 보는 경로 없음.

## TASK-006 — 화면 데이터 정합성
- [B] adapter→transform→v2 세그먼트 내부 정합성: 일치(검증). factory_diagnosis_results.obligations(171) → transform(169) → v2 필드 매핑 누락 0(WO-FRONT-DATA-SOURCE-001, CASE A).
- [A] 실 버튼→화면 정합성: **다른 계약**(rules[] vs obligations[]) — 두 경로가 만나지 않음.

## TASK-007 — 회귀 확인 (DB 직독, 무손상)
```
171 Raw 유지        ✓ raw_obligations=171
169 Display 유지    ✓ distinct 병합키=169
Trigger Source 유지 ✓ trigger_sources 보존(union)
Created_by 정상     ✓ has_created_by=true, is_latest=true
Verdict 불변        ✓ (이 WO 코드 변경 0)
Description 불변     ✓
Category 불변        ✓
```

## TASK-008 — E2E 최종 판정
```
사용자 버튼  →  Persist  →  Transform  →  결과 화면
[legal_engine]  [✗ 미연결]   [✗ 미호출]    [diagnosis-result.html]
  ↑ 실제 라이브 경로는 obligation/transform/v2 를 거치지 않음

[adapter]    →  Persist  →  Transform  →  v2 화면
  ✓ 0238b7fd     ✓ 171       ✓ 169         ✗ UI 미배선
  ↑ 신규 파이프는 검증됐으나 사용자 버튼과 단절
```
**판정: 보류 (NOT CLOSED).** 4단계가 단일 실행으로 연결되지 않음.

---

## 정직 보고 — 무엇이 닫혔고 무엇이 안 닫혔나
- 닫힘: ① 레거시 사용자 흐름(버튼→legal_engine→diagnosis-result.html). ② 신규 파이프의 persist→transform→169(검증, 단 어댑터 트리거).
- 안 닫힘: 사용자 버튼이 **신규 obligation 파이프를 타고 v2(169)에 도달**하는 운영 E2E.

## 남은 단일 연결 작업 (다음 WO — 본 WO 범위·역할경계 밖)
둘 중 하나만 선택(동시 변경 금지). 둘 다 legal_engine(GPT 소유) 또는 프론트 수정 포함 → Claude 단독 적용 불가, 대표/GPT 결정 필요.
```
(연결 A) diagnosis-step1 성공 → diagnosis-result-v2.html?diagnosis_id 로 이동
         + legal_engine/step1 이 obligations 를 factory_diagnosis_results 에 created_by 포함 persist
(연결 B) diagnosis-result.html 이 /diagnosis/transform/{id} 를 호출하도록 데이터소스 전환
```

## Boundary 준수
```
Applicability/Glue/Adapter/Persist/Transform/Frontend/Data Contract/Architecture: 전부 NO.
새 엔진/API/Router/Persist/Adapter/JSON: 생성 0. 법령로직/Check Engine: 미수정.
읽기·실행(DB 직독, 코드 직독) 검증만 수행.
```

## 완료 기준 대조
```
"사용자 진단하기 → 결과화면, 운영환경 단일 실행 실증"
→ 신규 obligation 파이프 기준: 미충족(버튼이 해당 파이프 미연결).
→ 레거시 기준: 충족(buttons→legal_engine→diagnosis-result.html 동작).
∴ "법령엔진 1단계 MVP 파이프라인 종료" 선언은 연결 WO 완료 후로 보류 권장.
```

*WO-E2E-OPERATIONAL-001 — 보류. 신규 파이프(171/169) 무손상·검증 완료. 사용자 버튼↔신규 파이프 단일 연결만 남음(다음 WO).*
