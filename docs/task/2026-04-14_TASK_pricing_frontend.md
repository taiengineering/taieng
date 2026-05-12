# pricing.html 전면 재작성 — 프론트엔드 작업지시서

> 2026-04-14 기획창 작성  
> 대상 레포: taiengineering/taieng  
> 대상 파일: nexas/pricing.html, nexas/assets/js/pricing.js  
> 브랜치: main (taieng 레포는 dev 브랜치 없음, main에 직접 push)  

---

## 현재 상태

- pricing.js v2 → 이미 main에 배포 완료 (commit 8bb33b9)
- pricing.html → 아직 구버전 (SHA: f0a9a9f3d50696d3edcf0cdaa91093cab20284ad) — 재작성 필요

---

## 작업: pricing.html 전면 재작성

### 파일 위치
```
nexas/pricing.html
```
기존 SHA(업데이트 시 필수): `f0a9a9f3d50696d3edcf0cdaa91093cab20284ad`

---

## 확정 구조

```
[히어로]

[메인 탭]
  탭 1: SaaS 구독
  탭 2: 법령진단 (단건)

[SaaS 탭]
  서브탭: 건물 | 산업 | 건설
  연간/월간 토글 (연간 = 월가격 × 10, "2개월 무료" 배지)

  건물 (시설당 월정액):
    BASIC 59,000원 / STANDARD 99,000원 (추천) / CUSTOM 별도 협의

  산업 (시설당 월정액):
    STARTER 79,000원 / BUSINESS 149,000원 (추천) / PRO 249,000원 / CUSTOM 별도 협의

  건설 (현장당 월정액):
    STANDARD 199,000원 (추천) / PREMIUM 399,000원 / CUSTOM 별도 협의

[법령진단 탭]
  서브탭: 건물 | 산업 | 건설

  건물 (2단계):
    무료(STEP 1) | 종합 299,000원(STEP 2)

  산업 (4단계):
    무료(STEP 1) | 표준 99,000원(STEP 2) | 설비 199,000원(STEP 3) | 종합 249,000원(STEP 4)

  건설 (2단계):
    무료(STEP 1) | 종합 299,000원(STEP 2)

[CTA 섹션]
```

---

## 기능 목록 (플랜 카드 표시)

### 건물
| 기능 | BASIC | STANDARD | CUSTOM |
|------|-------|----------|--------|
| 법령엔진 자동작동 | ✓ | ✓ | ✓ |
| 점검일정 자동생성 | ✓ | ✓ | ✓ |
| D-3 알림 | ✓ | ✓ | ✓ |
| 완료기록 자동화 | ✓ | ✓ | ✓ |
| 신고서식 자동화 | — | ✓ | ✓ |
| 법령변경 알림 | — | ✓ | ✓ |
| 기록보관 | 6개월 | 무제한 | 무제한 |
| 다수시설 통합 | — | — | ✓ |
| 전담매니저 | — | — | ✓ |

### 산업
| 기능 | STARTER | BUSINESS | PRO | CUSTOM |
|------|---------|----------|-----|--------|
| 법령엔진 | ✓ | ✓ | ✓ | ✓ |
| 점검일정 | ✓ | ✓ | ✓ | ✓ |
| 작업자배정 | ✓ | ✓ | ✓ | ✓ |
| D-3 알림 | ✓ | ✓ | ✓ | ✓ |
| 완료기록 | ✓ | ✓ | ✓ | ✓ |
| TBM 전자서명 | ✓ | ✓ | ✓ | ✓ |
| 신고서식 | — | ✓ | ✓ | ✓ |
| 법령변경 알림 | — | ✓ | ✓ | ✓ |
| QR 점검 | — | ✓ | ✓ | ✓ |
| 경영진 대시보드 | — | ✓ | ✓ | ✓ |
| 기록보관 | 6개월 | 무제한 | 무제한 | 무제한 |
| 경영진 리포트 | — | — | ✓ | ✓ |
| API 연동 | — | — | ✓ | ✓ |
| 다수시설 통합 | — | — | — | ✓ |
| 전담매니저 | — | — | — | ✓ |

### 건설
| 기능 | STANDARD | PREMIUM | CUSTOM |
|------|----------|---------|--------|
| 법령엔진 | ✓ | ✓ | ✓ |
| 공정별 점검일정 | ✓ | ✓ | ✓ |
| TBM 전자서명 | ✓ | ✓ | ✓ |
| 작업자배정 | ✓ | ✓ | ✓ |
| D-3 알림 | ✓ | ✓ | ✓ |
| 기록보관 | 무제한 | 무제한 | 무제한 |
| 위험성평가 자동 | — | ✓ | ✓ |
| 기상청 작업중지 연동 | — | ✓ | ✓ |
| 경영진 리포트 | — | ✓ | ✓ |
| 하도급관리 | — | ✓ | ✓ |
| 다수현장 통합 | — | — | ✓ |
| 발주처 리포트 | — | — | ✓ |
| 전담매니저 | — | — | ✓ |

---

## 법령진단 카드 기능 (공통)
- PDF 법령진단 리포트
- 적용 법령·의무 도출
- 과태료·벌칙 정보
- 감사 대응 서류 활용

법령진단 카드에 절대 넣지 말 것:
- 점검항목 자동 생성 (SaaS 기능)
- 일정 자동 생성 (SaaS 기능)
- TBM (SaaS 기능)

---

## pricing.js API 연동 방식

pricig.js v2는 이미 배포 완료. HTML의 `data-pricing-key` 속성과 연동:

```html
<!-- SaaS 가격 예시 (data-monthly 필수, 연간 토글 연동) -->
<span class="price-display" data-monthly="79000" data-pricing-key="saas-industry-starter">79,000</span>

<!-- 법령진단 가격 예시 (data-monthly 불필요) -->
<span class="price-display" data-pricing-key="diag-building-total">299,000</span>
```

**data-pricing-key 목록 (이 키 그대로 사용할 것):**

SaaS:
- `saas-building-basic` → 59,000
- `saas-building-standard` → 99,000
- `saas-industry-starter` → 79,000
- `saas-industry-business` → 149,000
- `saas-industry-pro` → 249,000
- `saas-construction-standard` → 199,000
- `saas-construction-premium` → 399,000

법령진단:
- `diag-building-total` → 299,000
- `diag-industry-basic` → 99,000
- `diag-industry-equipment` → 199,000
- `diag-industry-total` → 249,000
- `diag-construction-total` → 299,000

---

## JS 함수 구조

```html
<script>
var isAnnual = false;

// 메인 탭 전환
function switchPriceTab(tab, btn) { ... }

// SaaS 섹터 서브탭
function switchSaasSector(sector, btn) {
  // .saas-sector-panel 토글
  // #saas-sector-tabs .sector-btn 토글
}

// 법령진단 섹터 서브탭
function switchDiagSector(sector, btn) {
  // .diag-sector-panel 토글
  // #diag-sector-tabs .sector-btn 토글
}

// 연간/월간 토글
function toggleBilling() {
  isAnnual = !isAnnual;
  // .toggle-switch 클래스 토글
  // .price-display[data-monthly] → isAnnual ? monthly*10 : monthly
  // [data-period-unit] → isAnnual ? '연' : '월'
}

// 결제 버튼 (KG이니시스 미승인 기간: 준비 중 모달)
function startPayment(planKey, amount) {
  var modal = new bootstrap.Modal(document.getElementById('paymentPrepModal'));
  modal.show();
}
</script>
```

---

## HTML 구조 키포인트

```html
<!-- SaaS 섹터 탭 (id 필수) -->
<div class="sector-tabs" id="saas-sector-tabs">
  <button class="sector-btn active" onclick="switchSaasSector('building', this)">🏢 건물·시설</button>
  <button class="sector-btn" onclick="switchSaasSector('industry', this)">🏭 제조·산업</button>
  <button class="sector-btn" onclick="switchSaasSector('construction', this)">🏗️ 건설현장</button>
</div>

<!-- 연간/월간 토글 -->
<div class="billing-toggle-wrap">
  <span class="billing-label active-label" id="label-monthly">월간</span>
  <button class="toggle-switch" id="billing-toggle" onclick="toggleBilling()"></button>
  <span class="billing-label" id="label-annual">연간 <span class="annual-badge">2개월 무료</span></span>
</div>

<!-- 과금 기준 (건물·산업) -->
<div class="billing-note">시설당 월정액 · VAT 별도</div>

<!-- 과금 기준 (건설) -->
<div class="billing-note">현장당 월정액 · VAT 별도</div>

<!-- SaaS 패널 id 규칙: saas-{sector} -->
<div id="saas-building" class="saas-sector-panel active">...</div>
<div id="saas-industry" class="saas-sector-panel">...</div>
<div id="saas-construction" class="saas-sector-panel">...</div>

<!-- 법령진단 섹터 탭 (id 필수, SaaS와 구분) -->
<div class="sector-tabs" id="diag-sector-tabs">
  ...
</div>

<!-- 법령진단 패널 id 규칙: diag-{sector} -->
<div id="diag-building" class="diag-sector-panel active">...</div>

<!-- 무료 카드 버튼 -->
<a href="free-diagnosis.html" class="btn btn-border" ...>무료 진단 시작</a>

<!-- 유료 카드 버튼 -->
<button ... onclick="startPayment('diag_building_total', 299000)">바로 결제 299,000원</button>

<!-- 기간 단위 (토글 연동) -->
<div class="plan-period">/ 시설 · <span data-period-unit>월</span></div>
```

---

## 디자인 CSS 클래스 (기존 스타일 재활용)

```css
/* 기존 그대로 유지 */
.price-hero, .price-tab-wrap, .price-cta
.price-tab-btn.active { background: #0891b2 }
.plan-card, .plan-card.featured { border-color: #0891b2 }
.plan-badge { background: #0891b2 }

/* 새로 추가 */
.saas-sector-panel { display: none; }
.saas-sector-panel.active { display: block; }
.diag-sector-panel { display: none; }
.diag-sector-panel.active { display: block; }

.billing-toggle-wrap { display: flex; justify-content: center; align-items: center; gap: 12px; }
.toggle-switch { width: 50px; height: 28px; border-radius: 999px; background: #e2e8f0; }
.toggle-switch.on { background: #0891b2; }
.toggle-switch::after { /* 흰 동그라미 */ }

.billing-note { text-align: center; font-size: .78rem; font-weight: 700; color: #94a3b8; }

/* 법령진단 단계 배지 */
.step-free      { background: #f1f5f9; color: #64748b; }
.step-standard  { background: #eff6ff; color: #1d4ed8; }
.step-equipment { background: #faf5ff; color: #7c3aed; }
.step-total     { background: #fff7ed; color: #c2410c; }

.diag-card.free-card { background: #f8fafc; }
```

---

## 금지 사항 (절대 지킬 것)

- SMS/카카오/서류 포함 건수 표시 금지
- 초과 과금 안내 표시 금지
- 포함 인원 표시 금지 (시설당 과금)
- 크레딧 단어 사용 금지
- 소개비/소개수수료/인력소개/소개료 사용 금지
- 법령진단 카드에 "점검항목 자동 생성", "일정 자동 생성" 금지
- 규모(소규모/중소/중대/대형) 배지 및 기준표 금지
- CUSTOM 카드에 가격 숫자 표시 금지 ("별도 협의" + 문의 버튼)

---

## 공통 헤더/푸터

```html
<div id="tai-header"></div>
...
<div id="tai-footer"></div>
<script src="assets/js/header.js"></script>
<script src="assets/js/nav-auth.js"></script>
<script src="assets/js/footer.js"></script>
<script src="assets/js/pricing.js"></script>
```

---

## 완료 조건

- [ ] nexas/pricing.html → main 브랜치 push (SHA: f0a9a9f3d50696d3edcf0cdaa91093cab20284ad)
- [ ] SaaS 탭: 건물/산업/건설 서브탭 + 섹터별 플랜 카드
- [ ] SaaS 탭: 연간/월간 토글 작동
- [ ] SaaS 탭: 과금 기준 "시설당 월정액" / "현장당 월정액" 명시
- [ ] 법령진단 탭: 건물/산업/건설 서브탭 + 단계 카드
- [ ] 법령진단 탭: 규모 기준 안내 테이블 없음
- [ ] 모든 금지 사항 준수
- [ ] data-pricing-key 속성 정확히 적용
- [ ] header.js / footer.js / pricing.js 로드
