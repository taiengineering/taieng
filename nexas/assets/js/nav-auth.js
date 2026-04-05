/**
 * TAI — 헤더 로그인 상태 (localStorage, 실서비스 시 API·세션으로 교체)
 * tai_session === '1' 또는 access_token 존재 시 로그인으로 간주
 */
(function () {
  var STORAGE_KEY = 'tai_session';

  function isLoggedIn() {
    return (
      window.localStorage.getItem(STORAGE_KEY) === '1' ||
      !!window.localStorage.getItem('access_token')
    );
  }

  function clearAuthStorage() {
    var keys = [
      STORAGE_KEY,
      'access_token',
      'refresh_token',
      'user_name',
      'user_email',
      'role_code',
      'partner_role',
      'tai_flags',
      'user_id',
      'company_id',
      'factory_id',
      'user'
    ];
    keys.forEach(function (k) {
      try {
        window.localStorage.removeItem(k);
      } catch (e) {}
    });
    try {
      var all = Object.keys(window.localStorage);
      for (var i = 0; i < all.length; i++) {
        var k = all[i];
        if (/^tai_/i.test(k) || /^sb-/i.test(k) || k.indexOf('supabase') === 0) {
          window.localStorage.removeItem(k);
        }
      }
    } catch (e2) {}
    try {
      ['tai_session', 'access_token'].forEach(function (k) {
        window.sessionStorage.removeItem(k);
      });
    } catch (e3) {}
  }

  function applyNavAuth() {
    var guest = document.querySelectorAll('.nav-auth-guest');
    var user = document.querySelectorAll('.nav-auth-user');
    var logged = isLoggedIn();
    guest.forEach(function (el) {
      el.classList.toggle('d-none', logged);
    });
    user.forEach(function (el) {
      el.classList.toggle('d-none', !logged);
    });
  }

  function isIndexPage() {
    var p = window.location.pathname || '';
    return (
      /index\.html$/i.test(p) ||
      p === '/' ||
      /\/nexas\/?$/i.test(p)
    );
  }

  function onLogout(e) {
    var a = e.target && e.target.closest ? e.target.closest('a.tai-logout') : null;
    if (!a) return;
    e.preventDefault();
    e.stopPropagation();
    clearAuthStorage();
    applyNavAuth();
    if (typeof window.taiOnAuthCleared === 'function') {
      try {
        window.taiOnAuthCleared();
      } catch (err) {}
    }
    if (isIndexPage()) {
      window.location.reload();
      return;
    }
    window.location.replace('index.html');
  }

  function bindLoginForm() {
    var form = document.getElementById('tai-login-form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      window.localStorage.setItem(STORAGE_KEY, '1');
      var params = new URLSearchParams(window.location.search);
      var next = params.get('redirect') || 'mypage/';
      window.location.href = next;
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
    applyNavAuth();
    document.body.addEventListener('click', onLogout, true);
    bindLoginForm();
    bindSignupForm();
  });

  window.addEventListener('pageshow', function (ev) {
    applyNavAuth();
    if (typeof window.taiOnPageShowAuth === 'function') {
      try {
        window.taiOnPageShowAuth(!!(ev && ev.persisted));
      } catch (e) {}
    }
  });

  window.taiClearAuth = clearAuthStorage;
  window.taiApplyNavAuth = applyNavAuth;
})();
