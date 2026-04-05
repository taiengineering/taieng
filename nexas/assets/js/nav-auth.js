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

  function onLogout(e) {
    if (!e.target.closest || !e.target.closest('a.tai-logout')) return;
    e.preventDefault();
    clearAuthStorage();
    applyNavAuth();
    window.location.href = 'index.html';
  }

  function bindLoginForm() {
    var form = document.getElementById('tai-login-form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      window.localStorage.setItem(STORAGE_KEY, '1');
      var params = new URLSearchParams(window.location.search);
      var next = params.get('redirect') || 'mypage.html';
      window.location.href = next;
    });
  }

  function bindSignupForm() {
    var form = document.getElementById('tai-signup-form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      window.localStorage.setItem(STORAGE_KEY, '1');
      window.location.href = 'mypage.html';
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    applyNavAuth();
    document.body.addEventListener('click', onLogout);
    bindLoginForm();
    bindSignupForm();
  });
})();
