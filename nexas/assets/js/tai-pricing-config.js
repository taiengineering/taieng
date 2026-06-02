/**
 * TAI Pricing Config v4 — Single Source of Truth
 * 
 * 모든 마케팅 페이지(diagnosis.html, saas.html, pricing.html)가 이 파일을 참조합니다.
 * 가격 변경 시 이 파일만 수정하면 전 페이지에 반영됩니다.
 * 
 * 우선순위: API 응답 > 이 파일의 fallback
 * API: GET /public/pricing/saas-plans, GET /public/pricing/diagnosis-reports
 */
'use strict';

window.TAI_PRICING = (function() {

  var API_BASE = 'https://api.taieng.co.kr';

  // ══════ SaaS V3 확정 가격 (fallback) ══════
  var SAAS = {
    BUILDING: [
      { code: 'BUILDING_BASIC_V3',    name: '정밀관리',  price: 149000, basis: '5,000㎡ 이하',       featured: true,  custom: false, desc: '안전관리자 선임 의무 포함' },
      { code: 'BUILDING_STANDARD_V3', name: '대형건물',  price: 349000, basis: '5,000㎡ 초과',       featured: false, custom: false, desc: '석면·에너지·냉동 관련 의무 포함' },
      { code: 'BUILDING_CUSTOM_V3',   name: 'Enterprise', price: 0,     basis: '별도 커스터마이징',   featured: false, custom: true,  desc: '다동·복합 시설 특수 구성' },
    ],
    INDUSTRY: [
      { code: 'INDUSTRY_STARTER_V3',  name: 'STARTER',  price: 149000, basis: '49인 이하',           featured: false, custom: false, desc: '안전보건관리담당자' },
      { code: 'INDUSTRY_BUSINESS_V3', name: 'BUSINESS', price: 299000, basis: '50~299인',            featured: true,  custom: false, desc: '안전관리자 선임 (위탁 가능)' },
      { code: 'INDUSTRY_PRO_V3',      name: 'PRO',      price: 499000, basis: '300~499인',           featured: false, custom: false, desc: '안전관리자 전담 (위탁 불가)' },
      { code: 'INDUSTRY_CUSTOM_V3',   name: 'CUSTOM',   price: 0,      basis: '500인 이상',          featured: false, custom: true,  desc: '이사회 보고·승인 의무' },
    ],
    CONSTRUCTION: [
      { code: 'CONSTRUCTION_STANDARD_V3', name: 'STANDARD', price: 249000, basis: '50억 미만',       featured: true,  custom: false, desc: '건설안전법 기본 의무' },
      { code: 'CONSTRUCTION_PREMIUM_V3',  name: 'PREMIUM',  price: 499000, basis: '50억 이상',       featured: false, custom: false, desc: '중대재해처벌법 직접 적용' },
      { code: 'CONSTRUCTION_CUSTOM_V3',   name: 'CUSTOM',   price: 0,      basis: '별도 커스터마이징', featured: false, custom: true,  desc: '대형건설사 맞춤' },
    ],
  };

  // ══════ 법령진단 V4 확정 가격 (fallback) ══════
  var DIAG = {
    BUILDING: [
      { code: 'BUILDING_BASIC_DIAG_V4',    name: '정밀관리',  price: 149000, basis: '5,000㎡ 이하', featured: true },
      { code: 'BUILDING_STANDARD_DIAG_V4', name: '대형건물',  price: 349000, basis: '5,000㎡ 초과', featured: false },
    ],
    INDUSTRY: [
      { code: 'INDUSTRY_STARTER_DIAG_V4',  name: 'STARTER',  price: 149000, basis: '49인 이하',    featured: false },
      { code: 'INDUSTRY_BUSINESS_DIAG_V4', name: 'BUSINESS', price: 299000, basis: '50~299인',     featured: true },
      { code: 'INDUSTRY_PRO_DIAG_V4',      name: 'PRO',      price: 499000, basis: '300인 이상',   featured: false },
    ],
    CONSTRUCTION: [
      { code: 'CONSTRUCTION_STANDARD_DIAG_V4', name: 'STANDARD', price: 249000, basis: '50억 미만', featured: true },
      { code: 'CONSTRUCTION_PREMIUM_DIAG_V4',  name: 'PREMIUM',  price: 499000, basis: '50억 이상', featured: false },
    ],
  };

  // ══════ 공통 설정 ══════
  var CONFIG = {
    vatRate: 1.1,
    currency: 'WON',
    memberLimit: '무제한',       // V3부터 인원 무제한
    annualDiscount: 2,           // 연간 결제 시 2개월 무료 (10개월분)
    creditPolicy: {              // V4 전환 크레딧
      enabled: true,
      days: 30,
      rate: 1.0,                 // 100% 크레딧
      message: '유료 법령진단 구매 후 30일 이내 SaaS 가입 시 진단비 100% 크레딧 제공',
    },
    labels: {
      productName: '안전관리 설계서',    // "PDF 리포트" 금지
      saasUnit: '시설 1개 기준 / 월',
      diagUnit: '1회 진단',
      vatNote: 'VAT 별도',
    },
    sectorNotes: {
      BUILDING:     '건물 면적에 따라 적용되는 법조항이 달라집니다.',
      INDUSTRY:     '상시근로자 수에 따라 법적 의무가 단계적으로 증가합니다.',
      CONSTRUCTION: '공사금액에 따라 적용되는 법조항이 달라집니다.',
    },
  };

  // ══════ API에서 최신 가격 조회 (실패 시 fallback 사용) ══════
  var _apiSaas = null;
  var _apiDiag = null;

  async function fetchFromAPI() {
    try {
      var [saasRes, diagRes] = await Promise.allSettled([
        fetch(API_BASE + '/public/pricing/saas-plans'),
        fetch(API_BASE + '/public/pricing/diagnosis-reports'),
      ]);
      if (saasRes.status === 'fulfilled' && saasRes.value.ok) {
        var sj = await saasRes.value.json();
        _apiSaas = sj.data || sj.plans || sj || [];
      }
      if (diagRes.status === 'fulfilled' && diagRes.value.ok) {
        var dj = await diagRes.value.json();
        _apiDiag = dj.data || dj.reports || dj || [];
      }
    } catch(e) {
      console.warn('[TAI_PRICING] API fetch failed, using fallback:', e.message);
    }
  }

  // ══════ 가격 조회 함수 ══════

  function getSaasPlans(sector) {
    sector = (sector || '').toUpperCase();
    // API 데이터가 있으면 우선 사용
    if (_apiSaas && _apiSaas.length) {
      var filtered = _apiSaas.filter(function(p) {
        return (p.sector || p.plan_sector || '').toUpperCase() === sector;
      });
      if (filtered.length) return normalizeSaasAPI(filtered);
    }
    return SAAS[sector] || [];
  }

  function getDiagPlans(sector) {
    sector = (sector || '').toUpperCase();
    if (_apiDiag && _apiDiag.length) {
      var filtered = _apiDiag.filter(function(r) {
        return (r.sector || '').toUpperCase() === sector;
      });
      if (filtered.length) return normalizeDiagAPI(filtered);
    }
    return DIAG[sector] || [];
  }

  function getAllDiagPlans() {
    var all = [];
    ['BUILDING', 'INDUSTRY', 'CONSTRUCTION'].forEach(function(s) {
      getDiagPlans(s).forEach(function(p) { p.sector = s; all.push(p); });
    });
    return all;
  }

  function normalizeSaasAPI(raw) {
    return raw.map(function(p) {
      return {
        code:     p.plan_code || p.code || '',
        name:     p.plan_name || p.display_name || p.name || '',
        price:    parseInt(p.monthly_base_fee || p.price_monthly || p.price || 0),
        basis:    p.basis || p.target || '',
        featured: !!(p.is_recommended || p.featured),
        custom:   !!(p.is_custom || (p.plan_name || '').toUpperCase() === 'CUSTOM'),
        desc:     p.description || p.desc || '',
      };
    });
  }

  function normalizeDiagAPI(raw) {
    return raw.map(function(r) {
      return {
        code:     r.plan_code || r.facility_type_code || r.code || '',
        name:     r.plan_name || r.display_name || r.name || '',
        price:    parseInt(r.total_report_fee || r.price || r.amount || 0),
        basis:    r.basis || '',
        featured: !!(r.is_recommended || r.featured),
      };
    });
  }

  // ══════ 유틸 ══════

  function fmt(n) { return n.toLocaleString('ko-KR'); }

  function annualPrice(monthly) {
    return monthly * (12 - CONFIG.annualDiscount);
  }

  function annualMonthly(monthly) {
    return Math.round(annualPrice(monthly) / 12);
  }

  // ══════ Public API ══════
  return {
    SAAS: SAAS,
    DIAG: DIAG,
    CONFIG: CONFIG,
    fetchFromAPI: fetchFromAPI,
    getSaasPlans: getSaasPlans,
    getDiagPlans: getDiagPlans,
    getAllDiagPlans: getAllDiagPlans,
    fmt: fmt,
    annualPrice: annualPrice,
    annualMonthly: annualMonthly,
  };

})();
