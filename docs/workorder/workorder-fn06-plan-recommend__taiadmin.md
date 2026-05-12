# FN-06: 진단 기반 SaaS 플랜 추천 UI

> **상태:** ✅ 구현 완료 (2026-04-18)
> **선행조건:** BE-08 `GET /diagnosis/{diagnosis_id}/recommend-plan` 완료
> **연관 파일:**
> - `tadmin/.../diagnosis-result-v2.html` (tai-admin main) ← **이 창**
> - `nexas/pricing.html` (taiengineering/taieng main)

---

## 1. 진단 결과 페이지 — 추천 플랜 블록

### 위치
`diagnosis-result-v2.html` → `result-grid` 아래, `next-actions` 위

```html
<!-- FN-06: 진단 기반 플랜 추천 섹션 -->
<div class="mt-4" id="plan-recommend-section" style="display:none;">
  <div class="card">
    <div class="card-header pb-2 d-flex align-items-center gap-2">
      <i class="ti tabler-sparkles text-warning"></i>
      <h6 class="mb-0 fw-bold">진단 기반 맞춤 플랜 추천</h6>
      <span class="badge bg-label-secondary">법령엔진 자동 분석</span>
    </div>
    <div class="card-body" id="plan-recommend-body"><!-- JS 렌더 --></div>
  </div>
</div>
```

### API 호출 (JS)
```js
GET /diagnosis/{diagnosis_id}/recommend-plan
Authorization: Bearer {token}
```

**응답 스펙 (BE-08 기준):**
```json
{
  "recommended": "BUSINESS",
  "reasons": [
    "의무 항목 73건 — STARTER 한도(50건) 초과",
    "위험도 HIGH — 적극적 대응 플랜 필요",
    "작업자 120명 — 중규모 사업장 기준 적합"
  ],
  "alternatives": ["STARTER", "PRO"],
  "comparison": {
    "penalty_max_krw": 21000000,
    "subscription_annual_krw": 1788000,
    "roi_ratio": 11.7
  }
}
```

### UI 구성 (좌우 2컬럼 row g-4)

#### 왼쪽 (col-md-4) — 추천 플랜 카드
```
┌────────────────────────┐
│  [BUSINESS] 뱃지       │
│  ₩149,000 / 월         │
│  이 사업장에 가장 적합  │
│                        │
│  [🚀 지금 구독 시작]   │
│  [전체 플랜 비교]      │
└────────────────────────┘
```
- CTA → `pricing.html?recommend={plan}&diagnosis_id={id}`

#### 오른쪽 (col-md-8) — 이유 + 비교
```
추천 이유:
  ✓ 의무 항목 73건 — STARTER 한도 초과
  ✓ 위험도 HIGH — 적극 대응 필요
  ✓ 작업자 120명 — 중규모 기준

과태료 리스크 vs 구독료:
  최대 과태료    21,000,000원  ← 빨간색
  BUSINESS 연간   1,788,000원  ← 초록색
  ──────────────────────────
  비용 대비 효과  11.7배 절감  ← badge bg-label-success

다른 플랜: STARTER · PRO (링크)
```

### 과태료 bar 비교 (v2 개선 예정)
현재: 숫자 텍스트 비교
v2 목표:
```
최대 과태료  ████████████████████  21,000,000원
연간 구독료  ████                   1,788,000원
                         절감: 11.7배
```
구현 방법: `comparison.penalty_max_krw` 기준 100%, 구독료를 비율로 환산 → `width` CSS

### 플랜별 색상 테마 맵
```js
const PLAN_THEME = {
  STARTER:  { bg:'#f0fdf4', border:'#16a34a', text:'#15803d', badgeCls:'bg-success' },
  BUSINESS: { bg:'#eff6ff', border:'#1d4ed8', text:'#1e40af', badgeCls:'bg-primary' },
  PRO:      { bg:'#fdf4ff', border:'#7c3aed', text:'#6d28d9', badgeCls:'bg-primary' },
  CUSTOM:   { bg:'#fff7ed', border:'#ea580c', text:'#c2410c', badgeCls:'bg-warning' },
};
```

### CSS 클래스 (style 블록 내 추가)
```css
.plan-recommend-card { border-radius:14px; padding:18px 20px; border:2px solid transparent; }
.plan-name-badge     { font-size:.7rem; font-weight:800; padding:3px 10px; border-radius:999px; }
.plan-price-big      { font-size:1.8rem; font-weight:900; line-height:1.1; }
.plan-reason-item    { display:flex; align-items:flex-start; gap:8px; font-size:.83rem; padding:4px 0; border-bottom:1px solid #f1f5f9; }
.plan-reason-icon    { color:#16a34a; flex-shrink:0; }
.plan-comparison-box { background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px 16px; margin-top:14px; }
.plan-comp-row       { display:flex; justify-content:space-between; font-size:.82rem; padding:4px 0; }
.plan-comp-val-danger  { font-weight:800; color:#dc2626; font-size:.95rem; }
.plan-comp-val-success { font-weight:700; color:#059669; font-size:.95rem; }
```

### 동작 규칙
| 조건 | 동작 |
|------|------|
| `recommended` 없음 | 섹션 `display:none` 유지 |
| API 오류 | 조용히 실패 — 메인 렌더 블록하지 않음 |
| 정상 응답 | `sec.style.display = ''` 로 섹션 표시 |

---

## 2. pricing.html — 진단 유도 CTA

### 위치
`nexas/pricing.html` → FAQ 섹션 아래, `price-cta` 바로 위

```html
<section class="diag-nudge-section"> ... </section>
<section class="price-cta"> ... </section>
```

### UI 구성
```
┌─────────────────────────────────────────────────────────┐
│  [💡 플랜 선택 가이드]                                   │
│                                                          │
│  어떤 플랜이 맞는지          ✓ 법령 자동 도출           │
│  모르시겠습니까?             ✓ 의무항목 수 기반 추천     │
│                              ✓ 과태료 vs 구독료 비교     │
│  3분 진단 받으시면           ✓ 진단 결과에서 바로 구독   │
│  플랜 자동 추천              [3분 무료 진단으로 추천받기]│
│                              직접 상담을 원하시면 →      │
└─────────────────────────────────────────────────────────┘
```
- 배경: `linear-gradient(135deg, #1e1b4b, #312e81)`
- 주 CTA → `free-diagnosis.html`
- 보조 → `contact.html`

---

## 3. URL 파라미터 — 플랜 하이라이트

### 지원 파라미터
```
pricing.html?plan=INDUSTRY_PRO          ← 작업지시서 기준
pricing.html?highlight=BUSINESS
pricing.html?recommend=starter&diagnosis_id=abc123
```

### 구현 (JS)
```js
function highlightPlan(planName) {
  setTimeout(function() {
    document.querySelectorAll('.plan-name').forEach(function(el) {
      if (el.textContent.trim().toUpperCase() === planName) {
        var card = el.closest('.plan-card');
        if (card) {
          card.style.outline = '3px solid #7c3aed';
          card.style.boxShadow = '0 0 0 6px rgba(124,58,237,.15)';
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    });
  }, 800); // 카드 렌더 완료 대기
}

// 초기화 시 파라미터 확인
var params = new URLSearchParams(location.search);
var highlight = params.get('plan') || params.get('highlight') || params.get('recommend');
if (highlight) highlightPlan(highlight.toUpperCase());
```

### 파라미터 우선순위
`plan` > `recommend` > `highlight` (모두 동일 동작)

---

## 4. 사용자 플로우

```
경로 A (대다수):
  마케팅 사이트
    → free-diagnosis.html (무료 진단 입력)
    → 진단 완료
    → diagnosis-result-v2.html?diagnosis_id=xxx
    → result-grid 렌더 후 BE-08 호출
    → [플랜 추천 카드] 표시 (BUSINESS 예시)
    → "지금 구독 시작" 클릭
    → pricing.html?recommend=BUSINESS&diagnosis_id=xxx
    → BUSINESS 카드 하이라이트 + scrollIntoView
    → 결제 진행

경로 B (소수):
  pricing.html 직접 방문
    → 플랜 보다가 "모르겠다" 
    → FAQ 아래 [진단 유도 블록] 발견
    → "3분 무료 진단으로 플랜 추천받기" 클릭
    → 경로 A 합류
```

---

## 5. 구현 완료 체크리스트

- [x] `diagnosis-result-v2.html` — `#plan-recommend-section` 추가
- [x] `loadPlanRecommend()` — BE-08 비동기 호출, 조용히 실패 처리
- [x] `renderPlanRecommend()` — 카드 + 이유 + 비교박스 렌더
- [x] `PLAN_THEME` 색상 맵 (STARTER/BUSINESS/PRO/CUSTOM)
- [x] `pricing.html` — `.diag-nudge-section` 추가
- [x] URL 파라미터 `plan` / `highlight` / `recommend` → `highlightPlan()`
- [ ] BE-08 실 API 연동 테스트 (BE-08 완료 후)
- [ ] 과태료 비교 bar 시각화 고도화 (v2)
- [ ] 플랜 추천 섹션 스켈레톤 로딩 (v2)

---

## 6. 향후 개선 (v2)

| 항목 | 내용 |
|------|------|
| 과태료 bar | 숫자 → progress bar 시각화 |
| 수치 노출 | "현재 의무 항목 N건" 카드에 표시 |
| 스켈레톤 | 섹션 숨김 → 로딩 중 skeleton 표시 후 렌더 |
| A/B 테스트 | 추천 섹션 위치: result-grid 하단 전체폭 vs 우측 사이드바 |
