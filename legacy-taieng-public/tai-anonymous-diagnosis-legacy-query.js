/**
 * 구버전 taieng.co.kr (루트 정적 사이트) 전용.
 * GET /anonymous-diagnosis/{token} 에 ?tai_legacy_public=1 을 붙여 로그인 없이 전체 결과를 받습니다.
 * Nexas(new UI)에는 포함하지 않습니다.
 *
 * 사용: 결과 페이지에서 다른 스크립트보다 먼저 로드.
 */
(function () {
  var orig = window.fetch;
  window.fetch = function (input, init) {
    if (typeof input === 'string') {
      var base = input.split('?')[0];
      if (
        base.indexOf('anonymous-diagnosis') !== -1 &&
        input.indexOf('tai_legacy_public') === -1 &&
        /\/anonymous-diagnosis\/[^/]+$/i.test(base.replace(/\/+$/, ''))
      ) {
        input += (input.indexOf('?') >= 0 ? '&' : '?') + 'tai_legacy_public=1';
      }
    }
    return orig.call(this, input, init);
  };
})();
