/**
 * 파트너 전용 페이지: 승인되지 않은 경우 잠금 UI 표시
 * body.tai-page-partner + #taiMypagePartnerLocked / #taiMypageMain
 */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    if (!document.body.classList.contains('tai-page-partner')) return;
    if (typeof TaiMypageState === 'undefined') return;
    if (TaiMypageState.isPartnerApproved()) return;
    var main = document.getElementById('taiMypageMain');
    var locked = document.getElementById('taiMypagePartnerLocked');
    if (main) main.classList.add('d-none');
    if (locked) locked.classList.remove('d-none');
  });
})();
