# TAI 홈페이지 Navbar / Footer 개편 작업지시서

> 대상 레포: `taiengineering/tai-admin`  
> 대상 경로: `site/full-version/html/front-pages/` 내 **모든 HTML 파일**  
> 작업 방식: 아래 변경 사항을 전체 파일에 일괄 적용

---

## 변경 사항 요약

| 구분 | 현재 | 변경 후 |
|------|------|----------|
| 서비스 메뉴 | 드롭다운 | **1열 단순 나열** (드롭다운 제거) |
| 위험성진단·정밀안전점검 | 서비스 드롭다운 최하단 | **TAI Care 하부서비스**로 이동 |
| 상단 메뉴 항목 | 서비스·안전정보·FAQ·회사소개·문의 | **서비스·안전정보** 2개만 유지 |
| FAQ·문의·회사소개 | 상단 메뉴 | **풋터에만** 유지 (이미 있음, 상단만 제거) |
| 우측 버튼 (비로그인) | 로그인 / 서비스 신청 | **로그인 / 회원가입** |
| 우측 버튼 (로그인 후) | 그대로 유지 | **버튼 2개 숨김 + 유저명 표시** |
| 유저명 클릭 | 없음 | **마이페이지로 이동** |

---

## 1. NAVBAR 최종 구조 (모든 파일 동일 적용)

```html
<nav id="mainNav" class="navbar navbar-expand-lg navbar-light sticky-top bg-white">
  <div class="container">
    <a class="navbar-brand" href="index.html">
      <img src="assets/tai-logo.png" alt="TAI Engineering" height="50">
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navMenu">

      <!-- 메뉴: 서비스(1열 나열) + 안전정보 -->
      <ul class="navbar-nav mx-auto gap-1">

        <!-- 서비스 드롭다운: 1열 단순 나열, 준비중 항목은 TAI Care 아래 -->
        <li class="nav-item dropdown">
          <a class="nav-link fw-500 dropdown-toggle" href="#" data-bs-toggle="dropdown">서비스</a>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="tai-safe.html">TAI Safe</a></li>
            <li><a class="dropdown-item" href="tai-manager.html">TAI Manager</a></li>
            <li><a class="dropdown-item" href="tai-fix.html">TAI Fix</a></li>
            <!-- TAI Care + 하부서비스 -->
            <li><a class="dropdown-item" href="tai-care.html">TAI Care</a></li>
            <li>
              <a class="dropdown-item text-muted ps-4" href="coming-risk.html">
                └ 위험성진단 <span class="badge bg-secondary ms-1">준비중</span>
              </a>
            </li>
            <li>
              <a class="dropdown-item text-muted ps-4" href="coming-inspection.html">
                └ 정밀안전점검 <span class="badge bg-secondary ms-1">준비중</span>
              </a>
            </li>
          </ul>
        </li>

        <!-- 안전정보만 남김 -->
        <li class="nav-item"><a class="nav-link fw-500" href="safety-news.html">안전정보</a></li>

        <!-- FAQ, 회사소개, 문의 제거 -->
      </ul>

      <!-- 우측 버튼 영역 -->
      <div class="d-flex gap-2 mt-3 mt-lg-0" id="navButtons">
        <!-- 비로그인 상태: 로그인 + 회원가입 -->
        <a href="https://tadmin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html"
           class="btn btn-outline-primary btn-sm px-3" id="btnLogin">로그인</a>
        <a href="https://tadmin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html"
           class="btn btn-primary btn-sm px-3" id="btnSignup">회원가입</a>
        <!-- 로그인 상태: 유저명 표시 (JS로 동적 전환) -->
        <a href="https://tadmin.taieng.co.kr/html/horizontal-menu-template/index.html"
           class="btn btn-outline-primary btn-sm px-3 d-none" id="btnUser"></a>
      </div>
    </div>
  </div>
</nav>
```

---

## 2. FOOTER 변경 사항

풋터 `이용안내` 컬럼에 **FAQ, 문의, 회사소개** 이미 있으므로 유지.  
추가로 `이용약관` 링크도 유지.

```html
<!-- 풋터 이용안내 컬럼 (변경 없음, 확인만) -->
<div class="col-lg-3">
  <h6 class="fw-bold mb-3">이용안내</h6>
  <ul class="list-unstyled">
    <li class="mb-1"><a href="safety-news.html" class="text-white-50 text-decoration-none small">안전정보</a></li>
    <li class="mb-1"><a href="faq.html" class="text-white-50 text-decoration-none small">FAQ</a></li>
    <li class="mb-1"><a href="about.html" class="text-white-50 text-decoration-none small">회사소개</a></li>
    <li class="mb-1"><a href="contact.html" class="text-white-50 text-decoration-none small">이용문의</a></li>
    <li><a href="terms.html" class="text-white-50 text-decoration-none small">이용약관</a></li>
  </ul>
</div>
```

---

## 3. 로그인 상태 감지 JS (모든 파일 `</body>` 직전에 추가)

```html
<script>
// 로그인 상태 감지 — localStorage access_token 기준
(function() {
  const token = localStorage.getItem('access_token');
  const userName = localStorage.getItem('user_name') || localStorage.getItem('user_email') || '';
  if (token && userName) {
    // 로그인 상태: 버튼 2개 숨기고 유저명 표시
    const btnLogin  = document.getElementById('btnLogin');
    const btnSignup = document.getElementById('btnSignup');
    const btnUser   = document.getElementById('btnUser');
    if (btnLogin)  btnLogin.classList.add('d-none');
    if (btnSignup) btnSignup.classList.add('d-none');
    if (btnUser) {
      btnUser.textContent = userName.length > 10 ? userName.substring(0, 10) + '…' : userName;
      btnUser.classList.remove('d-none');
    }
  }
})();
</script>
```

**localStorage 키 기준:**
- `access_token` — 존재 시 로그인 상태
- `user_name` — 유저 이름 (없으면 `user_email` fallback)
- 마이페이지 URL: `https://tadmin.taieng.co.kr/html/horizontal-menu-template/index.html`

---

## 4. 적용 대상 파일 목록 (전체)

```
site/full-version/html/front-pages/index.html
site/full-version/html/front-pages/tai-safe.html
site/full-version/html/front-pages/tai-manager.html
site/full-version/html/front-pages/tai-fix.html
site/full-version/html/front-pages/tai-care.html
site/full-version/html/front-pages/for-manager.html
site/full-version/html/front-pages/for-repair.html
site/full-version/html/front-pages/safety-news.html
site/full-version/html/front-pages/safety-news-detail.html
site/full-version/html/front-pages/faq.html
site/full-version/html/front-pages/about.html
site/full-version/html/front-pages/contact.html
site/full-version/html/front-pages/terms.html
site/full-version/html/front-pages/apply-business.html
site/full-version/html/front-pages/apply-manager.html
site/full-version/html/front-pages/apply-repair.html
site/full-version/html/front-pages/coming-risk.html
site/full-version/html/front-pages/coming-inspection.html
```

---

## 5. 체크리스트

```
□ 모든 파일 navbar — 서비스 드롭다운 1열 구조로 교체
□ 모든 파일 navbar — 위험성진단·정밀안전점검을 TAI Care 하부(ps-4 들여쓰기)로 이동
□ 모든 파일 navbar — FAQ·회사소개·문의 nav-item 제거
□ 모든 파일 navbar — 우측 버튼: "서비스 신청" → "회원가입" (id="btnSignup")
□ 모든 파일 navbar — 로그인 버튼 id="btnLogin" 추가
□ 모든 파일 navbar — 유저명 버튼 id="btnUser" class="d-none" 추가
□ 모든 파일 footer — FAQ·문의·회사소개 유지 확인
□ 모든 파일 </body> 직전 — 로그인 감지 JS 추가
□ 배포 후 taieng.co.kr 에서 비로그인/로그인 상태 확인
```

---

## 6. 주의사항

- `apply-*.html` (폼 페이지)는 navbar가 간소화된 버전일 수 있음 — 동일 규칙 적용
- `survey.html`, `survey_pro.html`은 전체 페이지 폼이므로 **제외**
- `btnUser` 클릭 → `tadmin.taieng.co.kr` 마이페이지 (로그인된 상태이므로 대시보드로 이동)
- 유저명은 10자 초과 시 말줄임 처리
- `location.replace()` 규칙은 이 작업에 해당 없음 (링크 이동)
