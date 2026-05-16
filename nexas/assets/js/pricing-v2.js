/**
 * pricing-v2.js — DB 완전 연동 버전
 * pricing.html의 인라인 IIFE가 렌더링한 후, DB 데이터로 전체 카드를 재렌더링.
 * 하드코딩 FALLBACK을 완전히 대체.
 *
 * pricing-test-patch.js 대체.
 */
(function(){
'use strict';
var API = 'https://api.taieng.co.kr';
var isAnnual = false;
var _saasPlans = null;
var _diagReports = null;

// ── 섹터 레이블 ──
var SECTOR_LABELS = {
  BUILDING: '건물·시설', INDUSTRY: '제조·산업', CONSTRUCTION: '건설현장'
};

// ── API에서 전체 데이터 로드 ──
async function loadFromDB(){
  try {
    var res = await fetch(API+'/public/pricing/all');
    var json = await res.json();
    _saasPlans = json.saas_plans || [];
    _diagReports = json.diagnosis_plans || [];
  } catch(e){
    console.warn('[pricing-v2] API error:', e);
    return; // API 실패 시 기존 렌더링 유지
  }

  reRenderSaas('BUILDING', 'building');
  reRenderSaas('INDUSTRY', 'industry');
  reRenderSaas('CONSTRUCTION', 'construction');
  reRenderDiag();
}

// ══════════════════════════════════════════════════════════════
// SaaS 카드 렌더링
// ══════════════════════════════════════════════════════════════

function getSaasBySector(sector){
  return (_saasPlans||[]).filter(function(p){
    return (p.sector_code||'').toUpperCase() === sector.toUpperCase();
  });
}

function reRenderSaas(sector, domKey){
  var container = document.getElementById(domKey+'-cards');
  if(!container) return;
  var plans = getSaasBySector(sector);
  if(!plans.length) return; // DB 데이터 없으면 기존 유지

  container.innerHTML = plans.map(function(p){ return buildSaasCard(p); }).join('');
  container.style.display = '';
  var loading = document.getElementById(domKey+'-loading');
  if(loading) loading.style.display = 'none';
}

function buildSaasCard(p){
  var mon = parseInt(p.monthly_base_fee||0);
  var isCustom = p.is_custom;
  var isFeat = p.is_recommended;
  var features = p.features || [];
  if(typeof features === 'string') try { features = JSON.parse(features); } catch(e){ features = []; }
  var target = p.target || p.description || '';
  var name = p.display_name || p.plan_name || '';
  var incUsers = parseInt(p.included_users||10);
  var overFee = parseInt(p.extra_user_fee_v2||3000);
  var badge = p.badge_color || '';

  var cls = 'plan-card' + (isFeat?' featured':'') + (isCustom?' custom-card':'');
  if(badge==='danger') cls += '" style="border-color:#ff9500;';

  // 뱃지
  var badgeHtml = '';
  if(isFeat) badgeHtml = '<div class="plan-badge">✨ 가장 많이 선택</div>';
  else if(badge==='danger') badgeHtml = '<div class="plan-badge" style="background:#ff9500;">⚠️ 시험결제</div>';

  // 가격
  var priceHtml;
  if(isCustom){
    priceHtml = '<div class="plan-custom-price">별도 협의</div><div class="plan-price-sub" style="color:#94a3b8;">사업장·규모에 따라 결정</div><div class="plan-vat">&nbsp;</div>';
  } else {
    priceHtml = '<div class="plan-price"><span class="price-display" data-monthly="'+mon+'">'+mon.toLocaleString('ko-KR')+'</span>원</div>'
      +'<div class="plan-price-sub">/ 사업장 · <span class="period-unit">월</span></div>'
      +'<div class="plan-vat">VAT 별도</div>';
  }

  // 포함 인원
  var quotaHtml = '';
  if(!isCustom && incUsers < 99999){
    quotaHtml = '<div class="plan-quota-box">'
      +'<div class="q-row"><span class="q-label">👥 포함 인원</span><span class="q-val">'+incUsers+'명</span></div>'
      +'<div class="q-over">초과 인원당 '+overFee.toLocaleString('ko-KR')+'원/명/월</div>'
      +'</div>';
  }

  var featsHtml = features.map(function(f){ return '<li>'+f+'</li>'; }).join('');
  var targetHtml = target ? '<div class="mb-2" style="font-size:.78rem;color:#64748b;">'+target+'</div>' : '';

  var btnHtml;
  if(isCustom){
    btnHtml = '<a href="fix-request.html?from=pricing&type=general" class="btn btn-border" style="width:100%;font-weight:700;border-color:#7c3aed;color:#7c3aed;">도입 문의하기</a>';
  } else {
    var btnCls = isFeat ? 'btn-base' : 'btn-border';
    var btnStyle = badge==='danger' ? 'border-color:#ff9500;color:#ff9500;' : '';
    btnHtml = '<button class="btn '+btnCls+'" style="width:100%;font-weight:700;'+btnStyle+'"'
      +' onclick="startSaasPayment(\''+name.replace(/'/g,"\\'")+'\''
      +',\''+p.sector_code+'\''
      +','+mon+')">'
      +(badge==='danger' ? '시험 구독 ' : '구독 문의 / 결제')
      +'</button>';
  }

  return '<div class="col-lg-4 col-md-6"><div class="'+cls+'">'
    +badgeHtml
    +'<div class="plan-name" style="'+(isCustom?'color:#7c3aed;':(badge==='danger'?'color:#ff9500;':''))+'">'+name+'</div>'
    +priceHtml
    +'<div class="plan-divider"></div>'
    +targetHtml
    +quotaHtml
    +'<ul class="plan-features'+(isCustom?' custom-feat':'')+'">'+featsHtml+'</ul>'
    +btnHtml
    +'</div></div>';
}

// ══════════════════════════════════════════════════════════════
// 법령진단 카드 렌더링
// ══════════════════════════════════════════════════════════════

function reRenderDiag(){
  var mainCards = document.getElementById('diag-main-cards');
  if(!mainCards) return;
  var reports = (_diagReports||[]).filter(function(r){ return !r.is_special; });
  if(!reports.length) return;

  mainCards.innerHTML = reports.map(function(r){ return buildDiagCard(r); }).join('');
  mainCards.style.display = '';
  var loading = document.getElementById('diag-loading');
  if(loading) loading.style.display = 'none';

  // 특수시설
  var specials = (_diagReports||[]).filter(function(r){ return r.is_special; });
  var specWrap = document.getElementById('special-wrap');
  var specCards = document.getElementById('diag-special-cards');
  if(specials.length && specWrap && specCards){
    specCards.innerHTML = specials.map(function(r){ return buildDiagCard(r); }).join('');
    specWrap.style.display = '';
  }
}

function buildDiagCard(r){
  var price = parseInt(r.total_report_fee||0);
  var icon = r.icon || '📋';
  var name = r.facility_type_name || '';
  var sub = r.sub_label || r.sector_display || '';
  var goodsName = r.goods_name || name;
  var isFeat = r.is_recommended;
  var isSpec = r.is_special;
  var features = r.features || [];
  if(typeof features === 'string') try { features = JSON.parse(features); } catch(e){ features = []; }
  var isTest = (r.facility_type_code||'').indexOf('TEST') >= 0;

  var col = isSpec ? 'col-lg-4 col-md-6' : 'col-lg-3 col-md-6';
  var cls = 'diag-card' + (isFeat?' recommended':'') + (isSpec?' special-card':'');
  if(isTest) cls += '" style="border-color:#ff9500;';

  var recBadge = '';
  if(isFeat) recBadge = '<div class="diag-rec-badge">⭐ 가장 많이 선택</div>';
  else if(isTest) recBadge = '<div class="diag-rec-badge" style="background:#ff9500;">⚠️ 시험결제</div>';

  var featHtml = features.map(function(f){ return '<li>'+f+'</li>'; }).join('');

  var btnCls = isFeat ? 'btn-base' : 'btn-border';
  var btnStyle = isTest ? 'border-color:#ff9500;color:#ff9500;' : (isSpec ? 'border-color:#7c3aed;color:#7c3aed;' : '');

  return '<div class="'+col+'"><div class="'+cls+'">'
    +recBadge
    +'<span class="diag-icon"'+(isFeat?' style="margin-top:10px;"':'')+'>'+icon+'</span>'
    +'<div class="diag-type-name"'+(isTest?' style="color:#ff9500;"':'')+'>'+name+'</div>'
    +'<div class="diag-type-sub">'+sub+'</div>'
    +'<div class="diag-price">'+price.toLocaleString('ko-KR')+'<span class="unit">원</span></div>'
    +'<div class="diag-vat">VAT 별도 · 단건 1회성</div>'
    +'<div class="diag-period"'+(isTest?' style="color:#ff9500;"':'')+'>'+(isTest?'⚠️ PG 결제 테스트':'🕐 서비스 제공기간 12개월')+'</div>'
    +'<hr class="diag-divider">'
    +'<ul class="diag-features">'+featHtml+'</ul>'
    +'<button class="btn '+btnCls+'" style="width:100%;font-weight:700;'+btnStyle+'"'
    +' onclick="startDiagPayment(\''+goodsName.replace(/'/g,"\\'")+'\''+','+price+')">'
    +(isTest?'시험 결제 ':'바로 결제 ')+price.toLocaleString('ko-KR')+'원</button>'
    +'</div></div>';
}

// ── 연간/월간 토글 동기화 ──
var origToggle = window.toggleBilling;
window.toggleBilling = function(){
  if(origToggle) origToggle();
  isAnnual = document.getElementById('billing-toggle').classList.contains('on');
};

// ── 실행 ──
function waitAndLoad(){
  // 기존 IIFE가 카드 렌더링 완료한 후 덧어쓰기
  var el = document.getElementById('building-cards');
  if(el && el.children.length > 0){
    loadFromDB();
  } else {
    setTimeout(waitAndLoad, 200);
  }
}

if(document.readyState==='loading'){
  document.addEventListener('DOMContentLoaded', function(){ setTimeout(waitAndLoad, 600); });
} else {
  setTimeout(waitAndLoad, 600);
}

})();
