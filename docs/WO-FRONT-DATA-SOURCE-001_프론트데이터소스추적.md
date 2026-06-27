# WO-FRONT-DATA-SOURCE-001 — 프론트 결과 데이터 소스 추적

**작성일:** 2026-06-27 | **상태:** 추적 완료(읽기 전용). 코드/엔진/DB 변경 0.
**판정:** **CASE A — 프론트는 이미 `diagnosis_transform`과 호환.**

> 목적: SaaS/진단 Web이 어떤 JSON·API를 읽는지 확정하고 신규 `diagnosis_transform` 출력과 비교. 연결은 다음 단계.

---

## TASK-001 — SaaS 프론트 API 호출 (실파일 직독)

**파일:** `tai-admin / tadmin/full-version/html/horizontal-menu-template/diagnosis-result-v2.html` (화면명: **법령진단 결과**, 로그인 SaaS)

```
주 호출:  GET https://api.taieng.co.kr/diagnosis/transform/{diagnosis_id}
          headers: Authorization: Bearer <access_token(localStorage)>
          diagnosis_id ← URL ?diagnosis_id=
보조 호출: GET /diagnosis/{diagnosis_id}/recommend-plan   (FN-06 플랜추천, 선택적·실패시 조용히 숨김)
오류 처리: 403 → auth-login-cover.html 로 이동 / 404 → "결과 없음"
```

**프론트가 기대하는 response shape (d):**
```
d.schema_version                 (≠ 'v2026.04' 이면 "재진단 권장" 배너)
d.warnings[]      {level(INFO/WARN/DANGER), message}
d.headline        {summary, severity(LOW/MEDIUM/HIGH/CRITICAL)}
d.obligations[]   {category, risk_level, title, description, evidence[], auto_schedulable, action_url}
                   탭 카테고리: 선임 / 점검 / 신고 / 교육 / 서류
d.roi             {penalty_max_krw, subscription_annual_krw, roi_ratio, breakeven_days}
d.inspection_schedule[] {month, count, items[]}
d.next_actions[]  {label, url, type}
d.company_name, d.sector, d.tier, d.generated_at
```

## TASK-002 — 진단 Web / HTML / PDF 호출 위치 (코드 검색 확정)

```
routers/diagnosis_report.py        공개 PDF 리포트 (GET /diagnosis/report-pdf/{public_token})
routers/diagnosis_result_web.py    서버렌더 결과 Web
routers/anonymous_diagnosis.py     익명 무료진단 API
  → 셋 다 anonymous_diagnosis_results.full_result 를 읽음 (public_token 기반, 비로그인)
```
→ **공개/익명 무료진단 파이프**. 로그인 SaaS 결과화면(TASK-001)과 **별개**.

## TASK-003 — 실제 사용되는 JSON 저장 위치 확정

```
factory_diagnosis_results.result_data   ← SaaS 결과화면(diagnosis_transform)이 읽음. ★ 신규 엔진이 쓰는 곳.
anonymous_diagnosis_results.full_result ← 공개 PDF·익명 결과(별도 파이프).
inspection_master / inspection_set_items← SaaS 점검항목·일정(다른 기능, 진단결과 아님).
```

## TASK-004 — 신규 diagnosis_transform 출력 vs 프론트 기대 (필드 대조)

`GET /diagnosis/transform/{diagnosis_id}` = `transform_by_id` → `_fetch_row_by_id`(created_by 소유자 체크)
→ **`_build_transform`** (latest와 동일 빌더) → `_extract_obligations` → `_merge_by_clause_law`(dedup 169).
즉 by-id 경로도 검증본과 동일 출력(169·trigger_sources 포함).

```
프론트 기대               transform 제공          결과
schema_version            schema_version          ✓
warnings[]                warnings[]              ✓
headline{summary,severity}headline{...}           ✓
obligations[]             obligations[]           ✓ (category/risk_level/title/description/
  category·risk_level·                              evidence/auto_schedulable/action_url 전부 제공)
  title·description·                              + 추가필드(law_name/rule_type/source_clause_id/
  evidence·auto_schedulable·                        law_article/trigger_sources)는 프론트가 무시(무해)
  action_url
roi{4필드}                roi{4필드}              ✓
inspection_schedule[]     inspection_schedule[]   ✓
next_actions[]            next_actions[]          ✓
company_name/sector/      동일                    ✓
  tier/generated_at
```

**필드 누락·이름차이·배열차이: 없음.** 단, 깨지지 않는 **경미한 표시 불일치 3건**(연결과 무관):
```
1) schema_version="unknown" ≠ 'v2026.04' → 프론트가 "재진단 권장" 노란 배너 노출(경고일 뿐, 차단 아님).
   원인: from-instances persist의 result_data에 schema_version 미기록.
2) headline "총 171개" = rule_count(raw 171) 사용. 실제 리스트는 169. (표시 문구 불일치)
3) 탭 신고/교육 = 0건. 어댑터가 선임/점검/서류만 산출(빈 탭, 무해).
```

## TASK-005 — 연결 방식 판정

**CASE A — 프론트가 이미 `diagnosis_transform`과 호환.**
근거: 결과화면이 바로 그 엔드포인트(`/diagnosis/transform/{id}`)를 호출하도록 설계됐고, 기대 JSON과 transform 출력이 필드 단위로 일치. 얇은 adapter(B)·별도 ViewModel(C) **불필요**.

## TASK-006 — 변경 대상 최소화 (하나만)

**결과화면 연결 자체 = 수정 0** (CASE A).
연결을 위해 백엔드 response adapter도, 프론트 API 경로 변경도 필요 없음.

남은 단 하나의 미연결(이 WO 범위 밖, 다음 WO):
```
upstream 트리거 — SaaS 진단 실행 흐름이
  ① 인증 토큰으로 persist 호출(예: POST /obligation-adapter/from-instances/{factory_id}?persist=true)
  ② 반환 diagnosis_id 로 diagnosis-result-v2.html?diagnosis_id=X 이동
하도록 배선. (created_by FIX 로 ①의 권한·created_by 는 이미 충족.)
→ 변경 위치는 "프론트 트리거 흐름" 한 곳. 백엔드 adapter 불변.
```

---

## Boundary 준수
```
Applicability/Adapter/Persist/Data Contract/Architecture 변경: 전부 NO (읽기 전용 추적).
새 엔진/Persist/테이블/화면/법령로직/Check Engine: 생성 0.
```

## 성공 기준 대조
```
프론트가 읽는 JSON 경로 확정      ✓ /diagnosis/transform/{id} → factory_diagnosis_results.result_data
신규 transform 출력과 비교         ✓ 필드 완전 일치(누락 0)
CASE A/B/C 확정                    ✓ CASE A
수정 대상 1개 결정                 ✓ 결과화면=수정0 / 유일 미연결=upstream 트리거(다음 WO)
```

*WO-FRONT-DATA-SOURCE-001 — CASE A 확정. 결과화면은 추가 작업 없이 호환. 다음은 upstream 트리거 연결.*
