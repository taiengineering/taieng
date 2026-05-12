# TAI 프론트 작업지시서 — tadmin Nav 공통화

> 우선순위: 🔴  
> 작성일: 2026-03-31  
> 레포: taiengineering/tai-admin  
> 대상: `tadmin/full-version/`

---

## 배경 / 목표

현재 tadmin은 nav(상단 로고·아이콘·알림·유저 드롭다운) HTML이 19개 페이지마다 하드코딩되어 있어,  
nav를 수정하면 19개 파일을 전부 수정해야 한다.

**admin처럼** JS 파일 하나(`nav-tadmin.js`)만 수정하면 모든 tadmin 페이지에 즉시 반영되도록 공통화한다.

---

## 작업 1: `nav-tadmin.js` 신규 생성

**파일 경로:** `tadmin/full-version/assets/js/tai/nav-tadmin.js`

이 파일이 로드되면 자동으로:
1. `#layout-navbar` 안을 nav HTML로 채운다
2. `buildMenu('layout-menu')` 자동 실행 (각 페이지에서 수동 호출 불필요)
3. 유저명/회사명을 localStorage에서 읽어 바인딩

```javascript
/* ═══════════════════════════════════════════════════════════════
   TAI tadmin 공통 Nav — nav-tadmin.js
   이 파일 하나로 모든 tadmin 페이지 상단 Nav를 관리합니다.
   Nav 변경은 이 파일만 수정하면 됩니다.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* ── Nav HTML 정의 ── */
  function buildNavHtml() {
    return `
      <div class="container-xxl">
        <div class="navbar-brand app-brand demo d-none d-xl-flex py-0 me-4 ms-0">
          <a class="app-brand-link" href="index.html">
            <img alt="TAI Engineering" id="brand-logo"
              src="../../assets/img/tai-logo.png"
              style="height:110px;width:auto;object-fit:contain;"/>
          </a>
          <a class="layout-menu-toggle menu-link text-large ms-auto d-xl-none" href="javascript:void(0);">
            <i class="icon-base ti tabler-x icon-sm d-flex align-items-center justify-content-center"></i>
          </a>
        </div>
        <div class="layout-menu-toggle navbar-nav align-items-xl-center me-3 me-xl-0 d-xl-none">
          <a class="nav-item nav-link px-0 me-xl-6" href="javascript:void(0)">
            <i class="icon-base ti tabler-menu-2 icon-md"></i>
          </a>
        </div>
        <div class="navbar-nav-right d-flex align-items-center justify-content-end" id="navbar-collapse">
          <ul class="navbar-nav flex-row align-items-center ms-md-auto">
            <!-- 검색 -->
            <li class="nav-item navbar-search-wrapper btn btn-text-secondary btn-icon rounded-pill">
              <a class="nav-item nav-link search-toggler px-0" href="javascript:void(0);">
                <span class="d-inline-block text-body-secondary fw-normal" id="autocomplete"></span>
              </a>
            </li>
            <!-- 달력 아이콘 (점검 캘린더) -->
            <li class="nav-item me-1">
              <a class="nav-link btn btn-icon btn-text-secondary rounded-pill position-relative"
                href="inspection-calendar.html" title="점검 캘린더">
                <i class="icon-base ti tabler-calendar-check icon-22px text-heading"></i>
                <span class="badge bg-danger rounded-pill position-absolute top-0 start-100 translate-middle d-none"
                  id="calendar-badge" style="font-size:0.65rem;min-width:1.1rem;padding:0.2em 0.45em;"></span>
              </a>
            </li>
            <!-- 알림벨 -->
            <li class="nav-item dropdown me-3 me-xl-2">
              <a class="nav-link btn btn-icon btn-text-secondary rounded-pill position-relative"
                data-bs-auto-close="true" data-bs-toggle="dropdown"
                href="javascript:void(0);" id="notif-bell">
                <i class="icon-base ti tabler-bell icon-22px text-heading"></i>
                <span class="badge bg-danger rounded-pill position-absolute top-0 start-100 translate-middle d-none"
                  id="notif-badge" style="font-size:0.65rem;min-width:1.1rem;padding:0.2em 0.45em;">0</span>
              </a>
              <ul class="dropdown-menu p-0 tai-notif-dropdown" style="right:auto!important;left:0!important;">
                <li class="border-bottom px-3 py-2 d-flex align-items-center justify-content-between">
                  <span class="fw-semibold mb-0">🔔 알림</span>
                  <button class="btn btn-link btn-sm text-primary text-decoration-none p-0"
                    id="notif-mark-all" type="button">모두읽음</button>
                </li>
                <li class="px-0 py-0 tai-notif-scroll"><div id="notif-list"></div></li>
                <li class="border-top text-center py-2 small">
                  <a class="text-decoration-none" href="notification-list.html">전체 알림 보기</a>
                </li>
              </ul>
            </li>
            <!-- 유저 드롭다운 -->
            <li class="nav-item navbar-dropdown dropdown-user dropdown">
              <a class="nav-link dropdown-toggle hide-arrow p-0"
                data-bs-toggle="dropdown" href="javascript:void(0);">
                <div class="avatar avatar-online">
                  <img alt="" class="rounded-circle" src="../../assets/img/avatars/1.png"/>
                </div>
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <a class="dropdown-item mt-0" href="#">
                    <div class="d-flex align-items-center">
                      <div class="flex-shrink-0 me-2">
                        <div class="avatar avatar-online">
                          <img alt="" class="rounded-circle" src="../../assets/img/avatars/1.png"/>
                        </div>
                      </div>
                      <div class="flex-grow-1">
                        <h6 class="mb-0" id="nav-username">사용자</h6>
                        <small class="text-body-secondary" id="nav-company">회사명</small>
                      </div>
                    </div>
                  </a>
                </li>
                <li><div class="dropdown-divider my-1 mx-n2"></div></li>
                <li>
                  <div class="d-grid px-2 pt-2 pb-1">
                    <a class="btn btn-sm btn-danger d-flex" href="javascript:void(0);" onclick="doLogout()">
                      <small class="align-middle">로그아웃</small>
                      <i class="icon-base ti tabler-logout ms-2 icon-14px"></i>
                    </a>
                  </div>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>`;
  }

  /* ── Nav 삽입 ── */
  function injectNav() {
    var nav = document.getElementById('layout-navbar');
    if (!nav) return;
    // 이미 내용이 있으면 교체하지 않음
    if (nav.querySelector('.container-xxl')) return;
    nav.innerHTML = buildNavHtml();
  }

  /* ── 유저 정보 바인딩 ── */
  function bindUserInfo() {
    try {
      var info = JSON.parse(localStorage.getItem('user_info') || '{}');
      var nameEl = document.getElementById('nav-username');
      var compEl = document.getElementById('nav-company');
      if (nameEl) nameEl.textContent = info.name || info.user_name || '사용자';
      if (compEl) compEl.textContent = info.company_name || '';
    } catch (e) {}
  }

  /* ── 메뉴 자동 빌드 ── */
  function autoMenu() {
    if (typeof window.buildMenu === 'function') {
      window.buildMenu('layout-menu');
    } else {
      // buildMenu가 아직 로드되지 않은 경우 대기
      var attempts = 0;
      var timer = setInterval(function () {
        attempts++;
        if (typeof window.buildMenu === 'function') {
          clearInterval(timer);
          window.buildMenu('layout-menu');
        } else if (attempts > 20) {
          clearInterval(timer);
        }
      }, 100);
    }
  }

  /* ── 초기화 ── */
  function init() {
    injectNav();
    bindUserInfo();
    autoMenu();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
```

---

## 작업 2: 모든 tadmin HTML 페이지 수정

**대상 파일 목록 (`tadmin/full-version/html/horizontal-menu-template/`):**
```
auth-login-cover.html   ← nav 없음, 수정 불필요
contact.html
diagnosis-step1.html
education-list.html
education-setting.html
factory-list.html
index.html
inspection-anchor.html
inspection-calendar.html
inspection-custom.html
manager-permission.html
my-contract.html
my-diagnosis.html
my-equipment.html
my-inspection.html
notification-list.html
process-manage.html
process-select.html
tai_survey_v5.html
```

### 각 페이지에서 수행할 작업

#### A. `<nav>` 태그 내용 비우기

기존:
```html
<nav class="layout-navbar navbar navbar-expand-xl align-items-center" id="layout-navbar">
  <div class="container-xxl">
    ... (로고, 달력아이콘, 알림벨, 유저 드롭다운 전체 하드코딩) ...
  </div>
</nav>
```

변경 후:
```html
<nav class="layout-navbar navbar navbar-expand-xl align-items-center" id="layout-navbar">
  <!-- nav-tadmin.js 가 자동 주입 -->
</nav>
```

#### B. `buildMenu()` 수동 호출 제거

기존 (페이지 하단 script 블록):
```html
<script src="../../assets/js/tai/menu-tadmin.js"></script>
<script>buildMenu('layout-menu');</script>
```

변경 후:
```html
<script src="../../assets/js/tai/menu-tadmin.js"></script>
<script src="../../assets/js/tai/nav-tadmin.js"></script>
<!-- buildMenu() 수동 호출 제거 — nav-tadmin.js가 자동 실행 -->
```

#### C. `doLogout()` 함수 제거 (각 페이지의 인라인 선언 삭제)

기존 각 페이지에 인라인으로 있는:
```javascript
function doLogout(){
  ['access_token',...].forEach(function(k){localStorage.removeItem(k);});
  location.replace('https://tadmin.taieng.co.kr/...');
}
```

→ 이 함수를 **`nav-tadmin.js`에 전역으로 한 번만 정의**하므로, 각 페이지의 인라인 선언은 제거한다.

`nav-tadmin.js` 파일 맨 아래에 전역 함수 추가:
```javascript
/* ── 전역 공통 함수 ── */
window.doLogout = function () {
  ['access_token','refresh_token','role_code','user_name','user_id',
   'company_id','company_name','factory_id','selected_factory_id',
   'contract_plan_code','contract_sector','contract_level',
   'contract_addons','contract_service_type'
  ].forEach(function (k) { localStorage.removeItem(k); });
  location.replace('https://tadmin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html');
};
```

---

## 완료 체크리스트

```
□ nav-tadmin.js 신규 생성
  □ buildNavHtml() — nav 전체 HTML
  □ injectNav() — #layout-navbar에 삽입
  □ bindUserInfo() — localStorage에서 유저명/회사명 바인딩
  □ autoMenu() — buildMenu() 자동 실행
  □ window.doLogout() — 전역 로그아웃 함수
□ 각 tadmin HTML 18개 페이지
  □ <nav> 내용 비우기 (주석만 남김)
  □ nav-tadmin.js 스크립트 태그 추가
  □ buildMenu() 수동 호출 제거
  □ 인라인 doLogout() 함수 제거
□ GitHub push
```

---

## 변경 후 효과

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| 달력 아이콘 추가/제거 | 18개 파일 수정 | nav-tadmin.js 1줄 수정 |
| 알림벨 수정 | 18개 파일 수정 | nav-tadmin.js 1줄 수정 |
| 유저 드롭다운 수정 | 18개 파일 수정 | nav-tadmin.js 1줄 수정 |
| 로그아웃 URL 변경 | 18개 파일 수정 | nav-tadmin.js 1줄 수정 |
| 로고 변경 | 18개 파일 수정 | nav-tadmin.js 1줄 수정 |
