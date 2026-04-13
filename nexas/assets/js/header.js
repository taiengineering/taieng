/**
 * TAI 공통 Header — assets/js/header.js
 * 모든 페이지에서 <div id="tai-header"></div> + <script src="...assets/js/header.js"> 로 사용
 * v1.0.0 (2026-04-13): 통일된 사이트맵 기반 네비게이션
 *
 * 경로 자동 감지:
 *   루트 페이지 (nexas/*.html)         → base = ''
 *   서브폴더 (service/, target/, 등)   → base = '../'
 */
(function () {
  'use strict';

  /* ── 경로 기준점 자동 감지 ── */
  var path = window.location.pathname;
  var inSub = /\/(service|target|mypage)\//.test(path);
  var base = inSub ? '../' : '';

  /* ── 네비게이션 HTML ── */
  var NAV_HTML = [
    '<header class="navbar-area">',
    '  <nav class="navbar navbar-expand-lg">',
    '    <div class="container nav-container">',
    '      <div class="responsive-mobile-menu">',
    '        <button class="menu toggle-btn d-block d-lg-none" data-target="#tai_main_menu" aria-expanded="false" aria-label="메뉴">',
    '          <span class="icon-left"></span><span class="icon-right"></span>',
    '        </button>',
    '      </div>',
    '      <div class="logo">',
    '        <a class="main-logo" href="' + base + 'index.html">',
    '          <img src="' + base + 'assets/img/tai-logo.png" alt="TAI 엔지니어링">',
    '        </a>',
    '      </div>',
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

    /* 회사소개 ▼ */
    '          <li class="menu-item-has-children">',
    '            <a href="#">회사소개</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'about.html">회사소개</a></li>',
    '              <li><a href="' + base + 'patents.html">특허출원</a></li>',
    '              <li><a href="' + base + 'faq.html">FAQ</a></li>',
    '              <li><a href="' + base + 'safety-news.html">안전정보</a></li>',
    '            </ul>',
    '          </li>',

    '        </ul>',
    '      </div>',
    '      <div class="nav-right-part nav-right-part-desktop">',
    '        <ul>',
    '          <li class="nav-auth-guest"><a href="' + base + 'log-in.html">로그인</a></li>',
    '          <li class="nav-auth-user d-none"><a href="' + base + 'mypage/">마이페이지</a></li>',
    '          <li><a href="' + base + 'free-diagnosis.html" class="btn btn-base">무료 진단</a></li>',
    '        </ul>',
    '      </div>',
    '    </div>',
    '  </nav>',
    '</header>',
  ].join('\n');

  /* ── 삽입 ── */
  function inject() {
    /* 1) id="tai-header" 요소가 있으면 교체 */
    var ph = document.getElementById('tai-header');
    if (ph) {
      ph.outerHTML = NAV_HTML;
      afterInject();
      return;
    }
    /* 2) 기존 .navbar-area가 있으면 교체 */
    var existing = document.querySelector('.navbar-area');
    if (existing) {
      existing.outerHTML = NAV_HTML;
      afterInject();
      return;
    }
    /* 3) body 맨 앞에 삽입 */
    document.body.insertAdjacentHTML('afterbegin', NAV_HTML);
    afterInject();
  }

  /* ── 삽입 후 후처리: nav-auth.js와 동일한 로그인 상태 처리 ── */
  function afterInject() {
    try {
      var token = localStorage.getItem('access_token');
      if (token) {
        var guests = document.querySelectorAll('.nav-auth-guest');
        var users  = document.querySelectorAll('.nav-auth-user');
        guests.forEach(function(el){ el.classList.add('d-none'); });
        users.forEach(function(el){ el.classList.remove('d-none'); });
      }
    } catch(e) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
