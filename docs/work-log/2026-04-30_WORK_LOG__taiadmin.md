# 작업 내역 — 2026-04-30

## 완료 작업

### 1. 구 Supabase 프로젝트 삭제 완료
- 코드베이스 구 프로젝트 ID(`xntdkrjhgcscmqctdzyo`) 일괄 치환 → 서울(`vwlahtguyggrhvslabax`)
- `weather.py` v1.3.1, `precedent_api.py` v1.7.3, `health_probes.py` 수정
- `diagnosis_report_paid.html` SVG URL 치환 (sed 일괄)
- 구 프로젝트 삭제 전 역순 검증 완료 후 삭제

### 2. 이니시스 테스트 계정 확인
- `01022223333` / `123456!` → API 로그인 성공 확인 (HTTP 200, access_token 발급)

### 3. 메세지미 SMS 점검 및 아키텍처 전환
- `messaging.py` v6.2.0 — 타임아웃 60초 + 재시도 2회 + httpx 비동기
- Railway(싱가포르) → Edge Function(서울) 구간 타임아웃 확인
- Edge Function → 메세지미 직접 호출 정상 확인 (`code:100`, 881ms, 문자 도착)
- **원인:** Railway(싱가포르) → Supabase(서울) 네트워크 불안정

### 4. OTP Edge Function 신규 배포 (Railway 우회)
- `send-otp` Edge Function v1.0.0 서울 프로젝트 배포
- 기능: OTP 생성 → `otp_store` DB 저장 → 메세지미 SMS 발송
- TEST_BYPASS 포함 (`01047758888:123456`, `01083994168:000000`)
- 테스트 완료: 테스트 계정 인식 + DB 저장 성공 (2.8초)

### 5. 프론트엔드 OTP 직접 호출 전환
- `_utils.js` v1.1.0 — `sendOTP()`를 Edge Function 직접 호출로 오버라이드
- 구조 변경:
  - 변경 전: 앱 → Railway(싱가포르) `/auth/send-otp` → DB 저장 (SMS 미발송)
  - 변경 후: 앱 → Edge Function(서울) `/send-otp` → DB 저장 + SMS 발송
- `verifyOTP()`는 Railway 유지 (DB 조회만, 문제 없음)

### 6. Supabase MCP 서울 프로젝트 연결 확인
- 구 프로젝트 삭제 후 MCP 재연결
- `list_edge_functions`, `execute_sql` 정상 작동 확인

---

## 미해결 이슈

### ISSUE-01: 네이티브 푸시 전환 (높음)
- **파일:** `docs/ISSUE_NATIVE_PUSH.md`
- **상태:** 출시 후 첫 업데이트로 예정
- **문제:** 웹 Firebase SDK → 앱 종료/백그라운드 시 푸시 미수신
- **해결:** `@capacitor/push-notifications` 네이티브 플러그인 전환 + 리빌드

### ISSUE-02: 서브페이지 13개 뒤로가기 미수정
- **상태:** 작업지시서 제공됨, 미적용
- **문제:** 긴급신고(`emergency.html`) 외 서브페이지에서 뒤로가기 → 로그인 화면
- **대상:** inspect, construction_inspect, tbm, report, corrective, education, risk, work_request, attendance, history, qr_scan, notifications, profile (13개)
- **해결:** 각 파일의 `history.back()` → `location.href='index.html'` + popstate 리스너

### ISSUE-03: 로그인 직후 "서버 연결 실패" 알럿
- **상태:** 작업지시서 제공됨, 미적용
- **문제:** Capacitor 앱에서 Firebase 웹 SDK/서비스워커 에러
- **해결:** `initApp()` 내 API 호출 무음 실패 + Capacitor 환경 분기 (Firebase, 서비스워커 스킵)

### ISSUE-04: Capacitor 추가 플러그인 리빌드 미반영
- **상태:** npm install 완료, 리빌드 안 됨
- **플러그인:** `@capacitor/app`, `@capacitor/network`, `@capacitor/preferences`, `@capacitor/geolocation`
- **시점:** ISSUE-01(네이티브 푸시) 전환 시 같이 리빌드

### ISSUE-05: 안전관리 문서 서식 HTML 템플릿 미제작
- **상태:** DB에 11개 서식 등록, HTML 템플릿 0개
- **문제:** `form_templates` 테이블에 `html_storage_path`가 전부 null
- **영향:** PDF 생성 불가 (FORM-002만 로컬 fallback으로 동작)
- **Storage:** `form-templates`, `form-outputs`, `form-originals` 버킷 존재하나 파일 0개
- **필요 작업:** 11개 서식 HTML 제작 → `form-templates` 버킷 업로드
- **우선 서식:** FORM-001(산업재해 조사표), FORM-002(선임 보고서), FORM-030(산업재해 조사표)

### ISSUE-06: xhtml2pdf → Gotenberg 마이그레이션
- **상태:** BACKLOG (`docs/BACKLOG_xhtml2pdf_migration.md`)
- **대상:** `routers/report_forms.py`, `routers/contract_kmong.py`
- **이유:** xhtml2pdf 한글 렌더링 품질 문제
- **조건:** 기안 PDF(`diagnosis_proposal.py`, `diagnosis_report.py`)는 이미 Gotenberg 전환 완료

---

## 변경된 파일 목록

### tai-api (백엔드)
| 파일 | 변경 내용 |
|---|---|
| `routers/messaging.py` | v6.2.0 — 타임아웃 60초 + 재시도 + httpx 비동기 |
| `routers/weather.py` | v1.3.1 — 구 프로젝트 URL 수정 |
| `routers/precedent_api.py` | v1.7.3 — 구 프로젝트 URL 수정 |
| `services/health_probes.py` | 구 프로젝트 URL 수정 |
| `templates/diagnosis_report_paid.html` | SVG URL 일괄 치환 |

### tai-admin (프론트엔드)
| 파일 | 변경 내용 |
|---|---|
| `tadmin/full-version/app/_utils.js` | v1.1.0 — sendOTP Edge Function 직접 호출 오버라이드 |

### Supabase Edge Functions
| 함수 | 변경 내용 |
|---|---|
| `send-otp` | v1.0.0 신규 배포 — OTP 생성+DB저장+SMS 발송 |

### 인프라
| 항목 | 변경 내용 |
|---|---|
| 구 Supabase 프로젝트 | 삭제 완료 (xntdkrjhgcscmqctdzyo) |

---

## 다음 단계 (우선순위순)

1. ISSUE-02: 서브페이지 13개 뒤로가기 수정
2. ISSUE-03: 로그인 직후 알럿 제거
3. ISSUE-05: 안전관리 문서 HTML 템플릿 제작 (FORM-001, 002, 030)
4. Play Store 심사 승인 확인
5. ISSUE-01 + ISSUE-04: 네이티브 푸시 + 플러그인 리빌드
6. ISSUE-06: xhtml2pdf → Gotenberg 마이그레이션
