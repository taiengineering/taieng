# [Cursor 작업 지시서] for-safety-manager.html 히어로 — 배경 이미지 적용

작성일: 2026-05-01
대상 파일: `nexas/for-safety-manager.html` (단일 파일 수정)
배경: 첫 히어로(섹션 1)를 그라데이션 단색 → 배경 이미지(`safety-staff.png`) 방식으로 전환. 표준 높이 규칙 적용.

---

## ⚠️ 매우 중요 — 절대 지킬 것

**`.fs2-a` 클래스는 첫 히어로뿐 아니라 섹션 6(작업 허가)·섹션 13(최종 CTA)에서도 재사용됨.** `.fs2-a` 자체의 CSS를 변경하면 다른 섹션이 깨진다.

**해법:** 첫 히어로에만 있는 `id="fs2-top"`을 ID 셀렉터로 사용해, **첫 히어로 전용 추가 규칙**만 만든다. 기존 `.fs2-a` 정의는 손대지 말 것.

---

## 카피

**변경 없음.** 현재 카피 그대로 유지:

```
안전관리,
혼자 다 하고 계시죠?
```
- lead: "당신이 못해서가 아닙니다. / 구조가 그렇게 되어 있는 겁니다."
- sub: "아래로 내려가면, 속으로만 말하던 것들에 하나씩 답이 붙습니다."
- 스크롤 인디케이터: 그대로

이 카피는 안전관리자 페인포인트를 직격하는 강력한 워딩이라 변경하지 않는다.

---

## 이미지

`https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/safety-staff.png`

CSS `background-image`로 적용. `<img>` 태그 사용 금지.

---

## 작업 범위

수정 위치는 두 군데:

1. `<style>` 블록 끝부분(직전 `</style>` 위)에 **첫 히어로 전용 CSS 추가**
2. `<!-- 1 [A] -->` 주석으로 시작하는 `<section ... id="fs2-top">` 안에 **레이어 div 2개 추가**

기존 `.fs2-a`, `.fs2-a::before`, `.fs2-a .fs2-inner`, `.fs2-a h1`, `.fs2-a .lead`, `.fs2-a .sub` 등의 정의는 **절대 건드리지 말 것** — 다른 섹션이 의존함.

---

## 변경 1 — `<style>` 블록 끝부분에 새 CSS 추가

`</style>` 직전, 마지막 미디어쿼리 (`@media(max-width:768px) { #fs2 .fs2-flow-svg-d{display:none!important;} ... }`) 다음에 아래 블록을 **추가**한다.

### 추가할 CSS

```css
/* 첫 히어로 전용 — 배경 이미지 방식 (다른 .fs2-a 섹션에는 영향 없음) */
#fs2 #fs2-top {
  background: #080f1c;
  padding: 0;
}
#fs2 #fs2-top::before { display: none; }
#fs2 .fs2-hero-bg {
  position: absolute; inset: 0;
  background-image: url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/safety-staff.png');
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  z-index: 0;
}
#fs2 .fs2-hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8,15,28,0.80) 0%,
    rgba(8,15,28,0) 100%
  );
  z-index: 0;
}
#fs2 #fs2-top .fs2-inner {
  min-height: clamp(560px, 80vh, 720px);
  padding-top: calc(var(--tai-nav-h, 90px) + 44px);
  padding-bottom: 68px;
  position: relative;
  z-index: 1;
}
@media(max-width:991px) {
  #fs2 #fs2-top .fs2-inner {
    min-height: auto;
    padding-top: calc(var(--tai-nav-h, 90px) + 24px);
    padding-bottom: 48px;
  }
}
```

**핵심 동작:**
- `#fs2 #fs2-top { background: ... }` → ID 셀렉터(특이도 110)로 `.fs2-a`의 그라데이션(특이도 20)을 오버라이드. 첫 히어로에서만.
- `#fs2 #fs2-top::before { display: none; }` → 기존 radial 오버레이 무력화. 첫 히어로에서만.
- `.fs2-hero-bg`, `.fs2-hero-overlay` → 배경 이미지 + 좌→우 그라데이션 레이어.
- `#fs2-top .fs2-inner`의 `min-height`/`padding`을 표준 히어로 규칙으로 재정의. 첫 히어로에서만.

---

## 변경 2 — `<!-- 1 [A] -->` 섹션 HTML에 레이어 div 2개 추가

### Before

```html
<!-- 1 [A] -->
<section class="fs2-sec fs2-a" id="fs2-top">
  <div class="fs2-inner">
    <h1>안전관리,<br>혼자 다 하고 계시죠?</h1>
    <p class="lead">당신이 못해서가 아닙니다.<br>구조가 그렇게 되어 있는 겁니다.</p>
    <p class="sub">아래로 내려가면, 속으로만 말하던 것들에 하나씩 답이 붙습니다.</p>
    <div class="fs2-scroll">스크롤<i class="fas fa-chevron-down"></i></div>
  </div>
</section>
```

### After

```html
<!-- 1 [A] -->
<section class="fs2-sec fs2-a" id="fs2-top">
  <div class="fs2-hero-bg"></div>
  <div class="fs2-hero-overlay"></div>
  <div class="fs2-inner">
    <h1>안전관리,<br>혼자 다 하고 계시죠?</h1>
    <p class="lead">당신이 못해서가 아닙니다.<br>구조가 그렇게 되어 있는 겁니다.</p>
    <p class="sub">아래로 내려가면, 속으로만 말하던 것들에 하나씩 답이 붙습니다.</p>
    <div class="fs2-scroll">스크롤<i class="fas fa-chevron-down"></i></div>
  </div>
</section>
```

**변경점:** `<section>` 바로 안쪽 첫 줄에 `<div class="fs2-hero-bg"></div>`와 `<div class="fs2-hero-overlay"></div>` 두 줄만 추가. 다른 건 그대로.

---

## 검증 (수정 후)

1. **첫 히어로(`#fs2-top`):** 배경에 `safety-staff.png`가 보이고, 좌측은 어두운 오버레이 위에 텍스트가 잘 읽힘. 우측은 이미지가 자연스럽게 노출.
2. **섹션 6(작업 허가):** 기존 다크 그라데이션 그대로 유지되어야 함. 배경 이미지 안 보임.
3. **섹션 13(최종 CTA):** 기존 다크 그라데이션 그대로 유지. 배경 이미지 안 보임.
4. **첫 히어로 높이:** 데스크톱에서 약 720px 부근, 모바일에서 자동.
5. **카피·CTA 그대로:** "안전관리, 혼자 다 하고 계시죠?" / lead / sub / 스크롤 인디케이터 모두 그대로.
6. **하단 모든 섹션:** 변경 없음.

---

## 주의사항 (반드시 지킬 것)

- `.fs2-a` 정의(`#fs2 .fs2-a { background:linear-gradient(...) }`)는 절대 건드리지 말 것. 섹션 6, 13이 이걸 씀.
- `.fs2-a::before` 정의도 직접 변경하지 말 것. (첫 히어로에서만 `#fs2 #fs2-top::before { display: none; }`로 무력화.)
- `.fs2-a .fs2-inner` 정의도 직접 변경하지 말 것. (첫 히어로에서만 `#fs2 #fs2-top .fs2-inner`로 재정의.)
- HTML에서 `<h1>`, `.lead`, `.sub`, `.fs2-scroll` 텍스트와 마크업 그대로 유지.
- 섹션 2 이하 모든 섹션 그대로 유지.

---

## 커밋 메시지(권장)

```
feat(for-safety-manager): 히어로 배경 이미지 적용 + 표준 높이 (safety-staff.png)
```
