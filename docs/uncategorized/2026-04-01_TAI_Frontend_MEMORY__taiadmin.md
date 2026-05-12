# TAI Frontend 세션 메모리 — 2026-04-01

## 완료된 작업

### 1. menu-tadmin.js v2.5.0
- 견적관리 그룹 추가 (role=001 전용)
  - 진단구매 → diagnosis-purchase.html
  - 크몽관리 → kmong-list.html [NEW 배지]
- isAdmin() 함수 추가
- 파일: `tadmin/full-version/assets/js/tai/menu-tadmin.js`

### 2. kmong-list.html (크몽관리 페이지)
- 파일: `tadmin/full-version/html/horizontal-menu-template/kmong-list.html`
- 기능:
  - 신청 목록/통계 카드 (전체/신규/분석중/발송완료)
  - v1/v2/v3 모듈 필터, 상태 필터, 검색
  - 상세 모달: 신청정보 + 시설조건 + 법령진단 실행 + 결과 편집
  - 인쇄/PDF, 상태변경, 발송완료 처리
- API: GET/PATCH /admin/public-diagnosis-requests/*

### 3. taieng.co.kr 구조 개편
**문제:** site/full-version/html/index.html(메인사이트)이 SPA 폴백으로
모든 경로(/request/v1/ 등)를 가로채는 문제

**해결:**
```
변경 전:
  site/full-version/html/index.html  ← 메인사이트 전체 (SPA 폴백)
  request/v1/index.html              ← 저장소 루트 (잘못된 위치)

변경 후:
  site/full-version/html/index.html  ← /home/ 리다이렉트만 (182 bytes)
  site/full-version/html/home/index.html  ← 메인사이트 본체
  site/full-version/html/request/v1/index.html  ← 법령진단 신청
  site/full-version/html/request/v2/index.html  ← 공정진단 신청
  site/full-version/html/request/v3/index.html  ← 설비진단 신청
  site/full-version/html/login.html   ← tadmin 리다이렉트
  site/full-version/html/_redirects   ← 라우팅 규칙 v3
```

### 4. home/index.html 버그 수정
- **로그아웃 무한루프 수정:**
  - 구버전: `location.replace('login.html')` → login.html 없음 → SPA 폴백 → 무한루프
  - 수정: `location.reload()` (redirect 없이 리로드)
- **팝업 역할 선택 수정:**
  - 구버전: closeModal()만 실행 (메인에 머무름)
  - 수정: 모든 역할 선택 → tadmin으로 이동 (로그인 여부에 따라 대시보드 or 로그인)
- **Nav 로그인 상태 동적 표시:**
  - 토큰 있음: `{사용자명}님 | 대시보드 | 로그아웃`
  - 토큰 없음: `로그인 | 서비스 신청 →`

### 5. _redirects v3
```
/request/v1   /request/v1/index.html  200
/request/v1/  /request/v1/index.html  200
/request/v2   /request/v2/index.html  200
/request/v2/  /request/v2/index.html  200
/request/v3   /request/v3/index.html  200
/request/v3/  /request/v3/index.html  200
/login.html   https://tadmin.taieng.co.kr/.../auth-login-cover.html  302
/request/v1/login.html  /request/v1/  302
/request/v2/login.html  /request/v2/  302
/request/v3/login.html  /request/v3/  302
/             /home/  302
/index.html   /home/  302
```

## 미완료 / 진행 중

### request/v1,v2,v3 캐시 문제
- 증상: Cloudflare가 구버전 서빙 중 → /request/v2/login.html 무한루프
- Cloudflare 캐시 퍼지 후에도 일부 미반영
- 해결책: 캐시버스트 주석 추가 후 재push 필요
  ```html
  <!-- cache-bust: 20260401 -->
  ```

### 알럿관리 페이지 (작업지시만 작성, 미구현)
- 대상 파일: `tadmin/full-version/html/horizontal-menu-template/alert-list.html`
- menu-tadmin.js에 시스템관리 > 알럿관리 메뉴 추가 필요
- 백엔드 routers/alert_messages.py 신규 생성 필요

## 현재 URL 상태
| URL | 상태 |
|-----|------|
| taieng.co.kr/ | /home/ redirect ✓ |
| taieng.co.kr/home/ | 메인사이트 ✓ |
| taieng.co.kr/request/v1/ | 신청 페이지 (캐시 반영 중) |
| tadmin.taieng.co.kr | 정상 ✓ |
| admin.taieng.co.kr | 정상 ✓ |
| api.taieng.co.kr | 정상 ✓ |

## 핵심 학습
- Cloudflare Pages: `_redirects`의 200 rewrite가 실제 파일보다 우선
- SPA 폴백: 파일 없는 경로 → 항상 루트 index.html 반환
- 메인사이트를 home/ 하위로 이동시켜야 request/* 경로 차단 가능
- login.html이 없으면 doLogout() → location.replace('login.html') → SPA 폴백 → 무한루프
