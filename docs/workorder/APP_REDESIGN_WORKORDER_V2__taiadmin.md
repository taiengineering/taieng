# TAI Safe 앱 UI 2차 워크오더 — 인라인 스타일 삭제

## 문제
1차에서 `app-design.css` 링크를 추가하고 색상을 변수로 치환했지만,
**인라인 `<style>` 블록을 삭제하지 않아서 시각적 변화가 없음.**
같은 셀렉터가 인라인과 외부 CSS에 동시에 존재하여 외부 CSS가 무의미한 상태.

## 목표
각 HTML 파일의 `<style>` 블록에서 `app-design.css`에 이미 정의된 셀렉터를 **삭제**.
페이지 고유 스타일(app-design.css에 없는 것)만 인라인에 남긴다.

## 작업 방법

### 판단 기준
`app-design.css`에 정의된 23개 컴포넌트의 셀렉터 목록:

```
:root, *, html, body, .hidden,
.page, .tab-content, .scroll-area,
.app-header, .app-header-inner, .logo, .header-right, .notif-btn, .notif-dot, .emergency-btn,
.tab-bar, .tab-item, .tab-icon, .tab-badge,
.worker-card, .wc-left, .name, .meta, .date, .sector-badge,
.hero-cta, .hero-btn, .hero-btn.done, .hero-btn.warn, .hero-icon, .hero-text, .hero-label, .hero-sub, .hero-arrow,
.sub-grid, .sub-btn, .sb-icon, .sb-label, .sub-btn.needs-action,
.status-mini, .status-chip, .sc-val, .sc-lbl, .status-chip.done, .status-chip.bad,
.progress-card, .prog-head, .prog-label, .prog-count, .prog-bar-bg, .prog-bar-fill, .prog-sub,
.emergency-row, .emergency-full-btn,
.section, .section-title, .activity-list, .activity-item, .activity-icon, .activity-body, .activity-title, .activity-sub, .activity-time,
.overdue-banner, .ovd-title, .ovd-item, .ovd-law,
.menu-group, .menu-group-title, .menu-item, .menu-item-icon, .menu-item-text, .menu-item-label, .menu-item-sub, .menu-item-arrow,
.profile-card, .profile-avatar, .pname, .pmeta,
.auth-page, .auth-logo, .auth-sub, .auth-card, .auth-title, .auth-desc, .auth-label, .auth-input, .auth-btn, .otp-row, .otp-input, .resend-btn,
.sign-wrap, .sign-pad-area, .sign-guide, .sign-actions, .sign-clear, .sign-save, .sign-preview,
.logout-btn, .toast,
.btn-primary, .btn-secondary, .btn-danger,
.check-card, .ck-title, .ck-desc, .check-actions, .check-btn, .check-btn.selected-ok, .check-btn.selected-bad, .check-btn.selected-hold,
.sub-header, .back-btn, .sub-title
```

**위 목록에 해당하는 셀렉터가 인라인 `<style>`에 있으면 → 삭제.**
**위 목록에 없는 셀렉터가 인라인에 있으면 → 유지.**

### 작업 순서 (파일당)
1. `<style>` 블록을 열기
2. 위 셀렉터 목록과 대조
3. 중복 셀렉터 블록 삭제
4. 페이지 고유 스타일만 남기기
5. `<style>` 블록이 비면 `<style></style>` 태그 자체도 삭제

### 중요 예외
- **`<style>` 안에 있지만 `app-design.css`에 없는 페이지 고유 스타일은 반드시 유지**
  - 예: inspect.html의 `.photo-area`, `.cam-btn` 등
  - 예: tbm.html의 `.sig-list`, `.sig-item` 등
  - 예: risk.html의 `.risk-matrix`, `.cell` 등
- **인라인 `style="..."` 속성(HTML 태그에 직접 쓴 것)은 건드리지 말 것**
  - `<div style="margin:8px 16px 0;">` 같은 것은 유지

---

## 파일별 작업

### 1. `index.html` (48KB → 목표 ~20KB)
**가장 큰 파일. 인라인 `<style>`에 ~180줄 중복.**

삭제 대상 (app-design.css와 100% 중복):
- `:root` 블록 (이미 삭제됐다면 확인)
- `*, html, body, .hidden`
- `.page, .tab-content, .scroll-area`
- `.app-header` ~ `.emergency-btn:active`
- `.tab-bar` ~ `.tab-badge`
- `.worker-card` ~ `.sector-badge` (두 번 선언된 것 모두)
- `.hero-cta` ~ `.hero-arrow`
- `.sub-grid` ~ `.sub-btn.needs-action`
- `.emergency-row` ~ `.emergency-full-btn:active`
- `.status-mini` ~ `.status-chip.bad`
- `.progress-card` ~ `.prog-sub`
- `.activity-list` ~ `.activity-time`
- `.overdue-banner` ~ `.ovd-law`
- `.auth-page` ~ `.resend-btn`
- `.sign-wrap` ~ `.sign-preview img`
- `.profile-card` ~ `.pmeta`
- `.menu-group` ~ `.menu-item-arrow`
- `.logout-btn`
- `.toast` ~ `.toast.show`

유지 대상 (app-design.css에 없음):
- `.section` 내부 커스텀 (있다면)
- `quick-grid`, `quick-btn` 관련 (이미 삭제됐다면 확인)
- 페이지 고유 JS 관련 스타일

### 2. `inspect.html` (23KB)
삭제: `.sub-header`, `.back-btn`, `.sub-title`, `.check-card` ~ `.check-btn.selected-hold`, `.btn-primary`, `.btn-secondary`, `.toast`
유지: `.photo-area`, `.cam-btn`, `.result-card`, `.item-list` 등 점검 고유 스타일

### 3. `construction_inspect.html` (32KB)
inspect.html과 동일 패턴

### 4~17. 나머지 파일 공통
- `.sub-header`, `.back-btn`, `.sub-title` → 삭제
- `.btn-primary`, `.btn-secondary`, `.btn-danger` → 삭제
- `.toast` → 삭제
- 페이지 고유 스타일 → 유지

---

## 검증 방법

수정 후 각 파일에서 확인:
1. `<link rel="stylesheet" href="app-design.css">` 존재하는지
2. `<style>` 블록에 위 셀렉터 목록의 셀렉터가 남아있지 않은지
3. 페이지 고유 스타일은 살아있는지
4. 브라우저에서 열었을 때 레이아웃이 깨지지 않는지

## 커밋 메시지
```
fix: 인라인 <style> 중복 선언 삭제 — app-design.css 실제 적용
```
