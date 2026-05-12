# TAI Safe PWA 앱 세션 작업내역
> 최종 업데이트: 2026-04-10 | 윈도우: 기획/프론트 통합창
> 레포: taiengineering/tai-admin | 경로: tadmin/full-version/app/

---

## 세션 #1 완료 작업 (초기 구축)

| 항목 | 내용 | 커밋 |
|------|------|------|
| 탭바 Floating Pill 시도 후 원복 | 전통 전체너비 탭바 유지 | - |
| i18n.js 신규 생성 | 7개 언어팩 (ko/en/zh/vi/ne/km/tl) | c006a2d |
| 서명체크 알럿 3중 레이어 | tbm/risk/education 페이지 | b46cdbd |
| sw.js HTML Network First | v1.3 캐시 전략 개선 | ce7578b |
| app_subtitle 용어 변경 | '현장 안전관리 앱' | f0b7742 |

## 세션 #2 완료 작업 (버그수정 + 기능개선)

| # | 항목 | 파일 | 커밋 |
|---|------|------|------|
| 1 | OTP 000000 보안 제거 | index.html | bd32cb6 |
| 2 | 이상 버튼→홈 튕김 버그 | inspect.html | bd32cb6 |
| 3 | submit 무음 실패 → 로컬백업+재전송 | inspect.html | bd32cb6 |
| 4 | 전체 정상 원탭 버튼 | inspect.html | bd32cb6 |
| 5 | 버튼 터치 타겟 52px | inspect.html, index.html | bd32cb6 |
| 6 | 사진 첨부 (file input 직접 실행) | inspect.html | bd32cb6 |
| 7 | TBM factory_id 기반 경로 추가 | tbm.html | bd32cb6 |
| 8 | 완료율 현실화 (로컬 활동 기반) | index.html | afd3186 |
| 9 | TBM "-" → "완료 ✓" / "미완료" 표시 | index.html | afd3186 |
| 10 | 건설 점검: 전체양호버튼+터치타겟+submit로컬백업+사진첨부 | construction_inspect.html | afd3186 |
| 11 | i18n 200+ 키 확장, inspect/tbm t() 전면 적용 | i18n.js | dc357f7 |

---

## 현재 앱 파일 상태

```
tadmin/full-version/app/
├── index.html              — 홈+인증, 탭바, 서명등록 (OTP보안패치, 완료율현실화, TBM상태표시)
├── inspect.html            — 작업전점검 (전체정상버튼, 이상버그수정, 사진첨부, 로컬백업)
├── construction_inspect.html — 건설점검 (전체양호버튼, 사진첨부, 로컬백업)
├── tbm.html                — TBM서명 (factory_id경로, 터치타겟)
├── risk.html               — 위험성평가 (서명체크 알럿)
├── education.html          — 교육이수확인 (서명체크 알럿)
├── report.html             — 이상신고
├── corrective.html         — 시정조치확인
├── work_request.html       — 작업요청(허가)
├── history.html            — 점검이력
├── notifications.html      — 알림함
├── attendance.html         — 출퇴근/현장출입
├── profile.html            — 내정보/설정 (7개 언어 선택 UI)
├── qr_scan.html            — QR현장출입
├── emergency.html          — 긴급신고
├── install.html            — PWA설치안내
├── camera.html             — 카메라 (사용 안 함 — file input으로 대체됨)
├── i18n.js                 — 7개 언어팩 200+ 키
├── sw.js                   — 서비스워커 v1.3 (HTML Network First)
└── manifest.json           — PWA 설정
```

---

## i18n 현황 및 누락 키 목록

### 현재 커버된 페이지 (i18n 완료)
- ✅ index.html (홈/인증/서명) — 전체 t() 적용
- ✅ inspect.html — 전체 t() 적용
- ✅ tbm.html — 전체 t() 적용
- ⚠️ construction_inspect.html — 하드코딩 한글 다수 (이번 세션 미처리)

### 미완료 페이지 (하드코딩 한글 다수)
- ❌ report.html
- ❌ corrective.html
- ❌ risk.html
- ❌ education.html
- ❌ work_request.html
- ❌ profile.html
- ❌ notifications.html
- ❌ history.html
- ❌ attendance.html
- ❌ qr_scan.html
- ❌ emergency.html
- ❌ install.html

### i18n.js에 추가 필요한 키 범주 (다음 세션 할 일)

```javascript
// report 페이지
report_type_accident, report_type_near_miss, report_type_hazard,
report_type_equipment, report_type_fire, report_type_chemical, report_type_other,
report_location_placeholder, report_desc_placeholder,
report_severity_label, report_severity_low/medium/high/critical,
report_photo_add, report_submit_confirm, report_done_msg, report_empty_warn,

// risk 페이지
risk_page_title, risk_meeting_label, risk_loading, risk_content_title,
risk_confirm_text, risk_sign_label, risk_submit, risk_done_title, risk_done_msg,
risk_no_sign_alert, risk_need_confirm,

// education 페이지
edu_page_title, edu_meeting_label, edu_loading, edu_content_title,
edu_confirm_text, edu_sign_label, edu_submit, edu_done_title, edu_done_msg,

// work_request 페이지
work_req_page_title, work_req_type_label, work_req_type_hot/confined/height/electrical/excavation/other,
work_req_location/date/time/desc/hazard/measure_label,
work_req_submit, work_req_done_title, work_req_done_msg,
work_req_location/desc_placeholder,

// corrective 페이지
corrective_loading, corrective_status_pending/progress/done,
corrective_detail_title, corrective_photo_label, corrective_confirm_btn,
corrective_done_toast, corrective_deadline, corrective_assignee, corrective_reporter,

// profile 페이지
profile_title, profile_lang_title, profile_notif_title,
profile_notif_inspect/tbm/corrective/emergency,
profile_save, profile_save_toast, profile_version,

// notifications 페이지
notif_type_inspect/tbm/corrective/emergency,
notif_read, notif_unread,
notif_time_just/min/hour/day,

// attendance 페이지
attendance_mode_in/out, attendance_site/time/gps_label,
attendance_confirm_in/out, attendance_done_in/out,
attendance_history_title, attendance_empty,

// qr_scan 페이지
qr_scanning, qr_success, qr_fail, qr_result_label,
qr_confirm_btn, qr_manual_placeholder,

// emergency 페이지
emergency_type_label, emergency_type_injury/fire/fall/collapse/chemical/other,
emergency_location_label, emergency_call_btn, emergency_manager_btn,
emergency_submit, emergency_done, emergency_location_placeholder,

// history 페이지
history_month_label, history_total, history_bad/ok_count,
history_no_data, history_pdf_generating, history_pdf_done,

// install 페이지
install_step1/2/3/4_title, install_step1/2/3/4_desc,
install_ios_guide, install_android_guide,
```

---

## 다음 세션 작업 순서 (최우선)

1. **i18n.js 대규모 확장** — 위 누락 키들을 7개 언어로 추가
2. **각 HTML 파일 t() 적용** — report, corrective, risk, education, work_request, profile, notifications, history, attendance, qr_scan, emergency, install 순서로
3. **construction_inspect.html t() 적용** — 이번 세션 미처리
4. **법령→점검 파이프 연결** — work_schedules 자동생성 → 배정 → 알림

---

## 다음 세션 시작 프롬프트

```
safe.taieng.co.kr/app/ PWA 앱 작업 중.
레포: taiengineering/tai-admin, 경로: tadmin/full-version/app/
docs/TAI_Frontend_MEMORY_20260410.md 참조.

[이번 세션 목표] 전체 앱 페이지 i18n 한글 번역 완성
현재 i18n.js(7개언어)는 inspect/tbm/index만 완전 적용됨.
나머지 12개 페이지(report/corrective/risk/education/work_request/profile/notifications/history/attendance/qr_scan/emergency/install)의
모든 하드코딩 한글 텍스트를 i18n.js 키로 추가하고, 각 HTML에 data-i18n 또는 t() 적용.

작업 순서:
1. i18n.js — 누락 키 전체 추가 (7개 언어 번역 포함)
2. report.html → corrective.html → risk.html → education.html → work_request.html
3. profile.html → notifications.html → history.html → attendance.html
4. qr_scan.html → emergency.html → install.html → construction_inspect.html

SHA 없이 push_files 사용. 파일당 한 번에 처리.
```

---

## 기술 메모

### API 엔드포인트
- `POST /auth/send-otp` — OTP 발송
- `POST /auth/verify-otp` — OTP 검증 (000000 마스터키 제거됨)
- `POST /worker-check/submit` — 점검 결과 저장
- `POST /tbm/sign` — TBM 서명
- `GET /inspection-sets/{id}/items` — 점검 항목 로드
- `GET /inspection-set-items?factory_id={id}` — 공장별 항목

### 로컬스토리지 키
- `tai_user` — 로그인 사용자 정보
- `tai_sign` — 서명 DataURL
- `tai_activities` — 최근 활동 (홈 피드)
- `tai_lang_code` — 선택 언어 (ko/en/zh/vi/ne/km/tl)
- `tai_check_pending_*` — submit 실패 시 로컬 백업
- `tai_con_check_pending_*` — 건설 점검 submit 실패 백업
- `tai_fcm_token` — FCM 푸시 토큰
- `tai_notifs` — 로컬 알림 목록

### 배포
- Cloudflare Pages → `tadmin/full-version` 디렉토리
- main 브랜치 push → 자동 배포
- 배포 후 Ctrl+Shift+R 한 번 필요 (SW 업데이트)
