# [Cursor 작업 지시서] saas.html 히어로 이미지 잘림 수정

작성일: 2026-05-01
대상 파일: `nexas/service/saas.html`
배경: 이전 작업으로 배경 이미지 적용 완료. 그러나 `background-size: cover`로 인해 이미지 하단(회색 아이콘 패널)이 어색하게 잘려 보임. 이미지 비율 유지하면서 잘리지 않게 표시하도록 패치.

---

## 문제

`saas1.png`은 가로로 긴 timeline 일러스트(조선시대 → 2050년대 진화). `cover`는 컨테이너를 꽉 채우려고 비율을 유지하며 이미지를 자르는데, 히어로 비율과 이미지 비율이 달라 **하단의 회색 아이콘 패널이 부분적으로 잘려 어색하게 보임**.

## 해결

이미지 height를 히어로 height에 맞추고 width는 비율 유지(`background-size: auto 100%`). 우측 정렬해서 이미지가 통째로 우측에 보이고, 좌측은 그라데이션 오버레이로 자연스럽게 텍스트 영역 확보.

---

## 작업 범위

`<style>` 블록 안의 두 클래스 CSS만 교체:
1. `#saas-page .pat-hero-bg`
2. `#saas-page .pat-hero-overlay`

그리고 모바일 미디어쿼리(`@media(max-width:991px)`)에 히어로 이미지 처리 규칙 추가.

HTML은 절대 건드리지 말 것 (이미 정상).

---

## 변경 1 — `.pat-hero-bg` CSS 교체

### Before

```css
#saas-page .pat-hero-bg {
  position: absolute; inset: 0;
  background-image: url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/saas1.png');
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
}
```

### After

```css
#saas-page .pat-hero-bg {
  position: absolute; inset: 0;
  background-image: url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/saas1.png');
  background-size: auto 100%;
  background-position: right center;
  background-repeat: no-repeat;
}
```

**핵심 변경점:**
- `background-size: cover` → `auto 100%` (이미지 height를 컨테이너 height에 정확히 맞춤. width는 비율 유지로 자동)
- `background-position: center center` → `right center` (우측 정렬)
- 결과: 이미지가 우측에 통째로 보이고 잘림 없음

---

## 변경 2 — `.pat-hero-overlay` 그라데이션 강화

좌측 텍스트 영역의 가독성을 높이고, 이미지가 시작되는 영역으로 자연스럽게 페이드.

### Before

```css
#saas-page .pat-hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(
    90deg,
    rgba(15,23,42,0.80) 0%,
    rgba(15,23,42,0) 100%
  );
}
```

### After

```css
#saas-page .pat-hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(
    90deg,
    rgba(15,23,42,0.96) 0%,
    rgba(15,23,42,0.92) 30%,
    rgba(15,23,42,0.40) 55%,
    rgba(15,23,42,0) 75%
  );
}
```

**핵심 변경점:**
- 4-stop으로 변경. 좌측은 거의 불투명(0.96)으로 텍스트 가독성 확보, 55% 지점부터 빠르게 투명화, 75% 지점에서 완전 투명.
- 결과: 좌측 ~30%는 다크 배경, 중간은 페이드, 우측 ~25%는 이미지 그대로 노출.

---

## 변경 3 — 모바일 미디어쿼리에 이미지 처리 추가

`@media(max-width:991px)` 블록에서, 이미 추가된 `.pat-hero` / `.pat-hero-inner` 두 줄 다음에 이미지 처리 두 줄을 **추가**할 것.

### Before (해당 블록 일부)

```css
@media(max-width:991px) {
  #saas-page .pat-hero { min-height: auto; }
  #saas-page .pat-hero-inner { padding-top: calc(var(--tai-nav-h, 90px) + 24px); padding-bottom: 48px; }
  #saas-page .feat-visual { max-width: 100%; }
  ...
}
```

### After (해당 블록 일부)

```css
@media(max-width:991px) {
  #saas-page .pat-hero { min-height: auto; }
  #saas-page .pat-hero-inner { padding-top: calc(var(--tai-nav-h, 90px) + 24px); padding-bottom: 48px; }
  #saas-page .pat-hero-bg { background-size: cover; background-position: right top; opacity: .35; }
  #saas-page .pat-hero-overlay { background: linear-gradient(180deg, rgba(15,23,42,0.85) 0%, rgba(15,23,42,0.92) 100%); }
  #saas-page .feat-visual { max-width: 100%; }
  ...
}
```

**핵심 변경점 (모바일 전용):**
- 모바일에서는 컨테이너 폭이 좁아 `auto 100%` 적용 시 이미지 폭이 너무 길어져 우측이 화면 밖으로 나감 → `cover`로 다시 채우기
- 이미지를 흐리게(`opacity: .35`) 깔고 위에 진한 다크 오버레이를 덮어 텍스트만 또렷이 보이게
- 그라데이션 방향도 좌→우 대신 위→아래로 변경 (모바일은 세로 레이아웃이라)

이미 추가된 두 줄(`min-height: auto`, `padding-top`) 사이에 끼워 넣지 말고, 그 두 줄 **다음**에 두 줄을 추가할 것.

---

## 검증 (수정 후)

1. **데스크톱(1920×1080):** 이미지가 우측에 통째로 보임. 잘림 없음. timeline 일러스트의 모든 인물(조선시대~2050년대)과 하단 회색 패널까지 전부 보임. 좌측은 진한 다크 배경 위에 텍스트.
2. **태블릿(1024×768):** 이미지 height가 줄어 폭도 자동으로 줄어듦. 우측에 자연스럽게 정렬.
3. **모바일(375px):** 이미지가 흐리게 깔리고, 다크 오버레이 위에 텍스트가 또렷이 보임. 이미지 잘림 무시(흐려서 안 보임).
4. **하단 콘텐츠:** "총무팀장…" 섹션 이하 변경 없음.

---

## 주의사항

- HTML 건드리지 말 것. CSS 3개 위치만 수정.
- 다른 클래스(`.pat-hero` 자체, `.pat-eyebrow`, `.pat-hero h1` 등) 그대로 유지.
- 모바일 미디어쿼리 안의 다른 규칙(`.feat-visual`, `.feat-pair` 등) 그대로 유지.

---

## 커밋 메시지(권장)

```
fix(saas): 히어로 이미지 잘림 수정 (auto 100% + right 정렬 + 그라데이션 강화)
```
