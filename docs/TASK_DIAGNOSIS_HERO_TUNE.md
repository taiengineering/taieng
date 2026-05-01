# [Cursor 작업 지시서] diagnosis.html 히어로 미세조정

작성일: 2026-05-01
대상 파일: `nexas/service/diagnosis.html` (단일 파일 수정)
배경: 히어로를 배경 이미지 방식으로 전환했으나 (1) 오버레이가 너무 어둡고 (2) 표준 히어로 높이 규칙과 어긋남.

---

## 작업 범위

**히어로 섹션(상단)만 수정.** 그 외 콘텐츠/스크립트/하단 섹션 절대 건드리지 말 것.

수정 위치는 모두 `<style>` 블록 안에 있음:

1. `.diag-hero` 블록의 `min-height`
2. `.diag-hero-inner` 블록의 `padding-top`
3. `.diag-hero-overlay` 블록의 `background` (그라데이션)
4. `@media (max-width: 991px)` 안의 `.diag-hero-inner` `padding-top` (모바일 정합성)

HTML 구조, 텍스트, CTA, 그 외 클래스 전부 그대로 둘 것.

---

## 변경 1 — `.diag-hero` 높이 표준화

`min-height`를 표준 히어로 높이 규칙(`for-expert.html`과 동일)으로 맞춤.

### Before

```css
.diag-hero {
  background: #080f1c;
  min-height: clamp(520px, 78vh, 700px);
  display: flex; align-items: center;
  padding: 0; position: relative; overflow: hidden;
}
```

### After

```css
.diag-hero {
  background: #080f1c;
  min-height: clamp(560px, 80vh, 720px);
  display: flex; align-items: center;
  padding: 0; position: relative; overflow: hidden;
}
```

**변경점:** `clamp(520px, 78vh, 700px)` → `clamp(560px, 80vh, 720px)`. 그 외 모두 동일.

---

## 변경 2 — `.diag-hero-inner` 패딩 표준화

`padding-top`을 `+ 52px` → `+ 44px`로 변경 (표준 규칙).

### Before

```css
.diag-hero-inner {
  position: relative; z-index: 2;
  padding-top: calc(var(--tai-nav-h, 90px) + 52px);
  padding-bottom: 68px;
}
```

### After

```css
.diag-hero-inner {
  position: relative; z-index: 2;
  padding-top: calc(var(--tai-nav-h, 90px) + 44px);
  padding-bottom: 68px;
}
```

**변경점:** `+ 52px` → `+ 44px`. `padding-bottom: 68px`는 그대로.

---

## 변경 3 — 오버레이 그라데이션 (핵심)

좌측 80% 불투명 → 우측 0% (완전 투명)으로 단순화. 너무 어두운 문제 해결.

### Before

```css
.diag-hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8,15,28,0.96) 0%,
    rgba(8,15,28,0.88) 38%,
    rgba(8,15,28,0.55) 65%,
    rgba(8,15,28,0.08) 100%
  );
}
```

### After

```css
.diag-hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8,15,28,0.80) 0%,
    rgba(8,15,28,0) 100%
  );
}
```

**변경점:** 4-stop 그라데이션 → 2-stop. 좌 0.80, 우 0(투명).

---

## 변경 4 — 모바일 정합성 (`@media (max-width: 991px)`)

표준 패딩 규칙에 맞춰 모바일도 `+ 32px` → `+ 24px`로 조정.

### Before (해당 부분만)

```css
@media (max-width: 991px) {
  .diag-hero { min-height: auto; }
  .diag-hero-inner { padding-top: calc(var(--tai-nav-h, 90px) + 32px); padding-bottom: 48px; }
  ...
}
```

### After (해당 부분만)

```css
@media (max-width: 991px) {
  .diag-hero { min-height: auto; }
  .diag-hero-inner { padding-top: calc(var(--tai-nav-h, 90px) + 24px); padding-bottom: 48px; }
  ...
}
```

**변경점:** `+ 32px` → `+ 24px`. 미디어쿼리 안의 다른 셀렉터들(`.before-section, .after-section ...` 등)은 절대 건드리지 말 것.

---

## 주의사항

- HTML 구조 (`<section class="diag-hero"> ... <div class="diag-hero-bg"> ... <div class="diag-hero-overlay"> ...`) 그대로 유지.
- `.diag-hero-bg`의 `background-image` URL 그대로 유지: `https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/law-check2.png`
- `.diag-hero h1`, `.diag-eyebrow`, `.btn-hero` 등 텍스트 스타일은 건드리지 말 것.
- 다른 섹션(`.before-section`, `.why-section`, `.after-section` 등)의 padding/min-height 절대 건드리지 말 것.

---

## 검증 (수정 후)

1. 데스크톱(1920×1080)에서 히어로 높이가 약 720px 부근으로 보이는지.
2. 좌측 텍스트(헤드라인·서브카피·CTA)가 충분히 읽히는지(가독성 확보).
3. 우측 영역에 `law-check2.png` 이미지가 자연스럽게 보이는지(오버레이로 가려지지 않음).
4. 모바일(375px)에서 텍스트가 잘리거나 헤더와 겹치지 않는지.

---

## 커밋 메시지(권장)

```
fix(diagnosis): 히어로 높이 표준화 + 오버레이 80→0% 단순화
```
