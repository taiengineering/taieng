# 작업지시서: 히어로 높이 통일 + 탑 네비게이션 정비

## 작업 범위 2가지

### A. 히어로 높이 통일 (안전정보 4개 페이지 제외)
### B. 스크롤 시 탑 배경색 통일 + 탑 없는 페이지에 탑 추가 (전체 페이지)

---

## A. 히어로 높이 통일

### 기준: `service/diagnosis.html` (.diag-hero)
```css
min-height: 420px;
padding-top: 80px;
padding-bottom: 60px;
/* navbar 높이: --tai-nav-h: 90px */
```

### ⚠️ 제외 (현재 상태 유지)
아래 4개 페이지는 히어로 높이를 수정하지 마세요:
- `safety-news.html` — 검색 중심 페이지, 현재 높이 유지
- `accident-cases.html` — 검색 중심 페이지, 현재 높이 유지
- `law-updates.html` — 2칸 레이아웃, 현재 높이 유지
- `precedent-search.html` — 검색 중심 페이지, 현재 높이 유지

### 수정 대상 페이지

| # | 페이지 | 히어로 클래스 | 현재 min-height | 수정 |
|---|---|---|---|---|
| 1 | `index.html` | `.hero-split` | 420px | padding 확인만 |
| 2 | `service/diagnosis.html` | `.diag-hero` | 420px | **수정 금지 (기준)** |
| 3 | `service/saas.html` | `.pat-hero` | 420px | padding 확인 |
| 4 | `for-business-owner.html` | `.owner-hero-section` | **520px** | → **420px** |
| 5 | `for-safety-manager.html` | (인라인) | 없음 | → **420px 추가** |
| 6 | `for-expert.html` | (인라인) | 420px | padding 확인 |
| 7 | `for-repair.html` | 확인 필요 | - | → **420px** |
| 8 | `for-agency.html` | 확인 필요 | - | → **420px** |
| 9 | `for-consultant.html` | 확인 필요 | - | → **420px** |
| 10 | `target/building.html` | 확인 필요 | - | → **420px** |
| 11 | `target/factory.html` | 확인 필요 | - | → **420px** |
| 12 | `target/construction.html` | 확인 필요 | - | → **420px** |
| 13 | `pricing.html` | 확인 필요 | - | → **420px** |

### 각 페이지에서 히어로 CSS를 찾아 아래 값으로 통일:
```css
min-height: 420px;
padding-top: 80px;
padding-bottom: 60px;
```

### 모바일 반응형
```css
@media(max-width:991px) {
  min-height: auto;
  padding-top: calc(var(--tai-nav-h, 90px) + 24px);
  padding-bottom: 40px;
}
@media(max-width:575px) {
  padding-top: calc(var(--tai-nav-h, 90px) + 16px);
  padding-bottom: 32px;
}
```

### 텍스트/이미지 조정
- 히어로 높이가 줄어든 페이지(for-business-owner 520→420 등)는 h1 font-size나 간격 미세 조정
- 이미지 컨테이너도 420px에 맞춤

---

## B. 스크롤 시 탑 배경색 통일 (전체 페이지 대상)

### 현재 문제
- `style.css`에서 `.navbar-area-fixed`의 배경: `rgba(var(--main-color-opacity), 0.8)`
- 페이지마다 `--main-color-opacity` 값이 다르거나 미정의 → 배경이 투명하게 보이는 경우 발생
- 스크롤 시 로고, 메뉴 텍스트가 콘텐츠와 겹쳐 안 보임

### 통일 기준
스크롤 시 navbar 고정 배경: **navy gradient** (diagnosis 페이지와 동일)

### 수정 방법

`tai-main.css`에 아래 CSS를 추가하세요 (style.css의 변수 의존을 override):

```css
/* ── 스크롤 시 탑 배경색 통일 ── */
.navbar-area.navbar-area-fixed {
  background: rgba(15, 43, 74, 0.92) !important;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
}

/* 고정 시 로고 텍스트 색상 — 흰색 배경이면 navy, navy 배경이면 흰색 */
.navbar-area.navbar-area-fixed .tai-logo-text {
  color: #fff !important;
  text-shadow: none;
}

/* 고정 시 메뉴 텍스트 색상 */
.navbar-area.navbar-area-fixed .navbar-nav > li > a {
  color: rgba(255, 255, 255, 0.9) !important;
}

/* 고정 시 우측 버튼 */
.navbar-area.navbar-area-fixed .tai-nav-btn-outline {
  border-color: rgba(255, 255, 255, 0.55) !important;
  color: rgba(255, 255, 255, 0.9) !important;
}
.navbar-area.navbar-area-fixed .tai-nav-btn-solid {
  border-color: rgba(255, 255, 255, 0.9) !important;
  color: #0f2b4a !important;
  background: #fff !important;
}
.navbar-area.navbar-area-fixed button.tai-logout-btn {
  border-color: rgba(255, 255, 255, 0.55) !important;
  color: rgba(255, 255, 255, 0.9) !important;
}
```

### 적용 범위
- 이 CSS는 `tai-main.css`에 한 번만 추가하면 **모든 페이지**에 자동 적용됩니다
- 안전정보 4개 페이지 포함, 전체 사이트에 적용

---

## C. 탑(네비게이션) 없는 페이지에 탑 추가

### 확인 방법
모든 HTML 파일에서 아래 2개가 있는지 확인:
1. `<div id="tai-header"></div>` (body 시작 부분)
2. `<script src="assets/js/header.js"></script>` (body 끝 부분)

### 없으면 추가
```html
<!-- body 시작 직후 -->
<div class="preloader" id="preloader">...</div>
<div class="body-overlay" id="body-overlay"></div>
<div id="tai-header"></div>

<!-- body 종료 직전 -->
<div id="tai-footer"></div>
<script src="assets/js/jquery.3.6.min.js"></script>
<script src="assets/js/bootstrap.min.js"></script>
<script src="assets/js/main.js"></script>
<script src="assets/js/header.js"></script>
<script src="assets/js/nav-auth.js"></script>
<script src="assets/js/footer.js"></script>
```

### 확인 대상 페이지
아래 페이지들에서 `tai-header`가 없는지 확인:
- `connect.html`
- `faq.html`
- `contact.html`
- `privacy.html`
- `terms.html`
- `delete-account.html`
- `patents.html`
- `sign-up.html`
- `log-in.html`
- `about.html`
- `showcase.html`

---

## 주의사항

- **diagnosis.html은 수정하지 마세요** (기준 페이지)
- **안전정보 4개 페이지 히어로 높이는 수정하지 마세요** (B의 탑 배경색만 적용)
- `tai-brand.css` body class `home-X`가 있으면 제거 (보라색 이슈)
- header.js, footer.js는 수정하지 마세요
- git push origin main → Cloudflare 자동배포
