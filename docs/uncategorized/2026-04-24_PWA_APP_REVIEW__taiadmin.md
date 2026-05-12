# TAI Safe 작업자 PWA 전체 점검 리포트

- **점검일**: 2026-04-24
- **점검 범위**: `tadmin/full-version/app/` (21개 파일, 총 ~513KB) + 상위 `firebase-messaging-sw.js`
- **배포 URL**: https://safe.taieng.co.kr/app/index.html (정상 응답 확인)
- **점검 방법**: GitHub MCP 소스 읽기 + 배포 URL fetch + 프로젝트 시안(`tai_forklift_check_ui_html.html`) 대조

---

## 1. 심각도별 요약

| 등급 | 개수 | 핵심 주제 |
|---|---|---|
| 🔴 P0 치명 | 6건 | 긴급신고·이상신고 실패 은폐, 사진 데이터 유실, 인증 헤더 누락, FCM SW 잘못된 URL, 목업 데이터 혼입, 카메라 모듈 단절 |
| 🟠 P1 높음 | 11건 | 로그인 가드 부재, 오프라인 큐 인증 누락, PDF 내보내기 미구현, i18n 파편화, SW precache 부족, 언어 감지 없음 |
| 🟡 P2 중간 | 12건 | 하드코딩 locale, confirm/alert UX, 강제 geolocation 요청, 서명 캔버스 이중 초기화, 로그아웃 토큰 잔존 등 |
| 🔵 P3 정리 | 8건 | test.txt 잔존, hero-sub 격려문 i18n 미적용, 통계 계산 단순화, "완료율 100%" 고정 등 |

---

## 2. 🔴 P0 치명적 이슈 (즉시 수정 필요)

### P0-1. 긴급신고가 서버 실패를 은폐함 — `emergency.html`

```js
try { await fetch(API+'/emergency/report', ...); } catch(e){}
// 실패해도 그대로 done 화면 표시
document.getElementById('reportNum').textContent = 'EMG-'+Date.now().toString().slice(-6);
```

- `fetch` 실패해도 사용자에게 "신고 접수 완료"가 뜸 — 실제로는 서버 전송 실패
- 신고번호는 `Date.now()` 클라이언트 생성 → 서버 DB와 매칭 불가
- `Authorization` 헤더 없음
- 재시도 큐(오프라인 저장) 없음
- **사람 목숨이 걸린 기능이 가장 취약함.** 성공 여부 표시 + 오프라인 큐 + 서버 발급 번호 필요

### P0-2. 이상신고도 동일 패턴 — `report.html`

- Base64 사진 3장을 JSON body에 그대로 전송 → 수 MB 페이로드, 413 위험
- `Authorization` 없음
- fallback으로 `construction/sites/{site_id}/inspections` 재시도하지만 둘 다 실패해도 "접수 완료"
- 신고번호 `RPT-${Date.now()}` 클라이언트 생성

### P0-3. 사진 데이터 유실 — `inspect.html`

```js
const items = _items.map(it => ({
  name: it.name,
  result: _results[it.id]?.val || 'ok',
  memo: _results[it.id]?.memo || '',
  photo_count: (_results[it.id]?.photos || []).length  // 개수만 전송
}));
```

- 사진을 Base64로 localStorage에 쌓다가 서버 제출 body에는 `photo_count`만 보냄 — 사진 파일 자체는 서버로 안 감
- 작업자가 이상 발견 시 찍은 증거 사진이 서버에 저장 안 됨 → **법적 증빙 불가**
- iOS localStorage 5~10MB 쿼터에 Base64 사진 몇 장 쌓이면 초과

### P0-4. FCM SW 알림 클릭 URL이 404 — `firebase-messaging-sw.js`

```js
let url = 'https://safe.taieng.co.kr/html/horizontal-menu-template/worker-check.html';
```

- 이 경로는 현재 구조에 존재하지 않음. 백그라운드 푸시 알림 클릭 시 404
- `/app/index.html`로 수정해야 함
- Firebase config가 `index.html`과 이중 하드코딩 (키 유출 시 전체 갱신 필요)

### P0-5. 데모/목업 데이터가 프로덕션에 혼입 — `notifications.html`, `history.html`

- **notifications.html**: 첫 방문자에게 "라인 3 압축기 오일 누유 — 조치 완료 확인 필요" 같은 가짜 알림이 자동 생성됨. 서버 응답 후에도 `_notifs.filter(n=>n.id.startsWith('n'))`로 데모 알림이 섞임
- **history.html**: 서버 응답 0개면 8건 가짜 이력 자동 생성 (`hist_demo_name`)
- 프로덕션에서 사용자가 혼란을 겪고 TAI Safe 신뢰도 훼손
- 반드시 `if (!_notifs) _notifs = [];` (빈 배열)로 교체

### P0-6. camera.html과 inspect.html이 단절됨

- `inspect.html`의 `openCamera()`는 `<input type="file" capture>`만 호출 → `camera.html`은 참조 안 됨
- `camera.html`은 `sessionStorage` 기반 자체 뷰파인더인데 어디서도 호출되지 않음
- 사용 안 되는 고립된 파일이거나, 연결이 누락된 상태. 정리 또는 연결 필요

---

## 3. 🟠 P1 높은 우선순위 이슈

### P1-1. 로그인 가드 없음 (inspect, report, tbm, emergency 등 거의 전부)

```js
const user = JSON.parse(localStorage.getItem('tai_user') || '{}');
```

- `tai_user` 없어도 `{}`로 진행. `inspect.html?schedule_id=xxx` 직접 호출로 비로그인 접근 가능
- `_user.worker_id` 없어도 계속 진행되어 API로 null 전송
- 공통 `requireAuth()` 유틸 필요

### P1-2. access_token 저장 누락 + 오프라인 큐에 Authorization 없음

- `verifyOTP()` 응답을 `_user`로만 저장하고 `access_token`은 저장 안 하는 것으로 보임 (응답 body 구조 확인 필요)
- `loadOverdueBanner`, `loadHistory`만 Authorization 헤더 사용. 나머지 제출 API (`/worker-check/submit`, `/safety-reports`, `/tbm/sign`, `/emergency/report`)는 전부 헤더 없음
- inspect.html의 pending queue 재전송도 헤더 없음 → 401 반복 실패

### P1-3. PDF 내보내기 미구현 — `history.html`

```js
function exportPDF() { showToast(t('hist_pdf_wip')); }  // "준비 중"
```

- `index.html` 메뉴에서 "월별 점검기록부 · PDF 내보내기"라고 광고하는데 실제 기능 없음
- `i18n.js`에서도 `menu_history_sub: '월별 점검기록부 · PDF 내보내기'` 문구 노출
- 소비자 기대와 실제 동작 불일치 — 법령진단 pipeline 소비자 전달 문제와 동일 패턴

### P1-4. i18n 파편화 (emergency/report/qr/history/profile/notifications/install)

7개 페이지가 각자 `EM_EXT`, `REPORT_EXT`, `QR_EXT`, `HIST_EXT`, `PROFILE_EXT`, `NOTIF_EXT`, `INST_EXT`를 자체 선언해서 런타임에 `TAI_I18N`에 병합. 신규 언어 추가 시 8군데 수정 필요. i18n.js 단일 파일로 통합해야 함.

### P1-5. SW precache 부실 — `sw.js`

```js
const PRECACHE_URLS = ['/app/manifest.json', '/app/sw.js'];
```

- HTML/JS/아이콘 precache 없음 → 오프라인 첫 진입 실패
- `i18n.js`, 주요 HTML 20개, 아이콘 precache 필요
- jsQR 라이브러리는 외부 CDN 동적 로드 → 오프라인 QR 스캔 불가

### P1-6. 언어 자동 감지 없음 — `i18n.js`

```js
function getLang() {
  const stored = localStorage.getItem('tai_lang_code');
  return stored && TAI_I18N[stored] ? stored : 'ko';
}
```

- `navigator.language` 감지 없이 무조건 `ko`부터 시작. 베트남 작업자 첫 방문 시 한국어 화면
- 최초 호출 시 브라우저 locale로 default 설정 로직 필요

### P1-7. 로그아웃이 불완전

- `index.html` / `profile.html` 모두 `localStorage.removeItem('tai_user')`만 수행
- `tai_sign`, `tai_activities`, `tai_attendance`, `tai_fcm_token`, `tai_notifs`, `access_token` 모두 잔존
- 다음 로그인 사용자가 이전 사용자의 서명/이력 보게 됨 — **개인정보 누수 가능**

### P1-8. LocalStorage pending 큐 무한 축적 — `inspect.html`

```js
localStorage.setItem('tai_check_pending_'+Date.now(), JSON.stringify(body));
```

- 여러 번 실패하면 무한 누적. TTL/최대 개수 없음
- 키 prefix 방식이라 LocalStorage 크기 제한(5~10MB) 초과 시 조용히 실패

### P1-9. `html,body{overflow:hidden}`으로 스크롤 제한 — `index.html`

- iOS에서 키보드 올라올 때 레이아웃 밀림 현상 발생 가능
- 탭 전환 구조는 OK지만 auth 페이지의 `overflow-y:auto`는 예외. 일관성 부족

### P1-10. Firebase config + VAPID_KEY 하드코딩 이중 관리

- `index.html`에 직접 노출 + `firebase-messaging-sw.js`에 복제
- 도메인 제한이 Firebase Console에 설정돼야 안전 (확인 필요)
- 한 곳에서 관리 + 환경변수/config.js 분리 권장

### P1-11. test.txt 잔존 (60B)

- `TAI Safe deployment test - app folder, timestamp: 2026-04-09`
- 프로덕션에서 제거

---

## 4. 🟡 P2 중간 우선순위 이슈

| # | 파일 | 이슈 |
|---|---|---|
| P2-1 | inspect/tbm/emergency | `toLocaleTimeString('ko-KR')` 하드코딩 — 다국어에서 한글 출력 |
| P2-2 | tbm/qr_scan/camera | `confirm()`, `alert()` 사용 — 모바일 PWA 부적합 native dialog |
| P2-3 | report/emergency | 페이지 진입 즉시 geolocation 권한 요청 — 공격적 UX |
| P2-4 | index.html | 서명 캔버스 이중 `getContext` + `scale` 호출 |
| P2-5 | emergency.html | `selectType()` 클릭 즉시 `sendEmergency()` 자동 실행 — 오탐 터치 발송 가능 |
| P2-6 | qr_scan.html | jsQR 1회 스캔 후 `scanning=false` 고정, 재스캔 시 새로고침 필요 |
| P2-7 | report.html | '매우 긴급' 선택 시 emergency.html 이동하며 입력 내용 전부 손실 |
| P2-8 | notifications.html | `markAllRead` 시 서버 API 호출 없음 — 로컬에서만 읽음 처리 |
| P2-9 | profile.html | 서명 등록 메뉴가 `index.html`로 이동 (탭 스위치 아님, 혼란) |
| P2-10 | install.html | OS 자동 감지 없이 수동 탭 — iOS 사용자가 Android 가이드부터 봄 |
| P2-11 | inspect.html | "전체 정상" 버튼 사용 후 되돌리기 불가 |
| P2-12 | history.html | "완료율"이 `thisMonth.length ? '100%' : '0%'` 고정 — 계산 로직 없음 |

---

## 5. 🔵 P3 정리 이슈

1. `index.html`의 "오늘 점검 시작", "장갑 끼기 전에 끝납니다", "최근 활동", "수고하셨습니다 🙏" 등 hero-sub 문구 i18n 미적용
2. `profile.html`의 "Language / 语言 / ..." 다국어 서브타이틀에 한국어 누락
3. 모든 페이지의 빈 활동 안내문 i18n 미적용 다수
4. `tai_activities` 로컬 10개 제한으로 통계(`profile.html`의 점검/TBM/교육 수) 부정확
5. `camera.html` 하드코딩 한국어 전체 (i18n 미적용)
6. `emergency.html` 언어팩 품질 낮음 — km(크메르어) 일부 번역 어색
7. PWA `protocol_handlers: [{ "protocol": "tai" }]` 등록됐으나 실제 사용처 없음 (미래 확장 OK)
8. 여러 페이지에서 `History API` 사용 안 하고 `location.href`로 새 페이지 로드

---

## 6. 페이지별 1줄 요약

| 파일 | 크기 | 상태 | 핵심 이슈 |
|---|---|---|---|
| index.html | 46KB | 작동 | Firebase 하드코딩, 서명 탭 구조 복잡 |
| manifest.json | 2.4KB | ✅ 양호 | shortcuts + screenshots 잘 구성 |
| sw.js | 4.5KB | ⚠️ | Precache 부실, Stale-While-Revalidate 권장 |
| i18n.js | 86KB | 작동 | 페이지 EXT 파편화 심각 |
| inspect.html | 22.9KB | ⚠️ | 사진 데이터 서버 미전송 (P0) |
| construction_inspect.html | 31.8KB | (미상세) | 패턴상 인증/photo 이슈 동일 예상 |
| report.html | 31.4KB | 🔴 | 실패 은폐 + 사진 413 위험 |
| emergency.html | 16KB | 🔴 | 가장 취약. 서버 실패 은폐 |
| tbm.html | 16.7KB | ⚠️ | 인증 누락, 실패 처리 취약 |
| corrective.html | 25KB | (미상세) | 패턴상 유사 예상 |
| education.html | 24KB | (미상세) | 패턴상 유사 예상 |
| attendance.html | 16.6KB | (미상세) | 패턴상 유사 예상 |
| work_request.html | 37.2KB | (미상세) | 가장 큼. 별도 점검 필요 |
| camera.html | 9.6KB | 🔴 | 호출처 없음 (고립), i18n 미적용 |
| qr_scan.html | 17.2KB | 작동 | jsQR CDN 의존, 1회 스캔 제한 |
| notifications.html | 16.3KB | 🔴 | 목업 알림 프로덕션 혼입 |
| history.html | 16.8KB | 🔴 | 목업 데이터 + PDF 미구현 |
| profile.html | 16.9KB | ⚠️ | 로그아웃 데이터 잔존 |
| install.html | 27.7KB | 작동 | OS 자동감지 없음 |
| risk.html | 26KB | (미상세) | 패턴상 유사 예상 |
| test.txt | 60B | 🔵 | 삭제 필요 |
| firebase-messaging-sw.js | 1.7KB | 🔴 | 알림 클릭 URL 404 |

---

## 7. forklift 시안 vs 현행 inspect.html 비교

**결론: 현행 inspect.html이 훨씬 낫다. 시안은 버리는 게 맞음.**

| 항목 | forklift 시안 | 현행 inspect.html | 판단 |
|---|---|---|---|
| 레이아웃 | 데스크탑 그리드 (1.15fr 0.85fr) | 모바일 세로 | ✅ 현행 |
| 버튼 단계 | 3단계 (정상/이상/보류) | 2단계 (OK/이상) | ✅ 현행 (보류는 빈 상태가 대신) |
| 일괄 처리 | 없음 | "전체 정상" 한 번 버튼 | ✅ 현행 |
| 위험 태그 | 전도/충돌/추락/협착 | risk_collision 등 국제화된 태그 | ✅ 현행 |
| 오프라인 큐 | 없음 | tai_check_pending_* | ✅ 현행 |
| 자동 경고 | 우측 패널 | 별도 페이지(report.html) 분리 | = |
| 누적 데이터 | 우측 패널 | 별도 페이지(history.html) 분리 | = |

시안에서 가져올 만한 것 1가지: 위험 태그 배지 대비 강화(gray/red) — 현행 `.item-risk`도 있으나 덜 눈에 띔.

---

## 8. 수정 우선순위 제안

### 이번주 내 (P0)
1. `emergency.html` + `report.html` + `tbm.html` + `inspect.html` submit에 (a) Authorization 헤더 추가, (b) 실패 시 오프라인 큐 저장 + 사용자에게 실패 표시 통일
2. `inspect.html` 사진 업로드: `FormData`로 분리 또는 Supabase Storage 직접 업로드 → 제출 body에 URL만 포함
3. `firebase-messaging-sw.js` URL을 `/app/index.html`로 수정
4. `notifications.html` + `history.html` 데모 데이터 완전 제거 (또는 `?demo=1` 쿼리로 격리)
5. `camera.html` 연결하거나 삭제 — 현재 dead code
6. `test.txt` 삭제

### 2주 내 (P1)
7. 공통 `requireAuth()` + `apiFetch(url, options)` 유틸 (Authorization 자동 주입 + 401 처리 + 오프라인 큐)
8. `sw.js` precache에 주요 HTML + i18n.js + 아이콘 추가
9. 페이지별 i18n EXT들을 `i18n.js` 본체로 통합
10. 로그아웃 시 모든 `tai_*` 키 삭제 + `access_token` + `tai_fcm_token` 삭제
11. `getLang()`에 `navigator.language` 최초 감지 추가

### 여유 있을 때 (P2/P3)
12. `confirm`/`alert` → 커스텀 모달 전환
13. locale 하드코딩 제거 (`toLocaleTimeString`에서 인자 제거 → 브라우저 locale)
14. PDF 내보내기 실제 구현 (jsPDF 또는 서버 엔드포인트)
15. `install.html` OS 자동 감지
16. `emergency.html` 유형 선택 시 자동 발송 제거, 확인 버튼 명시적 요구

---

## 9. 미상세 파일 후속 점검 필요

1차 샘플링에서 패턴이 파악돼 본 리포트에서 상세 분석하지 않은 파일:

- `construction_inspect.html` (31.8KB) — 건설 모드 점검. inspect.html과 동일 패턴 예상
- `corrective.html` (25KB) — 시정조치 확인
- `education.html` (24KB) — 교육 이수 서명
- `risk.html` (26KB) — 위험성평가
- `attendance.html` (16.6KB) — 출퇴근/현장 출입
- `work_request.html` (37.2KB) — 작업 허가. 가장 큰 파일. 별도 점검 권장

2차 점검 시 중점 확인: (a) Authorization 헤더 유무, (b) 실패 시 사용자 피드백, (c) 사진 업로드 처리, (d) i18n EXT 추가 파편화 여부.

---

**담당자**: 심태왕  
**리포트 작성자**: Claude (AI 점검)  
**다음 단계**: 위 우선순위 순서대로 Cursor 작업지시서 작성 예정