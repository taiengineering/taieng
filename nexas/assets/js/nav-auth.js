/**
 * TAI — nav-auth.js v2
 * 1) 공통 nav 링크 자동 렌더링 (tai-nav 내 .nav-links 대상)
 * 2) 로그인 상태에 따른 게스트/유저 토글
 */
(function () {
  var STORAGE_KEY = 'tai_session';

  // ─── 공통 메뉴 정의 ───────────────────────────────────────
  var TAI_NAV_ITEMS = [
    { label: 'TAI SAFE',    href: 'index-1.html' },
    { label: 'TAI MANAGER', href: 'index-2.html' },
    { label: 'TAI FIX',    href: 'tai-fix.html' },
    { label: 'TAI AGENT',  href: 'index-3.html' },
    { label: 'TAI CARE',   href: 'index-4.html' },
    { label: '안전정보',     href: 'index-5.html' },
  ];

  // ─── nav 렌더링 ───────────────────────────────────────────
  function renderNavLinks() {
    var wrap = document.querySelector('.tai-nav .nav-links');
    if (!wrap) return;

    // 현재 파일명으로 active 판단
    var currentFile = (window.location.pathname.split('/').pop() || 'index.html').toLowerCase();

    var menuHTML = TAI_NAV_ITEMS.map(function (item) {
      var isActive = currentFile === item.href.toLowerCase();
      return '<a href="' + item.href + '"' + (isActive ? ' class="active"' : '') + '>' + item.label + '</a>';
    }).join('');

    menuHTML += '<span class="nav-sep">|</span>';
    menuHTML += '<a href="log-in.html" class="nav-auth-guest">로그인</a>';
    menuHTML += '<a href="sign-up.html" class="nav-auth-guest">회원가입</a>';
    menuHTML += '<a href="mypage/" class="nav-auth-user d-none">마이페이지</a>';
    menuHTML += '<a href="#" class="tai-logout nav-auth-user d-none">로그아웃</a>';
    menuHTML += '<a href="free-diagnosis.html" class="nav-cta" style="margin-left:8px;">무료 진단</a>';

    wrap.innerHTML = menuHTML;
  }

  // ─── 인증 ─────────────────────────────────────────────────
  function isLoggedIn() {
    return (
      window.localStorage.getItem(STORAGE_KEY) === '1' ||
      !!window.localStorage.getItem('access_token')
    );
  }

  function clearAuthStorage() {
    var keys = [
      STORAGE_KEY, 'access_token', 'refresh_token', 'user_name',
      'user_email', 'role_code', 'partner_role', 'tai_flags',
      'user_id', 'company_id', 'factory_id', 'user'
    ];
    keys.forEach(function (k) { try { window.localStorage.removeItem(k); } catch (e) {} });
    try {
      var all = Object.keys(window.localStorage);
      for (var i = 0; i < all.length; i++) {
        var k = all[i];
        if (/^tai_/i.test(k) || /^sb-/i.test(k) || k.indexOf('supabase') === 0)
          window.localStorage.removeItem(k);
      }
    } catch (e2) {}
    try { ['tai_session', 'access_token'].forEach(function (k) { window.sessionStorage.removeItem(k); }); } catch (e3) {}
  }

  function applyNavAuth() {
    var guest = document.querySelectorAll('.nav-auth-guest');
    var user  = document.querySelectorAll('.nav-auth-user');
    var logged = isLoggedIn();
    guest.forEach(function (el) { el.classList.toggle('d-none', logged); });
    user.forEach(function (el)  { el.classList.toggle('d-none', !logged); });
  }

  function isIndexPage() {
    var p = window.location.pathname || '';
    return /index\.html$/i.test(p) || p === '/' || /\/nexas\/?$/i.test(p);
  }

  function onLogout(e) {
    var a = e.target && e.target.closest ? e.target.closest('a.tai-logout') : null;
    if (!a) return;
    e.preventDefault(); e.stopPropagation();
    clearAuthStorage(); applyNavAuth();
    if (typeof window.taiOnAuthCleared === 'function') { try { window.taiOnAuthCleared(); } catch (err) {} }
    if (isIndexPage()) { window.location.reload(); return; }
    window.location.replace('index.html');
  }

  function bindLoginForm() {
    var form = document.getElementById('tai-login-form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      window.localStorage.setItem(STORAGE_KEY, '1');
      var params = new URLSearchParams(window.location.search);
      window.location.href = params.get('redirect') || 'mypage/';
    });
  }

  function bindSignupForm() {
    var form = document.getElementById('tai-signup-form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      window.localStorage.setItem(STORAGE_KEY, '1');
      window.location.href = 'mypage/';
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    renderNavLinks();
    applyNavAuth();
    document.body.addEventListener('click', onLogout, true);
    bindLoginForm();
    bindSignupForm();
  });

  window.addEventListener('pageshow', function (ev) {
    applyNavAuth();
    if (typeof window.taiOnPageShowAuth === 'function') {
      try { window.taiOnPageShowAuth(!!(ev && ev.persisted)); } catch (e) {}
    }
  });

  window.taiClearAuth   = clearAuthStorage;
  window.taiApplyNavAuth = applyNavAuth;
})();
