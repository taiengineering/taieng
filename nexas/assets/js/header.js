/**
 * TAI 공통 Header — assets/js/header.js
 * 모든 페이지에서 <div id="tai-header"></div> + <script src="...assets/js/header.js"> 로 사용
 * v2.1.2 (2026-04-15): 탑메뉴 '회사소개' 드롭다운 제거 → '안전정보' 단일 링크
 *
 * 경로 자동 감지:
 *   루트 페이지 (nexas/*.html)       → base = ''
 *   서브폴더 (service/, target/)    → base = '../'
 */
(function () {
  'use strict';

  /* ── 경로 기준점 자동 감지 ── */
  var path  = window.location.pathname;
  var inSub = /\/(service|target|mypage)\//.test(path);
  var base  = inSub ? '../' : '';

  /* ── 네비게이션 HTML (Nexas 원본 navbar-area 구조) ── */
  var html = [
    '<header class="navbar-area">',
    '  <nav class="navbar navbar-expand-lg">',
    '    <div class="container nav-container">',

    /* 모바일 토글 버튼 */
    '      <div class="responsive-mobile-menu">',
    '        <button class="menu toggle-btn d-block d-lg-none" data-target="#tai_main_menu" aria-expanded="false" aria-label="메뉴">',
    '          <span class="icon-left"></span><span class="icon-right"></span>',
    '        </button>',
    '      </div>',

    /* 로고 */
    '      <div class="logo">',
    '        <a class="main-logo" href="' + base + 'index.html">',
    '          <img src="' + base + 'assets/img/tai-logo.png" alt="TAI 엔지니어링">',
    '        </a>',
    '      </div>',

    /* 메뉴 */
    '      <div class="collapse navbar-collapse" id="tai_main_menu">',
    '        <ul class="navbar-nav menu-open text-end">',

    /* 서비스 ▼ */
    '          <li class="menu-item-has-children">',
    '            <a href="#">서비스</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'service/education.html">교육사업</a></li>',
    '              <li><a href="' + base + 'service/inapp.html">인앱 서비스</a></li>',
    '              <li><a href="' + base + 'service/repair.html">수선 연결</a></li>',
    '              <li><a href="' + base + 'service/consulting.html">컨설팅</a></li>',
    '              <li><a href="' + base + 'service/appointment.html">선임 연결</a></li>',
    '              <li><a href="' + base + 'service/saas.html">SaaS 구독</a></li>',
    '              <li><a href="' + base + 'service/diagnosis.html">법령진단</a></li>',
    '              <li style="border-top:1px solid rgba(255,255,255,.15);margin:4px 0;padding:0;"></li>',
    '              <li><a href="' + base + 'connect.html" style="color:#fbbf24;font-weight:700;">🔗 연결서비스 사전등록</a></li>',
    '            </ul>',
    '          </li>',

    /* 대상별 ▼ */
    '          <li class="menu-item-has-children">',
    '            <a href="#">대상별</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'target/building.html">건물·시설</a></li>',
    '              <li><a href="' + base + 'target/factory.html">제조공장</a></li>',
    '              <li><a href="' + base + 'target/construction.html">건설현장</a></li>',
    '            </ul>',
    '          </li>',

    /* 요금제 */
    '          <li><a href="' + base + 'pricing.html">요금제</a></li>',

    /* 안전정보 (단일 링크 — 드롭다운 없음) */
    '          <li><a href="' + base + 'safety-news.html">안전정보</a></li>',

    '        </ul>',
    '      </div>',

    /* 우측 버튼 (데스크톱) */
    '      <div class="nav-right-part nav-right-part-desktop">',
    '        <ul>',
    '          <li class="nav-auth-guest">',
    '            <a href="' + base + 'log-in.html">로그인</a>',
    '          </li>',
    '          <li class="nav-auth-user d-none">',
    '            <a href="' + base + 'mypage/">마이페이지</a>',
    '          </li>',
    '          <li>',
    '            <a href="' + base + 'free-diagnosis.html" class="btn btn-white">무료 진단</a>',
    '          </li>',
    '        </ul>',
    '      </div>',

    '    </div>',
    '  </nav>',
    '</header>',
  ].join('\n');

  /* ── 삽입 ── */
  function inject() {
    var ph = document.getElementById('tai-header');
    if (ph) {
      ph.outerHTML = html;
    } else {
      var existing = document.querySelector('header.navbar-area');
      if (existing) {
        existing.outerHTML = html;
      } else {
        document.body.insertAdjacentHTML('afterbegin', html);
      }
    }
    applyAuthState();
  }

  /* ── 로그인 상태 적용 ── */
  function applyAuthState() {
    try {
      var token = localStorage.getItem('access_token');
      if (token) {
        document.querySelectorAll('.nav-auth-guest').forEach(function(el) { el.classList.add('d-none'); });
        document.querySelectorAll('.nav-auth-user').forEach(function(el) { el.classList.remove('d-none'); });
      }
    } catch (e) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
