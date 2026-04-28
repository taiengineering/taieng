# Cursor 작업지시서: SaaS 페이지 로그인 도메인 수정

> **레포**: `taiengineering/taieng`
> **파일**: `nexas/service/saas.html` (84KB)
> **원칙**: 결제는 `taieng.co.kr`에서만 진행. SaaS 결제 전 로그인 필수 (기간연장/신규 구분 위해 회원값 필요)

---

## 문제

`saas.html`에 `safe.taieng.co.kr` 5곳 하드코딩 → 결제하기 클릭 시 `safe.taieng.co.kr` 로그인 페이지로 이동됨.
`taieng.co.kr`에 이미 로그인 페이지 존재: `nexas/log-in.html` (21KB)

## 변경

### STEP 1: safe.taieng.co.kr 참조 찾기

```bash
grep -n 'safe\.taieng\.co\.kr' nexas/service/saas.html
```

### STEP 2: 모든 safe.taieng.co.kr 로그인 URL → /log-in 으로 변경

```javascript
// 변경 전 (패턴)
window.location.href = 'https://safe.taieng.co.kr/html/horizontal-menu-template/auth-login-cover'
// 또는
'https://safe.taieng.co.kr/..../auth-login-cover?redirect=...'

// 변경 후
window.location.href = '/log-in?redirect=' + encodeURIComponent(window.location.href)
```

### STEP 3: safe.taieng.co.kr API 호출 → taieng.co.kr/_api 로 변경

`safe.taieng.co.kr`로의 API 호출(fetch/XMLHttpRequest)이 있다면:
```javascript
// 변경 전
fetch('https://safe.taieng.co.kr/...')

// 변경 후
fetch(SP_API + '/...')   // SP_API = 'https://taieng.co.kr/_api'
```

### STEP 4: 기타 safe.taieng.co.kr 링크

SaaS 대시보드 이동 등 safe.taieng.co.kr 링크가 있다면 유지 가능 (결제가 아닌 서비스 이용 링크는 safe 도메인이 맞음).
단, **결제 플로우 내** 리다이렉트만 `/log-in`으로 변경.

## 검증

변경 후:
```bash
grep -n 'safe\.taieng\.co\.kr' nexas/service/saas.html
```

결제 플로우 내 `safe.taieng.co.kr` 참조가 0건이어야 함.
(서비스 이동 링크는 예외 — "TAI Safe 바로가기" 등은 safe 도메인 유지 가능)

## 테스트

1. `taieng.co.kr/service/saas` 접속
2. 아무 플랜 "결제하기" 클릭
3. `taieng.co.kr/log-in` 로그인 페이지 표시 확인 (safe.taieng.co.kr 아님)
4. 로그인 후 원래 SaaS 페이지로 복귀 확인
