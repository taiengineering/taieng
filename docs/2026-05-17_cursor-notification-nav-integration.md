# Cursor 작업지시서: 알림센터 Nav 통합 + 모바일 복제 + notification.js v2.0

작성일: 2026-05-17
대상: tai-admin 레포
우선순위: P1

---

## 배경

Notification Engine Phase 1 완료.
- `notification-center.html` 페이지 생성 완료 (tadmin horizontal-menu)
- `notification.js` v2.0 (API 연동) tadmin에 적용 완료
- `notification-list.html` → redirect 처리 완료 (tadmin)

미완료: 사이드바 메뉴 + 헤더 벨 링크 + 모바일 레포 + site horizontal 복제

---

## TASK 1 — `menu-tadmin.js` (tadmin)

### 대상 파일
```
tadmin/full-version/assets/js/tai/menu-tadmin.js
```

### 작업

사이드바에 알림센터 항목 추가.

검색: `notification-list` 또는 `alert-list` 또는 `알림`

### 추가할 항목
```javascript
{
  label: '알림센터',
  icon: 'tabler-bell',   // ti ti-bell 또는 tabler-bell (기존 패턴 따라감)
  url: 'notification-center.html'
}
```

### 규칙
- `notification-list.html` 항목이 있으면 URL을 `notification-center.html`로 **교체**
- 메뉴 노출 조건: `Lv >= 1` (안전관리자 이상)
- 위치: 기존 알림 관련 메뉴 근처, 없으면 대시보드 섹션 하단

---

## TASK 2 — `nav-tadmin.js` (tadmin)

### 대상 파일
```
tadmin/full-version/assets/js/tai/nav-tadmin.js
```

### 작업

1. **드롭다운 「전체 알림 보기」 링크** → `notification-center.html`로 변경
   - 검색: `notification-list.html` 또는 `전체 알림`
   - 교체: `notification-center.html`

2. **`notification.js` 팝업 하단 링크 확인** (이미 v2.0에서 변경됨 — 확인만)
   - 파일: `tadmin/full-version/assets/js/tai/notification.js`
   - 확인: `notification-center.html` 링크 존재 여부

3. **벨 Ctrl/Cmd+클릭 시 알림센터 바로 이동**
   - `#notif-bell` 요소에 `href="notification-center.html"` 속성 추가 (또는 `<a>` 태그로 래핑)
   - 일반 클릭: 기존 팝업 동작 유지
   - Ctrl/Cmd+클릭: 새 탭에서 `notification-center.html` 열림

---

## TASK 3 — site `vertical-menu-template-no-customizer`

### 대상 경로
```
site/full-version/html/vertical-menu-template-no-customizer/
```

### 작업

#### 3-1. notification-center.html 복제
- `tadmin/full-version/html/horizontal-menu-template/notification-center.html` 복사
- 작업자용 네비 링크 조정: `worker-home.html`, `schedule-review.html` 등 site 레포 기준 경로

#### 3-2. notification-list.html redirect
```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8"/>
  <meta http-equiv="refresh" content="0;url=notification-center.html"/>
  <title>알림 | TAI Safe</title>
</head>
<body>
  <p>알림센터로 이동 중... <a href="notification-center.html">여기를 클릭하세요</a></p>
</body>
</html>
```

#### 3-3. menu-tadmin.js (site)
- 파일: `site/full-version/assets/js/tai/menu-tadmin.js`
- 알림센터 메뉴 항목 추가 (TASK 1과 동일 패턴)
- 작업자 탭에 `notification-center.html` 연결

#### 3-4. 기존 페이지 링크 갱신
- `worker-home.html` — 알림 관련 링크가 있으면 `notification-center.html`로 교체
- `safety-dashboard.html` — 알림 관련 링크가 있으면 `notification-center.html`로 교체
- 검색: `notification-list.html` → 교체: `notification-center.html`

#### 3-5. site horizontal-menu-template 복사
```
site/full-version/html/horizontal-menu-template/
```
- `notification-center.html` 복사
- `notification-list.html` redirect 복사
- 기존 벨 링크 호환 보장

---

## TASK 4 — `notification.js` v2.0 동기화

### 대상 파일
```
site/full-version/assets/js/tai/notification.js
```
(파일이 없으면 신규 생성)

### 작업

`tadmin/full-version/assets/js/tai/notification.js` v2.0 내용을 그대로 복사.

### 핵심 변경점 (Mock → API)
- Mock `mockItems()` 제거
- `GET /notification-inbox/feed?limit=5` — 팝업 Feed 로드
- `GET /notification-inbox/unread-count` — Badge 갱신
- 링크: `notification-list.html` → `notification-center.html`
- 30초 자동 갱신 (`setInterval`, 60000 → 30000 변경)

### API 엔드포인트 정리

| 용도 | Method | Path |
|---|---|---|
| Feed 목록 | GET | `/notification-inbox/feed?limit=5` |
| 미읽음 수 | GET | `/notification-inbox/unread-count` |
| 읽음 처리 | POST | `/notification-inbox/{id}/read` |
| Timeline | GET | `/notification-inbox/timeline/{trace_id}` |

### 인증
- `localStorage.getItem('access_token')` → `Authorization: Bearer {token}`
- Token 없으면 인증 없이 호출 (공개 Feed)

---

## 추가 (tadmin horizontal)

`tadmin/full-version/html/horizontal-menu-template/` 내:
- `notification-center.html` — 이미 존재 ✅
- `notification-list.html` — 이미 redirect ✅
- 메뉴/네비 URL이 동작하도록 TASK 1, 2 완료 필요

---

## 절대 규칙

1. **tai-api 레포 수정 금지** — Runtime 코드 변경 없음
2. **Bootstrap body 테마 클래스** — `home-2`~`home-6` body 클래스가 `tai-brand.css`를 override → 새 페이지에 적용 금지
3. `tai-brand.css` 명시적 링크 확인
4. notification-center.html은 standalone (Bootstrap5 CDN + 자체 CSS) — Vuexy 테마 의존 없음
5. 파일 수정 시 기존 기능 영향 최소화

---

## 확인 방법

1. **tadmin 로그인** → 사이드바 「알림센터」 클릭 → `notification-center.html` 이동
2. **헤더 벨 클릭** → 팝업 → 「알림센터 열기」 → `notification-center.html` 이동
3. **벨 Ctrl+클릭** → 새 탭에서 `notification-center.html` 열림
4. **site 작업자** → vertical-menu에서 알림센터 진입 가능
5. **벨 배지** → API 미읽음 수와 일치 (`user_id` / `company_id` in localStorage 필요)
6. `notification-list.html` 직접 접근 → 자동 redirect → `notification-center.html`

---

## 성공 기준

| # | 기준 | 대상 |
|---|---|---|
| 1 | tadmin 사이드바에 「알림센터」 표시 | menu-tadmin.js (tadmin) |
| 2 | 헤더 벨 → 팝업 → 「알림센터 열기」 동작 | nav-tadmin.js + notification.js |
| 3 | Ctrl/Cmd+벨 클릭 → 새 탭 알림센터 | nav-tadmin.js |
| 4 | site vertical-menu에 notification-center.html 존재 | site 레포 |
| 5 | site horizontal-menu에 notification-center.html 존재 | site 레포 |
| 6 | site notification.js v2.0 (API 연동) | site/assets/js/tai/ |
| 7 | 모든 notification-list.html → redirect | 전체 |
| 8 | worker-home, safety-dashboard 링크 갱신 | site 레포 |
| 9 | 기존 페이지 영향 없음 | 전체 |
