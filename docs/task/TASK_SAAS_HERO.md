# [Cursor 작업 지시서] saas.html 히어로 재제작 (배경 이미지 + 표준 높이)

작성일: 2026-05-01
대상 파일: `nexas/service/saas.html` (단일 파일 수정)
배경: SaaS 페이지 히어로를 그라데이션 단색 → 배경 이미지 방식으로 전환. 다른 서비스 페이지(`for-expert.html`, `diagnosis.html`)와 동일한 표준 높이·구조로 통일.

---

## 카피 (확정)

**메인:**
```
TAI를 쓰기 전과 후,
현장은 두 가지로 나뉩니다.
```

**서브 (대비 구조 — 사고 전/후 대구):**
```
한쪽은 사고가 나야 알 수 있고,
한쪽은 사고 전에 막을 수 있습니다.
```

eyebrow는 그대로 유지: `법령기반 산업안전 운영 플랫폼`
CTA 버튼 2개도 그대로 유지: `무료 법령진단 시작 →` / `화면 둘러보기 ↓`

---

## 이미지

`https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/saas1.png`

배경 이미지 방식. `<img>` 태그 쓰지 말고 CSS `background-image`로 적용.

---

## 작업 범위

**히어로 섹션(상단)만 수정.** 그 외 모든 섹션 절대 건드리지 말 것.

수정 위치는 두 군데:

1. `<style>` 블록 안의 `#saas-page .pat-hero { ... }` 관련 CSS (그리고 모바일 미디어쿼리)
2. `<body>` 안의 `<section class="pat-hero"> ... </section>` HTML

---

## 변경 1 — `.pat-hero` CSS 블록 교체

### Before

```css
#saas-page .pat-hero {
  min-height: 420px; background: linear-gradient(135deg, #0f2b4a, #1565c0);
  position: relative; display: flex; align-items: center; overflow: hidden;
  padding: 120px 0 60px;
}
#saas-page .pat-hero .container { position: relative; z-index: 2; }
```

### After

```css
#saas-page .pat-hero {
  min-height: clamp(560px, 80vh, 720px);
  background: #0f172a;
  position: relative; display: flex; align-items: center; overflow: hidden;
  padding: 0;
}
#saas-page .pat-hero-bg {
  position: absolute; inset: 0;
  background-image: url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/saas1.png');
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
}
#saas-page .pat-hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(
    90deg,
    rgba(15,23,42,0.80) 0%,
    rgba(15,23,42,0) 100%
  );
}
#saas-page .pat-hero-inner {
  position: relative; z-index: 2;
  padding-top: calc(var(--tai-nav-h, 90px) + 44px);
  padding-bottom: 68px;
}
```

**핵심 변경점:**
- `min-height`: `420px` → `clamp(560px, 80vh, 720px)` (표준 히어로 높이)
- `background`: 그라데이션 단색 → `#0f172a` (이미지 로딩 전 fallback)
- `padding`: `120px 0 60px` → `0` (안쪽 wrapper로 이동)
- 새 클래스 3개 추가: `.pat-hero-bg`, `.pat-hero-overlay`, `.pat-hero-inner`

---

## 변경 2 — 모바일 미디어쿼리에 히어로 규칙 추가

기존 `@media(max-width:991px)` 블록을 찾아 그 안의 첫 줄에 히어로 규칙 두 줄을 **추가**할 것. 다른 미디어쿼리 규칙들은 절대 건드리지 말 것.

### Before (해당 블록 일부)

```css
@media(max-width:991px) {
  #saas-page .feat-visual { max-width: 100%; }
  #saas-page .feat-pair .feat-info { min-width: 0; }
  ...
}
```

### After (해당 블록 일부)

```css
@media(max-width:991px) {
  #saas-page .pat-hero { min-height: auto; }
  #saas-page .pat-hero-inner { padding-top: calc(var(--tai-nav-h, 90px) + 24px); padding-bottom: 48px; }
  #saas-page .feat-visual { max-width: 100%; }
  #saas-page .feat-pair .feat-info { min-width: 0; }
  ...
}
```

**변경점:** 미디어쿼리 블록 맨 앞에 히어로 관련 두 줄만 추가. 그 외 줄들은 그대로 둘 것.

---

## 변경 3 — 히어로 HTML 교체

`<!-- ① 히어로 -->` 주석으로 시작하는 `<section class="pat-hero">` 블록 전체를 아래로 교체.

### Before

```html
<!-- ① 히어로 -->
<section class="pat-hero">
  <div class="container">
    <span class="pat-eyebrow">법령기반 산업안전 운영 플랫폼</span>
    <h1>법령을 진단하면,
운영이 시작됩니다.</h1>
    <p class="pat-hero-sub">무료 법령진단으로 법적 의무를 확인하세요.
TAI Safe가 점검·알림·증빙·보고까지 이어받습니다.</p>
    <div class="sp-hero-btns">
      <a href="../free-diagnosis.html" class="sp-btn-primary">무료 법령진단 시작 →</a>
      <a href="#screen-mocks" class="sp-btn-secondary">화면 둘러보기 ↓</a>
    </div>
  </div>
</section>
```

### After

```html
<!-- ① 히어로 -->
<section class="pat-hero">
  <div class="pat-hero-bg"></div>
  <div class="pat-hero-overlay"></div>
  <div class="container pat-hero-inner">
    <div class="row">
      <div class="col-lg-7 col-xl-6">
        <span class="pat-eyebrow">법령기반 산업안전 운영 플랫폼</span>
        <h1>TAI를 쓰기 전과 후,
현장은 두 가지로 나뉩니다.</h1>
        <p class="pat-hero-sub">한쪽은 사고가 나야 알 수 있고,
한쪽은 사고 전에 막을 수 있습니다.</p>
        <div class="sp-hero-btns">
          <a href="../free-diagnosis.html" class="sp-btn-primary">무료 법령진단 시작 →</a>
          <a href="#screen-mocks" class="sp-btn-secondary">화면 둘러보기 ↓</a>
        </div>
      </div>
    </div>
  </div>
</section>
```

**핵심 변경점:**
- `<div class="pat-hero-bg">`, `<div class="pat-hero-overlay">` 추가 (배경/오버레이 레이어)
- `<div class="container">` → `<div class="container pat-hero-inner">` (패딩 적용 wrapper)
- 안에 `<div class="row"><div class="col-lg-7 col-xl-6">` 추가하여 텍스트가 좌측 영역만 차지하게 (우측은 배경 이미지가 보이도록)
- `<h1>` 텍스트와 `<p class="pat-hero-sub">` 텍스트 교체
- eyebrow, CTA 버튼 2개는 그대로 유지

**주의:** `<h1>` 안의 줄바꿈은 그대로 `\n`(literal newline) 유지. `<br>` 태그로 바꾸지 말 것. 기존 CSS의 `white-space: pre-line`이 처리함.

---

## 검증 (수정 후)

1. **데스크톱(1920×1080):** 히어로 높이 약 720px, 좌측 텍스트(헤드라인·서브·CTA)가 충분히 읽히고, 우측 영역에 `saas1.png` 이미지가 자연스럽게 보임.
2. **헤드라인 줄바꿈:** "TAI를 쓰기 전과 후," / "현장은 두 가지로 나뉩니다." 두 줄로 표시.
3. **서브 줄바꿈:** "한쪽은 사고가 나야 알 수 있고," / "한쪽은 사고 전에 막을 수 있습니다." 두 줄로 표시.
4. **모바일(375px):** 텍스트가 잘리거나 헤더와 겹치지 않음. 배경 이미지가 어두운 오버레이 위에 자연스럽게 보임.
5. **하단 콘텐츠:** "총무팀장 안전관리자도 맡고 계신가요?" 섹션 등 그 아래는 변경 없음.

---

## 주의사항 (반드시 지킬 것)

- 다른 섹션(`.sp-sec`, `.feat-pair`, `.sp-final` 등)의 padding·height·CSS 절대 건드리지 말 것.
- `<style>` 블록 안의 `.pat-hero` 외 클래스(`.pat-eyebrow`, `.pat-hero h1`, `.pat-hero-sub`, `.sp-hero-btns`, `.sp-btn-primary` 등) 그대로 유지.
- HTML에서 ② 이후 섹션(`<!-- ② 겸직 안전관리자 타겟 -->` 이하) 그대로 유지.
- 결제 폼, 스크립트 블록 그대로 유지.

---

## 커밋 메시지(권장)

```
feat(saas): 히어로 배경 이미지 방식 + 카피 변경 (TAI 전후 대비)
```
