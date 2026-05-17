# Cursor 작업지시서: 알림 페이지 Vuexy 레이아웃 통일

작성일: 2026-05-17
대상: tai-admin 레포
우선순위: P0 (디자인 통일)

---

## 배경

최근 생성된 알림 관련 페이지들이 standalone(Bootstrap CDN + 자체 CSS)으로 되어 있어,
기존 페이지들과 디자인(탑바/푸터/사이드바 등)이 다릅니다.

기존 페이지 레퍼런스: `alert-list.html`, `factory-list.html`, `index.html` 등

---

## 수정 대상 파일

### tadmin (safe.taieng.co.kr 데스크톱)
1. `tadmin/full-version/html/horizontal-menu-template/notification-center.html`
2. `tadmin/full-version/html/horizontal-menu-template/notification-list.html` (이것은 redirect라 그대로)

### site (모바일 PWA)
3. `site/full-version/html/vertical-menu-template-no-customizer/notification-center.html`
4. `site/full-version/html/vertical-menu-template-no-customizer/notification-list.html` (redirect라 그대로)
5. `site/full-version/html/horizontal-menu-template/notification-center.html` (있으면)

---

## 작업 내용

### TASK 1: tadmin notification-center.html

**레퍼런스**: `tadmin/full-version/html/horizontal-menu-template/alert-list.html`

기존 alert-list.html의 레이아웃 구조를 그대로 사용하되, body 내용만 알림센터 콘텐츠로 교체.

확인해야 할 것:

1. **`<head>` 섹션** — alert-list.html과 동일한 CSS/Font 임포트
   - `core.css`, `demo.css`, `tabler-icons.css`, `node-waves.css`, `perfect-scrollbar.css`
   - `tai-brand.css` 링크 확인
   - `helpers.js`, `config.js`

2. **Navbar (`<nav>`)** — alert-list.html과 동일한 HTML 구조
   - `#notif-bell` + `#notif-badge` 요소 포함
   - 사용자 드롭다운, 검색, 등

3. **Menu (사이드바 또는 horizontal)** — `menu-tadmin.js`가 주입하는 `<ul class="menu-inner">` 영역

4. **Footer** — alert-list.html과 동일

5. **Core JS** — alert-list.html 하단 script 태그 동일
   - jquery, popper, bootstrap, node-waves, menu.js, main.js
   - `nav-tadmin.js`, `menu-tadmin.js`, `notification.js`

6. **Body content** — 현재 notification-center.html의 콘텐츠 (Health 위젯 + Feed + Settings + Timeline 모달) 유지

### 구체적 작업:

```
alert-list.html에서 복사:
  - <head> 전체 (title만 "알림센터 | TAI Safe"로 변경)
  - <body> ~ <div class="layout-wrapper"> ~ <nav> ~ <aside> ~ <div class="layout-page">
  - <footer> + 하단 <script> 전체

notification-center.html에서 유지:
  - <div class="container-xxl flex-grow-1 container-p-y"> 내부 콘텐츠 (Health + 탭 + Feed + Settings)
  - <div class="modal fade" id="timelineModal"> 모달
  - <style> 블록 (nc-health-grid, nc-feed-item 등)
  - 마지막 <script> 블록 (API 로직)
```

### 주의:
- `body` 태그에 `home-2`~`home-6` 클래스 절대 적용 금지
- `tai-brand.css` 링크 확인
- notification.js는 nav-tadmin.js에서 로드할 수 있으나, 명시적 링크도 OK

---

### TASK 2: site vertical notification-center.html

**레퍼런스**: `site/full-version/html/vertical-menu-template-no-customizer/worker-home.html`

worker-home.html의 레이아웃(세로 메뉴, 모바일 네비) 그대로 사용.

body 내용만 알림센터 콘텐츠로 교체.

동일한 작업: head/nav/menu/footer/scripts 동일화 + body content 유지

---

### TASK 3: site horizontal notification-center.html (있으면)

**레퍼런스**: site horizontal의 기존 페이지

TASK 2와 동일 작업.

---

## 절대 규칙

1. **tai-api 레포 수정 금지**
2. **콘텐츠 로직 변경 금지** — API 호출/렌더링 JS는 그대로 유지
3. **Bootstrap body 테마 클래스** — `home-2`~`home-6` 적용 금지
4. **`tai-brand.css` 명시적 링크 확인**
5. **기존 페이지 영향 없음**

---

## 확인 방법

1. safe.taieng.co.kr 로그인 → 알림센터 접속
2. **탑바** — 기존 페이지(alert-list 등)와 동일한 로고+벨+사용자 드롭다운
3. **사이드바/메뉴** — 기존 페이지와 동일하게 사이드바 렌더링
4. **푸터** — 기존 페이지와 동일
5. **콘텐츠** — Feed/Timeline/Settings/Health 정상 동작
6. **모바일(site)** — worker-home과 동일한 네비/푸터

---

## 성공 기준

| # | 기준 |
|---|---|
| 1 | tadmin notification-center의 탑바가 alert-list와 동일 |
| 2 | tadmin notification-center의 푸터가 alert-list와 동일 |
| 3 | tadmin notification-center의 사이드바가 alert-list와 동일 |
| 4 | site notification-center의 네비가 worker-home과 동일 |
| 5 | 콘텐츠 (Feed/Timeline/Settings/Health) 정상 동작 |
| 6 | 기존 페이지 영향 없음 |
