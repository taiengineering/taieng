# Cursor 작업지시서 — 2026-05-01 오후

**레포:** `taiengineering/taieng` (`nexas/` 디렉토리)  
**배포:** Cloudflare Pages → taieng.co.kr  
**작성:** 이창은 (Claude Sonnet 인계)

---

## ⚡ 절대 규칙

1. **히어로 섹션(탑)만 수정** — 하단 콘텐츠 절대 건드리지 않음
2. `header.js` 색상/파비콘 수정은 반드시 `header.js` 직접 수정
3. 판단이 필요한 경우 작업 중단 후 보고

---

## TASK-01 【즉시】 `header.js` setFavicon() — favicon.ico로 교체

**파일:** `nexas/assets/js/header.js`  
**현재:** v3.5.3 — `setFavicon()`이 `favicon.svg`만 참조  
**목표:** v3.5.4 — `favicon.ico` (1순위) + `favicon.svg` (폴백)

**수정할 함수만 교체** (나머지 코드 절대 건드리지 않음):

```js
/* ── 파비콘 전역 세팅 (모든 페이지 적용) ── */
function setFavicon() {
  try {
    /* 기존 favicon 링크 모두 제거 */
    document.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]').forEach(function(el) {
      el.parentNode && el.parentNode.removeChild(el);
    });
    /* favicon.ico — 크롬/엣지/파이어폭스 등 모든 브라우저 */
    var ico = document.createElement('link');
    ico.rel = 'icon';
    ico.type = 'image/x-icon';
    ico.href = base + 'assets/img/favicon.ico';
    document.head.appendChild(ico);
    /* favicon.svg — 모던 브라우저 고해상도 폴백 */
    var svg = document.createElement('link');
    svg.rel = 'icon';
    svg.type = 'image/svg+xml';
    svg.href = base + 'assets/img/favicon.svg';
    document.head.appendChild(svg);
  } catch (e) {}
}
```

**버전 주석 상단에 추가:**
```
 * v3.5.4 (2026-05-01): 파비콘 favicon.ico로 교체 (svg 폴백 유지)
```

**완료 후 커밋:** `fix(header): setFavicon → favicon.ico 우선 적용 (v3.5.4)`

---

## TASK-02 【확인 후 수정】 index.html 히어로 구도 확정

**파일:** `nexas/index.html`  
**현재 커밋:** `db7213a` — 2컬럼 flex (`.idx-hero`)  
**상태:** 배포 후 실제 화면 스크린샷 미확인

**현재 CSS 핵심:**
```css
.idx-hero { display:flex; min-height:520px; }
.idx-hero-left  { flex: 0 0 42%; padding: calc(var(--tai-nav-h,90px)+44px) 48px 60px 80px; }
.idx-hero-right { flex: 0 0 58%; }
.idx-hero-img   { object-fit:cover; object-position:center center; }
```

**확인 사항:**
- `taieng.co.kr` 접속 후 히어로 섹션 스크린샷
- 이미지가 자연스럽게 채워지는지 확인
- 이상 있으면 `object-position` 조정

**판단 필요 시 → 작업 중단, 스크린샷 첨부 후 보고**

---

## TASK-03 【순서대로】 미검토 페이지 히어로 CSS 링크 표준화

**기준:** `docs/TASK_HERO_STANDARDIZE.md` 참고  
**표준 `<head>` 링크 순서:**
```html
<link rel="stylesheet" href="assets/css/style.css">
<link rel="stylesheet" href="assets/css/responsive.css">
<link rel="stylesheet" href="assets/css/tai-brand.css">
<link rel="stylesheet" href="assets/css/tai-main.css">
<link rel="stylesheet" href="assets/css/tai-hero.css">
```

**대상 파일 (히어로 상단만, 하단 콘텐츠 절대 건드리지 않음):**

| 파일 | 작업 |
|------|------|
| `nexas/for-agency.html` | CSS 링크 표준화 확인 (`fa2-*` 커스텀 히어로 — HTML 건드리지 않음) |
| `nexas/for-business-owner.html` | 히어로 구조 확인 → 필요 시 CSS 링크만 표준화 |
| `nexas/about.html` | 히어로 구조 확인 → 필요 시 CSS 링크만 표준화 |
| `nexas/pricing.html` | 히어로 구조 확인 → 필요 시 CSS 링크만 표준화 |
| `nexas/connect.html` | 히어로 구조 확인 → 필요 시 CSS 링크만 표준화 |

**각 파일 처리 순서:**
1. `<head>` 열어서 CSS 링크 순서 확인
2. `tai-hero-fix.css` 링크가 있으면 제거 (단, `diagnosis.html`은 유지)
3. 표준 순서대로 재정렬
4. **히어로 HTML 구조는 건드리지 않음**

**완료 후 커밋:** `fix: CSS 링크 표준화 (for-agency, for-business-owner, about, pricing, connect)`

---

## TASK-04 【간단】 루트 레포 .DS_Store 제거

**위치:** `tai-engineering` 루트 레포 (taieng 레포와 별개)

```bash
# tai-engineering 루트 디렉토리에서:
git rm --cached .DS_Store
git commit -m "chore: 루트 .DS_Store 추적 제거"
git push
```

---

## 오늘 완료된 작업 (참고용)

- [x] `header.js` v3.5.2 — fixed 헤더 텍스트/버튼 흰색 수정
- [x] `tai-hero.css` — 표준 히어로 모듈 생성
- [x] `for-expert.html` — 히어로 높이 clamp(560px,80vh,720px) + 버블 균등 배치
- [x] `favicon.svg` — TAI 마크 아이콘 (다크 네이비 배경, 흰 배경 제거)
- [x] `favicon.ico` — 업로드 완료 (`nexas/assets/img/favicon.ico`)
- [x] `header.js` v3.5.3 — `setFavicon()` 추가 (현재 svg 참조, TASK-01에서 ico로 교체 필요)
- [x] construction/factory/building/for-expert/for-safety-manager/for-consultant/for-repair 히어로 정리
