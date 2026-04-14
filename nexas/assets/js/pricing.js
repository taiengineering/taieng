/**
 * TAI pricing.js — API 연동 가격 자동 반영
 * v1.0.0 (2026-04-14)
 * - GET /api/v1/public/pricing 에서 가격 데이터 로드
 * - 5분 sessionStorage 캐시 / API 실패 시 하드코딩 fallback 유지
 * - DOM 요소의 [data-pricing-key] 속성으로 자동 반영
 */
(function () {
  'use strict';

  var API_BASE  = 'https://api.taieng.co.kr';
  var CACHE_KEY = 'tai_pricing_v1';
  var CACHE_TTL = 5 * 60 * 1000; // 5분

  /** data-pricing-key 속성을 가진 모든 요소에 값 적용 */
  function applyPricing(data) {
    if (!data) return;
    document.querySelectorAll('[data-pricing-key]').forEach(function (el) {
      var key = el.dataset.pricingKey;
      if (data[key] !== undefined && data[key] !== null) {
        var raw = data[key];
        var num = Number(raw);
        el.textContent = isNaN(num) ? raw : num.toLocaleString('ko-KR');
      }
    });
  }

  /** API 호출 → 캐시 → fallback */
  async function loadPricing() {
    try {
      // 1) 캐시 확인
      var cached = sessionStorage.getItem(CACHE_KEY);
      if (cached) {
        var obj = JSON.parse(cached);
        if (Date.now() - obj.ts < CACHE_TTL) {
          applyPricing(obj.data);
          return;
        }
      }
      // 2) API 호출
      var res = await fetch(API_BASE + '/api/v1/public/pricing', {
        headers: { 'Accept': 'application/json' }
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      var json = await res.json();
      var data = json.data || json;
      sessionStorage.setItem(CACHE_KEY, JSON.stringify({ data: data, ts: Date.now() }));
      applyPricing(data);
    } catch (e) {
      // 3) 실패 시 하드코딩 fallback 그대로 유지 (아무것도 안 함)
      console.warn('[TAI pricing] API 실패 — fallback 하드코딩 유지:', e.message);
    }
  }

  // DOMContentLoaded 또는 즉시 실행
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadPricing);
  } else {
    loadPricing();
  }
})();
