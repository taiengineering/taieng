# Cursor 작업지시서: 알림센터 Nav 통합 + 모바일 복제

작성일: 2026-05-17
대상: tai-admin 레포

---

## 배경

Notification Engine Phase 1 완료. notification-center.html 페이지 + notification.js v2.0 (API 연동) 완료.
현재 미완료: **사이드바 메뉴 항목 추가** + **모바일 레포 복제**

---

## TASK 1: menu-tadmin.js 사이드바 알림센터 항목 추가

### 대상 파일
```
tadmin/full-version/assets/js/tai/menu-tadmin.js
```

### 작업

메뉴 정의 배열에 알림센터 항목 추가.

검색 문자열: `notification-list` 또는 `알림` 또는 `alert-list`

기존에 `notification-list.html` 또는 `alert-list.html` 링크가 있으면 그 근처에 추가.
없으면 대시보드/보고 섹션 하단에 추가.

### 추가할 항목

```javascript
{
  label: '알림센터',
  icon: 'ti ti-bell',
  url: 'notification-center.html'
}
```

### 주의
- `notification-list.html` 항목이 기존에 있으면 URL을 `notification-center.html`로 **교체**
- 아이콘: `ti ti-bell` (기존 Tabler Icons 사용)
- 라벨: `알림센터`

---

## TASK 2: nav-tadmin.js 헤더 알림 벨 링크 확인

### 대상 파일
```
tadmin/full-version/assets/js/tai/nav-tadmin.js
```

### 작업

헤더 네비게이션 바에 `#notif-bell` 요소가 존재하는지 확인.
존재하면 클릭 시 `notification-center.html`로 이동하는지 확인.
(`notification.js` v2.0이 이미 연결함 — 추가 작업 불필요할 수 있음)

---

## TASK 3: 모바일 PWA 레포 알림센터 복제

### 대상
```
site/full-version/html/vertical-menu-template-no-customizer/
```

### 작업

1. `notification-center.html`을 위 경로에 복제
2. `notification-list.html`이 있으면 동일 redirect 처리:
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
3. `site/full-version/assets/js/tai/menu-tadmin.js`에도 동일 항목 추가
4. `site/full-version/assets/js/tai/notification.js`가 존재하면 `tadmin` 버전과 동일하게 업데이트 (API 연동 v2.0)

---

## TASK 4: notification.js 모바일 레포 버전 동기화

### 대상 파일
```
site/full-version/assets/js/tai/notification.js
```

### 작업

`tadmin/full-version/assets/js/tai/notification.js` v2.0 내용을 그대로 복사.

핵심 변경점:
- mock 데이터 → 실제 API 호출 (`/notification-inbox/feed`, `/notification-inbox/unread-count`)
- `notification-list.html` → `notification-center.html` 링크
- 60초 주기 badge refresh

---

## 절대 규칙

1. **Runtime 코드 수정 금지** — tai-api 레포 수정 없음
2. **파일 400줄 초과 시 Router/Service/Schema 분리** (tai-admin은 해당 없음)
3. **Bootstrap body 테마 클래스 확인** — `home-2`~`home-6` body 클래스가 `tai-brand.css`를 override하므로 새 페이지에 적용 금지
4. `tai-brand.css` 명시적 링크 확인
5. notification-center.html은 standalone 페이지 (Bootstrap5 CDN + 자체 CSS) — Vuexy 테마 의존 없음

---

## 성공 기준

1. 사이드바에 "알림센터" 메뉴 항목 표시
2. 클릭 시 notification-center.html 이동
3. 모바일 레포에 notification-center.html 존재
4. 모바일 notification.js v2.0 (API 연동) 적용
5. 기존 페이지 영향 없음
