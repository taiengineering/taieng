/**
 * TAI 공통 Header — assets/js/header.js
 * 모든 페이지에서 <div id="tai-header"></div> + <script src="...assets/js/header.js"> 로 사용
 * v2.3.1 (2026-04-19): 안전정보 드롭다운 — 판례검색(precedent-search)·안전정보(safety-news)
 * v2.3.0 (2026-04-19): 03_nav — 서비스·업종별·역할별·안전정보, nexas base 보정
 *
 * 경로:
 *   URL에 /nexas/가 있으면 그 이후 경로 깊이로 ../ 계산
 *   그 외에는 service|target(1단) / mypage(다단) 보조 규칙
 */
(function () {
  'use strict';

  function nexasRelBase() {
    var path = window.location.pathname || '';
    var marker = '/nexas/';
    var i = path.indexOf(marker);
    if (i < 0) return '';
    var rest = path.slice(i + marker.length);
    var parts = rest.split('/').filter(Boolean);
    if (parts.length <= 1) return '';
    var depth = parts.length - 1;
    return new Array(depth + 1).join('../');
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
    '              <li><a href="' + base + 'service/diagnosis.html">법령진단</a></li>',
    '              <li><a href="' + base + 'service/saas.html">SaaS 구독</a></li>',
    '              <li><a href="' + base + 'service/education.html">교육사업</a></li>',
    '              <li><a href="' + base + 'service/appointment.html">전문가 매칭</a></li>',
    '              <li><a href="' + base + 'pricing.html">요금제</a></li>',
    '              <li style="border-top:1px solid rgba(255,255,255,.15);margin:4px 0;padding:0;"></li>',
    '              <li><a href="' + base + 'service/inapp.html">인앱 서비스</a></li>',
    '              <li><a href="' + base + 'fix-request.html?from=nav&type=repair">수선 연결</a></li>',
    '              <li><a href="' + base + 'fix-request.html?from=nav&type=consulting">컨설팅</a></li>',
    '              <li><a href="' + base + 'fix-request.html?from=nav&type=appointment">선임 연결</a></li>',
    '              <li><a href="' + base + 'connect.html" style="color:#fbbf24;font-weight:700;">연결서비스 사전등록</a></li>',
    '            </ul>',
    '          </li>',

    /* 업종별 ▼ */
    '          <li class="menu-item-has-children">',
    '            <a href="#">업종별</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'target/building.html">건물·시설</a></li>',
    '              <li><a href="' + base + 'target/factory.html">제조공장</a></li>',
    '              <li><a href="' + base + 'target/construction.html">건설현장</a></li>',
    '            </ul>',
    '          </li>',

    /* 역할별 ▼ */
    '          <li class="menu-item-has-children">',
    '            <a href="#">역할별</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'for-safety-manager.html">안전관리자</a></li>',
    '              <li><a href="' + base + 'for-business-owner.html">사업주</a></li>',
    '              <li><a href="' + base + 'provider-register.html">전문가</a></li>',
    '            </ul>',
    '          </li>',

    '          <li class="menu-item-has-children">',
    '            <a href="#">안전정보</a>',
    '            <ul class="sub-menu">',
    '              <li><a href="' + base + 'precedent-search.html">판례 검색</a></li>',
    '              <li><a href="' + base + 'safety-news.html">안전정보</a></li>',
    '            </ul>',
    '          </li>',

    '        </ul>',
    '      </div>',

    '      <div class="nav-right-part nav-right-part-desktop">',
    '        <ul>',
    '          <li class="nav-auth-guest">',
    '            <a href="' + base + 'log-in.html' + loginRedirectQs + '">로그인</a>',
    '          </li>',
    '          <li class="nav-auth-user d-none">',
    '            <a href="' + base + 'mypage/">마이페이지</a>',
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
