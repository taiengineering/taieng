# 세션 작업 핸드오프 — 사이트 네비게이션 정리

**일자**: 2026-05-04 (UTC 14:50 ~ 15:15)
**범위**: `taiengineering/taieng` 레포 (`nexas/` 디렉토리)
**작업 도구**: GitHub MCP (`github-tai`)
**배포**: Cloudflare Pages 자동 배포 (taieng.co.kr)

---

## 1. 세션 목적

직전 세션에서 헤더/풋터/메뉴 정리, 메인 페이지 히어로 리뉴얼, `free-diagnosis.html`에 헤더 추가 작업이 있었음. 이번 세션은 그 후속으로 두 가지 마무리 작업.

1. 메인 페이지 히어로 높이를 `service/diagnosis.html`과 동일하게 맞추기
2. `free-diagnosis.html`의 헤더/풋터 누락 보강 (직전 세션에서 누락된 페이지 발견)

---

## 2. 커밋 내역 (3개)

### 커밋 #1 — `e7698bc919514f2d6304adab8f18f88a228ec2b8`
**메시지**: `style(taieng): 히어로 높이를 service/diagnosis와 동일하게 — clamp(560px, 80vh, 720px)`
**파일**: `nexas/index.html`

#### 변경 내용
| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| 데스크톱 높이 | `height: 540px` 고정 | `min-height: clamp(560px, 80vh, 720px)` |
| 이미지 처리 | `width:100%; height:540px` | `position: absolute; inset:0; width:100%; height:100%` (부모 채움) |
| 모바일 break-point | 768px | **991px** (diagnosis와 일치) |
| 모바일 높이 | 520px 고정 | `min-height: 520px` |

#### 의도
`service/diagnosis.html`의 히어로는 `min-height: clamp(560px, 80vh, 720px)`로 viewport에 따라 가변. 메인은 540px 고정이라 두 페이지가 시각적으로 다른 높이로 보였음. 동일 CSS 값으로 맞춰 일관된 첫인상 제공.

#### 결과
- viewport 높이 700px → 560px (min)
- viewport 높이 900px → 720px (max)
- 일반 데스크톱(900px+) → 720px로 표시
- 이미지가 부모 가변 영역을 `object-fit: cover`로 자동 채움

---

### 커밋 #2 — `efce2a51826d8c555b8fcbdb8a6ae1da2ffb40a0`
**메시지**: `fix(taieng): free-diagnosis 페이지에 헤더/풋터 추가 + sticky 사이드바 nav 충돌 방지`
**파일**: `nexas/free-diagnosis.html`

#### 발견된 누락 (5곳)
| 누락 요소 | 다른 페이지에는 |
|---|---|
| `<div id="tai-header"></div>` | ✅ 있음 |
| `<script src="assets/js/header.js">` | ✅ 있음 |
| `<script src="assets/js/nav-auth.js">` | ✅ 있음 |
| `<div id="tai-footer"></div>` | ✅ 있음 |
| `<script src="assets/js/footer.js">` | ✅ 있음 |

#### 변경 내용
1. `<body>` 시작부에 `<div id="tai-header"></div>` 추가 (preloader/overlay 다음)
2. `</body>` 직전에 `<div id="tai-footer"></div>` 추가
3. `<script>` 영역에 `header.js`, `nav-auth.js`, `footer.js` 추가
4. `.diag-layout` CSS: `min-height: 100vh` → `calc(100vh - var(--tai-nav-h, 90px))` (헤더 차감)
5. `.diag-left` CSS: `top: 0` → `top: var(--tai-nav-h, 90px)`, `height: 100vh` → `calc(100vh - var(--tai-nav-h, 90px))` (sticky 사이드바 헤더 충돌 방지)

#### 결과
- 좌측 사이드바: 헤더 아래에서 sticky로 정상 동작 ✅
- 우측 콘텐츠: **여전히 천장(y=0)부터 시작 — 헤더와 진행바 겹침** ❌ → 커밋 #3에서 후속 처리

---

### 커밋 #3 — `946c5e685d5ac067923ad9f9315cf7516444317f`
**메시지**: `fix(taieng): free-diagnosis 우측 콘텐츠도 헤더 아래에서 시작 — .diag-layout에 margin-top 90px 추가`
**파일**: `nexas/free-diagnosis.html`

#### 원인
커밋 #2에서 `.diag-left`만 sticky `top: 90px`으로 처리했지만, `.diag-layout` 자체는 천장(y=0)부터 시작이라 grid의 두 번째 자식 `.diag-right`는 헤더 아래에서 시작하지 않음.

외부 CSS에서 `.navbar-area`가 fixed/absolute로 처리되어 흐름에서 빠지는 것이 근본 원인. 사용자 스크린샷에서 헤더 메뉴("서비스", "업종별", "역할별", "안전정보", "마이페이지", "로그아웃")와 우측 진행바(0~4)가 같은 줄에 겹쳐 보임.

#### 변경 내용
```css
/* Before (커밋 #2 결과) */
.diag-layout {
  min-height: calc(100vh - var(--tai-nav-h, 90px));
  display: grid;
  grid-template-columns: 420px 1fr;
}

/* After (커밋 #3) */
.diag-layout {
  margin-top: var(--tai-nav-h, 90px);  /* ← 추가 */
  min-height: calc(100vh - var(--tai-nav-h, 90px));
  display: grid;
  grid-template-columns: 420px 1fr;
}
```

`.diag-layout` 전체를 헤더 높이만큼 아래로 내림. `.diag-left`의 sticky `top: 90px`은 그대로 유지.

---

## 3. 미해결 이슈 / 검증 필요

### ⚠️ ISSUE-01: free-diagnosis 우측 콘텐츠 위치 — 검증 미완료

**상태**: 커밋 #3 푸시 후 사용자가 동일한 스크린샷(`1777907206152_image.png`, 직전 메시지와 같은 파일)을 다시 첨부하며 같은 문제 보고.

**가능성**:
1. **캐시 또는 배포 지연** (가장 유력): Cloudflare Pages 배포가 완료되기 전 또는 브라우저 캐시 화면을 본 것. 첨부 파일명이 직전과 동일하므로 같은 이미지를 재첨부했을 가능성 큼.
2. **margin-collapse 이슈**: `.diag-layout`이 body의 자식이고, `<div id="tai-header"></div>`가 빈 div인 경우 인접 형제 margin collapse는 일반적으로 발생하지 않지만, 외부 CSS 또는 header.js의 outerHTML 처리 방식에 따라 발생 가능성 잠재.

**다음 세션 1차 조치**:
1. 강제 새로고침(`Ctrl+Shift+R`) 후 시각 검증
2. 시크릿 창에서 https://taieng.co.kr/free-diagnosis 접속 비교
3. 그래도 동일하면 `margin-top` → `padding-top`으로 변경 (margin-collapse 회피):
```css
.diag-layout {
  padding-top: var(--tai-nav-h, 90px);
  min-height: 100vh;
  display: grid;
  grid-template-columns: 420px 1fr;
}
```

### ⚠️ ISSUE-02: 다른 페이지의 헤더/풋터 누락 가능성

**상태**: `free-diagnosis.html`에서 헤더/풋터/스크립트 5종이 모두 누락되어 있던 것으로 보아, 다른 페이지에도 같은 패턴이 있을 가능성. 일괄 점검 필요.

**점검 대상 후보**:
- `nexas/fix-request.html`
- `nexas/connect.html`
- `nexas/for-business-owner.html`
- `nexas/for-safety-manager.html`
- `nexas/service/*.html` (diagnosis.html은 정상 확인됨)
- `nexas/mypage/*.html`

**점검 방법** (다음 세션):
1. 각 파일에서 다음 5개 항목 grep:
   - `<div id="tai-header"></div>`
   - `<div id="tai-footer"></div>`
   - `assets/js/header.js`
   - `assets/js/nav-auth.js`
   - `assets/js/footer.js`
2. 누락된 페이지 일괄 보강

---

## 4. 핵심 인프라 정보 (참조용)

- **Repo**: `taiengineering/taieng`, 디렉토리 `nexas/`
- **헤더 높이 변수**: `--tai-nav-h: 90px` (`assets/js/header.js`에서 정의)
- **헤더 동적 주입**: `<div id="tai-header"></div>`에 `header.js`가 outerHTML로 `<header class="navbar-area">...</header>` 삽입
- **풋터 동적 주입**: `<div id="tai-footer"></div>`에 `footer.js`가 outerHTML로 `<footer>...</footer>` 삽입
- **`.navbar-area` 위치 처리**: 외부 CSS(`assets/css/style.css` 등)에서 fixed/absolute로 처리되는 것으로 추정 (정확한 CSS 확인 필요시 별도 점검)
- **메인 히어로 이미지**: `https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/main/hero-diagnosis-main.png`

---

## 5. 다음 세션 작업 우선순위 권장

1. **ISSUE-01 검증**: 사용자에게 강제 새로고침 후 결과 확인. 필요시 `padding-top`으로 후속 수정.
2. **ISSUE-02 일괄 점검**: 위 후보 페이지 파일을 순회하며 헤더/풋터 누락 일괄 보강.
3. **인박스 시스템 Phase 4 또는 Phase 5** (`tai-api/docs/inbox-system/HANDOFF_20260504.md` 참조): Phase 5(마케팅+SaaS 의견 폼) 우선 권장.

---

## 6. 작업 패턴 메모

- GitHub MCP `create_or_update_file`은 SHA 명시하면서 단일 파일 업데이트 — 변경 한 줄짜리도 70KB 파일 전체를 매번 보내야 해서 비효율적이지만 안전. 큰 파일 다중 수정 시 Cursor 로컬 편집 후 git push가 더 효율적.
- `free-diagnosis.html`은 69KB 단일 파일에 CSS+HTML+JS 모두 인라인이라 부분 수정 비용이 큼. 향후 컴포넌트 분리 검토 가치 있음.
- main push → Cloudflare Pages 자동 배포 (1~2분). 사용자 시각 검증 시 강제 새로고침(`Ctrl+Shift+R`) 안내 필수.
