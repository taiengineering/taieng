# TAI Frontend 세션 기록 — 2026-04-11

## tai-admin 작업

### PWA i18n 7개 언어 적용 완료

`tadmin/full-version/app/` 하위 모든 HTML 파일에 i18n 적용 완료.

**지원 언어:** ko / en / zh / vi / ne / km / tl (7개국)

**완료 파일 목록:**

| 파일 | EXT 키 | 상태 |
|---|---|---|
| index.html | 기존 완료 | ✅ |
| inspect.html | 기존 완료 | ✅ |
| tbm.html | 기존 완료 | ✅ |
| report.html | REPORT_EXT | ✅ |
| corrective.html | CORRECTIVE_EXT | ✅ |
| risk.html | RISK_EXT | ✅ |
| education.html | EDU_EXT | ✅ |
| work_request.html | WR_EXT (SAFETY_MAP 언어화) | ✅ |
| profile.html | PROFILE_EXT | ✅ |
| notifications.html | NOTIF_EXT (탭/데모 데이터) | ✅ |
| history.html | HIST_EXT (select options 포함) | ✅ |
| attendance.html | ATTEND_EXT (달력 요일) | ✅ |
| qr_scan.html | QR_EXT | ✅ |
| emergency.html | EM_EXT (유형버튼 포함) | ✅ |
| install.html | INST_EXT (단계별 iOS/Android 가이드) | ✅ |
| construction_inspect.html | CON_EXT (공정명 i18n화) | ✅ |

**특이사항:**
- work_request.html: 안전조치 체크리스트 (`wr_s_height`, `wr_s_fire` 등) 데이터 배열로 7개국어 제공, type_key 매핑 활용
- construction_inspect.html: 건설 공정명 로컬라이징 (`con_proc_temp` 등), 점검항목 단어(건설 전문용어)는 한국어 유지
- install.html: iOS/Android 수동설치 4단계 모두 7개국어 포함

**i18n 패턴 (표준):**
```js
const PAGE_EXT = {ko:{...}, en:{...}, zh:{...}, vi:{...}, ne:{...}, km:{...}, tl:{...}};
Object.keys(PAGE_EXT).forEach(lang => {
  if (TAI_I18N[lang]) Object.assign(TAI_I18N[lang], PAGE_EXT[lang]);
});
```

---

## 커밋 목록 (tai-admin, 이번 세션)

| 커밋 | 내용 |
|---|---|
| 92ace45 | work_request.html i18n |
| afd7986 | profile.html i18n |
| 35bce67 | notifications.html i18n |
| 41e7907 | history.html i18n |
| 1b1e3d4 | attendance.html i18n |
| 8989bc0 | qr_scan.html i18n |
| a639b14 | emergency.html, install.html i18n |
| 9cf1f28 | construction_inspect.html i18n |

---

## tai-api 병행 작업 (이번 세션)

### users.sector 컬럼 추가 + CONSTRUCTION 설정
- `ALTER TABLE users ADD COLUMN IF NOT EXISTS sector TEXT DEFAULT 'INDUSTRY'`
- `UPDATE users SET sector = 'CONSTRUCTION' WHERE phone = '01047758888'` (심태왕)

### auth.py v3.5.0 — PWA OTP 인증 API
- `POST /auth/send-otp` — OTP 발송 (개발용 dev_otp 응답 포함)
- `POST /auth/verify-otp` — OTP 검증 → sector 포함 사용자 정보 반환
- PWA 로그인 시 sector=CONSTRUCTION → construction_inspect.html 라우팅

---

## 다음 세션 작업 예정

- safe.taieng.co.kr 작업자 대시보드 페이지 구성
- law engine → auto-schedule 파이프라인 연결
- SMS 실제 발송 연동 (SENS/Solapi)
- otp_store 테이블 DDL 추가
