# 2026-04-19 프론트 작업 로그 (taieng 리포)

**브랜치**: dev
**작업창**: 프론트 전용
**작업자**: 심태왕 + Claude

---

## 커밋 목록 (시간순)

### 1. `1dc9416` — feat(nexas): 판례 검색 페이지 분리

**배경**: safety-news.html 한 장에 "안전정보 뉴스"와 "이 판례, 알고 계셨나요?" 두 개의 컨텐츠가 섞여 있어 페이지 분리 요청.

**변경**:
- `nexas/safety-news.html`: 하단 '이 판례' 섹션 제거, 관련 CSS/JS 정리
- `nexas/precedent-search.html` 신규: 검색바 + 구분 필터(전체/산업안전/산재) + 카드 리스트 + 더보기 + API fallback

---

### 2. `1511f33` — chore(nexas/safety-news): 하단 판례 CTA 섹션 삭제

**배경**: 초기 분리 시 safety-news.html 하단에 판례 페이지 유도 CTA를 남겨뒀으나 불필요하다고 판단됨.

**변경**: `.prec-cta` CSS + CTA 박스 완전 삭제. 안전정보 페이지는 뉴스 목록만 노출.

---

### 3. `e155636` — refactor(nexas/precedent-search): patents.html 표준 히어로 적용

**배경**: 사용자 지적 "탑부분이 어수선함. patents.html 방식이 표준". 수정할 때마다 페이지 디자인이 달라지는 문제를 일관성 확보로 해결.

**변경** (precedent-search.html 히어로 전면 교체):
- `.prec-hero`: `min-height:520px` + flex + absolute bg layer + gradient overlay (patents의 `.pat-hero`와 동일 구조)
- eyebrow 배지 + h1 + sub 3단 좌측 정렬 타이포
- 검색창 `margin-top:-40px` 제거 → 독립 섹션(`.search-sec`)으로 완전 분리 (히어로와 겹치지 않음)
- 반응형 브레이크포인트 patents 동일 (991/575px)

**표준 원칙 확정**: `patents.html`의 `.pat-hero` 구조(eyebrow + h1 + sub)를 모든 페이지 상단 타이틀 표준으로 고정.

---

### 4. `df7c6ee` — refactor(nexas/fix-request): 상단 어수선함 해결

**배경**: new.taieng.co.kr/fix-request에서 네비가 좌측 다크 패널에 묻혀 흐릿, 좌측 패널 타이포가 표준과 달라 어수선함.

**변경** (최소 침습 원칙 — 레이아웃·채팅 UI·JS 그대로):
1. `.navbar-area`: 흰색 배경 + box-shadow + z-index:100 → 네비 가독성 확보
2. 좌측 패널 타이포를 patents 표준으로 교체:
   - 이모지 🎧 제거
   - eyebrow 배지 추가 ("TAI Fix · 전문가 매칭")
   - h2 → h1, `clamp()` + `font-weight:900` + `letter-spacing` + text-shadow
   - `em` 강조로 "전문 업체" 하이라이트 (#60a5fa)
3. `.fix-left`: `justify-content:flex-start` + `padding:64px 40px 48px`로 상단부터 자연스럽게
4. 배경 그라데이션 patents 동일 톤 (#0a0a1a → #111b3a → #0a0a1a)

---

### 5. `77743fd` — feat(nexas/assets): 로고 PNG → SVG 전환 + 헤더 2배 확대

**배경**: 사용자 요청 "로고를 지금보다 두 배로. 틀을 벗어나지 않는 한도에서 제일 크게". PNG 확대 시 화질 저하 우려 → SVG로 전환 결정.

**변경** (4개 파일 동시):
1. `nexas/assets/img/tai-logo.svg` 신규 생성
   - 제공받은 고해상도 원본(1045×290) 이미지 분석 기반 SVG 재작성
   - 구성: 건축 스캐폴딩 격자 + 2색 지붕(파랑/회색) + TAI 스텐실 글자 + 텍스트 2줄
   - 색상: 파랑 `#2274C6`, 회색 `#6C7280`, 네이비 텍스트 `#1E293B`, 서브 `#475569`
   - ⚠️ 원본 벡터 파일이 아닌 PNG 관찰 기반 근사본 — 디자인 미세 차이 존재
2. `header.js` v2.2.0: `tai-logo.png` → `tai-logo.svg`
3. `footer.js` v2.4.1: `tai-logo.png` → `tai-logo.svg`, 풋터 로고 36 → 44px 소폭 확대
4. `tai-main.css` v1.10: 헤더 로고 전역 크기 규칙 신규 추가 — 60px (데스크톱) / 48px (991px↓) / 42px (575px↓), `!important`로 Nexas 원본 오버라이드

**유지**: 기존 `tai-logo.png`는 삭제하지 않음 (이메일/소셜 프리뷰 참조 보존).

---

## 이슈 (미해결)

### ISSUE-1: SVG 로고가 원본과 살짝 다름

**상태**: 내일 AI 원본 파일 수령 후 교체 예정 (2026-04-20)

**현상**:
- 건축 스캐폴딩 격자: 원본은 복잡한 교차, SVG는 수직 5줄 + 수평 3줄로 단순화
- TAI 글자 스텐실 디테일: 각도·비율이 완벽히 일치하지 않음
- 텍스트 폰트: 원본 유료 폰트일 경우 `Noto Sans KR / Pretendard` 폴백으로 글자 두께·간격 미세 차이

**조치 예정**: `.ai` 원본 수령 → Illustrator에서 SVG export → `tai-logo.svg` 덮어쓰기. 경로·크기 규칙은 그대로 유효.

---

## 다음 세션 인수인계

### main 머지 대기 (dev → main PR 예정)
dev 브랜치에 5개 커밋 누적. 내일 AI 파일 수령해 로고 교체한 뒤 일괄 PR 권장.

### 표준 원칙
앞으로 신규 페이지는 **patents.html의 `.pat-hero` 구조 필수 준수**:
- `min-height:520~560px`, `position:relative`, `display:flex align-items:center`
- 배경은 `.xxx-hero-bg` absolute 레이어 + 그라데이션 오버레이
- 콘텐츠 컨테이너: `max-width:1200px`, `padding:100px 48px 72px`
- 좌측 정렬 텍스트 블록: eyebrow → h1 → sub
- 인터랙티브 요소(검색·필터·CTA)는 **별도 섹션**, 히어로와 절대 겹침 금지

### 표준 미적용 페이지 (향후 통일 작업 대상)
- safety-news.html (히어로 단순 네이비 배경)
- free-diagnosis.html (좌우분리 레이아웃 — 사용자 요청대로 유지 중)
- log-in.html, contact.html 등

### 금지어·정책 재확인
- 소개비/소개수수료/인력소개 → "플랫폼 이용료/연결 서비스료/매칭 서비스료"
- 카카오 API 전면 금지 (주소=juso.go.kr, 역지오=Vworld, 알림=MessageMi)
- 진단 문구: "기계적 대조" → "정밀 분석하여 도출", "더 많이 입력하면 더 정확" → "해당 법령이 추가 적용됩니다"
- 브라우저 테스트 금지 — Python 파일 또는 Supabase MCP만
