# [Cursor 작업지시] pricing.html — 가격 단일 소스(TAI_PRICING) 정렬 (2026-06-03)

> 기준 페이지: `nexas/service/saas.html` (이미 올바르게 단일 소스 사용)
> 단일 소스: `nexas/assets/js/tai-pricing-config.js` (`window.TAI_PRICING`)
> 원칙: **임의판단 금지. 확장 금지. 아래 명시된 변경만 수행.**

---

## 0. 작업 범위
- **수정 대상: `nexas/pricing.html` 1파일.** (config·다른 페이지·다른 JS 수정 금지)
- 목표: 화면의 SaaS·법령진단 가격과 정책 문구가 **오직 `window.TAI_PRICING`(=tai-pricing-config.js)** 에서 나오게 한다. saas.html과 동일한 출처.

### 금지
- `tai-pricing-config.js` 수정 금지 (`getSaasPlans`/`getDiagPlans`/`CONFIG` 이미 존재함).
- 결제 흐름 변경 금지 — `startSaasPayment`/`proceedDiagPayment`의 현재 동작(`fix-request.html` 이동)은 **그대로 유지**. (실결제 전환은 별도 범위)
- 페이지 레이아웃·탭 구조·CSS 클래스(`.plan-card`/`.diag-card`/탭) 변경 금지.
- 새 라이브러리/스크립트 추가 금지.

---

## 1. `pricing-v2.js` 제거 (DB 덮어쓰기 차단)
파일 맨 끝 부분의 아래 한 줄을 **삭제**:
```html
<script src="/assets/js/pricing-v2.js" defer></script>
```
(이 스크립트가 `/public/pricing/all` DB값으로 카드를 재렌더 → 단일 소스를 무력화. saas.html엔 없음.)

## 2. 인라인 스크립트: 죽은 config 참조 → 단일 소스 함수로 교체
인라인 `pricing.js v4` IIFE 내부에서:

**(2-1) 죽은 참조 제거.** 아래 블록을 삭제:
```js
var SAAS_FALLBACK = _P.SAAS_FALLBACK || {};
var MAIN_CODES = _P.MAIN_DIAG_CODES || [];
var SPECIAL_CODES = _P.SPECIAL_DIAG_CODES || [];
var DIAG_META = _P.DIAG_META || {};
```
(`var _P = window.TAI_PRICING || {};` 줄은 유지)

**(2-2) 데이터 로딩을 config에 위임.** `loadPricingData()`의 자체 `fetch(...)` 2건을 제거하고, 대신 config의 API override를 먼저 태운 뒤 렌더하도록 변경:
```js
async function loadPricingData(){
  if (_P.fetchFromAPI) { try { await _P.fetchFromAPI(); } catch(e){} }
  renderSaasSector('BUILDING', 'building');
  renderSaasSector('INDUSTRY', 'industry');
  renderSaasSector('CONSTRUCTION', 'construction');
  renderDiagSection();
  var params = new URLSearchParams(location.search);
  var highlight = params.get('highlight') || params.get('recommend');
  if(highlight) highlightPlan(highlight.toUpperCase());
}
```
(기존 `_saasPlans`/`_diagReports`/`getPlansBySector`/`normalizeSaasPlans`/`getDiagPrice`는 더 이상 사용 안 함 — 호출부 제거 후 미사용 함수는 남겨둬도 무방하나 호출하지 말 것.)

**(2-3) SaaS 렌더를 `getSaasPlans`로.** `renderSaasSector`를 config 데이터 기반으로:
```js
function renderSaasSector(sector, domKey){
  var loading = document.getElementById(domKey+'-loading');
  var cards   = document.getElementById(domKey+'-cards');
  var plans = (_P.getSaasPlans ? _P.getSaasPlans(sector) : []).map(function(p){
    return {
      plan_code: p.code, plan_name: p.name, sector: sector,
      price_monthly: p.price, is_recommended: p.featured, is_custom: p.custom,
      target: p.desc, basis: p.basis, features: p.features || []
    };
  });
  cards.innerHTML = plans.map(function(p){ return renderSaasCard(p); }).join('');
  if(loading) loading.style.display = 'none';
  cards.style.display = '';
  cards.className = 'row g-4 justify-content-center';
}
```

**(2-4) `renderSaasCard`에서 "포함 인원/초과 3,000원" 박스 제거 (무제한 정책).**
`quotaHtml`을 만드는 블록과, 카드 조립부에서 `+quotaHtml`을 **삭제**. 대신 `basis`(면적/인원/공사금액 기준)를 plan-price-sub 근처에 한 줄로 노출:
- 가격 표시 아래에 `<div class="plan-vat">VAT 별도 · 관리자/작업자 무제한</div>` 형태로 통일(기존 `VAT 별도`를 이 문구로 교체).
- `targetHtml`은 `p.target`(=desc) 유지, 그 옆/아래에 `p.basis`를 작은 글씨로 표시.

**(2-5) 법령진단 렌더를 `getDiagPlans`로.** `renderDiagSection`을 섹터 기반으로 재작성(특수시설/`MAIN_CODES`/`DIAG_META` 제거):
```js
function renderDiagSection(){
  var loading   = document.getElementById('diag-loading');
  var mainCards = document.getElementById('diag-main-cards');
  var specWrap  = document.getElementById('special-wrap');
  var sectors = ['BUILDING','INDUSTRY','CONSTRUCTION'];
  var html = '';
  sectors.forEach(function(sec){
    (_P.getDiagPlans ? _P.getDiagPlans(sec) : []).forEach(function(p){
      html += renderDiagCardV4(sec, p);
    });
  });
  if(loading) loading.style.display = 'none';
  mainCards.innerHTML = html;
  mainCards.style.display = '';
  if(specWrap) specWrap.style.display = 'none';   // V4 진단엔 특수시설 카드 없음
}
```
그리고 진단 카드 빌더를 config 필드(`code/name/price/basis/featured/features`)로 새로 작성(`renderDiagCardV4`). 기존 `.diag-card` 마크업/클래스 그대로 사용하되 가격·이름·기준·features는 config 값으로 채우고, 버튼은 기존 `startDiagPayment(goodsName, price)` 호출 유지(goodsName = `p.name + ' 진단'`).

## 3. 하드코딩된 구(舊)정책/가격 문구 정정 (V4 정렬)
- `<meta name="description">`에서 `59,000원~`, `99,000원~` 등 **구가격 수치 제거** (예: "건물·산업·건설 SaaS 구독과 법령진단으로 과태료 리스크를 해결합니다."). V4 가격 수치를 직접 적지 말 것(가격은 config가 단일 소스).
- "포함 10명", "초과 3,000원/명/월" 표기 **전부 제거 → "관리자/작업자 무제한"** 으로 교체:
  - billing-note(`사업장(시설/현장)당 월정액 · VAT 별도 · 포함 10명 초과 시 3,000원/명`) → `시설 1개 기준 · 월정액 · VAT 별도 · 관리자/작업자 무제한`
  - SaaS 모달의 `포함 인원`/`초과 단가` 행 삭제, `포함 인원 10명` 텍스트 삭제.
  - price-notice의 `포함 인원(10명) 초과 시 3,000원/명/월...` 문장 삭제.
  - FAQ의 "포함 인원 초과 시 어떻게 되나요?" 항목 → 무제한 안내로 교체 또는 삭제.
- 용어: "PDF 법령진단 **리포트**", "리포트 재발행" 등 "리포트" → **"안전관리 설계서"** (CONFIG.labels.productName 기준). diag 모달의 안내문 포함.

## 4. 완료 기준 (검증)
1. `pricing.html`에 `pricing-v2.js` 참조가 없다.
2. 페이지 로드 시 SaaS 3섹터·법령진단 카드가 **`tai-pricing-config.js`의 V4 가격**(건물 149K/349K, 산업 149K/299K/499K, 건설 249K/499K)으로 표시된다. (DB와 무관)
3. "포함 인원 10명 / 3,000원" 문구가 페이지 어디에도 없고 "관리자/작업자 무제한"으로 통일.
4. "리포트" 표기가 "안전관리 설계서"로 바뀜.
5. 결제 버튼 동작(fix-request 이동)은 기존과 동일(이번 변경 대상 아님).
6. `git diff`는 `nexas/pricing.html` 1파일만 변경.
