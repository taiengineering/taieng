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

    /* 전문가 활성화 여부 — getExpertStatus 우선, 구 partnerStatus 폴백 */
    var hasActiveExpert = false;
    var activeTypes = [];
    if (w.TaiMypageState && typeof w.TaiMypageState.getExpertStatus === 'function') {
      ['safety', 'fix', 'consult'].forEach(function (t) {
        if (w.TaiMypageState.getExpertStatus(t) === 'active') {
          hasActiveExpert = true;
          activeTypes.push(t);
        }
      });
    } else {
      /* 구버전 폴백 */
      hasActiveExpert = st.partnerStatus === 'APPROVED';
    }

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
    /* 전문가 등록 — 구 파트너 신청 대체 */
    html += item('expert-application', 'mypage/expert-intro.html', '전문가 등록', 'fa-user-tie');

    /* 활성화된 전문가 유형별 전용 메뉴 */
    if (hasActiveExpert) {
      html += '<div class="tai-mypage-nav-head mt-4 mb-3 pt-3 border-top"><span class="small text-uppercase text-muted fw-bold">전문가</span></div>';

      var EXPERT_LABELS = {
        safety:  { label: '안전관리 대행', icon: 'fa-shield-alt' },
        fix:     { label: '시공·수선',     icon: 'fa-tools' },
        consult: { label: '진단·컨설팅',   icon: 'fa-clipboard-list' }
      };

      activeTypes.forEach(function (t) {
        var info = EXPERT_LABELS[t] || { label: t, icon: 'fa-star' };
        html += item('expert-' + t, 'mypage/expert/' + t + '/', info.label, info.icon);
      });
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
