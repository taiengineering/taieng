/* KG이니시스 폼 파라미터 수정 — 매뉴얼 기준
 * 1. accept-charset: euc-kr → UTF-8
 * 2. acceptmethod: CARDONLY:CARDPOINT 제거, centerCd(Y)만 유지
 */
(function() {
  var f = document.getElementById('diag_inicis_form');
  if (!f) return;
  f.acceptCharset = 'UTF-8';
  var am = f.querySelector('[name="acceptmethod"]');
  if (am) am.value = 'centerCd(Y)';
})();
