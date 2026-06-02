# 작업지시서: 가격 하드코딩 → tai-pricing-config.js 참조로 리팩토링

## 배경
diagnosis.html, saas.html, pricing.html에 가격이 하드코딩되어 있어 가격 변경 시 3개 파일을 모두 수정해야 함.
`assets/js/tai-pricing-config.js`를 단일 소스로 만들어 모든 페이지가 참조하도록 변경.

## 생성 완료된 파일
- `nexas/assets/js/tai-pricing-config.js` — 가격 단일 소스 (SaaS V3 + 법령진단 V4)

## 구조
```
window.TAI_PRICING.SAAS.BUILDING[0]     → { code, name, price, basis, featured, custom, desc }
window.TAI_PRICING.SAAS.INDUSTRY[0]     → ...
window.TAI_PRICING.SAAS.CONSTRUCTION[0] → ...
window.TAI_PRICING.DIAG.BUILDING[0]     → { code, name, price, basis, featured }
window.TAI_PRICING.DIAG.INDUSTRY[0]     → ...
window.TAI_PRICING.DIAG.CONSTRUCTION[0] → ...
window.TAI_PRICING.CONFIG               → { vatRate, memberLimit, labels, sectorNotes, creditPolicy }
window.TAI_PRICING.getSaasPlans(sector) → API 우선, fallback 자동
window.TAI_PRICING.getDiagPlans(sector) → API 우선, fallback 자동
window.TAI_PRICING.fmt(number)          → 한국어 포맷 (예: "149,000")
```

## 리팩토링 대상 (3개 파일)

### 1. `nexas/service/diagnosis.html`

**현재:** 가격 카드가 HTML에 하드코딩 (99,000, 79,000, 149,000 등)
**변경:**

1. `<script src="../assets/js/tai-pricing-config.js"></script>` 추가 (footer.js 앞)
2. 가격 카드 영역을 빈 컨테이너로 변경:
```html
<div class="sector-panel active" id="panel-building">
  <div class="sector-note">...</div>
  <div id="diag-building-cards" class="row g-4 justify-content-center"></div>
</div>
```
3. JS로 렌더링:
```javascript
function renderDiagSector(sector, containerId) {
  var P = window.TAI_PRICING;
  var plans = P.getDiagPlans(sector);
  var freeCard = '...'; // 무료 카드는 고정 HTML
  var html = freeCard + plans.map(function(p) {
    return '<div class="col-lg-'+(sector==='INDUSTRY'?'3':'4')+' col-md-6">'
      + '<div class="price-card'+(p.featured?' featured':'')+'">'
      + '<div class="pc-tier">'+p.name+'</div>'
      + '<div class="pc-name">'+p.basis+'<br><small style="...">'+P.fmt(p.price)+'원</small></div>'
      + '<div class="pc-price">'+P.fmt(p.price)+'<span style="font-size:1rem;">원</span></div>'
      + '<div class="pc-unit">1회 진단 · VAT 별도</div><hr>'
      + '<ul><li>'+P.CONFIG.labels.productName+' (웹 + PDF + Excel)</li>...</ul>'
      + '<button class="pc-cta" onclick="diagPay(\'DIAG_'+sector+'\',\''+p.code+'\','+p.price+',\''+sector+' '+p.name+' 진단\')">결제하고 진단받기</button>'
      + '</div></div>';
  }).join('');
  document.getElementById(containerId).innerHTML = html;
}
// 초기화
renderDiagSector('BUILDING', 'diag-building-cards');
renderDiagSector('INDUSTRY', 'diag-industry-cards');
renderDiagSector('CONSTRUCTION', 'diag-construction-cards');
```
4. diagPay() 함수는 그대로 유지 (이니시스 결제 로직)

### 2. `nexas/service/saas.html`

**현재:** 가격이 HTML에 하드코딩 (149,000, 299,000 등) + planCode가 V2
**변경:**

1. `<script src="../assets/js/tai-pricing-config.js"></script>` 추가
2. 가격 카드 영역을 빈 컨테이너로 변경:
```html
<div class="sp-sector-panel active" id="panel-building">
  <div class="sp-sector-note">...</div>
  <div id="saas-building-cards" class="row g-4 justify-content-center"></div>
</div>
```
3. JS로 렌더링:
```javascript
function renderSaasSector(sector, containerId) {
  var P = window.TAI_PRICING;
  var plans = P.getSaasPlans(sector);
  var html = plans.map(function(p) {
    if (p.custom) {
      return '...(협의 카드)...';
    }
    return '<div class="col-lg-3 col-md-6"><div class="sp-price">'
      + '<div class="tier">'+p.name+'</div>'
      + '<div class="plan-name">'+p.desc+'</div>'
      + '<div class="amt">'+P.fmt(p.price)+'<span style="font-size:1rem;">원</span></div>'
      + '<div class="unit">/월 · VAT 별도</div><hr>'
      + '<ul>...</ul>'
      + '<button class="sp-price-cta" onclick="spPay(event,\'SAAS_'+sector+'\',\''+p.code+'\','+p.price+',\'TAI Safe '+sector+' '+p.name+'\')">결제하기</button>'
      + '</div></div>';
  }).join('');
  document.getElementById(containerId).innerHTML = html;
}
```
4. spPay() 함수는 그대로 유지
5. sector-note의 텍스트도 `TAI_PRICING.CONFIG.sectorNotes[sector]`에서 가져오기

### 3. `nexas/pricing.html`

**현재:** SAAS_FALLBACK과 DIAG_META에 하드코딩
**변경:**

1. `<script src="assets/js/tai-pricing-config.js"></script>` 추가
2. SAAS_FALLBACK 전체 삭제 → `TAI_PRICING.getSaasPlans(sector)` 사용
3. DIAG_META 가격 부분 삭제 → `TAI_PRICING.getDiagPlans(sector)` 사용
4. loadPricingData()에서:
```javascript
async function loadPricingData() {
  await TAI_PRICING.fetchFromAPI(); // API 조회 (실패 시 fallback 자동)
  renderSaasSector('BUILDING', 'building');
  renderSaasSector('INDUSTRY', 'industry');
  renderSaasSector('CONSTRUCTION', 'construction');
  renderDiagSection();
}
```
5. 인원 관련: "포함 10명 초과 시 3,000원/명" → `TAI_PRICING.CONFIG.memberLimit` ("무제한") 사용
6. "PDF 리포트" → `TAI_PRICING.CONFIG.labels.productName` ("안전관리 설계서") 사용

## 추가 수정 (saas.html planCode)
현재 saas.html의 spPay() 호출에서 planCode가 V2:
- `INDUSTRY_STARTER_V2` → `INDUSTRY_STARTER_V3`
- `INDUSTRY_BUSINESS_V2` → `INDUSTRY_BUSINESS_V3`
- 등등
리팩토링 시 config에서 `p.code`를 사용하므로 자동 해결됨.

## 규칙
- `tai-pricing-config.js`의 가격이 유일한 소스
- HTML에 금액 하드코딩 금지
- "PDF 리포트" 금지 → `CONFIG.labels.productName` 사용
- "포함 10명" 금지 → `CONFIG.memberLimit` 사용
- 이니시스 결제 함수(diagPay, spPay)는 수정하지 않음 (amount만 config에서 가져옴)
