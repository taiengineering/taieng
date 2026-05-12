# Cursor 작업지시서: 작업자 웹앱 페이지 복사 + auth-guard 수정 (추가분)

## 배경
이전 작업지시서(`docs/WORKORDER_worker_routing.md`)에서 로그인 라우팅은 완료되었으나,
worker-home.html의 하단 탭바가 링크하는 페이지 2개가 `tadmin/` 경로에 없어 404 → auth-guard 리다이렉트로 버튼이 작동하지 않는 문제가 남아있습니다.

## 수정 내용 (3단계)

### 1단계: 페이지 복사 (2파일)

`site/full-version/html/vertical-menu-template-no-customizer/` 에서 아래 파일을 복사합니다:

**원본 → 대상:**
- `schedule-review.html` → `tadmin/full-version/html/horizontal-menu-template/schedule-review.html`
- `tbm-list.html` → `tadmin/full-version/html/horizontal-menu-template/tbm-list.html`

**복사 후 수정 사항:**
- 로그인 체크 리다이렉트 경로를 절대경로로 통일:
  - `../../html/horizontal-menu-template/auth-login-cover.html` → `/html/horizontal-menu-template/auth-login-cover.html`
- assets 경로는 동일하게 `../../assets/` 그대로 유지 (같은 depth이므로)

### 2단계: notification-list.html 플레이스홀더 생성

`tadmin/full-version/html/horizontal-menu-template/notification-list.html`

원본 `site/`에도 이 파일은 아직 없으므로, 간단한 플레이스홀더를 만듭니다.
worker-home.html과 동일한 스타일 기반으로:

```html
<!doctype html>
<html lang="ko" dir="ltr" data-skin="default">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
  <title>알림 | TAI Safe</title>
  <link rel="icon" type="image/x-icon" href="../../assets/img/favicon-safe/favicon.ico" />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../../assets/vendor/fonts/iconify-icons.css" />
  <!-- worker-home.html과 동일한 base CSS 복사 (body, bottom-tab, tab-item 등) -->
  <style>
    /* worker-home.html의 리셋, 하단탭바 CSS만 복사 */
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Noto Sans KR', sans-serif; background: #f0f2f5; color: #0f172a; min-height: 100dvh; padding-bottom: 72px; }
    a { text-decoration: none; color: inherit; }
    .top-header { background: #1e293b; color: #fff; padding: 16px 20px 20px; position: sticky; top: 0; z-index: 100; }
    .top-header h2 { font-size: 18px; font-weight: 700; }
    .empty-state { text-align: center; padding: 80px 24px; color: #94a3b8; }
    .empty-state .icon { font-size: 48px; margin-bottom: 12px; }
    .empty-state .msg { font-size: 15px; font-weight: 500; }
    .empty-state .sub { font-size: 13px; margin-top: 6px; }
    .bottom-tab { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; border-top: 1px solid #e2e8f0; display: grid; grid-template-columns: repeat(4, 1fr); padding: 8px 0 env(safe-area-inset-bottom); z-index: 200; box-shadow: 0 -4px 16px rgba(0,0,0,0.08); }
    .tab-item { display: flex; flex-direction: column; align-items: center; gap: 3px; padding: 6px 0; min-height: 56px; cursor: pointer; color: #94a3b8; }
    .tab-item.active { color: #3b82f6; }
    .tab-item .ti { font-size: 22px; }
    .tab-item .tab-label { font-size: 10px; font-weight: 600; }
  </style>
</head>
<body>
  <div class="top-header">
    <h2>🔔 알림</h2>
  </div>
  <div class="empty-state">
    <div class="icon">🔔</div>
    <div class="msg">아직 알림이 없습니다</div>
    <div class="sub">새로운 알림이 오면 여기에 표시됩니다</div>
  </div>
  <!-- 하단 탭바 — worker-home과 동일 구조 -->
  <nav class="bottom-tab">
    <a href="worker-home.html" class="tab-item"><i class="ti tabler-home"></i><span class="tab-label">홈</span></a>
    <a href="schedule-review.html" class="tab-item"><i class="ti tabler-clipboard-check"></i><span class="tab-label">점검</span></a>
    <a href="tbm-list.html" class="tab-item"><i class="ti tabler-users"></i><span class="tab-label">TBM</span></a>
    <a href="notification-list.html" class="tab-item active"><i class="ti tabler-bell"></i><span class="tab-label">알림</span></a>
  </nav>
  <script>
    if (!localStorage.getItem('access_token'))
      location.replace('/html/horizontal-menu-template/auth-login-cover.html');
  </script>
</body>
</html>
```

### 3단계: auth-guard.js 화이트리스트 업데이트

현재 auth-guard.js에서 작업자 페이지를 `worker-` 패턴으로만 허용하고 있습니다.
작업자가 접근 가능한 페이지 목록을 확장해야 합니다.

**현재 코드:**
```javascript
var isWorkerPage = path.indexOf('worker-') !== -1;
if (WORKER_ROLES.indexOf(role) !== -1 && !isWorkerPage) {
    window.location.replace('/html/horizontal-menu-template/worker-home.html');
    return;
}
```

**변경 코드:**
```javascript
var WORKER_ALLOWED = ['worker-', 'schedule-review', 'tbm-list', 'notification-list'];
var isWorkerPage = WORKER_ALLOWED.some(function(p) { return path.indexOf(p) !== -1; });
if (WORKER_ROLES.indexOf(role) !== -1 && !isWorkerPage) {
    window.location.replace('/html/horizontal-menu-template/worker-home.html');
    return;
}
```

## 테스트 시나리오

1. worker@tai.com / Tai1234! 로 로그인
2. worker-home.html 표시 확인
3. 하단 "점검" 탭 클릭 → schedule-review.html 이동 확인
4. 하단 "TBM" 탭 클릭 → tbm-list.html 이동 확인
5. 하단 "알림" 탭 클릭 → notification-list.html (플레이스홀더) 이동 확인
6. 작업자가 URL 직접 입력으로 관리자 대시보드(index.html) 접근 → worker-home으로 리다이렉트 확인

## 관련 파일 경로 요약

```
tadmin/full-version/
├── html/horizontal-menu-template/
│   ├── worker-home.html          ← 이미 있음 (변경 없음)
│   ├── schedule-review.html      ← site/ 에서 복사
│   ├── tbm-list.html             ← site/ 에서 복사
│   └── notification-list.html    ← 신규 플레이스홀더
└── assets/js/tai/
    └── auth-guard.js             ← WORKER_ALLOWED 배열 수정
```
