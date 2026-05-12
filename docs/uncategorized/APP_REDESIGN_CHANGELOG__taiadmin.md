# TAI Safe 앱 리디자인 + 마케팅 사이트 작업 내역 (2026-04-30)

## 1. 앱 디자인 시스템 (tai-admin)

### app-design.css 진화
| 버전 | 내용 | 커밋 |
|---|---|---|
| v1.0 | 23개 컴포넌트, 절제된 색상 | `f51f95f` |
| v2.0 | 다크/라이트 테마, 28개 시맨틱 토큰 | `109e2df` → Cursor 덮어씀 → `cb4d8cc` 재적용 |
| v2.1 | 히어로/긴급/버튼 무채색화, 숫자·아이콘에만 색 | `8be0857` |
| v2.2 | 카본 파이버 텍스처 배경 (CSS 패턴, 다크 전용), 헤더 투명화 | `1bf4fe0` |

### HTML v1→v2 토큰 치환
- 15개 서브페이지 `<style>` 블록 내 v1→v2 변수 치환 (페이지 고유 스타일 보존)
- `data-theme="dark"` + `app-design.css` 링크 보장
- 그라데이션 → 단색, 밝은 배경 → subtle 토큰
- 커밋: `c7e1eab`

### emergency.html 전면 재작성
- v1 미정의 변수 11개(`--yellow`, `--dark2`, `--gray2` 등) → v2 치환
- `color:var(--bg-1)` (텍스트 안 보임) → `color:var(--text-0)` 수정
- 커밋: `8aa51ce`

### i18n.js 구문 오류 수정
- 단일 따옴표 안 줄바꿈 → `\n` 치환 (상태 머신 파서 `scripts/fix-i18n-newlines.js` v2)
- 정규식 v1 스크립트가 파일 파괴 (1500줄→43줄) → `8a00402`로 복원 후 v2 파서로 수정

### Cloudflare 캐시 버스팅
- CSS/JS 변경이 반영 안 됨 → `?v=N` 캐시 버스팅 적용 (현재 v=4)
- `scripts/fix-cache.js` — 버전 일괄 업데이트 스크립트

### 테마 토글 기능
- `_utils.js`에 `toggleTheme()` / `initTheme()` 추가
- localStorage 기반 테마 유지, 홈 헤더 ☀️ 버튼

### 기능 점검 결과
- ✅ API 서버 healthy (DB/법령엔진/Fix채팅 OK)
- ✅ 로그인 유지 (localStorage `tai_user` 기반, 새로고침 후 인증 건너뜀)
- ✅ i18n `t()` 함수 정상, 점검 항목 5건 렌더링
- ✅ 전 페이지 v1 변수 잔존 0건

---

## 2. 앱 스크린샷 자동 캡처

### Puppeteer 스크립트
- `scripts/capture-app.js` — 전체 페이지 자동 캡처
- 390×844 @2x, 목업 데이터(박현수, 산업모드, 활동이력 5건) 주입
- 다크 모드 12/15 성공 (tbm/risk/education 타임아웃)
- 라이트 모드 캡처도 완료

### Supabase Storage 업로드
- `site-assets/app-screenshots/` 경로에 다크+라이트 캡처 PNG 업로드
- 파일명 규칙: `01-home.png` (다크), `01-home-light.png` (라이트)

---

## 3. 마케팅 사이트 (taieng)

### `nexas/index.html`
- `.app-screen-area` SVG 3장 → 실제 라이트 캡처 교체 (홈/점검/긴급)
- 이미지 URL: `site-assets/app-screenshots/01-home-light.png` 등
- 커밋: `84f5691` (다크) → `84f3aea` (라이트 교체)

### `nexas/for-business-owner.html`
- ③ 해결카드와 ④ 감독관시나리오 사이에 앱 프리뷰 섹션 신규 추가
- 다크 배경 `#0b0f14` + "작업자가 이렇게 쉽게 씁니다" 카피 + 홈+점검 2장
- 커밋: `4f7ab37` (다크) → `84f3aea` (라이트 교체)

---

## 4. GitHub 이슈 현황

| # | 제목 | 상태 |
|---|---|---|
| #6 | [완료] 앱 디자인 시스템 v2.2 전면 리디자인 | ✅ Closed |
| #7 | [UI] education.html 상단 배너 밝은 색 잔존 | 🔴 Open |
| #8 | [인프라] Cloudflare Pages 캐시 정책 | 🔴 Open |
| #9 | [마케팅] 앱 UI 캡처 → 마케팅 사이트 적용 | 🔴 Open (일부 완료) |
| #10 | [주의] clean-app-html.js 사용 금지 | 🔴 Open |

---

## 5. 핵심 규칙

- **`app-design.css`는 Claude MCP 전용.** Cursor 수정 시 v1으로 덮어쓰는 사고 반복됨
- CSS 변경 후 `scripts/fix-cache.js`로 `?v=N` 올리고 푸시 필수
- 서브페이지 `<style>` 블록은 보존 (페이지 고유 스타일 포함), 내부 변수만 치환
- `tai-admin` 레포는 `main` 직접 커밋 (staging 없음)
- `scripts/clean-app-html.js` 사용 금지 (Issue #10)

---

## 6. PENDING 작업

### 마케팅 사이트 캡처 배치 (나머지)
- `for-safety-manager.html` (39KB) — 시정조치/이력/프로필 캡처
- `service/diagnosis.html` — 홈 캡처 1장
- `service/saas.html` — 미구현

### 앱 UI 수정
- `education.html` 상단 배너 밝은 색 (Issue #7)
- Cloudflare 캐시 정책 근본 해결 (Issue #8, `_headers` 파일 추가 권장)
- tbm/risk/education 캡처 실패 — protocolTimeout 증가로도 해결 안 됨

### 임시 파일 삭제
- `nexas/_temp_swap` — taieng 레포에서 삭제 필요
