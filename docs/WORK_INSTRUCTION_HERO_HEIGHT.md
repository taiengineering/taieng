# 작업지시서: 전체 페이지 히어로 높이 통일

## 기준

`service/diagnosis.html`의 `.diag-hero` 섹션을 기준으로 통일합니다.

### 기준 히어로 스펙 (diagnosis)
```css
/* 기준값 */
min-height: 420px;
padding-top: 80px;     /* navbar 90px 고려 */
padding-bottom: 60px;
/* 실제 렌더링 높이: ~617px */
```

### navbar 높이
```
--tai-nav-h: 90px;
```

## 공통 CSS 클래스 추가 (`tai-main.css` 또는 인라인)

모든 페이지의 히어로에 아래 공통 스타일을 적용하세요:

```css
/* 히어로 통일 높이 420px, padding-top 80px (nav 90px 고려) */
.tai-hero-standard {
  min-height: 420px;
  padding-top: 80px;
  padding-bottom: 60px;
}
@media(max-width:991px) {
  .tai-hero-standard {
    min-height: auto;
    padding-top: calc(var(--tai-nav-h, 90px) + 24px);
    padding-bottom: 40px;
  }
}
@media(max-width:575px) {
  .tai-hero-standard {
    padding-top: calc(var(--tai-nav-h, 90px) + 16px);
    padding-bottom: 32px;
  }
}
```

## 페이지별 수정 내역

### 1. index.html (홈)
- **현재:** `.hero-split` — min-height: 420px → 이미 맞음
- **확인만:** padding-top이 80px인지 확인, 아니면 조정

### 2. service/diagnosis.html (법령진단) — 기준 페이지
- **현재:** `.diag-hero` — min-height: 420px, padding: 80px 0 60px ✅
- **수정 불필요** (기준)

### 3. service/saas.html (SaaS)
- **현재:** `.pat-hero` — min-height: 420px → 맞음
- **확인:** padding-top 80px, padding-bottom 60px으로 조정

### 4. for-business-owner.html (사업주)
- **현재:** `.owner-hero-section` + `.owner-hero-left-col` — min-height: **520px** ❌
- **수정:** min-height: **420px**, padding: 80px 48px 60px 80px
- **우측 이미지:** `.owner-hero-right-col` min-height도 420px로 맞춤
- **모바일:** min-height: auto, padding 조정

### 5. for-safety-manager.html (안전관리자)
- **현재:** 히어로 클래스명 없음 (Vuexy 템플릿 인라인 스타일 사용)
- **수정:** 히어로 섹션에 min-height: 420px, padding-top: 80px, padding-bottom: 60px 적용
- **주의:** body class에 `home-X` 같은 Vuexy 테마 클래스가 있으면 제거 (보라색 이슈 발생)

### 6. for-expert.html (전문가)
- **현재:** min-height: 420px → 맞음
- **확인:** padding-top 80px 맞추기

### 7. for-repair.html (수선연결)
- **현재:** 확인 필요
- **수정:** 히어로 섹션 min-height: 420px, padding-top: 80px, padding-bottom: 60px

### 8. for-agency.html (선임연결)
- **현재:** 확인 필요
- **수정:** 동일

### 9. for-consultant.html (컨설팅)
- **현재:** 확인 필요
- **수정:** 동일

### 10. safety-news.html (안전자료)
- **현재:** `.sh-hero` — padding: calc(var(--tai-nav-h,90px) + 40px) 0 48px
- **수정:** min-height: 420px 추가, padding-top: 80px, padding-bottom: 60px
- **검색바 위치:** 힅어로 내 아래쪽으로 자연스럽게 배치

### 11. accident-cases.html (재해사례)
- **현재:** `.ac-hero` — padding: calc(var(--tai-nav-h,90px) + 40px) 0 48px
- **수정:** min-height: 420px 추가, padding-top: 80px, padding-bottom: 60px

### 12. law-updates.html (개정법령)
- **현재:** 2칸 스플릿 레이아웃, 좌측이 히어로 역할
- **수정:** 좌측 패널의 상단 영역을 420px 높이에 맞춰 padding 조정

### 13. precedent-search.html (판례검색)
- **현재:** 확인 필요
- **수정:** min-height: 420px, padding-top: 80px, padding-bottom: 60px

### 14. target/building.html, target/factory.html, target/construction.html
- **현재:** 확인 필요
- **수정:** 동일

## 작업 방법

1. 각 페이지의 히어로 섹션을 열고
2. 인라인 `<style>` 또는 CSS에서 히어로 관련 스타일 찾기
3. 아래 값으로 통일:
   ```
   min-height: 420px;
   padding-top: 80px;
   padding-bottom: 60px;
   ```
4. 모바일 반응형은 각 페이지의 기존 브레이크포인트를 유지하되, padding-top은 `calc(var(--tai-nav-h, 90px) + 16px~24px)` 사용
5. 텍스트가 쟘리거나 넘치는 경우 font-size 또는 h1 line-height 조정
6. 이미지가 있는 히어로 (사업주, 진단 등)는 이미지 컨테이너도 420px에 맞춤

## 주의사항

- **diagnosis.html은 수정하지 마세요** (기준 페이지)
- `tai-brand.css` body class `home-X`가 있으면 제거해야 보라색 이슈 안 남
- header.js, footer.js는 수정하지 마세요
- git push origin main → Cloudflare 자동배포
