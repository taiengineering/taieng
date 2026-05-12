# TAI 프론트 작업지시서 — tadmin Auth 가드 `<head>` 삽입

> 우선순위: 🔴  
> 작성일: 2026-03-31  
> 레포: taiengineering/tai-admin  
> 대상: `tadmin/full-version/html/horizontal-menu-template/` (로그인 후 화면만)

---

## 배경 / 목표

권한 체크가 `<body>` 하단에서만 동작하면 **페이지가 먼저 그려진 뒤** 리다이렉트되어, 미로그인 사용자에게 화면이 잠깐 노출될 수 있다.

**동기 실행** 가드 스크립트를 `<head>`에서 **viewport 메타 직후**에 두면, 브라우저가 본문을 그리기 전에 리다이렉트할 수 있어 깜빡임을 줄인다.

---

## 작업 1: 공통 스크립트

**파일:** `tadmin/full-version/assets/js/tai/auth-guard.js`

- `localStorage.access_token` 없으면 tadmin 로그인(`auth-login-cover.html`)으로 `location.replace`
- 경로에 `auth-login` / `auth-register` 가 포함되면 **가드 스킵** (로그인·회원가입 페이지 자체)
- 로그인 URL은 이 파일 **한 곳**에서 관리

---

## 작업 2: 각 보호 페이지 `<head>`에 삽입

**삽입 위치:** `<meta charset>` · viewport 메타 **직후**, 그 외 대부분의 CSS/JS보다 **앞**.

```html
<script src="../../assets/js/tai/auth-guard.js"></script>
```

**제외 (가드 태그 자체를 넣지 않음)**

- `auth-login-cover.html` — 로그인 페이지
- `auth-register.html` — 회원가입
- `tai_survey_v5.html` — 공개 설문 UI (기존에 토큰 가드 없음, 동작 유지)

---

## 작업 3: 중복 제거

같은 페이지 하단에 **토큰 없을 때만** `location.replace` 하는 블록이 있으면, 가드와 중복이므로 **제거**한다.  
(대시보드 등 `access_token` 확인 후 **이름 바인딩** 등 다른 로직은 유지)

---

## admin 쪽 (참고)

`admin/full-version/` 은 별도 `admin/full-version/assets/js/tai/auth-guard.js` 를 사용한다. 역할·리다이렉트 규칙은 해당 파일 주석을 따른다.

---

## 완료 체크리스트

```
□ tadmin auth-guard.js 유지·검토
□ 보호 대상 HTML head에 script 태그 삽입
□ 로그인/회원가입/공개 설문 제외
□ 하단 중복 access_token-only 리다이렉트 제거
□ GitHub push
```
