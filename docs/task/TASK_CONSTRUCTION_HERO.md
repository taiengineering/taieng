# 작업지시서: target/construction.html 히어로 교체 + 보라색 제거

> **작업자:** Cursor / Claude Code
> **대상 파일:** `taieng` 레포 → `nexas/target/construction.html` (12KB)
> **작업 유형:** 히어로 교체 + tai-brand.css 추가 + 폰트 변경
> **배경 이미지:** `https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/build.png`

---

## 1. `<head>` 수정

### (A) `tai-brand.css` 추가 — `style.css` 바로 아래:

```html
<link rel="stylesheet" href="../assets/css/style.css">
<link rel="stylesheet" href="../assets/css/tai-brand.css">  <!-- 추가 -->
<link rel="stylesheet" href="../assets/css/responsive.css">
```

### (B) Lato → Noto Sans KR:

기존:
```html
<link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,300;0,400;0,700;0,900;1,400&display=swap" rel="stylesheet">
```
변경:
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
```

---

## 2. 히어로 섹션 교체

### 기존 (삭제)

```html
<!-- 히어로 -->
<section class="breadcrumb-area text-center">
  ...전체 삭제...
</section>
```

### 새 히어로 (교체)

```html
<!-- 히어로 -->
<section class="tai-hero" id="construction-hero">
  <div class="tai-hero-bg"></div>
  <div class="tai-hero-overlay"></div>
  <div class="container" style="position:relative;z-index:2;">
    <div class="row align-items-center" style="min-height:420px;">
      <div class="col-lg-7 py-5">
        <p class="tai-hero-eyebrow">건설현장</p>
        <h1 class="tai-hero-title">
          오늘도 서류 먼저 쓰고,<br>
          <span class="tai-hero-accent">현장은 나중입니다.</span>
        </h1>
        <p class="tai-hero-sub">
          TBM, 위험성평가, 안전관리계획서, 일보...<br>
          서류에 묻혀 정작 현장을 못 봅니다.
        </p>
        <p class="tai-hero-micro">
          TAI Safe는 서류를 자동화해서<br>
          안전관리자가 현장에 집중할 수 있게 만듭니다.<br>
          우리 현장에 적용되는 법령, 3분이면 확인됩니다.
        </p>
        <div class="tai-hero-cta">
          <a class="tai-btn-pri" href="../free-diagnosis.html">무료 법령진단 시작 →</a>
          <a class="tai-btn-sec" href="../fix-request.html?from=target-construction&type=general">도입 문의</a>
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
/* ===== 히어로 (이미지 배경) ===== */
.tai-hero {
  position: relative;
  overflow: hidden;
  background: #0a0f1a;
}

.tai-hero-bg {
  position: absolute;
  inset: 0;
  background-image: url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/build.png');
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

## 4. 나머지 섹션 컬러 확인

construction.html은 보라색이 아닌 **오렌지/앰버(`#b45309`, `#fffbeb`, `#78350f`)** 를 사용 중.
이건 건설 섹터 고유색으로 **변경하지 않음** (TAI 브랜드 블루와 충돌 없음).

단, `tai-brand.css`가 추가되면서 Vuexy 기본 `.breadcrumb-area`, `.subscribe-area` 등의 보라색이 자동 차단됨.

---

## 5. 검증 체크리스트

- [ ] 히어로 배경에 build.png 이미지 표시
- [ ] 보라색 완전 제거 (히어로 영역)
- [ ] 헤드라인: "오늘도 서류 먼저 쓰고, / 현장은 나중입니다."
- [ ] "현장은 나중입니다." 파란색(#60a5fa) 강조
- [ ] CTA 버튼 2개 정상 작동 (무료진단 + 도입문의)
- [ ] 모바일(375px) 레이아웃 정상
- [ ] tai-brand.css 링크 존재
- [ ] 폰트가 Noto Sans KR로 적용
- [ ] duty-card 좌측 보더 오렌지(#b45309) 유지 (변경 없음)
- [ ] auto-block 배경 앰버(#fffbeb) 유지 (변경 없음)
