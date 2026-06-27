# WO-FRONT-DATA-SOURCE-001 — 프론트 결과 데이터 소스 추적 (읽기 전용)

**작성일:** 2026-06-27 | **상태:** 추적 완료 | **판정:** **CASE A** (이미 호환, 연결 수정 0)
**목적:** SaaS/진단 프론트가 어떤 API·JSON·테이블을 읽는지 코드로 확정. 엔진/출력구조 변경 없음.

---

## TASK-001 — SaaS 프론트 API 호출 (결과 화면)
```
파일 : tai-admin/tadmin/full-version/html/horizontal-menu-template/diagnosis-result-v2.html
화면 : 법령진단 결과 (로그인 SaaS)
주 API : GET https://api.taieng.co.kr/diagnosis/transform/{diagnosis_id}
         헤더 Authorization: Bearer <access_token>  (localStorage.access_token)
         diagnosis_id = URL 쿼리 ?diagnosis_id=
부 API : GET /diagnosis/{diagnosis_id}/recommend-plan  (FN-06 플랜추천, 선택·실패시 숨김)
403 → auth-login-cover.html 리다이렉트 / 404 → 에러표시
```

### 프론트가 기대하는 response shape (d)
```
d.schema_version                 ('v2026.04' 아니면 재진단 배너 표시)
d.warnings[]    {level, message}
d.headline      {summary, severity}
d.obligations[] {category, risk_level, title, description, evidence[], auto_schedulable, action_url}
                 → 탭: 선임/점검/신고/교육/서류 (category로 필터)
d.roi           {penalty_max_krw, subscription_annual_krw, roi_ratio, breakeven_days}
d.inspection_schedule[] {month, count, items[]}
d.next_actions[] {label, url, type}
d.company_name, d.sector, d.tier, d.generated_at
```

## TASK-002 — 진단 Web / HTML / PDF 호출
```
routers/diagnosis_report.py        → 공개 PDF (report-pdf/{public_token})
routers/diagnosis_result_web.py    → 서버렌더 공개 결과
routers/anonymous_diagnosis.py     → 익명 진단
  → 세 파일 모두 anonymous_diagnosis_results.full_result 읽음 (public_token 기반, 로그인 아님)
  → SaaS 결과 화면과 별도 파이프. diagnosis_transform과 무관.
```

## TASK-003 — 결과 JSON 저장 위치 (실사용)
```
SaaS 결과 화면        → factory_diagnosis_results.result_data   ✅ (신규 엔진이 쓰는 곳)
공개/익명 PDF·HTML   → anonymous_diagnosis_results.full_result   (별도)
SaaS 점검항목·일정    → inspection_master / inspection_set_items   (다른 기능, 결과아님)
```

## TASK-004 — 프론트 기대 vs diagnosis_transform 실응답 비교
라이브 HTTP 응답(diagnosis_id 0238b7fd)과 필드 대조:
```
프론트 읽는 필드            transform 제공         결과
schema_version              O                     ✅ (값 "unknown" → 경고배너만, 브레이크 아님)
warnings[]{level,message}   O ([])                 ✅
headline{summary,severity}  O                     ✅
obligations[] category/risk_level/title/
  description/evidence/auto_schedulable/action_url  O (전부)  ✅
  (추가필드 law_name/rule_type/source_clause_id/
   law_article/trigger_sources → 프론트 무시, 무해)
roi{penalty/subscription/ratio/breakeven}  O       ✅
inspection_schedule[]{month,count,items}   O       ✅
next_actions[]{label,url,type}             O       ✅
company_name/sector/tier/generated_at      O       ✅
```
**by-id 경로 확인:** GET /diagnosis/transform/{diagnosis_id} = transform_by_id → _fetch_row_by_id(created_by 소유자 체크) → **_build_transform (latest와 동일 빌더)** → _extract_obligations에 dedup(_merge_by_clause_law, 169) 포함. 즉 프론트가 부르는 경로도 169·동일 구조.

### 비도구 마찰(코스메틱, 연결 브레이크 아님)
```
1. schema_version "unknown" ≠ 'v2026.04' → "재진단 권장" 노란 배너 (result_data에 schema_version 미포함)
2. headline "총 171개" = rule_count(raw 171), 리스트는 169 (숨자 불일치)
3. 탭 신고/교육 = 0 (어댑터 출력이 서류/선임/점검만) → 빈 탭, 브레이크 아님
```

## TASK-005 — 연결 방식 판정
```
✅ CASE A : 프론트가 이미 diagnosis_transform과 호환.
            프론트(diagnosis-result-v2)는 바로 그 엔드포인트(/diagnosis/transform/{id})를 위해 제작됨.
            어댑터/뷰모델 불필요. API 연결만으로 동작.
```

## TASK-006 — 변경 대상 최소화
```
결과 화면 연결 자체 = 수정 0 (백엔드 adapter 불필요, 프론트 API 경로 변경 불필요).

유일한 미연결은 결과 화면이 아니라 **upstream 트리거**:
  SaaS 진단 실행 흐름이 인증 토큰으로 persist를 호출해
  factory_diagnosis_results(created_by=현사용자) 행을 만들고,
  반환된 diagnosis_id로 diagnosis-result-v2.html?diagnosis_id=X 로 이동.
  → 이건 "프론트 API 경로(트리거)" 쪽. 별도 WO  uad8c장.
  → created_by 인증은 WO-CREATEDBY-FIX-001로 이미 해결됨.
```

## 성공 기준 대조
```
프론트 읽는 JSON 경로 확정   ✅ GET /diagnosis/transform/{id} → factory_diagnosis_results.result_data
transform 출력과 비교        ✅ 필드 완전 일치 (추가필드는 프론트 무시)
CASE A/B/C 확정            ✅ CASE A
수정 대상 1개 결정         ✅ 결과화면 수정 0; 미연결=upstream 트리거(다음 WO)
```

## 금지사항 준수
```
새 엔진/Persist/DB테이블/화면 생성 0. 기존 엔진/법령로직/Check Engine 미수정.
읽기 전용 추적만 수행 (코드 변경 없음).
```

---

*WO-FRONT-DATA-SOURCE-001 — SaaS 결과화면은 factory_diagnosis_results.result_data를 /diagnosis/transform으로 읽으며 필드 완전 호환(CASE A). 공개 PDF는 anonymous_diagnosis_results 별도 파이프. 연결 수정 0, 미연결은 upstream 트리거.*
