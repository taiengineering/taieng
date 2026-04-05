/**
 * 마이페이지 mock 상태 — 추후 GET /me 등으로 교체
 * localStorage tai_mypage_mock_state 에서 병합 (개발·데모용)
 */
(function (w) {
  var STORAGE_KEY = 'tai_mypage_mock_state';

  var DEFAULT = {
    accountType: 'USER',
    partnerStatus: 'NONE',
    partnerRole: null,
    summary: {
      contractsActive: 0,
      diagnosisRecent: 0,
      paymentsCount: 0,
    },
  };

  var LABELS = {
    partnerStatus: {
      NONE: '신청 없음',
      DRAFT: '작성 중',
      SUBMITTED: '제출 완료',
      UNDER_REVIEW: '검토 중',
      REVISION_REQUESTED: '보완 요청',
      APPROVED: '승인 완료',
      REJECTED: '반려',
    },
    partnerRole: {
      SAFETY: '안전관리 파트너',
      REPAIR: '시공·수선업체 파트너',
    },
  };

  function load() {
    try {
      var raw = w.localStorage.getItem(STORAGE_KEY);
      var o = raw ? JSON.parse(raw) : {};
      return Object.assign({}, DEFAULT, o, {
        summary: Object.assign({}, DEFAULT.summary, o.summary || {}),
      });
    } catch (e) {
      return Object.assign({}, DEFAULT);
    }
  }

  function save(partial) {
    var cur = load();
    var next = Object.assign({}, cur, partial);
    if (partial && partial.summary) {
      next.summary = Object.assign({}, cur.summary, partial.summary);
    }
    try {
      w.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch (e2) {}
    return next;
  }

  function reset() {
    try {
      w.localStorage.removeItem(STORAGE_KEY);
    } catch (e) {}
  }

  /**
   * URL ?mock=under_review | approved | none 등으로 임시 덮어쓰기 (세션만, 저장 안 함)
   */
  function applyQueryMock() {
    try {
      var q = new URLSearchParams(w.location.search).get('mock');
      if (!q) return;
      var map = {
        none: { partnerStatus: 'NONE', partnerRole: null },
        draft: { partnerStatus: 'DRAFT', partnerRole: 'SAFETY' },
        submitted: { partnerStatus: 'SUBMITTED', partnerRole: 'SAFETY' },
        review: { partnerStatus: 'UNDER_REVIEW', partnerRole: 'SAFETY' },
        revision: { partnerStatus: 'REVISION_REQUESTED', partnerRole: 'REPAIR' },
        approved: { partnerStatus: 'APPROVED', partnerRole: 'SAFETY' },
        rejected: { partnerStatus: 'REJECTED', partnerRole: null },
      };
      var m = map[q.toLowerCase()];
      if (m) {
        w.__TAI_MYPAGE_QUERY_OVERRIDE = m;
      }
    } catch (e) {}
  }

  function get() {
    applyQueryMock();
    var base = load();
    var o = w.__TAI_MYPAGE_QUERY_OVERRIDE;
    return o ? Object.assign({}, base, o) : base;
  }

  function partnerStatusLabel() {
    var s = get().partnerStatus;
    return LABELS.partnerStatus[s] || s || '—';
  }

  function partnerRoleLabel() {
    var r = get().partnerRole;
    if (!r) return '—';
    return LABELS.partnerRole[r] || r;
  }

  w.TaiMypageState = {
    load: get,
    save: save,
    reset: reset,
    isPartnerApproved: function () {
      return get().partnerStatus === 'APPROVED';
    },
    partnerStatusLabel: partnerStatusLabel,
    partnerRoleLabel: partnerRoleLabel,
    DEFAULT: DEFAULT,
    /** 콘솔에서 TaiMypageState.save({ partnerStatus: 'APPROVED', partnerRole: 'SAFETY' }) */
  };
})(typeof window !== 'undefined' ? window : this);
