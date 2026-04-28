/* KG이니시스 폼 파라미터 수정 — 매뉴얼 기준
 * 1. accept-charset: euc-kr → UTF-8
 * 2. acceptmethod: centerCd(Y)만 유지
 * 3. returnUrl/closeUrl: 현재 도메인에 맞게 동적 설정
 *    이니시스 V023: 결제페이지와 returnUrl이 동일 도메인이어야 함
 */
(function() {
  var f = document.getElementById('diag_inicis_form');
  if (!f) return;
  f.acceptCharset = 'UTF-8';
  var am = f.querySelector('[name="acceptmethod"]');
  if (am) am.value = 'centerCd(Y)';

  // returnUrl/closeUrl을 현재 도메인 기반으로 동적 설정
  var origin = window.location.origin;
  var correctReturn = origin + '/_api/payments/inicis/return';
  var correctClose = origin + '/_api/payments/result?resultCode=CLOSE';

  // INIStdPay.pay() 호출 전에 returnUrl을 강제 수정
  // setInterval로 폼 값 변경을 감지 (MutationObserver는 property 변경 미감지)
  var fixInterval = setInterval(function() {
    var retEl = f.elements['returnUrl'];
    var clsEl = f.elements['closeUrl'];
    if (retEl && retEl.value && retEl.value.indexOf('/_api/') > -1) {
      if (retEl.value !== correctReturn) {
        retEl.value = correctReturn;
      }
      if (clsEl && clsEl.value !== correctClose) {
        clsEl.value = correctClose;
      }
    }
  }, 200);

  // INIStdPay.pay 호출을 가로채서 직전에 returnUrl 강제 수정
  var checkPay = setInterval(function() {
    if (typeof INIStdPay !== 'undefined' && INIStdPay.pay) {
      var origPay = INIStdPay.pay;
      INIStdPay.pay = function(formId) {
        var form = document.getElementById(formId);
        if (form) {
          var ret = form.elements['returnUrl'];
          var cls = form.elements['closeUrl'];
          if (ret) ret.value = origin + '/_api/payments/inicis/return';
          if (cls) cls.value = origin + '/_api/payments/result?resultCode=CLOSE';
        }
        return origPay.call(this, formId);
      };
      clearInterval(checkPay);
    }
  }, 100);

  // 30초 후 정리
  setTimeout(function() {
    clearInterval(fixInterval);
    clearInterval(checkPay);
  }, 30000);
})();
