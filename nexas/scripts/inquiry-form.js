/**
 * Phase 5 — 마케팅 사이트 통합 인박스 (anon → inquiries)
 * nexas/scripts/inquiry-form.js
 *
 * - 푸터 "TAI에 바란다" FEEDBACK 모달 (footer.js에서 로드)
 * - contact.html INQUIRY 제출 (initContactPage)
 *
 * 라벨·키: docs/inbox-system/PHASE5_FORMS.md §4 (Phase 4 / 슬랙과 동일)
 */
(function (w) {
  'use strict';

  var REST = 'https://vwlahtguyggrhvslabax.supabase.co/rest/v1';
  var ANON_KEY =
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3bGFodGd1eWdncmh2c2xhYmF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcyOTE1OTYsImV4cCI6MjA5Mjg2NzU5Nn0.Yp6P7ahaCuna_gwYC8_S2KD081Ov9Fs65e9o_AenP48';

  var TYPE_LABEL = {
    INQUIRY: '도입 문의',
    FEEDBACK: 'TAI에 바란다',
  };

  var INQUIRY_CATEGORIES = [
    { key: 'consult', label: '법적진단 컨설팅' },
    { key: 'safety', label: '안전관리자 선임대행' },
    { key: 'electric', label: '전기설비 점검' },
    { key: 'risk', label: '위험성평가' },
    { key: 'csia', label: '중대재해처벌법' },
    { key: 'saas', label: 'SaaS 서비스' },
    { key: 'repair', label: '수선중개' },
    { key: 'edu', label: '안전보건교육' },
    { key: 'partner', label: '파트너/협력 제안' },
    { key: 'other', label: '기타' },
  ];

  var FEEDBACK_CATEGORIES = [
    { key: 'fb_feature', label: '기능 제안' },
    { key: 'fb_bug', label: '버그/오류' },
    { key: 'fb_ux', label: '사용성 불편' },
    { key: 'fb_idea', label: '아이디어' },
    { key: 'fb_praise', label: '응원·칭찬' },
  ];

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function toastMarketing(msg, isErr) {
    try {
      if (w.bootstrap && w.bootstrap.Toast) {
        var el = document.getElementById('taiInquiryToast');
        if (!el) {
          el = document.createElement('div');
          el.id = 'taiInquiryToast';
          el.className = 'toast align-items-center border-0 position-fixed bottom-0 end-0 m-3';
          el.setAttribute('role', 'alert');
          el.style.zIndex = '10800';
          el.innerHTML =
            '<div class="d-flex"><div class="toast-body" id="taiInquiryToastBody"></div>' +
            '<button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button></div>';
          document.body.appendChild(el);
        }
        document.getElementById('taiInquiryToastBody').textContent = msg;
        el.classList.toggle('text-bg-danger', !!isErr);
        el.classList.toggle('text-bg-success', !isErr);
        var t = new w.bootstrap.Toast(el, { delay: 3800 });
        t.show();
        return;
      }
    } catch (e) {
      console.warn('[inquiry-form] toast fallback', e);
    }
    alert(msg);
  }

  function validateRow(row) {
    var c = (row.content || '').trim();
    if (c.length < 10 || c.length > 2000) {
      return { ok: false, error: '내용은 10자 이상 2000자 이하로 입력해주세요.' };
    }
    if (['marketing', 'safe'].indexOf(row.source) < 0) {
      return { ok: false, error: 'internal: invalid source' };
    }
    if (['INQUIRY', 'FEEDBACK'].indexOf(row.inquiry_type) < 0) {
      return { ok: false, error: 'internal: invalid type' };
    }
    return { ok: true };
  }

  function scrub(row) {
    var o = {};
    Object.keys(row).forEach(function (k) {
      var v = row[k];
      if (v === undefined || v === '') return;
      o[k] = v;
    });
    return o;
  }

  function insertInquiry(row) {
    var v = validateRow(row);
    if (!v.ok) return Promise.resolve(v);
    var payload = scrub(row);
    return fetch(REST + '/inquiries', {
      method: 'POST',
      headers: {
        apikey: ANON_KEY,
        Authorization: 'Bearer ' + ANON_KEY,
        'Content-Type': 'application/json',
        Prefer: 'return=minimal',
      },
      body: JSON.stringify(payload),
    }).then(function (r) {
      if (r.ok) return { ok: true };
      return r.json().catch(function () {
        return {};
      }).then(function (err) {
        console.error('[inquiry] insert failed:', r.status, err);
        return { ok: false, error: '전송에 실패했습니다. 잠시 후 다시 시도해주세요.' };
      });
    }).catch(function (e) {
      console.error('[inquiry] insert failed:', e);
      return { ok: false, error: '전송에 실패했습니다. 잠시 후 다시 시도해주세요.' };
    });
  }

  var modalInjected = false;

  function injectFeedbackModalHtml() {
    if (modalInjected) return;
    modalInjected = true;
    var catOpts = FEEDBACK_CATEGORIES.map(function (x) {
      return '<option value="' + esc(x.key) + '">' + esc(x.label) + '</option>';
    }).join('');
    var html =
      '<div class="modal fade" id="taiMarketingFeedbackModal" tabindex="-1" aria-hidden="true" style="z-index:10700">' +
      '  <div class="modal-dialog modal-dialog-centered">' +
      '    <div class="modal-content">' +
      '      <div class="modal-header">' +
      '        <h5 class="modal-title">' + esc(TYPE_LABEL.FEEDBACK) + '</h5>' +
      '        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="닫기"></button>' +
      '      </div>' +
      '      <div class="modal-body">' +
      '        <p class="small text-muted mb-3">TAI를 더 좋게 만들 의견을 보내주세요. 서비스에 반영합니다.</p>' +
      '        <div class="mb-3">' +
      '          <label class="form-label" for="taiFbCategory">분류</label>' +
      '          <select id="taiFbCategory" class="form-select">' + catOpts + '</select>' +
      '        </div>' +
      '        <div class="mb-3">' +
      '          <label class="form-label" for="taiFbContent">내용 <span class="text-danger">*</span></label>' +
      '          <textarea id="taiFbContent" class="form-control" rows="5" maxlength="2000" required placeholder="어떤 점이 불편하셨나요? 또는 어떤 기능이 있으면 좋겠나요?"></textarea>' +
      '        </div>' +
      '        <div class="mb-3">' +
      '          <label class="form-label" for="taiFbName">이름 (선택)</label>' +
      '          <input type="text" id="taiFbName" class="form-control" maxlength="120" />' +
      '        </div>' +
      '        <div class="mb-0">' +
      '          <label class="form-label" for="taiFbEmail">이메일 (선택)</label>' +
      '          <input type="email" id="taiFbEmail" class="form-control" maxlength="200" />' +
      '          <div class="form-text">입력하시면 답변을 받으실 수 있습니다.</div>' +
      '        </div>' +
      '      </div>' +
      '      <div class="modal-footer">' +
      '        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">닫기</button>' +
      '        <button type="button" class="btn btn-primary" id="taiFbSubmit">보내기</button>' +
      '      </div>' +
      '    </div>' +
      '  </div>' +
      '</div>';
    document.body.insertAdjacentHTML('beforeend', html);

    document.getElementById('taiFbSubmit').addEventListener('click', function () {
      var content = (document.getElementById('taiFbContent').value || '').trim();
      var v0 = validateRow({
        source: 'marketing',
        inquiry_type: 'FEEDBACK',
        content: content,
      });
      if (!v0.ok) {
        toastMarketing(v0.error, true);
        return;
      }
      var btn = document.getElementById('taiFbSubmit');
      btn.disabled = true;
      insertInquiry({
        source: 'marketing',
        inquiry_type: 'FEEDBACK',
        category: document.getElementById('taiFbCategory').value,
        content: content,
        name: (document.getElementById('taiFbName').value || '').trim() || null,
        email: (document.getElementById('taiFbEmail').value || '').trim() || null,
        page_url: w.location.href,
        is_member: false,
      }).then(function (res) {
        btn.disabled = false;
        if (res.ok) {
          toastMarketing('의견 감사합니다. 신중하게 검토하겠습니다.', false);
          var el = document.getElementById('taiMarketingFeedbackModal');
          if (el && w.bootstrap) {
            var inst = w.bootstrap.Modal.getInstance(el) || new w.bootstrap.Modal(el);
            inst.hide();
          }
          document.getElementById('taiFbContent').value = '';
          document.getElementById('taiFbName').value = '';
          document.getElementById('taiFbEmail').value = '';
        } else {
          toastMarketing(res.error || '전송에 실패했습니다. 잠시 후 다시 시도해주세요.', true);
        }
      });
    });
  }

  function openMarketingFeedbackModal() {
    injectFeedbackModalHtml();
    var el = document.getElementById('taiMarketingFeedbackModal');
    if (!el || !w.bootstrap || !w.bootstrap.Modal) {
      alert('모달을 열 수 없습니다. 페이지를 새로고침 후 다시 시도해주세요.');
      return;
    }
    var m = new w.bootstrap.Modal(el);
    m.show();
  }

  function bindFooterTrigger() {
    if (document.body.dataset.taiFooterFeedbackBound === '1') return;
    document.body.dataset.taiFooterFeedbackBound = '1';
    document.body.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('#tai-footer-feedback-open');
      if (!a) return;
      e.preventDefault();
      openMarketingFeedbackModal();
    });
  }

  function initContactPage() {
    var form = document.getElementById('contactMarketingForm');
    if (!form || form.dataset.inquiryBound === '1') return;
    form.dataset.inquiryBound = '1';
    var catSel = document.getElementById('contactCategory');
    if (catSel && catSel.options.length <= 1) {
      INQUIRY_CATEGORIES.forEach(function (c) {
        var o = document.createElement('option');
        o.value = c.key;
        o.textContent = c.label;
        catSel.appendChild(o);
      });
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var agree = document.getElementById('contactAgree');
      if (!agree || !agree.checked) {
        toastMarketing('개인정보 수집 및 이용에 동의해 주세요.', true);
        return;
      }
      var name = (document.getElementById('contactName').value || '').trim();
      var email = (document.getElementById('contactEmail').value || '').trim();
      var content = (document.getElementById('contactContent').value || '').trim();
      if (!name || !email) {
        toastMarketing('이름과 이메일은 필수입니다.', true);
        return;
      }
      var v0 = validateRow({
        source: 'marketing',
        inquiry_type: 'INQUIRY',
        content: content,
      });
      if (!v0.ok) {
        toastMarketing(v0.error, true);
        return;
      }
      var btn = document.getElementById('contactSubmitBtn');
      if (btn) btn.disabled = true;
      insertInquiry({
        source: 'marketing',
        inquiry_type: 'INQUIRY',
        category: (document.getElementById('contactCategory').value || 'other').trim(),
        title: (document.getElementById('contactTitle').value || '').trim() || null,
        content: content,
        name: name,
        email: email,
        phone: (document.getElementById('contactPhone').value || '').trim() || null,
        company: (document.getElementById('contactCompany').value || '').trim() || null,
        page_url: w.location.href,
        is_member: false,
      }).then(function (res) {
        if (btn) btn.disabled = false;
        if (res.ok) {
          toastMarketing('문의가 접수되었습니다. 영업일 1일 이내 회신드리겠습니다.', false);
          form.reset();
          if (agree) agree.checked = false;
        } else {
          toastMarketing(res.error || '전송에 실패했습니다.', true);
        }
      });
    });
  }

  w.TaiInquiryForm = {
    TYPE_LABEL: TYPE_LABEL,
    INQUIRY_CATEGORIES: INQUIRY_CATEGORIES,
    FEEDBACK_CATEGORIES: FEEDBACK_CATEGORIES,
    insertInquiry: insertInquiry,
    initMarketingFooterModal: function () {
      bindFooterTrigger();
    },
    initContactPage: initContactPage,
  };

  bindFooterTrigger();
  function bootContact() {
    initContactPage();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootContact);
  } else {
    bootContact();
  }
  window.addEventListener('load', bootContact);
})(window);
