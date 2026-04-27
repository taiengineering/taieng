/* KG이니시스 폼 파라미터 수정 — 매뉴얼 기준
 * 1. accept-charset: euc-kr → UTF-8
 * 2. acceptmethod: CARDONLY:CARDPOINT 제거, centerCd(Y)만 유지
 * 3. returnUrl/closeUrl: 현재 도메인에 맞게 동적 설정
 *    이니시스는 결제페이지와 returnUrl이 동일 도메인이어야 함
 */
(function() {
  var f = document.getElementById('diag_inicis_form');
  if (!f) return;
  f.acceptCharset = 'UTF-8';
  var am = f.querySelector('[name="acceptmethod"]');
  if (am) am.value = 'centerCd(Y)';

  // returnUrl/closeUrl을 현재 도메인 기반으로 동적 설정
  // taieng.co.kr에서 열면 → taieng.co.kr/_api/...
  // new.taieng.co.kr에서 열면 → new.taieng.co.kr/_api/...
  var origin = window.location.origin; // https://taieng.co.kr
  var origPrepare = window._origInicisSetForm;

  // API 응답 후 폼 값 세팅 시점에 returnUrl/closeUrl 오버라이드
  var observer = new MutationObserver(function() {
    var retEl = f.querySelector('[name="returnUrl"]');
    var closeEl = f.querySelector('[name="closeUrl"]');
    if (retEl && retEl.value && !retEl.value.startsWith(origin)) {
      retEl.value = origin + '/_api/payments/inicis/return';
      if (closeEl) closeEl.value = origin + '/_api/payments/result?resultCode=CLOSE';
      observer.disconnect();
    }
  });
  observer.observe(f, { subtree: true, attributes: true, attributeFilter: ['value'] });

  // fallback: 2초 후 강제 확인
  setTimeout(function() {
    var retEl = f.querySelector('[name="returnUrl"]');
    var closeEl = f.querySelector('[name="closeUrl"]');
    if (retEl && retEl.value && !retEl.value.startsWith(origin)) {
      retEl.value = origin + '/_api/payments/inicis/return';
      if (closeEl) closeEl.value = origin + '/_api/payments/result?resultCode=CLOSE';
    }
  }, 2000);
})();
