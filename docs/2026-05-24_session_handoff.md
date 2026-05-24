# 세션 핸드오프 — PDF/Documents 와이어링 복구 스프린트

**세션 일시:** 2026-05-24
**세션 유형:** TAI Safe 오픈 준비 분석 → PDF→Documents 와이어링 복구 → Runtime 실증
**작성 시점 상태:** 와이어링 코드 완료, runtime 부분 실증 완료, TBM route 미해결

---

## 1. 세션에서 수행한 작업 (시간순)

### Phase 1: TAI Open Readiness 전수 분석
- 백엔드 인프라(140+ 라우터, 58K 규칙, RLS 전 테이블) 분석
- 고객 핵심 플로우 미검증 상태 식별
- Critical blocker 7개 특정
- 가격 테이블 정정 (PRICING_FINAL.md 일치), TBM 템플릿 시드 25건, 무료체험 플랜 3건 INSERT
- **산출물:** `outputs/TAI_Open_Readiness_Report.md`

### Phase 2: PDF→Documents Flow 정밀 조사
- `document_svc.py` v1.0.0 완전 구현 확인 (`register_generated()` 함수)
- `documents` 테이블 33컬럼, `doc_category` enum 13종, `doc_source` enum 3종 확인
- Storage bucket `company-docs` (private) 존재 확인
- **핵심 발견:** 모든 PDF 라우터에서 `register_generated()` import 없음 → 연결이 설계되었으나 와이어링되지 않은 상태
- **중요 수정:** `report_forms.py`는 자체 Storage(`form-outputs` 버킷 + `form_submissions.pdf_url`)가 이미 동작 — 수정 대상 아님
- **산출물:** `outputs/TAI_PDF_Documents_Flow_Audit.md`

### Phase 3: Cursor 코드 수정
- 4개 파일에 `register_generated()` 와이어링 추가 (+129줄)
- `contract_kmong.py`는 `def` → `async def` 전환
- py_compile PASS
- **Cursor 작업지시서:** `taieng/docs/2026-05-24_cursor_pdf_documents_wiring.md`

### Phase 4: 코드 검증 + PR 머지
- dev 브랜치 커밋 (58a2fac) → 4개 라우터 와이어링
- `router_registry/document_engine.py`에 `routers.document_engine` 추가 (f4113a0)
- PR #85 (dev→main) 충돌로 닫음
- `fix/pdf-documents-wiring` 브랜치 생성 (main에서 분기)
- PR #86 (fix→main) **squash 머지 완료** (7576d76)
- Railway auto-deploy 실행

### Phase 5: Runtime 실증
- `/` 엔드포인트로 모듈 상태 확인: 모든 그룹 loaded, failed=0
- 진단 제안서 `/diagnosis/proposal-pdf/` HTTP 302 성공 (캐시 URL 문제 해결 후)
- Gotenberg PDF 생성, Storage 업로드 정상 확인
- TBM route loaded=6 (7이어야 함) — 미해결

---

## 2. 현재 main 브랜치 상태

### 변경된 파일 (PR #86으로 main에 반영)

| 파일 | 변경 | 상태 |
|------|------|------|
| `routers/document_engine.py` | 와이어링 + 복원 | ⚠️ 문자 오염 (패처→패철, 해HTML) |
| `routers/diagnosis_report.py` | 와이어링 +36줄 | ⚠️ compiler 코드 -37줄 의도하지 않은 삭제 |
| `routers/diagnosis_proposal.py` | 와이어링 +39줄 | ✅ 정상 (순수 추가) |
| `routers/contract_kmong.py` | 와이어링 +23줄, async 전환 | ✅ 정상 |
| `router_registry/document_engine.py` | `routers.document_engine` 추가 | ✅ 정상 (7개 항목) |

### 의도하지 않은 변경 (복구 필요)

**`diagnosis_report.py`에서 삭제된 코드:**
- `_load_compiler_report_tables()` 함수 전체 (~20줄)
- `compiler_session_id`, `compiler_candidates`, `compiler_penalties`, `compiler_schedule_hints` 템플릿 변수 (~10줄)
- **원인:** `git checkout dev -- routers/diagnosis_report.py` 실행 시 dev에 있던 와이어링 외 변경 유입
- **복구:** PR #86 머지 전 main의 `diagnosis_report.py` (SHA: `98aaf574`)에서 해당 함수/변수 복원

**`document_engine.py` 문자 오염:**
- `패처` → `패철` (주석), `HTML 미리보기` → `해HTML 미리보기` (docstring)
- **원인:** Claude `push_files` Unicode 인코딩 실수
- **영향:** 기능 영향 없음 (주석/docstring만)

---

## 3. 미해결 이슈

### 이슈 1: TBM route 미로드 (Priority: High, 비차단)

**증상:** `document_engine` 그룹 loaded=6 (7이어야 함), `/document-forms/*` 404
**확인된 사항:**
- GitHub main에 7개 항목 정상 등록
- 모든 import 대상 파일 존재 확인 (fetcher, renderer, template)
- 3회 재배포 후에도 loaded=6 유지
- Railway Deploy Logs **시작 부분 미확인** (runtime 로그만 확보)

**다음 조치:**
1. Railway Deploy Logs 시작 부분에서 `[document_engine] FAILED to load routers.document_engine` 메시지 확인
2. import error 메시지로 정확한 원인 특정
3. 최소 수정 (구조 변경 금지)

### 이슈 2: documents INSERT 실증 미완료

**원인:** 테스트 데이터 모두 `company_id=null`
**다음 조치:** TBM route 활성화 후 company_id 있는 factory 데이터로 테스트

### 이슈 3: diagnosis_report.py compiler 코드 복원

**상태:** 코드 삭제되어 있으나 기능 영향 미확인
**다음 조치:** 템플릿에서 compiler 변수 사용 여부 확인 → 사용 시 복원

---

## 4. 변경하지 않은 것 (확인)

| 항목 | 상태 |
|------|------|
| `services/document_svc.py` | 수정 없음 |
| `documents` 테이블 스키마 | 변경 없음 |
| `doc_category` / `doc_source` enum | 변경 없음 |
| Storage bucket `company-docs` | 변경 없음 |
| Gotenberg 설정 | 변경 없음 |
| `routers/report_forms.py` | 수정 없음 (자체 Storage 동작 중) |
| 엔진 구조 (`services/document_engine/`) | 수정 없음 |

---

## 5. DB 변경 사항

| 테이블 | 변경 | 건수 |
|--------|------|------|
| `price_saas_plan` | UPDATE (가격 정정) | 7건 |
| `tbm_templates` | INSERT (시드 데이터) | 25건 |
| `price_saas_plan` | INSERT (TRIAL 플랜) | 3건 |
| `anonymous_diagnosis_results` | UPDATE (proposal_pdf_url NULL, 테스트용) | 1건 (복원됨) |

---

## 6. 인프라 상태

| 구성요소 | 상태 | 비고 |
|----------|------|------|
| Railway tai-api-prod | ✅ Online | api.taieng.co.kr |
| Railway Gotenberg | ✅ Online | internal:3000 |
| Supabase Seoul | ✅ Active | vwlahtguyggrhvslabax |
| Storage `company-docs` | ✅ private | documents용 |
| `/health` | ⚠️ degraded | law_engine, fix_chat fail (기존 이슈) |

---

## 7. 커밋/PR 이력

| SHA/PR | 브랜치 | 내용 |
|--------|--------|------|
| 58a2fac | dev | 4개 라우터 와이어링 |
| f4113a0 | dev | router_registry 등록 |
| PR #85 | dev→main | 충돌로 닫음 |
| PR #86 (7576d76) | fix→main | **squash 머지 완료** |
| 02f5ad7 | main | registry 강제 업데이트 |

---

## 8. 다음 세션 우선순위

### 즉시 (시작 시 1분)
- Railway Deploy Logs 시작 부분 → `[document_engine] FAILED` 확인 → TBM route 원인 특정

### Priority 1: 고객 시나리오 E2E
- 실제 브라우저에서 가입→로그인→현장 생성→작업자 등록→점검→PDF→결제→구독 적용
- 판단 기준: "고객이 혼자 사용할 수 있는가"

### Priority 2: 결제→플랜 적용 실증

### Priority 3: 관리자 운영 + 모바일 UX

### 금지
- TBM route 구조 재설계
- engine 수정
- registry 리팩토링
- 기술 완벽주의 과몰입

---

## 9. 참조 파일

| 파일 | 위치 |
|------|------|
| Open Readiness 보고서 | `outputs/TAI_Open_Readiness_Report.md` |
| PDF Flow Audit | `outputs/TAI_PDF_Documents_Flow_Audit.md` |
| Cursor 작업지시서 | `taieng/docs/2026-05-24_cursor_pdf_documents_wiring.md` |
| 검증 보고서 | `outputs/2026-05-24_wiring_verification_report.md` |
| 다음 세션 지시 | `taieng/docs/2026-05-24_next_session_e2e_verification.md` |
| 핸드오프 문서 | `taieng/docs/2026-05-24_session_handoff.md` |
