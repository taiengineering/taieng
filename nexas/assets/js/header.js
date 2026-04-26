/**
 * TAI 공통 Header — assets/js/header.js
 * v3.0.0 (2026-04-26): 로고 아이콘+텍스트 방식 전환 (SVG→PNG+TAI텍스트)
 * v2.9.0 (2026-04-25): 안전정보 > 개정법령 메뉴 추가
 * v2.8.0 (2026-04-21): 로고 Supabase Storage URL 적용
 * v2.5.0 (2026-04-20): --tai-nav-h CSS 변수 주입
 *
 * ┌ 헤더 높이 기준 ─────────────────────────────────────────────────┐
 * │  실제 렌더링 높이: 90px                                           │
 * │  CSS 변수: --tai-nav-h (전 페이지에서 calc()에 사용 가능)         │
 * └──────────────────────────────────────────────────────────────────┘
 */
(function () {
  'use strict';

  var ICON_URL = 'https://xntdkrjhgcscmqctdzyo.supabase.co/storage/v1/object/public/site-assets/tai-icon.png';

  /* ── 헤더 높이 CSS 변수 + 로고 스타일 주입 ── */
  (function injectNavCss() {
    if (document.getElementById('tai-nav-vars')) return;
    var css = [
      ':root { --tai-nav-h: 90px; }',
      '.full-vp-layout { min-height: calc(100vh - var(--tai-nav-h)); }',
      '.full-vp-left {',
      '  position: sticky;',
      '  top: var(--tai-nav-h);',
      '  height: calc(100vh - var(--tai-nav-h));',
      '}',
      '@media(max-width:768px){',
      '  .full-vp-left { position: relative; height: auto; top: 0; }',
      '}',
      '.full-vp-right {',
      '  height: calc(100vh - var(--tai-nav-h));',
      '}',
      '@media(max-width:768px){',
      '  .full-vp-right { height: calc(100vh - 280px); min-height: 400px; }',
      '}',
      '.tai-page-top { padding-top: var(--tai-nav-h); }',
      /* 로고 아이콘+텍스트 */
      '.tai-logo-combo {',
      '  display: flex !important;',
      '  align-items: center;',
      '  gap: 10px;',
      '  text-decoration: none !important;',
      '}',
      '.tai-logo-combo:hover { text-decoration: none !important; }',
      '.tai-logo-icon {',
      '  width: 38px; height: 38px;',
      '  border-radius: 8px;',
      '  object-fit: cover;',
      '  box-shadow: 0 2px 8px rgba(0,0,0,.15);',
      '}',
      '.tai-logo-text {',
      '  font-family: "DM Sans", "Arial Black", Arial, sans-serif;',
      '  font-weight: 900;',
      '  font-size: 1.5rem;',
      '  letter-spacing: -.02em;',
      '  color: #fff;',
      '  line-height: 1;',
      '  text-shadow: 0 1px 4px rgba(0,0,0,.2);',
      '}',
      /* 스크롤 후 밝은 배경에서 텍스트 다크 */
      '.navbar-area.navbar-area-fixed .tai-logo-text {',
      '  color: #0f2b4a;',
      '  text-shadow: none;',
      '}',
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
    '        <a class="tai-logo-combo" href="' + base + 'index.html">',
    '          <img class="tai-logo-icon" src="' + ICON_URL + '" alt="TAI">',
    '          <span class="tai-logo-text">TAI</span>',
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
    '              <li><a href="' + base + 'for-repair.html">\uC218\uC120 \uC5F0\uACB0</a></li>',
    '              <li><a href="' + base + 'for-consultant.html">\uCEE8\uC124\uD305</a></li>',
    '              <li><a href="' + base + 'for-agency.html">\uC120\uC784 \uC5F0\uACB0</a></li>',
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
    '              <li><a href="' + base + 'for-expert">\uC804\uBB38\uAC00</a></li>',
    '            </ul>',
    '          </li>',

    /* 안전정보 */
    '          <li class="menu-item-has-children">',
    '            <a href="#">\uC548\uC804\uC815\uBCF4</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'precedent-search.html">\uD310\uB840 \uAC80\uC0C9</a></li>',
    '              <li><a href="' + base + 'safety-news.html">\uC548\uC804\uC815\uBCF4</a></li>',
    '              <li><a href="' + base + 'law-updates.html">\uAC1C\uC815\uBC95\uB839</a></li>',
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
