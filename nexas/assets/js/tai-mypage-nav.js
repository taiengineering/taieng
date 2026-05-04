/**
 * 마이페이지 사이드 네비게이션 렌더
 * v2026-05-04: 전문가 등록 메뉴 + 활성 전문가 유형별 섹션 미노출
 * 각 페이지: body.tai-mypage-body, body[data-tai-active], window.TAI_NEXAS_ROOT
 * 로그인 가드는 각 HTML head의 인라인 스크립트에서 처리
 */
(function (w) {
  function href(pathFromNexasRoot) {
    var root = w.TAI_NEXAS_ROOT || '../';
    return root + pathFromNexasRoot;
  }

  function navHtml(activeId) {
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
    html += item('dashboard',  'mypage/',            '대시보드',    'fa-th-large');
    html += item('profile',    'mypage/profile/',    '내 정보',     'fa-user');
    html += item('contracts',  'mypage/contracts/',  '계약 관리',   'fa-file-contract');
    html += item('payments',   'mypage/payments/',   '결제 내역',   'fa-credit-card');
    html += item('diagnosis',  'mypage/diagnosis/',  '법령진단',    'fa-clipboard-check');

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
