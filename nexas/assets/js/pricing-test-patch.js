/**
 * pricing-test-patch.js
 * 시험결제 10,000원 상품 카드를 pricing.html에 동적 삽입.
 * 이니시스 실키 발급 후 제거 또는 is_active=false 전환.
 */
(function(){
'use strict';

function makeSaasTestCard(sector, label){
  return '<div class="col-lg-4 col-md-6"><div class="plan-card" style="border-color:#ff9500;">'
    +'<div class="plan-badge" style="background:#ff9500;">⚠️ 시험결제</div>'
    +'<div class="plan-name" style="color:#ff9500;">시험결제</div>'
    +'<div class="plan-price"><span>10,000</span>원</div>'
    +'<div class="plan-price-sub">/ 사업장 · 월</div>'
    +'<div class="plan-vat">VAT 포함</div>'
    +'<hr class="plan-divider">'
    +'<div class="mb-2" style="font-size:.78rem;color:#ff9500;font-weight:700;">⚠️ '+label+' PG 결제 테스트 상품</div>'
    +'<ul class="plan-features"><li>KG이니시스 PG 결제 테스트</li><li>실제 결제 발생 (1만원)</li><li>이니시스 승인 확인용</li></ul>'
    +'<button class="btn btn-border" style="width:100%;font-weight:700;border-color:#ff9500;color:#ff9500;"'
    +' onclick="startSaasPayment(\'\uc2dc\ud5d8\uacb0\uc81c\',\''+sector+'\',10000)">시험 구독 10,000원</button>'
    +'</div></div>';
}

function makeDiagTestCard(label){
  return '<div class="col-lg-3 col-md-6"><div class="diag-card" style="border-color:#ff9500;">'
    +'<span class="diag-icon">⚠️</span>'
    +'<div class="diag-type-name" style="color:#ff9500;">'+label+' 시험</div>'
    +'<div class="diag-type-sub">PG 결제 테스트</div>'
    +'<div class="diag-price">10,000<span class="unit">원</span></div>'
    +'<div class="diag-vat">VAT 포함 · 시험결제</div>'
    +'<div class="diag-period" style="color:#ff9500;">⚠️ PG 결제 테스트 상품</div>'
    +'<hr class="diag-divider">'
    +'<ul class="diag-features"><li>KG이니시스 결제 테스트</li><li>실제 결제 발생 (1만원)</li></ul>'
    +'<button class="btn btn-border" style="width:100%;font-weight:700;border-color:#ff9500;color:#ff9500;"'
    +' onclick="startDiagPayment(\''+label+' \uc2dc\ud5d8\uc9c4\ub2e8\',10000)">시험 결제 10,000원</button>'
    +'</div></div>';
}

function inject(){
  var b=document.getElementById('building-cards');
  var i=document.getElementById('industry-cards');
  var c=document.getElementById('construction-cards');
  var d=document.getElementById('diag-main-cards');

  if(b) b.insertAdjacentHTML('afterbegin', makeSaasTestCard('BUILDING','건물'));
  if(i) i.insertAdjacentHTML('afterbegin', makeSaasTestCard('INDUSTRY','산업'));
  if(c) c.insertAdjacentHTML('afterbegin', makeSaasTestCard('CONSTRUCTION','건설'));

  if(d){
    d.insertAdjacentHTML('afterbegin', makeDiagTestCard('건설'));
    d.insertAdjacentHTML('afterbegin', makeDiagTestCard('산업'));
    d.insertAdjacentHTML('afterbegin', makeDiagTestCard('건물'));
  }
}

var tries=0;
function poll(){
  var b=document.getElementById('building-cards');
  if(b && b.children.length>0){ inject(); }
  else if(tries<30){ tries++; setTimeout(poll,300); }
}

if(document.readyState==='loading'){
  document.addEventListener('DOMContentLoaded',function(){setTimeout(poll,500);});
} else { setTimeout(poll,500); }

})();
