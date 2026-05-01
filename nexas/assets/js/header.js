/**
 * TAI 공통 Header — assets/js/header.js
 * v3.5.1 (2026-05-01): 마이페이지 경로 버그 수정 (/mypage/ trailing slash 처리)
 * v3.5.0 (2026-05-01): 안전정보 메뉴 4섹션 재구성 + 모바일 로고 수정
 * v3.4.0 (2026-04-30): 로고 이미지 최적화 (1024px 263KB → 96px 21KB)
 * v3.3.0 (2026-04-29): Supabase 신규 프로젝트(서울) URL로 교체
 * v3.2.0 (2026-04-28): 로그인전 로그인/회원가입, 로그인후 마이페이지/로그아웃
 * v3.1.0 (2026-04-26): 로고 텍스트 TAI → TAI Engineering
 * v3.0.0 (2026-04-26): 로고 아이콘+텍스트 방식 전환 (SVG→PNG+텍스트)
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'tai_session';
  var ICON_URL = 'https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/tai-icon-96.png';

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
      '.tai-logo-combo {',
      '  display: flex !important;',
      '  align-items: center;',
      '  gap: 10px;',
      '  text-decoration: none !important;',
      '}',
      '.tai-logo-combo:hover { text-decoration: none !important; }',
      '.tai-logo-icon,',
      '.navbar-area .nav-container .logo a img.tai-logo-icon {',
      '  width: 38px !important; height: 38px !important;',
      '  max-width: 38px !important;',
      '  border-radius: 8px;',
      '  object-fit: cover;',
      '  box-shadow: 0 2px 8px rgba(0,0,0,.15);',
      '}',
      '@media(max-width:575px){',
      '  .tai-logo-icon,',
      '  .navbar-area .nav-container .logo a img.tai-logo-icon {',
      '    width: 32px !important; height: 32px !important;',
      '    max-width: 32px !important;',
      '  }',
      '}',
      '.tai-logo-text {',
      '  font-family: "DM Sans", "Arial Black", Arial, sans-serif;',
      '  font-weight: 900;',
      '  font-size: 1.15rem;',
      '  letter-spacing: -.01em;',
      '  color: #fff;',
      '  line-height: 1.1;',
      '  text-shadow: 0 1px 4px rgba(0,0,0,.2);',
      '  white-space: nowrap;',
      '}',
      '.navbar-area.navbar-area-fixed .tai-logo-text {',
      '  color: #0f2b4a;',
      '  text-shadow: none;',
      '}',
      '@media(max-width:575px){',
      '  .tai-logo-text { font-size: 1rem; }',
      '}',
      '.tai-nav-btn {',
      '  display: inline-flex !important;',
      '  align-items: center;',
      '  justify-content: center;',
      '  font-size: .82rem;',
      '  font-weight: 700;',
      '  border-radius: 8px;',
      '  padding: 7px 14px;',
      '  line-height: 1.2;',
      '  text-decoration: none !important;',
      '  transition: background .15s, color .15s, border-color .15s;',
      '  white-space: nowrap;',
      '}',
      '.tai-nav-btn-outline {',
      '  border: 1.5px solid rgba(255,255,255,.55);',
      '  color: rgba(255,255,255,.9) !important;',
      '  background: transparent;',
      '}',
      '.tai-nav-btn-outline:hover {',
      '  border-color: #fff;',
      '  color: #fff !important;',
      '  background: rgba(255,255,255,.08);',
      '}',
      '.tai-nav-btn-solid {',
      '  border: 1.5px solid rgba(255,255,255,.9);',
      '  color: #0f2b4a !important;',
      '  background: #fff;',
      '}',
      '.tai-nav-btn-solid:hover {',
      '  background: #f0f6ff;',
      '  border-color: #f0f6ff;',
      '  color: #0f2b4a !important;',
      '}',
      '.navbar-area-fixed .tai-nav-btn-outline {',
      '  border-color: rgba(15,43,74,.45);',
      '  color: #0f2b4a !important;',
      '}',
      '.navbar-area-fixed .tai-nav-btn-outline:hover {',
      '  border-color: #0f2b4a;',
      '  background: rgba(15,43,74,.06);',
      '}',
      '.navbar-area-fixed .tai-nav-btn-solid {',
      '  border-color: #0f2b4a;',
      '  background: #0f2b4a;',
      '  color: #fff !important;',
      '}',
      '.navbar-area-fixed .tai-nav-btn-solid:hover {',
      '  background: #1565c0;',
      '  border-color: #1565c0;',
      '}',
      'button.tai-logout-btn {',
      '  cursor: pointer;',
      '  background: transparent;',
      '  border: 1.5px solid rgba(255,255,255,.55);',
      '  color: rgba(255,255,255,.9);',
      '}',
      'button.tai-logout-btn:hover {',
      '  border-color: #fff;',
      '  color: #fff;',
      '  background: rgba(255,255,255,.08);',
      '}',
      '.navbar-area-fixed button.tai-logout-btn {',
      '  border-color: rgba(15,43,74,.45);',
      '  color: #0f2b4a;',
      '}',
      '.navbar-area-fixed button.tai-logout-btn:hover {',
      '  border-color: #0f2b4a;',
      '  background: rgba(15,43,74,.06);',
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
    /* v3.5.1: /mypage/ (trailing slash만) + /mypage/xxx 모두 처리 */
    if (/\/mypage(\/|$)/.test(path)) {
      var after = path.replace(/.*\/mypage\/?/, '');
      var n = after.split('/').filter(Boolean).length;
      if (n >= 2) return '../../';
      return '../';
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

  function isLoggedIn() {
    try {
      return (
        localStorage.getItem(STORAGE_KEY) === '1' ||
        !!localStorage.getItem('access_token')
      );
    } catch (e) { return false; }
  }

  function clearAuthStorage() {
    var keys = [
      STORAGE_KEY, 'access_token', 'refresh_token', 'user_name',
      'user_email', 'role_code', 'partner_role', 'tai_flags',
      'user_id', 'company_id', 'factory_id', 'user'
    ];
    keys.forEach(function (k) { try { localStorage.removeItem(k); } catch (e) {} });
    try {
      var all = Object.keys(localStorage);
      for (var i = 0; i < all.length; i++) {
        var k = all[i];
        if (/^tai_/i.test(k) || /^sb-/i.test(k) || k.indexOf('supabase') === 0)
          localStorage.removeItem(k);
      }
    } catch (e2) {}
    try { [STORAGE_KEY, 'access_token'].forEach(function (k) { sessionStorage.removeItem(k); }); } catch (e3) {}
  }

  function buildNavRight() {
    var logged = isLoggedIn();
    if (logged) {
      return [
        '<div class="nav-right-part nav-right-part-desktop">',
        '  <ul style="display:flex;align-items:center;gap:8px;list-style:none;margin:0;padding:0;">',
        '    <li>',
        '      <a href="' + base + 'mypage/" class="tai-nav-btn tai-nav-btn-outline">마이페이지</a>',
        '    </li>',
        '    <li>',
        '      <button class="tai-nav-btn tai-logout-btn" id="tai-header-logout">로그아웃</button>',
        '    </li>',
        '  </ul>',
        '</div>',
      ].join('\n');
    } else {
      return [
        '<div class="nav-right-part nav-right-part-desktop">',
        '  <ul style="display:flex;align-items:center;gap:8px;list-style:none;margin:0;padding:0;">',
        '    <li>',
        '      <a href="' + base + 'log-in.html' + loginRedirectQs + '" class="tai-nav-btn tai-nav-btn-outline">로그인</a>',
        '    </li>',
        '    <li>',
        '      <a href="' + base + 'sign-up.html" class="tai-nav-btn tai-nav-btn-solid">회원가입</a>',
        '    </li>',
        '  </ul>',
        '</div>',
      ].join('\n');
    }
  }

  function bindLogout() {
    var btn = document.getElementById('tai-header-logout');
    if (!btn) return;
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      clearAuthStorage();
      window.location.href = base + 'index.html';
    });
  }

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
    '          <img class="tai-logo-icon" src="' + ICON_URL + '" width="38" height="38" alt="TAI Engineering" loading="eager">',
    '          <span class="tai-logo-text">TAI Engineering</span>',
    '        </a>',
    '      </div>',
    '      <div class="collapse navbar-collapse" id="tai_main_menu">',
    '        <ul class="navbar-nav menu-open text-end">',
    '          <li class="menu-item-has-children">',
    '            <a href="#">\uC11C\uBE44\uC2A4</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'service/diagnosis.html">\uBC95\uB839\uC9C4\uB2E8</a></li>',
    '              <li><a href="' + base + 'service/saas.html">SaaS \uAD6C\uB3C5</a></li>',
    '              <li><a href="' + base + 'service/education.html">\uAD50\uC721\uC0AC\uC5C5</a></li>',
    '              <li><a href="' + base + 'service/appointment.html">\uC804\uBB38\uAC00 \uB9E4\uCE6D</a></li>',
    '              <li style="border-top:1px solid rgba(255,255,255,.15);margin:4px 0;padding:0;"></li>',
    '              <li><a href="' + base + 'service/inapp.html">\uC778\uC571 \uC11C\uBE44\uC2A4</a></li>',
    '              <li><a href="' + base + 'for-repair.html">\uC218\uC120 \uC5F0\uACB0</a></li>',
    '              <li><a href="' + base + 'for-consultant.html">\uCEE8\uC124\uD305</a></li>',
    '              <li><a href="' + base + 'for-agency.html">\uC120\uC784 \uC5F0\uACB0</a></li>',
    '              <li><a href="' + base + 'connect.html" style="color:#fbbf24;font-weight:700;">\uC5F0\uACB0\uC11C\uBE44\uC2A4 \uC0AC\uC804\uB4F1\uB85D</a></li>',
    '            </ul>',
    '          </li>',
    '          <li class="menu-item-has-children">',
    '            <a href="#">\uC5C5\uC885\uBCC4</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'target/building.html">\uAC74\uBB3C\u00B7\uC2DC\uC124</a></li>',
    '              <li><a href="' + base + 'target/factory.html">\uC81C\uC870\uACF5\uC7A5</a></li>',
    '              <li><a href="' + base + 'target/construction.html">\uAC74\uC124\uD604\uC7A5</a></li>',
    '            </ul>',
    '          </li>',
    '          <li class="menu-item-has-children">',
    '            <a href="#">\uC5ED\uD560\uBCC4</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'for-safety-manager">\uC548\uC804\uAD00\uB9AC\uC790</a></li>',
    '              <li><a href="' + base + 'for-business-owner">\uC0AC\uC5C5\uC8FC</a></li>',
    '              <li><a href="' + base + 'for-expert">\uC804\uBB38\uAC00</a></li>',
    '            </ul>',
    '          </li>',
    '          <li class="menu-item-has-children">',
    '            <a href="#">\uC548\uC804\uC815\uBCF4</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'safety-news.html">\uC548\uC804\uC790\uB8CC</a></li>',
    '              <li><a href="' + base + 'accident-cases.html">\uC7AC\uD574\uC0AC\uB840</a></li>',
    '              <li><a href="' + base + 'law-updates.html">\uAC1C\uC815\uBC95\uB839</a></li>',
    '              <li><a href="' + base + 'precedent-search.html">\uD310\uB840\uAC80\uC0C9</a></li>',
    '            </ul>',
    '          </li>',
    '        </ul>',
    '      </div>',
    '      <div id="tai-nav-right-placeholder"></div>',
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
    var rightPh = document.getElementById('tai-nav-right-placeholder');
    if (rightPh) {
      rightPh.outerHTML = buildNavRight();
    }
    bindLogout();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }

  window.addEventListener('pageshow', function (ev) {
    if (ev && ev.persisted) {
      var rightArea = document.querySelector('.nav-right-part.nav-right-part-desktop');
      if (rightArea) {
        var tmp = document.createElement('div');
        tmp.innerHTML = buildNavRight();
        rightArea.outerHTML = tmp.innerHTML;
        bindLogout();
      }
    }
  });

  window.taiClearAuth = function () {
    clearAuthStorage();
  };
})();
