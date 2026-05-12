# 작업 내역 — 2026-04-29 (하이브리드 앱 v1.1.0 출시)

## 완료 작업

### 1. Capacitor server.url 복원
- **문제:** 이전 세션에서 `capacitor.config.ts`의 `server.url`이 안전관리자 어드민 로그인 페이지(`/html/horizontal-menu-template/auth-login-cover`)로 설정되어 있었음
- **수정:** 작업자 앱(`/app/index.html`)으로 복원
- **커밋:** `be4782c` — `fix(capacitor): server URL을 작업자 앱(/app/)으로 복원`

### 2. 버전 업데이트 v1.1.0
- `android/app/build.gradle`: versionCode 3→4, versionName "1.0.2"→"1.1.0"
- `package.json`: version "1.0.0"→"1.1.0"
- **커밋:** `4df5865`, `bbd46cc`

### 3. OTP 에러 핸들링 강화 (프론트)
- `sendOTP()`: `res.ok` 체크, 404/기타 에러/네트워크 에러 분기 처리
- 실패 시 `step2`로 이동하지 않고 현재 화면에서 에러 토스트 표시
- `verifyOTP()`: 동일하게 `res.ok` 기반 실패 처리 추가
- **커밋:** `0f31075` — `fix: OTP 발송/검증 실패 시 단계 전환 차단` (Cursor)

### 4. OTP 테스트 우회 등록 (백엔드)
- `routers/auth.py`의 `TEST_BYPASS`에 `01083994168: "000000"` 추가
- **커밋:** `3a713ce` — `fix: add 01083994168 to OTP TEST_BYPASS with 000000`

### 5. 테스트 사용자 DB 등록
- `users` 테이블: 심태왕 / 01083994168 / 타이엔지니어링 / 인천공장 / role_code 007
- `worker_registry` 테이블: 동일 정보

### 6. Play Store 등록 정보 작성
- `docs/PLAY_STORE_LISTING.md` 생성
- 짧은 설명 (71자) + 전체 설명 (약 1,600자)
- Play Console 입력 가이드 + 이미지 에셋 체크리스트

### 7. Play Store v1.1.0 프로덕션 제출
- AAB 업로드 (versionCode 4, versionName 1.1.0)
- 국가: 대한민국
- Google 심사 중 (3~7일 예상)

---

## 미해결 이슈

### ISSUE-01: 네이티브 푸시 전환 (높음)
- **파일:** `docs/ISSUE_NATIVE_PUSH.md`
- **상태:** 출시 후 첫 업데이트로 예정
- **문제:** 현재 웹 Firebase SDK 사용 → 앱 종료/백그라운드/로그아웃 시 푸시 미수신
- **해결:** `@capacitor/push-notifications` 네이티브 플러그인으로 전환
- **예상 소요:** 코드 3시간 + 빌드 2시간 + 재심사 3~7일

### ISSUE-02: SMS OTP 미발송
- **상태:** 미해결
- **문제:** `POST /auth/send-otp`가 OTP를 DB에 저장만 하고 실제 SMS를 발송하지 않음
- **현재 우회:** TEST_BYPASS로 고정 OTP 사용
- **해결 필요:** 메세지미(MessageMi) API 연동하여 실제 SMS 발송
- **관련 파일:** `routers/auth.py` send_otp 함수

### ISSUE-03: Supabase 프로젝트 연결 확인 필요
- **상태:** 미확인
- **문제:** Railway API 서버의 `SUPABASE_URL` 환경변수가 구 프로젝트(xntdkrjhgcscmqctdzyo)를 바라보고 있을 가능성
- **증상:** MCP로 신규 프로젝트(vwlahtguyggrhvslabax) otp_store에 삽입한 OTP가 API에서 인식 안 됨
- **확인 방법:** Railway Variables 탭에서 SUPABASE_URL 확인
- **영향:** OTP 저장/조회, 사용자 조회 등 전체 DB 연동

### ISSUE-04: Capacitor 추가 플러그인 미설치
- **상태:** 대기
- **필요 플러그인:** `@capacitor/app` (뒤로가기), `@capacitor/network` (오프라인감지), `@capacitor/preferences` (저장소), `@capacitor/geolocation` (GPS)
- **시점:** 네이티브 푸시 전환 시 같이 설치 후 리빌드

---

## 변경된 파일 목록

### tai-admin (프론트엔드)
| 파일 | 변경 내용 |
|---|---|
| `capacitor.config.ts` | server.url → `/app/index.html` |
| `android/app/build.gradle` | versionCode 4, versionName "1.1.0" |
| `package.json` | version "1.1.0" |
| `tadmin/full-version/app/index.html` | sendOTP/verifyOTP 에러 핸들링 |
| `docs/PLAY_STORE_LISTING.md` | 신규 생성 |
| `docs/ISSUE_NATIVE_PUSH.md` | 신규 생성 |
| `docs/WORK_LOG_20260429.md` | 신규 생성 (본 파일) |

### tai-api (백엔드)
| 파일 | 변경 내용 |
|---|---|
| `routers/auth.py` | TEST_BYPASS에 01083994168 추가 |

### Supabase (DB)
| 테이블 | 변경 내용 |
|---|---|
| `users` | 심태왕 (01083994168) 테스트 계정 추가 |
| `worker_registry` | 동일 작업자 등록 |
| `otp_store` | 테스트 OTP 삽입 (현재 유효) |

---

## 다음 단계 (우선순위순)

1. Play Store 심사 승인 대기 (3~7일)
2. Railway SUPABASE_URL 환경변수 확인 (ISSUE-03)
3. SMS OTP 메세지미 연동 (ISSUE-02)
4. 네이티브 푸시 전환 + 추가 플러그인 (ISSUE-01, ISSUE-04)
5. 앱 로그인 테스트 (000000 우회 코드로)
