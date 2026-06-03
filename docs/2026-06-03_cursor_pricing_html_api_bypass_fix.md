# [Cursor 작업지시 #2] pricing.html — API 우회 제거 + 연간할인 토글 제거 (2026-06-03)

> 기준 문서: `tai-api/docs/PRICING_FINAL.md` (V4, 유일 가격 기준)
> 기준 페이지: `nexas/service/saas.html` (config-only 렌더, 정상 동작)
> 단일 소스: `nexas/assets/js/tai-pricing-config.js` (`window.TAI_PRICING`)
> 원칙: **임의판단 금지. 확장 금지. 추측 금지. 아래 명시된 변경만.**

## 배경 (왜 다시 고치나)
직전 작업에서 `loadPricingData()`에 `await _P.fetchFromAPI()`를 추가했는데, 이 때문에 config의 `getSaasPlans/getDiagPlans`가 **DB/API 데이터(시험결제 10,000원·구가격 99,000/145,000/249,000·포함인원 5명·PDF 리포트)** 를 V4 상수보다 우선해서 렌더했다. 기준 페이지 `saas.html`은 `fetchFromAPI`를 호출하지 않고 V4 상수만 쓴다. pricing.html도 동일하게 만든다.

## 작업 범위
- **수정 파일: `nexas/pricing.html` 1개뿐.** config·saas.html·다른 JS·다른 페이지·CSS·DB 절대 건드리지 말 것.
- 결제 흐름(`startSaasPayment`/`proceedDiagPayment` → `fix-request.html`) 변경 금지.
- 레이아웃/탭/카드 마크업/디자인 변경 금지(아래 토글 제거 제외).

## 할 일 (이것만)

### 1. API 우회 제거 — config V4만 사용
인라인 `loadPricingData()`에서 `fetchFromAPI` 호출 블록을 **삭제**한다.

변경 전:
```js
async function loadPricingData(){
  if(_P.fetchFromAPI){
    try { await _P.fetchFromAPI(); } catch(e) {}
  }

  renderSaasSector('BUILDING', 'building');
```
변경 후:
```js
function loadPricingData(){
  renderSaasSector('BUILDING', 'building');
```
(나머지 `renderSaasSector` 3회 + `renderDiagSection()` + highlight 처리 줄은 그대로 둔다. `async` 제거해도 되고 둬도 무방하나 `await`는 남기지 말 것.)
→ 결과: `getSaasPlans/getDiagPlans`가 `_apiSaas/_apiDiag` 미설정 상태이므로 V4 상수(SAAS/DIAG)만 반환 = saas.html과 동일.

### 2. 연간/월간 토글 제거 (할인/프로모션 금지)
SaaS 탭 HTML에서 아래 `billing-toggle-wrap` 블록 **전체 삭제**:
```html
      <div class="billing-toggle-wrap">
        <span class="billing-label active-label" id="label-monthly">월간</span>
        <button class="toggle-switch" id="billing-toggle" onclick="toggleBilling()"></button>
        <span class="billing-label" id="label-annual">연간 <span class="annual-badge">2개월 무료</span></span>
      </div>
```
(바로 아래 `<div class="billing-note">시설 1개 기준 / 월 · VAT 별도 · 관리자/작업자 무제한</div>`는 유지)

인라인 JS에서 `window.toggleBilling = function(){ ... };` 함수 **전체 삭제**. (미사용이 된 `var isAnnual = false;`도 삭제 가능 — 무해하면 둬도 됨)

`renderSaasCard`의 가격 표기 중 `<span class="period-unit">월</span>`는 그대로 둔다(정적 "월"). `data-monthly` 속성은 남아도 무해.

### 3. SaaS 안내 문구에서 연간 할인 문장 제거
변경 전:
```
<p>월 구독 기준이며, 연간 구독 시 2개월 무료 혜택이 제공됩니다. 구독은 언제든지 취소 가능하며 위약금이 없습니다.
        관리자/작업자 등록은 무제한입니다. 세금계산서 발행이 가능합니다.</p>
```
변경 후:
```
<p>월 구독 기준이며, 구독은 언제든지 취소 가능하며 위약금이 없습니다.
        관리자/작업자 등록은 무제한입니다. 세금계산서 발행이 가능합니다.</p>
```

## 완료 기준 (검증)
1. `loadPricingData`에 `fetchFromAPI`/`await`/`fetch(` 없음.
2. 배포 후 화면에 **시험결제(10,000원)·"PG 테스트"·0원 14일 무료체험 카드가 사라짐**.
3. SaaS 가격: 건물 149,000/349,000/협의 · 산업 149,000/299,000/499,000/협의 · 건설 249,000/499,000/협의.
4. 법령진단 가격: 건물 149,000/349,000 · 산업 149,000/299,000/499,000 · 건설 249,000/499,000. (99,000/145,000 등 구가격 없음)
5. "포함 인원 5명/3,000원" 없음, "PDF 법령진단 리포트" 없음(= API 미사용으로 자동 해소).
6. 월간/연간 토글 UI·`toggleBilling` 없음.
7. `git diff`는 `nexas/pricing.html` 1파일만, 위 변경만 포함.

작업 후 `git diff`와 완료 기준 점검 결과를 보고하라. 불확실하면 멈추고 질문하라.
