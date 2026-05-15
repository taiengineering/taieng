# TAI Safe 오픈 전 남은 이슈 (2026-05-14)

---

## 🔴 오픈 블로커 (즉시 필요)

### ISSUE-01: 구독 활성화 연결 미검증
- **현상:** subscriptions 테이블 24건 PENDING, 0건 ACTIVE
- **원인:** 이니시스 결제 콜백 → subscription status ACTIVE 전환 플로우 미검증
- **영향:** 고객이 결제해도 SaaS 기능 잠김 상태 유지
- **확인 필요:**
  - `routers/payment_billing.py` 결제 성공 콜백에서 `subscriptions.status = 'active'` 업데이트 로직 존재 여부
  - 이니시스 테스트 결제 → subscription 상태 변경 E2E 검증
- **담당:** Claude/Cursor
- **심각도:** 🔴 Critical

### ISSUE-02: 면책 문구 미삽입
- **현상:** 법령진단 결과 화면 + PDF 리포트에 법적 면책 문구 없음
- **필요 문구:** "본 진단 결과는 참고용이며 법적 효력이 없습니다. 정확한 법적 판단은 관련 전문가에게 문의하시기 바랍니다."
- **삽입 위치:**
  1. `tadmin/.../diagnosis-result-v2.html` 결과 상단/하단
  2. `templates/diagnosis_report_paid.html` PDF 리포트 하단
  3. `nexas/free-diagnosis-result.html` 무료진단 결과
- **담당:** Cursor
- **심각도:** 🔴 법적 리스크

### ISSUE-03: document_forms form_json 데이터 확인
- **현상:** DOC-03 UI 완성했지만, DB의 서식 레코드에 field 정의(form_json)가 비어 있으면 폼 렌더 불가
- **확인 필요:**
  - `SELECT doc_id, doc_name, form_json FROM document_form_schemas WHERE form_json IS NOT NULL LIMIT 10`
  - form_json이 비어 있으면 서식별 필드 정의 적재 필요
- **담당:** Supabase 확인 → GPT/Claude 데이터 적재
- **심각도:** 🔴 DOC-03 기능 무효화

---

## 🟡 GPT 전담 (Claude 절대 금지)

### ISSUE-04: Admin Review 229건 법령 판단
- **내용:** 관리자 리뷰 대기 중인 229건 법령 데이터 판단
- **담당:** GPT 엔진 전담

### ISSUE-05: token_family_registry 확장
- **내용:** 토큰 패밀리 레지스트리 확장 (엔진 도메인)
- **담당:** GPT 엔진 전담

### ISSUE-06: Document Engine 7개 서비스 파일 검증 후 push
- **내용:** 문서 엔진 서비스 레이어 7개 파일 최종 검증
- **담당:** GPT 엔진 전담

### ISSUE-07: Runtime Compiler 방향 B 후속
- **내용:** 런타임 컴파일러 방향 B 후속 개발
- **담당:** GPT 엔진 전담

---

## 🟢 오픈 후 가능 (비블로커)

### ISSUE-08: Gotenberg 마이그레이션
- **대상:** `routers/report_forms.py` (25KB), `routers/contract_kmong.py` (10KB)
- **현상:** xhtml2pdf 사용 중, CSS custom properties 미지원
- **영향:** 현재 동작은 하지만 렌더링 품질 제한
- **담당:** Cursor (대형 파일)

### ISSUE-09: INTERNAL_API_SECRET 로테이션
- **현상:** 세션 중 노출됨
- **조치:** Railway 환경변수 변경 + 코드 재배포
- **담당:** 대표님

### ISSUE-10: worker-check.html 경로 누락
- **현상:** `site/full-version/html/vertical-menu-template-no-customizer/`에 `worker-check.html` 미존재 가능
- **영향:** WORKER-03 빠른 액션 "점검 시작" 클릭 시 404
- **조치:** 해당 경로에 파일 복사 또는 경로 수정
- **담당:** Cursor

### ISSUE-11: my-inspection.html 전체선택 스코프
- **현상:** 2개 테이블이 같은 `.row-check` 클래스 → 전체선택 시 양쪽 모두 토글
- **조치:** 테이블별 스코프 분리 (`#table1 .row-check`, `#table2 .row-check`)
- **담당:** Cursor

### ISSUE-12: 서비스 레이어 분리
- **대상:** legal_engine (77KB), construction (58KB), payment (52KB), law_rule_generator (46KB), matching (42KB), inspection_sets (38KB)
- **규칙:** Router = HTTP only, Service = business logic, Schema = Pydantic, max 400 lines (15KB)
- **담당:** Cursor

---

## 오픈 전 체크리스트

- [ ] ISSUE-01: 구독 활성화 E2E 검증
- [ ] ISSUE-02: 면책 문구 3곳 삽입
- [ ] ISSUE-03: document_form_schemas form_json 데이터 확인
- [ ] ISSUE-04~07: GPT 전담 엔진 작업 완료 확인
- [ ] 이니시스 실결제 테스트 (테스트 모드 → 운영 모드)
- [ ] 전체 사이트 수동 QA (회원가입→진단→구독→점검→문서 E2E)

---

## 다음 세션 시작 프롬프트

```
이전 세션 누적 31건 완료.
오픈 전 남은 블로커: ISSUE-01(구독활성화), ISSUE-02(면책문구), ISSUE-03(form_json 데이터).
docs/2026-05-14_OPEN_REMAINING_ISSUES.md 참조.
역할: Product/SaaS/Runtime Ops Architect. 엔진 아키텍처 변경 금지.
```
