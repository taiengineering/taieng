/**
 * TAI Pricing Config v4 — Single Source of Truth
 * 가격 변경 시 이 파일만 수정하면 전 페이지에 반영됩니다.
 */
'use strict';

window.TAI_PRICING = (function() {

  var API_BASE = 'https://api.taieng.co.kr';

  // ══════ SaaS V3 확정 가격 ══════
  var SAAS = {
    BUILDING: [
      { code: 'BUILDING_BASIC_V3', name: '정밀관리', price: 149000, basis: '5,000㎡ 이하', featured: true, custom: false, desc: '안전관리자 선임 의무 포함',
        features: ['건물 전체 정보 등록 → 법적 의무 자동 산출','점검 일정 + D-day 알림 (SMS)','점검 기록 자동 보관 + 서류 자동 생성','안전관리자 대시보드','보고서 자동 생성','개정된 최신법으로 진단'] },
      { code: 'BUILDING_STANDARD_V3', name: '대형건물', price: 349000, basis: '5,000㎡ 초과', featured: false, custom: false, desc: '석면·에너지·냉동 관련 의무 포함',
        features: ['정밀관리와 동일 기능','5,000㎡ 초과 추가 법조항 반영','석면·에너지·냉동 관련 의무 포함'] },
      { code: 'BUILDING_CUSTOM_V3', name: 'Enterprise', price: 0, basis: '별도 커스터마이징', featured: false, custom: true, desc: '다동·복합 시설 특수 구성',
        features: ['별도 커스터마이징이 필요한 경우','다동·복합 시설 특수 구성'] },
    ],
    INDUSTRY: [
      { code: 'INDUSTRY_STARTER_V3', name: 'STARTER', price: 149000, basis: '49인 이하', featured: false, custom: false, desc: '안전보건관리담당자',
        features: ['건물 + 특수설비 등록 → 기본 법적 의무 산출','점검 일정 + D-day 알림','안전관리자 대시보드','개정된 최신법으로 진단'] },
      { code: 'INDUSTRY_BUSINESS_V3', name: 'BUSINESS', price: 299000, basis: '50~299인', featured: true, custom: false, desc: '안전관리자 선임 (위탁 가능)',
        features: ['STARTER 전체 포함','공정 등록 → 공정별 추가 법적 의무 산출','현장 QR 점검 앱 + TBM 전자서명','보고서 자동 생성'] },
      { code: 'INDUSTRY_PRO_V3', name: 'PRO', price: 499000, basis: '300~499인', featured: false, custom: false, desc: '안전관리자 전담 (위탁 불가)',
        features: ['BUSINESS 전체 포함','설비 등록 → 설비별 추가 법적 의무 산출','설비 QR 관리'] },
      { code: 'INDUSTRY_CUSTOM_V3', name: 'CUSTOM', price: 0, basis: '500인 이상', featured: false, custom: true, desc: '이사회 보고·승인 의무',
        features: ['별도 커스터마이징이 필요한 경우'] },
    ],
    CONSTRUCTION: [
      { code: 'CONSTRUCTION_STANDARD_V3', name: 'STANDARD', price: 249000, basis: '50억 미만', featured: true, custom: false, desc: '건설안전법 기본 의무',
        features: ['공사장 법령 의무 자동 산출','점검 일정 + D-day 알림','현장 QR 점검 앱 + TBM 전자서명','하도급 관리','보고서 자동 생성'] },
      { code: 'CONSTRUCTION_PREMIUM_V3', name: 'PREMIUM', price: 499000, basis: '50억 이상', featured: false, custom: false, desc: '중대재해처벌법 직접 적용',
        features: ['STANDARD와 동일 기능','50억 이상 추가 법조항 반영','중대재해처벌법 직접 적용'] },
      { code: 'CONSTRUCTION_CUSTOM_V3', name: 'CUSTOM', price: 0, basis: '별도 커스터마이징', featured: false, custom: true, desc: '대형건설사 맞춤',
        features: ['별도 커스터마이징이 필요한 경우'] },
    ],
  };

  // ══════ 법령진단 V4 확정 가격 ══════
  var DIAG = {
    BUILDING: [
      { code: 'BUILDING_BASIC_DIAG_V4', name: '정밀관리', price: 149000, basis: '5,000㎡ 이하', featured: true,
        features: ['무료 진단 전체 포함','안전관리 설계서 (웹 + PDF + Excel)','의무별 실행 카드 (기한·서류·신고처)','관련 판례 연동','과태료 합산 분석','체크리스트 (출력용)','기안 PDF (품의서 첨부용)'] },
      { code: 'BUILDING_STANDARD_DIAG_V4', name: '대형건물', price: 349000, basis: '5,000㎡ 초과', featured: false,
        features: ['정밀관리 진단 전체 포함','다층·복합 건물 추가 법조항 적용','석면·에너지·냉동 관련 의무 포함'] },
    ],
    INDUSTRY: [
      { code: 'INDUSTRY_STARTER_DIAG_V4', name: 'STARTER', price: 149000, basis: '49인 이하', featured: false,
        features: ['무료 진단 전체 포함','안전관리 설계서 (웹 + PDF + Excel)','상시근로자 49인 이하 사업장','선임·신고 의무 상세','관련 판례 연동','과태료 합산 분석'] },
      { code: 'INDUSTRY_BUSINESS_DIAG_V4', name: 'BUSINESS', price: 299000, basis: '50~299인', featured: true,
        features: ['STARTER 진단 전체 포함','50~299인 사업장 추가 의무 적용','안전관리자 선임·위탁 의무 포함','체크리스트 (출력용)','기안 PDF'] },
      { code: 'INDUSTRY_PRO_DIAG_V4', name: 'PRO', price: 499000, basis: '300인 이상', featured: false,
        features: ['BUSINESS 진단 전체 포함','300인 이상 사업장 추가 의무 적용','안전관리자 전담 선임 의무 포함'] },
    ],
    CONSTRUCTION: [
      { code: 'CONSTRUCTION_STANDARD_DIAG_V4', name: 'STANDARD', price: 249000, basis: '50억 미만', featured: true,
        features: ['무료 진단 전체 포함','안전관리 설계서 (웹 + PDF + Excel)','공종별 안전시설 기준','건설기술진흥법 의무 항목','관련 판례 연동','과태료 합산 분석'] },
      { code: 'CONSTRUCTION_PREMIUM_DIAG_V4', name: 'PREMIUM', price: 499000, basis: '50억 이상', featured: false,
        features: ['STANDARD 진단 전체 포함','중대재해처벌법 직접 적용 법조항','안전관리계획서 대응','협력업체 안전관리 의무'] },
    ],
  };

  var FREE_CARDS = {
    BUILDING: { inputs: '주소·면적·용도 등 8항목 입력', features: ['적용 법령·의무 목록 확인','선임 의무 해당 여부','개정된 최신법으로 진단'] },
    INDUSTRY: { inputs: '주소·업종·인원수·면적 4항목 입력', features: ['적용 법령·의무 목록 확인','안전관리자 선임 여부','개정된 최신법으로 진단'] },
    CONSTRUCTION: { inputs: '현장주소·공사금액·투입인원·공사기간 4항목 입력', features: ['적용 법령·의무 목록 확인','안전관리자 선임 여부','개정된 최신법으로 진단'] },
  };

  var CONFIG = {
    vatRate: 1.1,
    currency: 'WON',
    memberLimit: '무제한',
    annualDiscount: 2,
    creditPolicy: { enabled: true, days: 30, rate: 1.0, message: '유료 법령진단 구매 후 30일 이내 SaaS 가입 시 진단비 100% 크레딧 제공' },
    labels: { productName: '안전관리 설계서', saasUnit: '시설 1개 기준 / 월', diagUnit: '1회 진단', vatNote: 'VAT 별도' },
    sectorNotes: {
      BUILDING: '건물 면적에 따라 적용되는 법조항이 달라집니다.',
      INDUSTRY: '상시근로자 수에 따라 법적 의무가 단계적으로 증가합니다.',
      CONSTRUCTION: '공사금액에 따라 적용되는 법조항이 달라집니다.',
    },
  };

  // ══════ API ══════
  var _apiSaas = null, _apiDiag = null;
  async function fetchFromAPI() {
    try {
      var [saasRes, diagRes] = await Promise.allSettled([fetch(API_BASE+'/public/pricing/saas-plans'), fetch(API_BASE+'/public/pricing/diagnosis-reports')]);
      if (saasRes.status==='fulfilled' && saasRes.value.ok) { var sj=await saasRes.value.json(); _apiSaas=sj.data||sj.plans||sj||[]; }
      if (diagRes.status==='fulfilled' && diagRes.value.ok) { var dj=await diagRes.value.json(); _apiDiag=dj.data||dj.reports||dj||[]; }
    } catch(e) { console.warn('[TAI_PRICING] API fetch failed:', e.message); }
  }
  function getSaasPlans(sector) { sector=(sector||'').toUpperCase(); if(_apiSaas&&_apiSaas.length){var f=_apiSaas.filter(function(p){return(p.sector||p.plan_sector||'').toUpperCase()===sector;});if(f.length)return normalizeSaasAPI(f);} return SAAS[sector]||[]; }
  function getDiagPlans(sector) { sector=(sector||'').toUpperCase(); if(_apiDiag&&_apiDiag.length){var f=_apiDiag.filter(function(r){return(r.sector||'').toUpperCase()===sector;});if(f.length)return normalizeDiagAPI(f);} return DIAG[sector]||[]; }
  function normalizeSaasAPI(raw) { return raw.map(function(p){return{code:p.plan_code||p.code||'',name:p.plan_name||p.display_name||p.name||'',price:parseInt(p.monthly_base_fee||p.price_monthly||p.price||0),basis:p.basis||p.target||'',featured:!!(p.is_recommended||p.featured),custom:!!(p.is_custom||(p.plan_name||'').toUpperCase()==='CUSTOM'),desc:p.description||p.desc||'',features:p.features||[]};}); }
  function normalizeDiagAPI(raw) { return raw.map(function(r){return{code:r.plan_code||r.facility_type_code||r.code||'',name:r.plan_name||r.display_name||r.name||'',price:parseInt(r.total_report_fee||r.price||r.amount||0),basis:r.basis||'',featured:!!(r.is_recommended||r.featured),features:r.features||[]};}); }

  // ══════ 유틸 ══════
  function fmt(n) { return n.toLocaleString('ko-KR'); }
  function vatAmount(base) { return Math.round(base * (CONFIG.vatRate - 1)); }
  function totalWithVat(base) { return Math.round(base * CONFIG.vatRate); }
  function annualPrice(monthly) { return monthly * (12 - CONFIG.annualDiscount); }
  function annualMonthly(monthly) { return Math.round(annualPrice(monthly) / 12); }

  // ══════ Mount: diagnosis.html ══════
  function mountDiagnosisServiceCards() {
    var sectors = [
      { key: 'BUILDING', panel: 'panel-building', type: 'DIAG_BUILDING', cols: 'col-lg-4 col-md-6' },
      { key: 'INDUSTRY', panel: 'panel-industry', type: 'DIAG_INDUSTRY', cols: 'col-lg-3 col-md-6' },
      { key: 'CONSTRUCTION', panel: 'panel-construction', type: 'DIAG_CONSTRUCTION', cols: 'col-lg-4 col-md-6' },
    ];
    sectors.forEach(function(s) {
      var container = document.querySelector('#' + s.panel + ' .row');
      if (!container) return;
      var plans = getDiagPlans(s.key);
      var free = FREE_CARDS[s.key];
      var noFeats = ['의무별 실행 가이드','판례 연동',CONFIG.labels.productName];
      var html = '<div class="' + s.cols + '"><div class="price-card">'
        + '<div class="pc-tier">FREE</div><div class="pc-name">무료 기초 진단</div>'
        + '<div class="pc-price free">0원</div><div class="pc-unit">회원가입 없이 바로 시작</div><hr>'
        + '<ul><li>' + free.inputs + '</li>'
        + free.features.map(function(f){return '<li>'+f+'</li>';}).join('')
        + noFeats.map(function(f){return '<li class="no">'+f+'</li>';}).join('')
        + '</ul><a href="../free-diagnosis.html" class="pc-cta free-cta">무료 진단 시작하기</a>'
        + '</div></div>';
      html += plans.map(function(p) {
        var featHtml = (p.features||[]).map(function(f){return '<li>'+f+'</li>';}).join('');
        return '<div class="' + s.cols + '"><div class="price-card' + (p.featured?' featured':'') + '">'
          + '<div class="pc-tier">' + p.name + '</div>'
          + '<div class="pc-name">' + p.basis + '</div>'
          + '<div class="pc-price">' + fmt(p.price) + '<span style="font-size:1rem;">원</span></div>'
          + '<div class="pc-unit">1회 진단 · VAT 별도</div>'
          + '<hr><ul>' + featHtml + '</ul>'
          + '<button class="pc-cta' + (p.featured?' blue-cta':'') + '" onclick="diagPay(\'' + s.type + '\',\'' + p.code + '\',' + p.price + ',\'' + p.name + ' 진단\')">결제하고 진단받기</button>'
          + '</div></div>';
      }).join('');
      container.innerHTML = html;
    });
  }

  // ══════ Mount: saas.html ══════
  function mountSaasServiceCards() {
    var sectors = [
      { key: 'BUILDING', panel: 'panel-building', type: 'SAAS_BUILDING' },
      { key: 'INDUSTRY', panel: 'panel-industry', type: 'SAAS_FACILITY' },
      { key: 'CONSTRUCTION', panel: 'panel-construction', type: 'SAAS_CONSTRUCTION' },
    ];
    sectors.forEach(function(s) {
      var container = document.querySelector('#' + s.panel + ' .row');
      if (!container) return;
      var plans = getSaasPlans(s.key);
      var colSize = plans.length > 3 ? 'col-lg-3 col-md-6' : 'col-xl-4 col-md-6';
      var html = plans.map(function(p) {
        var featHtml = (p.features||[]).map(function(f){return '<li>'+f+'</li>';}).join('');
        if (p.custom) {
          return '<div class="' + colSize + '"><div class="sp-price">'
            + '<div class="tier">' + p.name + '</div><div class="plan-name">' + p.desc + '</div>'
            + '<div class="amt consult">별도 협의</div><div class="unit">커스터마이징 · 범위 협의</div><hr>'
            + '<ul>' + featHtml + '</ul>'
            + '<a href="../fix-request.html?from=saas&type=general" class="sp-price-cta consult-cta">도입 문의</a>'
            + '</div></div>';
        }
        return '<div class="' + colSize + '"><div class="sp-price">'
          + '<div class="tier">' + p.name + '</div>'
          + '<div class="plan-name">' + p.desc + '<br><small style="font-weight:500;color:#94a3b8;font-size:.78rem;">' + p.basis + '</small></div>'
          + '<div class="amt">' + fmt(p.price) + '<span style="font-size:1rem;">원</span></div>'
          + '<div class="unit">/월 · VAT 별도</div>'
          + '<hr><ul>' + featHtml + '</ul>'
          + '<button class="sp-price-cta" onclick="spPay(event,\'' + s.type + '\',\'' + p.code + '\',' + p.price + ',\'TAI Safe ' + p.name + '\')">결제하기</button>'
          + '</div></div>';
      }).join('');
      container.innerHTML = html;
    });
  }

  return {
    SAAS: SAAS, DIAG: DIAG, CONFIG: CONFIG,
    fetchFromAPI: fetchFromAPI, getSaasPlans: getSaasPlans, getDiagPlans: getDiagPlans,
    getAllDiagPlans: function(){var a=[];['BUILDING','INDUSTRY','CONSTRUCTION'].forEach(function(s){getDiagPlans(s).forEach(function(p){p.sector=s;a.push(p);});});return a;},
    fmt: fmt, vatAmount: vatAmount, totalWithVat: totalWithVat,
    annualPrice: annualPrice, annualMonthly: annualMonthly,
    mountDiagnosisServiceCards: mountDiagnosisServiceCards,
    mountSaasServiceCards: mountSaasServiceCards,
  };
})();
