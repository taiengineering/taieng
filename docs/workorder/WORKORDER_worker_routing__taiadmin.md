# Cursor 작업지시서: 작업자(014) 로그인 시 worker-home 라우팅

## 배경
`safe.taieng.co.kr/app` 경로에서 작업자(role_code: '014')로 로그인하면
관리자용 SaaS 대시보드(index.html)가 표시됩니다.
작업자 전용 페이지(worker-home.html)로 이동해야 합니다.

## 현재 구조

### 도메인-경로 매핑
- `safe.taieng.co.kr` → `tadmin/full-version/` (Cloudflare Pages)
- `admin.taieng.co.kr` → `admin/full-version/` (Cloudflare Pages)

### 역할 코드 체계
| role_code | 역할 | 로그인 대상 |
|---|---|---|
| 001 | 최고관리자 | admin.taieng.co.kr |
| 002 | 관리자 | admin.taieng.co.kr |
| 003 | 경영책임자 | safe |
| 004 | 현장소장 | safe (앱) |
| 006 | 관리감독자 | safe (앱) |
| 010 | 안전관리자 | safe |
| 011 | 보건관리자 | safe |
| 012 | 안전보건관리담당자 | safe |
| 013 | 관리자(사업장) | safe |
| 014 | **작업자** | safe (앱/웹앱) |
| 022 | 하도급작업자 | safe (앱) |

### 현재 코드 흐름 (문제 지점)

**`tadmin/full-version/html/horizontal-menu-template/auth-login-cover.html`** (25KB)

```javascript
// 상단 role 배열
var ADMIN_ONLY_ROLES  = ['001', '002'];
var APP_ONLY_ROLES    = ['004', '006', '014', '022'];  // ← 014 작업자 포함
var IS_NATIVE_APP     = !!(window.Capacitor && ...);

// doLogin() 함수 내 — 로그인 성공 후:
if (ADMIN_ONLY_ROLES.indexOf(role) !== -1) {
  // admin-role-msg 표시 → 차단
}
if (!IS_NATIVE_APP && APP_ONLY_ROLES.indexOf(role) !== -1) {
  // app-only-msg 표시 → 차단  ← 웹에서 작업자 로그인 시 여기서 막힘
}
// 위 두 조건 모두 아닐 때:
location.replace('/html/horizontal-menu-template/index.html');  // ← 모든 role이 같은 곳으로
```

**`tadmin/full-version/assets/js/tai/auth-guard.js`** (630B)
- 토큰 유무만 확인, role 분기 없음

### worker-home.html 위치
- **존재**: `site/full-version/html/vertical-menu-template-no-customizer/worker-home.html`
- **미존재**: `tadmin/full-version/html/horizontal-menu-template/worker-home.html` ← 여기에 필요

## 수정 범위 (3개 파일)

### 1. `tadmin/.../auth-login-cover.html` — 로그인 후 role 분기 추가

**변경 위치**: `doLogin()` 함수 내, `await saveContractInfo(token);` 다음 줄

**현재 코드 (약 라인 195):**
```javascript
await saveContractInfo(token);
location.replace('/html/horizontal-menu-template/index.html');
```

**변경 코드:**
```javascript
await saveContractInfo(token);

// 작업자 role → worker-home으로 라우팅
var WORKER_ROLES = ['014', '022'];
if (WORKER_ROLES.indexOf(role) !== -1) {
  location.replace('/html/horizontal-menu-template/worker-home.html');
} else {
  location.replace('/html/horizontal-menu-template/index.html');
}
```

**추가 변경**: `APP_ONLY_ROLES`에서 `'014'`를 제거하여 웹 브라우저에서도 작업자 로그인 허용

**현재:**
```javascript
var APP_ONLY_ROLES = ['004', '006', '014', '022'];
```

**변경:**
```javascript
var APP_ONLY_ROLES = ['004', '006'];
```

> 014(작업자)와 022(하도급작업자)는 웹에서도 로그인 가능하게 변경.
> safe.taieng.co.kr에서 worker-home.html로 이동하면 됩니다.

**주의**: 이 변경은 파일 상단의 `<script>` 블록(초기 리다이렉트)에도 동일하게 적용해야 합니다:

```javascript
// 파일 상단 즉시실행함수 내
if (token) {
  if (ADMIN_ONLY_ROLES.indexOf(role) !== -1 ||
      (!IS_NATIVE_APP && APP_ONLY_ROLES.indexOf(role) !== -1)) {
    // 토큰 삭제 후 로그인 페이지 유지
  } else {
    // ★ 여기도 role 분기 추가
    var WORKER_ROLES = ['014', '022'];
    if (WORKER_ROLES.indexOf(role) !== -1) {
      location.replace('/html/horizontal-menu-template/worker-home.html');
    } else {
      location.replace('/html/horizontal-menu-template/index.html');
    }
  }
}
```

### 2. `tadmin/.../auth-guard.js` — role 기반 접근 제어 추가

**현재 전체 코드 (630B):**
```javascript
(function () {
  var path = window.location.pathname || '';
  var isAuthPage = path.indexOf('auth-login') !== -1 || path.indexOf('auth-register') !== -1;
  var isPublicSurvey = path.indexOf('tai_survey') !== -1;
  if (isAuthPage || isPublicSurvey) return;

  var token = localStorage.getItem('access_token');
  if (!token) {
    window.location.replace('/html/horizontal-menu-template/auth-login-cover.html');
  }
})();
```

**변경 코드:**
```javascript
(function () {
  var path = window.location.pathname || '';
  var isAuthPage = path.indexOf('auth-login') !== -1 || path.indexOf('auth-register') !== -1;
  var isPublicSurvey = path.indexOf('tai_survey') !== -1;
  if (isAuthPage || isPublicSurvey) return;

  var token = localStorage.getItem('access_token');
  if (!token) {
    window.location.replace('/html/horizontal-menu-template/auth-login-cover.html');
    return;
  }

  // 작업자가 관리자 페이지 접근 시 → worker-home으로 리다이렉트
  var role = localStorage.getItem('role_code') || '';
  var WORKER_ROLES = ['014', '022'];
  var isWorkerPage = path.indexOf('worker-') !== -1;
  if (WORKER_ROLES.indexOf(role) !== -1 && !isWorkerPage) {
    window.location.replace('/html/horizontal-menu-template/worker-home.html');
    return;
  }
})();
```

### 3. worker-home.html 복사

`site/full-version/html/vertical-menu-template-no-customizer/worker-home.html`
→ `tadmin/full-version/html/horizontal-menu-template/worker-home.html`

**복사 후 수정 사항:**
- assets 경로 조정: `vertical-menu-template-no-customizer` → `horizontal-menu-template` 기준 상대경로
- auth-guard.js 로드 확인
- 로그아웃 함수가 safe.taieng.co.kr 로그인 페이지로 이동하는지 확인

## 테스트 시나리오

1. **작업자 웹 로그인**: `safe.taieng.co.kr` → worker@tai.com / Tai1234! → worker-home.html 표시 확인
2. **관리자 웹 로그인**: 관리자 계정 → index.html(기존 대시보드) 표시 확인
3. **작업자가 관리자 URL 직접 접근**: `/html/horizontal-menu-template/index.html` → worker-home.html로 리다이렉트
4. **관리자가 worker-home URL 직접 접근**: 차단하지 않음 (관리자는 모든 페이지 접근 가능)
5. **로그아웃 후 재접근**: 로그인 페이지로 이동

## 주의사항

- `auth-login-cover.html`은 25KB(약 650줄) — 전체 파일 수정 시 주의
- `APP_ONLY_ROLES` 변경은 파일 내 2곳(상단 script + doLogin 함수 위)에서 같은 배열 참조
- `site/` 경로의 worker-home.html은 건드리지 않음 (앱용 별도 유지)
- 서비스 계층 분리 규칙: 이 작업은 프론트엔드 JS만 수정하므로 해당 없음

## 관련 파일 경로 요약

```
tadmin/full-version/
├── html/horizontal-menu-template/
│   ├── auth-login-cover.html    ← 수정 (role 분기 + APP_ONLY_ROLES 변경)
│   ├── index.html               ← 기존 관리자 대시보드 (변경 없음)
│   └── worker-home.html         ← 신규 (site/ 에서 복사+경로 수정)
└── assets/js/tai/
    └── auth-guard.js            ← 수정 (role 기반 리다이렉트 추가)
```
