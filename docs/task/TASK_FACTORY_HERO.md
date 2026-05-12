# 작업지시서: target/factory.html 히어로 교체 + 보라색 제거

> **작업자:** Cursor / Claude Code
> **대상 파일:** `taieng` 레포 → `nexas/target/factory.html` (12KB, MCP 가능하나 Cursor 권장)
> **작업 유형:** 히어로 교체 + 보라색 수정
> **배경 이미지:** `https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/factory.png`

---

## 1. 보라색 원인 및 수정

### 원인
- `tai-brand.css` 링크가 없음
- 히어로가 Vuexy 기본 `.breadcrumb-area` 클래스를 사용 → 보라색 그라데이션 배경

### 수정 방법

**(A) `<head>`에 `tai-brand.css` 추가 — `style.css` 바로 아래:**

```html
<link rel="stylesheet" href="../assets/css/style.css">
<link rel="stylesheet" href="../assets/css/tai-brand.css">  <!-- 추가 -->
<link rel="stylesheet" href="../assets/css/responsive.css">
```

**(B) Lato 폰트 → Noto Sans KR로 변경:**

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

### 기존 히어로 (삭제 대상)

```html
<!-- 히어로 -->
<section class="breadcrumb-area text-center">
  ...전체 삭제...
</section>
```

### 새 히어로 (교체)

```html
<!-- 히어로 -->
<section class="tai-hero" id="factory-hero">
  <div class="tai-hero-bg"></div>
  <div class="tai-hero-overlay"></div>
  <div class="container" style="position:relative;z-index:2;">
    <div class="row align-items-center" style="min-height:420px;">
      <div class="col-lg-6 py-5">
        <p class="tai-hero-eyebrow">제조 · 산업현장</p>
        <h1 class="tai-hero-title">
          산업현장 안전관리<br>
          <span class="tai-hero-accent">이제는 바뀌어야 합니다.</span>
        </h1>
        <p class="tai-hero-sub">
          종이 체크리스트와 엑셀은 한계가 있습니다.<br>
          TAI Safe가 법령 의무를 자동 파악하고,<br>
          작업자에게 배정하고, 누락 없이 관리합니다.
        </p>
        <p class="tai-hero-micro">
          산업안전보건법 · 중대재해처벌법 · 화학물질관리법<br>
          우리 공장에 적용되는 법령, 3분이면 확인됩니다.
        </p>
        <div class="tai-hero-cta">
          <a class="tai-btn-pri" href="../free-diagnosis.html">무료 법령진단 시작 →</a>
          <a class="tai-btn-sec" href="../fix-request.html?from=target-factory&type=general">도입 문의</a>
        </div>
      </div>
      <div class="col-lg-6 d-none d-lg-block">
        <!-- 오른쪽은 배경 이미지가 채움 -->
      </div>
    </div>
  </div>
</section>
```

---

## 3. 추가할 CSS

기존 `<style>` 블록 맨 위에 아래 CSS를 추가:

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
  background-image: url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/factory.png');
  background-size: cover;
  background-position: center;
  opacity: 0.45;
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

## 4. 추가 확인사항

### body 클래스
현재 `<body class="sc5">` — `home-X` 클래스 없으므로 OK. 변경 불필요.

### 브랜드 컬러 확인
- Primary: `#1565c0` (tai-brand.css 기준)
- 히어로 버튼에 `#1565c0` 사용 (보라색 아님)
- `.breadcrumb-area` 재정의로 혹시 남아있는 보라색도 차단

### 나머지 섹션
§2(적용 법령), §3(점검 의무), §4(TAI 자동화), §5(CTA)는 변경 없음.
단, `tai-brand.css`가 추가되면 전체 텍스트 컬러/링크 컬러가 브랜드 기준으로 통일됨.

---

## 5. 검증 체크리스트

- [ ] 히어로 배경에 factory.png 이미지 표시
- [ ] 보라색 완전 제거 (히어로 + 기타 영역)
- [ ] 헤드라인: "산업현장 안전관리 / 이제는 바뀌어야 합니다."
- [ ] "이제는 바뀌어야 합니다." 파란색(#60a5fa) 강조
- [ ] CTA 버튼 2개 정상 작동 (무료진단 + 도입문의)
- [ ] 모바일(375px) 레이아웃 정상
- [ ] tai-brand.css 링크 존재
- [ ] 폰트가 Noto Sans KR로 적용
