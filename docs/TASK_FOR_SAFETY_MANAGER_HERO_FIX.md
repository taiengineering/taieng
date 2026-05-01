# [Cursor 작업 지시서] for-safety-manager.html 히어로 — 말풍선 잘림 수정

작성일: 2026-05-01
대상 파일: `nexas/for-safety-manager.html`
배경: 이전 작업으로 배경 이미지(`safety-staff.png`) 적용 완료. 그러나 `background-size: cover`로 인해 인물 양쪽의 말풍선들이 잘려서 의미 손상.

---

## 문제

`safety-staff.png`은 인물(안전관리자)을 중심으로 사방에 생각 말풍선이 배치된 일러스트. 콘텐츠가 가장자리까지 분산되어 있어 `cover`로 비율 맞추는 과정에서 좌우 가장자리 말풍선들("서류가 너무 많아…", "현장은 계속 바쁘고…", "혹시 놓치는 건 없을까…", "보고는 끝이 없어…", "사고는 왜 반복될까…")이 잘림.

## 해결

이미지 height를 히어로 height에 정확히 맞추고(`auto 100%`), 우측 정렬해서 이미지 전체가 잘리지 않게. 좌측 텍스트 영역은 그라데이션 오버레이로 처리. saas 페이지와 동일한 패턴.

---

## 작업 범위

`<style>` 블록 안의 두 클래스 CSS만 교체:
1. `#fs2 .fs2-hero-bg`
2. `#fs2 .fs2-hero-overlay`

그리고 모바일 미디어쿼리 안의 히어로 처리 부분에 이미지 처리 두 줄 추가.

HTML은 절대 건드리지 말 것.

---

## 변경 1 — `.fs2-hero-bg` CSS 교체

### Before

```css
#fs2 .fs2-hero-bg {
  position: absolute; inset: 0;
  background-image: url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/safety-staff.png');
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  z-index: 0;
}
```

### After

```css
#fs2 .fs2-hero-bg {
  position: absolute; inset: 0;
  background-image: url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/safety-staff.png');
  background-size: auto 100%;
  background-position: right center;
  background-repeat: no-repeat;
  z-index: 0;
}
```

**핵심 변경점:**
- `background-size: cover` → `auto 100%`
- `background-position: center center` → `right center`

---

## 변경 2 — `.fs2-hero-overlay` 그라데이션 강화

### Before

```css
#fs2 .fs2-hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8,15,28,0.80) 0%,
    rgba(8,15,28,0) 100%
  );
  z-index: 0;
}
```

### After

```css
#fs2 .fs2-hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8,15,28,0.96) 0%,
    rgba(8,15,28,0.92) 30%,
    rgba(8,15,28,0.40) 55%,
    rgba(8,15,28,0) 75%
  );
  z-index: 0;
}
```

**핵심 변경점:** 4-stop 그라데이션. 좌측 30%까지 거의 불투명(텍스트 영역 보호), 55% 지점부터 빠르게 투명화, 75%에서 완전 투명.

---

## 변경 3 — 모바일 미디어쿼리에 이미지 처리 추가

이전 작업으로 추가했던 `@media(max-width:991px)` 블록의 `#fs2 #fs2-top .fs2-inner { ... }` 다음에 두 줄 추가.

### Before (해당 블록)

```css
@media(max-width:991px) {
  #fs2 #fs2-top .fs2-inner {
    min-height: auto;
    padding-top: calc(var(--tai-nav-h, 90px) + 24px);
    padding-bottom: 48px;
  }
}
```

### After (해당 블록)

```css
@media(max-width:991px) {
  #fs2 #fs2-top .fs2-inner {
    min-height: auto;
    padding-top: calc(var(--tai-nav-h, 90px) + 24px);
    padding-bottom: 48px;
  }
  #fs2 #fs2-top .fs2-hero-bg { background-size: cover; background-position: right top; opacity: .35; }
  #fs2 #fs2-top .fs2-hero-overlay { background: linear-gradient(180deg, rgba(8,15,28,0.85) 0%, rgba(8,15,28,0.92) 100%); }
}
```

**핵심 변경점 (모바일 전용):**
- 모바일에서는 폭이 좁아 `auto 100%` 적용 시 이미지가 화면 밖으로 나감 → `cover`로 채움
- `opacity: .35`로 흐리게 깔고 위에 진한 다크 오버레이를 덮어 텍스트만 또렷이
- 그라데이션 방향 좌→우 대신 위→아래로 (모바일 세로 레이아웃)

`@media(max-width:768px)` 등 다른 미디어쿼리는 절대 건드리지 말 것.

---

## 검증

1. **데스크톱:** 인물과 사방의 말풍선 5개 모두 잘리지 않고 보임. 좌측은 진한 다크 위에 텍스트 또렷.
2. **태블릿:** 이미지 height가 줄면서 폭도 자동으로 줄어듦. 우측 정렬 유지.
3. **모바일:** 이미지가 흐리게 배경으로 깔리고, 다크 오버레이 위 텍스트만 또렷.
4. **다른 섹션 영향 없음:** 섹션 6, 13의 `.fs2-a` 그라데이션 그대로 유지.

---

## 주의사항

- HTML 건드리지 말 것. CSS 3곳만 수정.
- `.fs2-a` 자체 정의는 절대 건드리지 말 것 (다른 섹션 의존).
- `#fs2 #fs2-top` 외의 셀렉터는 건드리지 말 것.
- 카피(`<h1>`, `.lead`, `.sub`) 그대로 유지.
- `@media(max-width:768px)`, `@media(max-width:640px)` 등 다른 미디어쿼리 그대로.

---

## 커밋 메시지(권장)

```
fix(for-safety-manager): 히어로 말풍선 잘림 수정 (auto 100% + right 정렬 + 그라데이션 강화)
```
