# [Cursor 작업지시] pricing.html 법령진단 탭: 섹터 분리 + 이니시스 결제 연결 (2026-06-03)

## 문제
pricing.html "법령진단(단건)" 탭이 ① 건물/산업/건설로 안 나뉘고 한 묶음(`#diag-main-cards`)으로만 표시됨 ② 카드 클릭 시 이니시스 결제창이 아니라 입력폼 모달(`diagPayModal`)이 뜨고 `fix-request.html`로 이동함(매칭 챗). 로직이 틀림.

## 정답 (기준 파일: `nexas/service/diagnosis.html`)
diagnosis.html은 (a) `.sector-tabs` + 3개 `.sector-panel`로 섹터 분리, (b) 카드 onclick = `diagPay(productType, planCode, amount, goodname)` → `POST https://api.taieng.co.kr/payments/inicis/prepare` → 응답으로 `#diag_inicis_form` 채움 → `INIStdPay.pay('diag_inicis_form')`로 이니시스 결제창. INIStdPay SDK + `inicis-fix.js` 로드. **이 흐름을 pricing.html에 이식한다.**

## 작업 (pricing.html 한 파일만)

### 1. 법령진단 탭 HTML — 섹터 서브탭 + 3패널로 교체
`<div id="tab-diagnosis" class="tab-panel">` 안에서, 인트로 문구(`<div class="text-center mb-5">…12개월…</div>`)는 유지하고, 그 아래 `#diag-loading` + `#diag-main-cards` + `#special-wrap` 3블록을 아래로 교체:
```html
      <div class="sector-tabs">
        <button class="sector-tab-btn active" onclick="switchDiagSectorTab('building', this)"><span class="sector-icon">🏢</span>건물·시설</button>
        <button class="sector-tab-btn" onclick="switchDiagSectorTab('industry', this)"><span class="sector-icon">🏭</span>제조·산업</button>
        <button class="sector-tab-btn" onclick="switchDiagSectorTab('construction', this)"><span class="sector-icon">🏗️</span>건설현장</button>
      </div>
      <div id="diag-sector-building" class="sector-panel active"><div id="diag-building-cards" class="row g-4 justify-content-center"></div></div>
      <div id="diag-sector-industry" class="sector-panel"><div id="diag-industry-cards" class="row g-4 justify-content-center"></div></div>
      <div id="diag-sector-construction" class="sector-panel"><div id="diag-construction-cards" class="row g-4 justify-content-center"></div></div>
```
`price-notice`(법령진단이란?) 블록은 그대로 유지. (`special-wrap`/`toggleSpecial` 제거)

### 2. 섹터 탭 스위처 — 스코프 분리(중요)
기존 SaaS용 `window.switchSectorTab`는 `document.querySelectorAll('.sector-panel')`로 전역 토글이라, 법령진단 탭에도 `.sector-panel`이 생기면 충돌한다. 두 함수 모두 **자기 탭 안으로 스코프**할 것:
- `switchSectorTab`(SaaS): 쿼리를 `#tab-saas` 컨테이너 내부로 한정.
- 신규 `window.switchDiagSectorTab = function(sector, btn){ ... }`: `#tab-diagnosis` 내부의 `.sector-tab-btn`/`.sector-panel`만 토글하고 `#diag-sector-<sector>`를 active.

### 3. 렌더링 — 섹터별로 3패널에 채우기
`renderDiagSection()`을 아래로 교체(기존 `#diag-main-cards`/`special-wrap` 로직 제거):
```js
function renderDiagSection(){
  renderDiagSector('BUILDING', 'diag-building');
  renderDiagSector('INDUSTRY', 'diag-industry');
  renderDiagSector('CONSTRUCTION', 'diag-construction');
}
function renderDiagSector(sector, domKey){
  var cards = document.getElementById(domKey + '-cards');
  if(!cards) return;
  var icons = { BUILDING:'🏢', INDUSTRY:'🏭', CONSTRUCTION:'🏗️' };
  var plans = _P.getDiagPlans ? _P.getDiagPlans(sector) : [];
  cards.innerHTML = plans.map(function(p){ return renderDiagCard(p, sector, icons[sector]||'📋'); }).join('');
}
```

### 4. 카드 버튼 → diagPay (이니시스)
`renderDiagCard`의 결제 버튼 onclick을 `startDiagPayment(...)`에서 아래로 변경:
```js
+' onclick="diagPay(\'DIAG_'+sector+'\',\''+p.code+'\','+price+',\''+goodsName.replace(/'/g,"\\'")+'\')">바로 결제 '+price.toLocaleString('ko-KR')+'원</button>'
```
(goodsName은 기존대로 `(p.name||'')+' 진단'`. p.code는 config getDiagPlans가 제공.)

### 5. 이니시스 결제 자산 이식 (diagnosis.html에서 복사)
- `</body>` 앞에 `#diag_inicis_form` 히든 폼을 **diagnosis.html과 동일하게** 추가(필드 동일: version/gopaymethod/currency/langtype/acceptmethod/use_chkfake/mid/mKey/oid/price/tax/taxfree/goodname/buyername/buyertel/buyeremail/timestamp/signature/verification/returnUrl/closeUrl).
- 스크립트 로드 추가(footer.js 뒤, tai-pricing-config.js 앞):
  `<script src="https://stdpay.inicis.com/stdjs/INIStdPay.js" charset="utf-8"></script>`
  `<script src="assets/js/inicis-fix.js"></script>`
  (pricing.html은 루트이므로 `assets/js/...` 경로. diagnosis.html의 `../assets/js/...`와 다름에 주의.)
- diagnosis.html의 `diagPay(productType, planCode, amount, goodname)` 함수 + `DIAG_API/DIAG_RETURN/DIAG_CLOSE` 상수를 **그대로 복사**해 pricing.html 인라인 스크립트에 추가(INIStdPay.pay('diag_inicis_form') 포함).

### 6. 틀린 흐름 제거
- HTML: `#diagPayModal`(법령진단 결제 입력폼 모달) 전체 삭제. 기존 미사용 `#payForm`(ini_mid TAI_MID_PLACEHOLDER) 히든폼도 삭제.
- JS: `window.startDiagPayment`, `window.proceedDiagPayment`, `window.toggleSpecial` 함수 삭제. (관련 변수 `_pendingGoods/_pendingAmount`도 미사용이면 삭제)
- **SaaS 결제 흐름(startSaasPayment/saasModal)은 건드리지 말 것.** (이번 범위 아님)

## 완료 기준
1. 법령진단 탭에 건물·시설/제조·산업/건설현장 서브탭 표시, 각 탭에 해당 섹터 카드만 렌더(건물 2·산업 3·건설 2).
2. SaaS 탭 섹터 전환과 법령진단 탭 섹터 전환이 서로 간섭하지 않음.
3. 법령진단 카드 "바로 결제" 클릭 → 입력폼 모달 없이 **이니시스 결제창**(INIStdPay)으로 진입. fix-request로 가지 않음.
4. `diagPayModal`/`payForm`/`startDiagPayment`/`proceedDiagPayment`/`special-wrap` 흔적 없음.
5. `git diff`는 `nexas/pricing.html` 1파일만.

작업 후 `git diff`와 완료 기준 점검 결과 보고. 불확실하면 멈추고 질문.
