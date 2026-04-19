/**
 * 무료 익명 진단 — API 헤더, 로그인 유도 시 redirect 보조
 */
(function (w) {
  var TAI_API = w.TAI_API_BASE || 'https://api.taieng.co.kr';

  w.taiDiagApiHeaders = function () {
    var h = { 'Content-Type': 'application/json' };
    try {
      var t = localStorage.getItem('access_token');
      if (t) h['Authorization'] = 'Bearer ' + t;
    } catch (e) {}
    return h;
  };

  w.taiDiagGoLoginForFull = function (token) {
    if (!token) return;
    try {
      localStorage.setItem('pendingDiagnosisToken', token);
      var back = 'free-diagnosis-result.html?token=' + encodeURIComponent(token);
      localStorage.setItem('postLoginRedirect', back);
    } catch (e) {}
    w.location.href = 'log-in.html?redirect=' + encodeURIComponent(back);
  };

  w.TAI_API_BASE = TAI_API;
})(typeof window !== 'undefined' ? window : this);
