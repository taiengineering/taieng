/**
 * TAI Analytics — GA4 이벤트 추적 유틸
 * 정적 HTML 사이트용 (jQuery/Bootstrap 환경)
 */
(function () {
  'use strict';

  window.TAI_EVENTS = {
    SIGNUP_START: 'signup_start',
    SIGNUP_COMPLETE: 'signup_complete',
    CONSULTATION_CLICK: 'consultation_click',
    PRICING_VIEW: 'pricing_view',
    AI_SEARCH: 'ai_search',
    AI_ANSWER_COMPLETE: 'ai_answer_complete',
    DOCUMENT_GENERATED: 'document_generated',
    PAYMENT_COMPLETE: 'payment_complete',
    CTA_CLICK: 'cta_click',
    FREE_DIAGNOSIS_START: 'free_diagnosis_start',
    FREE_DIAGNOSIS_COMPLETE: 'free_diagnosis_complete',
    MODULE_FILTER: 'module_filter',
    MODULE_DETAIL_VIEW: 'module_detail_view'
  };

  window.taiTrack = function (eventName, params) {
    if (typeof window.gtag !== 'function') return;
    try { window.gtag('event', eventName, params || {}); } catch (e) {}
  };

  document.addEventListener('DOMContentLoaded', function () {
    var path = window.location.pathname;

    if (path.indexOf('pricing') >= 0) {
      taiTrack(TAI_EVENTS.PRICING_VIEW, { page: path });
      // pricing-v2: DB 완전 연동 (하드코딩 FALLBACK 대체)
      var s = document.createElement('script');
      s.src = '/assets/js/pricing-v2.js';
      document.body.appendChild(s);
    }

    if (path.indexOf('free-diagnosis') >= 0 || path.indexOf('diagnosis') >= 0) {
      taiTrack(TAI_EVENTS.FREE_DIAGNOSIS_START, { page: path });
    }

    var tracked = document.querySelectorAll('[data-tai-track]');
    for (var i = 0; i < tracked.length; i++) {
      (function (el) {
        el.addEventListener('click', function () {
          var evt = el.getAttribute('data-tai-track') || 'cta_click';
          var loc = el.getAttribute('data-tai-location') || '';
          var txt = el.textContent.trim().substring(0, 50);
          taiTrack(evt, { location: loc, button_text: txt, page: window.location.pathname });
        });
      })(tracked[i]);
    }

    var consultBtns = document.querySelectorAll(
      'a[href*="connect"], a[href*="consult"], button[class*="consult"]'
    );
    for (var j = 0; j < consultBtns.length; j++) {
      (function (el) {
        el.addEventListener('click', function () {
          taiTrack(TAI_EVENTS.CONSULTATION_CLICK, {
            location: 'auto_detect',
            button_text: el.textContent.trim().substring(0, 50),
            page: window.location.pathname
          });
        });
      })(consultBtns[j]);
    }
  });
})();
