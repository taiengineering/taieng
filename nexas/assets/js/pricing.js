/**
 * TAI pricing.js — API 연동 가격 자동 반영
 * v2.0.0 (2026-04-14)
 *
 * 엔드포인트:
 *   GET /public/pricing/saas-plans        → is_active=true SaaS 플랜 목록
 *   GET /public/pricing/diagnosis-reports → is_active=true 법령진단 리포트 목록
 *
 * 캐시: sessionStorage, 5분 TTL
 * fallback: API 실패 시 HTML 하드코딩 가격 그대로 유지 (아무것도 덮어쓰지 않음)
 *
 * DOM 연동: [data-pricing-key] 속성으로 가격 자동 반영
 *   SaaS 요소: data-monthly 속성도 함께 업데이트 (연간/월간 토글 연동)
 */
(function () {
  'use strict';

  var API_BASE  = 'https://api.taieng.co.kr';
  var CACHE_KEY = 'tai_pricing_v2';
  var CACHE_TTL = 5 * 60 * 1000; // 5분

  /**
   * SaaS plan_code → data-pricing-key 매핑
   * plan_code는 DB의 saas_subscription_plans.plan_code 기준
   */
  var SAAS_KEY_MAP = {
    'BUILDING_BASIC':         'saas-building-basic',
    'BUILDING_STANDARD':      'saas-building-standard',
    'INDUSTRY_STARTER':       'saas-industry-starter',
    'INDUSTRY_BUSINESS':      'saas-industry-business',
    'INDUSTRY_PRO':           'saas-industry-pro',
    'CONSTRUCTION_STANDARD':  'saas-construction-standard',
    'CONSTRUCTION_PREMIUM':   'saas-construction-premium'
  };

  /**
   * 법령진단 facility_type_code + fee 필드 → data-pricing-key 매핑
   * 필드: basic_fee / process_fee / equipment_fee / total_report_fee
   */
  var DIAG_KEY_MAP = {
    'BUILDING_V2': {
      total_report_fee: 'diag-building-total'
    },
    'INDUSTRY_V2': {
      basic_fee:        'diag-industry-basic',
      equipment_fee:    'diag-industry-equipment',
      total_report_fee: 'diag-industry-total'
    },
    'CONSTRUCTION_V2': {
      total_report_fee: 'diag-construction-total'
    }
  };

  /** data-pricing-key 요소에 가격 적용 */
  function applyByKey(key, value, updateMonthly) {
    var num = Number(value);
    if (isNaN(num) || num <= 0) return;
    document.querySelectorAll('[data-pricing-key="' + key + '"]').forEach(function (el) {
      el.textContent = num.toLocaleString('ko-KR');
      // SaaS 요소: data-monthly도 업데이트해야 연간/월간 토글이 올바르게 동작
      if (updateMonthly && 'monthly' in el.dataset) {
        el.dataset.monthly = num;
      }
    });
  }

  /** SaaS 플랜 배열 적용 */
  function applySaasPlans(plans) {
    if (!Array.isArray(plans)) return;
    plans.forEach(function (plan) {
      var key = SAAS_KEY_MAP[plan.plan_code];
      if (key && plan.monthly_base_fee) {
        applyByKey(key, plan.monthly_base_fee, true);
      }
    });
  }

  /** 법령진단 리포트 배열 적용 */
  function applyDiagnosis(reports) {
    if (!Array.isArray(reports)) return;
    reports.forEach(function (report) {
      var fieldMap = DIAG_KEY_MAP[report.facility_type_code];
      if (!fieldMap) return;
      Object.keys(fieldMap).forEach(function (field) {
        if (report[field]) {
          applyByKey(fieldMap[field], report[field], false);
        }
      });
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
          applySaasPlans(obj.saas);
          applyDiagnosis(obj.diag);
          return;
        }
      }

      // 2) 병렬 API 호출
      var saasRes = await fetch(API_BASE + '/public/pricing/saas-plans', {
        headers: { 'Accept': 'application/json' }
      });
      var diagRes = await fetch(API_BASE + '/public/pricing/diagnosis-reports', {
        headers: { 'Accept': 'application/json' }
      });

      var saasJson = saasRes.ok ? await saasRes.json() : {};
      var diagJson = diagRes.ok ? await diagRes.json() : {};

      // data 래퍼 또는 배열 직접 처리
      var saas = Array.isArray(saasJson) ? saasJson : (Array.isArray(saasJson.data) ? saasJson.data : []);
      var diag = Array.isArray(diagJson) ? diagJson : (Array.isArray(diagJson.data) ? diagJson.data : []);

      // 3) 캐시 저장
      sessionStorage.setItem(CACHE_KEY, JSON.stringify({ saas: saas, diag: diag, ts: Date.now() }));

      // 4) DOM 반영
      applySaasPlans(saas);
      applyDiagnosis(diag);

    } catch (e) {
      // 5) 실패 → fallback 하드코딩 유지 (HTML 그대로)
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
