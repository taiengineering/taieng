/**
 * 마이페이지 사이드 네비게이션 렌더
 * 각 페이지: body.tai-mypage-body, body[data-tai-active], window.TAI_NEXAS_ROOT
 * 로그인 가드는 각 HTML head의 인라인 스크립트에서 처리
 */
(function (w) {
  function href(pathFromNexasRoot) {
    var root = w.TAI_NEXAS_ROOT || '../';
    return root + pathFromNexasRoot;
  }

  function navHtml(activeId) {
    var st = w.TaiMypageState ? w.TaiMypageState.load() : {};
    var approved = st.partnerStatus === 'APPROVED';

    function item(id, path, label, icon) {
      var isActive = activeId === id;
      return (
        '<a class="tai-mypage-nav-link' +
        (isActive ? ' active' : '') +
        '" href="' +
        href(path) +
        '">' +
        '<i class="fas ' +
        icon +
        ' me-2" aria-hidden="true"></i>' +
        label +
        '</a>'
      );
    }

    var html = '';
    html += '<div class="tai-mypage-nav-head mb-3"><span class="small text-uppercase text-muted fw-bold">나의 서비스</span></div>';
    html += item('dashboard', 'mypage/', '대시보드', 'fa-th-large');
    html += item('profile', 'mypage/profile/', '내 정보', 'fa-user');
    html += item('contracts', 'mypage/contracts/', '계약 관리', 'fa-file-contract');
    html += item('payments', 'mypage/payments/', '결제 내역', 'fa-credit-card');
    html += item('diagnosis', 'mypage/diagnosis/', '법령진단', 'fa-clipboard-check');
    html += item('partner-application', 'mypage/partner-application/', '파트너 전환 신청', 'fa-handshake');

    if (approved) {
      html += '<div class="tai-mypage-nav-head mt-4 mb-3 pt-3 border-top"><span class="small text-uppercase text-muted fw-bold">파트너</span></div>';
      html += item('partner', 'mypage/partner/', '파트너 대시보드', 'fa-chart-line');
      html += item('partner-profile', 'mypage/partner/profile/', '파트너 정보', 'fa-id-card');
      html += item('partner-requests', 'mypage/partner/requests/', '요청 관리', 'fa-inbox');
      html += item('partner-quotes', 'mypage/partner/quotes/', '제출 견적', 'fa-file-invoice-dollar');
      html += item('partner-contracts', 'mypage/partner/contracts/', '파트너 계약', 'fa-briefcase');
    }

    return html;
  }

  function renderNav() {
    if (!document.body.classList.contains('tai-mypage-body')) return;
    var active = document.body.getAttribute('data-tai-active') || 'dashboard';
    var host = document.getElementById('taiMypageSidebar');
    if (host) host.innerHTML = navHtml(active);
  }

  document.addEventListener('DOMContentLoaded', renderNav);
  w.taiMypageRenderNav = renderNav;
})(typeof window !== 'undefined' ? window : this);
