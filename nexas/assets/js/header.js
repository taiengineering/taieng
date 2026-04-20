/**
 * TAI 공통 Header — assets/js/header.js
 * v2.5.0 (2026-04-20): --tai-nav-h CSS 변수 주입 + 풀뷰포트 레이아웃 자동 보정
 * v2.4.0 (2026-04-19): 역할별 링크 .html 제거
 * v2.3.1 (2026-04-19): 안전정보 드롭다운 — 판례검색·안전정보
 * v2.3.0 (2026-04-19): 03_nav — 서비스·업종별·역할별·안전정보
 *
 * ┌ 헤더 높이 기준 ─────────────────────────────────────────────────┐
 * │  실제 렌더링 높이: 90px                                           │
 * │  CSS 변수: --tai-nav-h (전 페이지에서 calc()에 사용 가능)         │
 * │  풀뷰포트 레이아웃 클래스: .full-vp-layout                       │
 * │  → min-height/height 자동으로 calc(100vh - 90px) 적용           │
 * │  → sticky 요소 top 자동으로 90px 적용                           │
 * └──────────────────────────────────────────────────────────────────┘
 */
(function () {
  'use strict';

  /* ── 헤더 높이 CSS 변수 + 풀뷰포트 레이아웃 유틸 주입 ── */
  (function injectNavCss() {
    if (document.getElementById('tai-nav-vars')) return;
    var css = [
      /* 헤더 높이 전역 변수 */
      ':root { --tai-nav-h: 90px; }',

      /* .full-vp-layout: fix-request 등 풀뷰포트 그리드 레이아웃 */
      '.full-vp-layout { min-height: calc(100vh - var(--tai-nav-h)); }',

      /* .full-vp-left: sticky 사이드패널 */
      '.full-vp-left {',
      '  position: sticky;',
      '  top: var(--tai-nav-h);',
      '  height: calc(100vh - var(--tai-nav-h));',
      '}',
      '@media(max-width:768px){',
      '  .full-vp-left { position: relative; height: auto; top: 0; }',
      '}',

      /* .full-vp-right: 우측 스크롤 패널 */
      '.full-vp-right {',
      '  height: calc(100vh - var(--tai-nav-h));',
      '}',
      '@media(max-width:768px){',
      '  .full-vp-right { height: calc(100vh - 280px); min-height: 400px; }',
      '}',

      /* .tai-page-top: 헤더 fixed일 때 콘텐츠가 헤더 뒤로 숨지 않도록 */
      '.tai-page-top { padding-top: var(--tai-nav-h); }',
    ].join('\n');

    var el = document.createElement('style');
    el.id = 'tai-nav-vars';
    el.textContent = css;
    document.head.appendChild(el);
  })();

  /* ── 경로 계산 ── */
  function nexasRelBase() {
    var path = window.location.pathname || '';
    var marker = '/nexas/';
    var i = path.indexOf(marker);
    if (i < 0) return '';
    var rest = path.slice(i + marker.length);
    var parts = rest.split('/').filter(Boolean);
    if (parts.length <= 1) return '';
    return new Array(parts.length).join('../');
  }

  function legacyRelBase() {
    var path = window.location.pathname || '';
    if (/\/(service|target)\//.test(path)) return '../';
    var m = path.match(/\/mypage\/(.+)/);
    if (m) {
      var n = m[1].split('/').filter(Boolean).length;
      return n >= 2 ? '../../' : '../';
    }
    return '';
  }

  var base = nexasRelBase();
  if (!base) base = legacyRelBase();

  var loginRedirectQs = '';
  try {
    var lp = window.location.pathname || '';
    if (!/\/log-in\.html$/i.test(lp)) {
      loginRedirectQs =
        '?redirect=' +
        encodeURIComponent(lp + (window.location.search || '') + (window.location.hash || ''));
    }
  } catch (e) {}

  var html = [
    '<header class="navbar-area">',
    '  <nav class="navbar navbar-expand-lg">',
    '    <div class="container nav-container">',

    '      <div class="responsive-mobile-menu">',
    '        <button class="menu toggle-btn d-block d-lg-none" data-target="#tai_main_menu" aria-expanded="false" aria-label="\uBA54\uB274">',
    '          <span class="icon-left"></span><span class="icon-right"></span>',
    '        </button>',
    '      </div>',

    '      <div class="logo">',
    '        <a class="main-logo" href="' + base + 'index.html">',
    '          <img src="' + base + 'assets/img/tai-logo.png" alt="TAI \uC5D4\uC9C0\uB2C8\uC5B4\uB9C1">',
    '        </a>',
    '      </div>',

    '      <div class="collapse navbar-collapse" id="tai_main_menu">',
    '        <ul class="navbar-nav menu-open text-end">',

    /* 서비스 */
    '          <li class="menu-item-has-children">',
    '            <a href="#">\uC11C\uBE44\uC2A4</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'service/diagnosis.html">\uBC95\uB839\uC9C4\uB2E8</a></li>',
    '              <li><a href="' + base + 'service/saas.html">SaaS \uAD6C\uB3C5</a></li>',
    '              <li><a href="' + base + 'service/education.html">\uAD50\uC721\uC0AC\uC5C5</a></li>',
    '              <li><a href="' + base + 'service/appointment.html">\uC804\uBB38\uAC00 \uB9E4\uCE6D</a></li>',
    '              <li><a href="' + base + 'pricing.html">\uC694\uAE08\uC81C</a></li>',
    '              <li style="border-top:1px solid rgba(255,255,255,.15);margin:4px 0;padding:0;"></li>',
    '              <li><a href="' + base + 'service/inapp.html">\uC778\uC571 \uC11C\uBE44\uC2A4</a></li>',
    '              <li><a href="' + base + 'fix-request.html?from=nav&type=repair">\uC218\uC120 \uC5F0\uACB0</a></li>',
    '              <li><a href="' + base + 'fix-request.html?from=nav&type=consulting">\uCEE8\uC124\uD305</a></li>',
    '              <li><a href="' + base + 'fix-request.html?from=nav&type=appointment">\uC120\uC784 \uC5F0\uACB0</a></li>',
    '              <li><a href="' + base + 'connect.html" style="color:#fbbf24;font-weight:700;">\uC5F0\uACB0\uC11C\uBE44\uC2A4 \uC0AC\uC804\uB4F1\uB85D</a></li>',
    '            </ul>',
    '          </li>',

    /* 업종별 */
    '          <li class="menu-item-has-children">',
    '            <a href="#">\uC5C5\uC885\uBCC4</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'target/building.html">\uAC74\uBB3C\u00B7\uC2DC\uC124</a></li>',
    '              <li><a href="' + base + 'target/factory.html">\uC81C\uC870\uACF5\uC7A5</a></li>',
    '              <li><a href="' + base + 'target/construction.html">\uAC74\uC124\uD604\uC7A5</a></li>',
    '            </ul>',
    '          </li>',

    /* 역할별 */
    '          <li class="menu-item-has-children">',
    '            <a href="#">\uC5ED\uD560\uBCC4</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'for-safety-manager">\uC548\uC804\uAD00\uB9AC\uC790</a></li>',
    '              <li><a href="' + base + 'for-business-owner">\uC0AC\uC5C5\uC8FC</a></li>',
    '              <li><a href="' + base + 'provider-register">\uC804\uBB38\uAC00</a></li>',
    '            </ul>',
    '          </li>',

    /* 안전정보 */
    '          <li class="menu-item-has-children">',
    '            <a href="#">\uC548\uC804\uC815\uBCF4</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'precedent-search.html">\uD310\uB840 \uAC80\uC0C9</a></li>',
    '              <li><a href="' + base + 'safety-news.html">\uC548\uC804\uC815\uBCF4</a></li>',
    '            </ul>',
    '          </li>',

    '        </ul>',
    '      </div>',

    '      <div class="nav-right-part nav-right-part-desktop">',
    '        <ul>',
    '          <li class="nav-auth-guest">',
    '            <a href="' + base + 'log-in.html' + loginRedirectQs + '">\uB85C\uADF8\uC778</a>',
    '          </li>',
    '          <li class="nav-auth-user d-none">',
    '            <a href="' + base + 'mypage/">\uB9C8\uC774\uD398\uC774\uC9C0</a>',
    '          </li>',
    '        </ul>',
    '      </div>',

    '    </div>',
    '  </nav>',
    '</header>',
  ].join('\n');

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

  function applyAuthState() {
    try {
      var token = localStorage.getItem('access_token');
      if (token) {
        document.querySelectorAll('.nav-auth-guest').forEach(function (el) { el.classList.add('d-none'); });
        document.querySelectorAll('.nav-auth-user').forEach(function (el) { el.classList.remove('d-none'); });
      }
    } catch (e) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
