# [Cursor 작업지시 #3 · 통합/최종] pricing.html 정리 (2026-06-03)

> 기준 문서: `tai-api/docs/PRICING_FINAL.md` (V4, 유일 가격 기준 — 할인/프로모션·특전 정책 없음)
> 기준 페이지: `nexas/service/saas.html` (config-only)
> 단일 소스: `nexas/assets/js/tai-pricing-config.js`
> 원칙: **임의판단·확장·추측 금지. 아래만. 각 단계는 멱등(있으면 제거).**
> 이 문서는 작업지시 #2를 포함/대체한다.

## 작업 범위
- **수정 파일: `nexas/pricing.html` 1개뿐.** config·saas.html·다른 JS·다른 페이지·CSS·DB 절대 금지.
- 결제 흐름(`startSaasPayment`/`proceedDiagPayment` → `fix-request.html`) 변경 금지.

## 할 일

### 1. API 우회 제거 (config V4만 사용)
`loadPricingData()`에서 아래 블록이 있으면 삭제(함수는 비-async):
```js
  if(_P.fetchFromAPI){
    try { await _P.fetchFromAPI(); } catch(e) {}
  }
```
→ `renderSaasSector` 3회 + `renderDiagSection()` + highlight 처리는 유지. `await` 남기지 말 것.
(이유: config `getSaasPlans/getDiagPlans`가 API 데이터를 V4 상수보다 우선해서 DB의 시험결제·구가격·포함인원 5명이 렌더됨. saas.html은 API를 안 부른다.)

### 2. 월간/연간 토글 제거 (할인/프로모션 정책 없음)
- SaaS 탭의 `<div class="billing-toggle-wrap"> … </div>` 블록 전체 삭제. 아래 `billing-note`는 유지.
- 인라인 JS의 `window.toggleBilling = function(){ … };` 전체 삭제.
- SaaS 안내(`price-notice`) 문구에서 "연간 구독 시 2개월 무료 혜택이 제공됩니다." 문장만 삭제.

### 3. "도입 특전" 섹션 전체 삭제 (실제 없는 정책)
아래 주석~닫는 태그 전체 삭제:
```html
<!-- 혜택 섹션 -->
<section class="price-benefit">
  … (첫 달 무료 체험 / 법령진단→구독 전환 할인 / 전담 온보딩 / "도입 문의 · 특전 상담") …
</section>
```
(첫 달 무료·전환 할인·특별 요금·온보딩 특전은 PRICING_FINAL에 근거 없는 문구이므로 섹션째 제거.)

### 4. 마지막 CTA 섹션 삭제
페이지 맨 아래 CTA 섹션 전체 삭제:
```html
<!-- CTA -->
<section class="price-cta">
  <div class="container">
    <h2>지금 무료로 시작하세요</h2>
    … (무료 법령진단 시작 / 도입 문의하기 버튼) …
  </div>
</section>
```

## 완료 기준 (검증)
1. `loadPricingData`에 `fetchFromAPI`/`await`/`fetch(` 없음.
2. 화면에서 시험결제(10,000원)·"PG 테스트"·0원 14일 무료체험 카드 사라짐.
3. SaaS: 건물 149,000/349,000/협의 · 산업 149,000/299,000/499,000/협의 · 건설 249,000/499,000/협의.
4. 진단: 건물 149,000/349,000 · 산업 149,000/299,000/499,000 · 건설 249,000/499,000.
5. "포함 인원 5명/3,000원"·"PDF 법령진단 리포트"·월간/연간 토글 없음.
6. "도입 특전(price-benefit)" 섹션 없음. 맨 아래 "지금 무료로 시작하세요(price-cta)" 섹션 없음.
7. `git diff`는 `nexas/pricing.html` 1파일만, 위 변경만 포함.

## 손대지 말 것 (확인 전)
- `diag-nudge-section`("플랜 선택 가이드 / 어떤 플랜이 맞는지 모르시겠습니까?") 블록은 **이번엔 건드리지 마라.** (사용자 확인 후 별도 처리)

작업 후 `git diff`와 완료 기준 점검 결과 보고. 불확실하면 멈추고 질문.
