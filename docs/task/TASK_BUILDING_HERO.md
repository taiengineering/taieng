# 작업지시서: target/building.html 히어로 교체 + 보라색 제거

> **작업자:** Cursor / Claude Code
> **대상 파일:** `taieng` 레포 → `nexas/target/building.html` (12KB)
> **작업 유형:** 히어로 교체 + 보라색 CSS 수정 + tai-brand.css 추가
> **배경 이미지:** `https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/building.png`

---

## 1. 보라색 제거 (factory.html과 동일 패턴)

### (A) `<head>`에 `tai-brand.css` 추가 — `style.css` 바로 아래:

```html
<link rel="stylesheet" href="../assets/css/style.css">
<link rel="stylesheet" href="../assets/css/tai-brand.css">  <!-- 추가 -->
<link rel="stylesheet" href="../assets/css/responsive.css">
```

### (B) Lato 폰트 → Noto Sans KR:

기존:
```html
<link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,300;0,400;0,700;0,900;1,400&display=swap" rel="stylesheet">
```
변경:
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
```

### (C) 인라인 보라색 제거

`<style>` 블록 안에 보라색(`#7B55EA`, `#4c1d95`, `#f5f3ff`)이 있음. 모두 TAI 브랜드 컬러로 교체:

| 기존 (보라색) | 변경 (TAI 브랜드) |
|---|---|
| `var(--main-color, #7B55EA)` | `#1565c0` |
| `color: #4c1d95` | `color: #0f2b4a` |
| `background: #f5f3ff` | `background: #eff6ff` |

---

## 2. 히어로 섹션 교체

### 기존 히어로 (삭제)

```html
<!-- 히어로 -->
<section class="breadcrumb-area text-center">
  ...전체 삭제...
</section>
```

### 새 히어로 (교체)

```html
<!-- 히어로 -->
<section class="tai-hero" id="building-hero">
  <div class="tai-hero-bg"></div>
  <div class="tai-hero-overlay"></div>
  <div class="container" style="position:relative;z-index:2;">
    <div class="row align-items-center" style="min-height:420px;">
      <div class="col-lg-7 py-5">
        <p class="tai-hero-eyebrow">건물 · 시설관리</p>
        <h1 class="tai-hero-title">
          우리 건물에 적용되는 법,<br>
          <span class="tai-hero-accent">몇 개인지 아십니까?</span>
        </h1>
        <p class="tai-hero-sub">
          소방, 전기, 승강기, 가스, 다중이용업소법...<br>
          하나라도 놓치면 과태료입니다.
        </p>
        <p class="tai-hero-micro">
          건물 하나에 적용되는 법정 점검만 연간 수십 건.<br>
          어떤 법이 적용되는지 모르는 것 자체가 위반의 시작입니다.<br>
          3분이면 확인됩니다.
        </p>
        <div class="tai-hero-cta">
          <a class="tai-btn-pri" href="../free-diagnosis.html">무료 법령진단 시작 →</a>
          <a class="tai-btn-sec" href="../fix-request.html?from=target-building&type=general">도입 문의</a>
        </div>
      </div>
      <div class="col-lg-5 d-none d-lg-block">
        <!-- 오른쪽은 배경 이미지가 채움 -->
      </div>
    </div>
  </div>
</section>
```

---

## 3. 추가할 CSS

기존 `<style>` 블록 맨 위에 삽입:

```css
/* ===== 히어로 (보라색 제거, 이미지 배경) ===== */
.tai-hero {
  position: relative;
  overflow: hidden;
  background: #0a0f1a;
}

.tai-hero-bg {
  position: absolute;
  inset: 0;
  background-image: url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/building.png');
  background-size: cover;
  background-position: center;
  opacity: 0.4;
}

.tai-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(10,15,26,0.97) 0%,
    rgba(10,15,26,0.88) 40%,
    rgba(10,15,26,0.35) 75%,
    rgba(10,15,26,0.15) 100%
  );
}

.tai-hero-eyebrow {
  font-size: 12px;
  font-weight: 700;
  color: #60a5fa;
  letter-spacing: 0.08em;
  margin: 0 0 14px;
  font-family: 'Noto Sans KR', sans-serif;
}

.tai-hero-title {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: clamp(1.6rem, 4.5vw, 2.5rem);
  font-weight: 900;
  color: #fff;
  line-height: 1.25;
  margin: 0 0 20px;
  letter-spacing: -0.02em;
}

.tai-hero-accent {
  color: #60a5fa;
}

.tai-hero-sub {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: clamp(0.92rem, 2vw, 1.05rem);
  font-weight: 500;
  color: rgba(255,255,255,0.82);
  line-height: 1.7;
  max-width: 38ch;
  margin: 0 0 16px;
  border-left: 3px solid #60a5fa;
  padding-left: 16px;
}

.tai-hero-micro {
  font-size: 0.82rem;
  color: rgba(255,255,255,0.4);
  max-width: 44ch;
  line-height: 1.65;
  margin: 0 0 24px;
  font-family: 'Noto Sans KR', sans-serif;
}

.tai-hero-cta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tai-btn-pri {
  display: inline-flex;
  align-items: center;
  padding: 13px 24px;
  border-radius: 10px;
  background: #1565c0;
  color: #fff !important;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  font-family: 'Noto Sans KR', sans-serif;
  transition: background 0.15s;
}
.tai-btn-pri:hover {
  background: #0f4c91;
  color: #fff !important;
  text-decoration: none;
}

.tai-btn-sec {
  display: inline-flex;
  align-items: center;
  padding: 13px 24px;
  border-radius: 10px;
  background: transparent;
  color: rgba(255,255,255,0.85) !important;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  border: 1px solid rgba(255,255,255,0.25);
  font-family: 'Noto Sans KR', sans-serif;
  transition: border-color 0.15s;
}
.tai-btn-sec:hover {
  border-color: rgba(255,255,255,0.5);
  color: #fff !important;
  text-decoration: none;
}

/* 모바일 */
@media (max-width: 768px) {
  .tai-hero-bg {
    background-position: top center;
    opacity: 0.25;
  }
  .tai-hero-overlay {
    background: linear-gradient(
      180deg,
      rgba(10,15,26,0.95) 0%,
      rgba(10,15,26,0.88) 100%
    );
  }
  .tai-hero-title {
    font-size: 1.6rem;
  }
}

/* Vuexy breadcrumb 보라색 완전 차단 */
.breadcrumb-area {
  background: linear-gradient(160deg, #0a0f1a 0%, #0f172a 40%, #1e3a5f 100%) !important;
}
```

---

## 4. duty-card 보라색 수정

기존 `<style>` 블록에서 `.duty-card`, `.auto-block`의 보라색을 TAI 브랜드 컬러로 변경:

```css
/* 기존 */
.duty-card { border-left: 4px solid var(--main-color, #7B55EA); }
.duty-card .duty-cycle { color: var(--main-color, #7B55EA); }
.auto-block { background: #f5f3ff; }
.auto-block h5 { color: #4c1d95; }

/* 변경 */
.duty-card { border-left: 4px solid #1565c0; }
.duty-card .duty-cycle { color: #1565c0; }
.auto-block { background: #eff6ff; }
.auto-block h5 { color: #0f2b4a; }
```

---

## 5. 검증 체크리스트

- [ ] 히어로 배경에 building.png 이미지 표시
- [ ] 보라색 완전 제거 (히어로 + duty-card + auto-block)
- [ ] 헤드라인: "우리 건물에 적용되는 법, / 몇 개인지 아십니까?"
- [ ] "몇 개인지 아십니까?" 파란색(#60a5fa) 강조
- [ ] CTA 버튼 2개 정상 작동
- [ ] 모바일(375px) 레이아웃 정상
- [ ] tai-brand.css 링크 존재
- [ ] 폰트가 Noto Sans KR로 적용
- [ ] duty-card 좌측 보더가 파란색(#1565c0)
- [ ] auto-block 배경이 연파란(#eff6ff), 제목이 남색(#0f2b4a)
