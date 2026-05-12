# TAI Safe 앱 v2 리디자인 — Cursor 워크오더

## 배경
Samsara / MaintainX / Fleetio 참고하여 전면 리디자인.
다크 모드 기본 + 라이트 모드 전환.

## 핵심 변경

### 1. 테마 시스템
모든 HTML 파일의 `<html>` 태그에 `data-theme="dark"` 추가:
```html
<html lang="ko" data-theme="dark">
```

### 2. 테마 토글 JS
`_utils.js`에 아래 추가:
```javascript
// 테마 전환
function toggleTheme() {
  const html = document.documentElement;
  const current = html.dataset.theme || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  html.dataset.theme = next;
  localStorage.setItem('tai_theme', next);
}

// 저장된 테마 복원
(function() {
  const saved = localStorage.getItem('tai_theme') || 'dark';
  document.documentElement.dataset.theme = saved;
})();
```

### 3. 테마 토글 버튼 배치
`index.html` 헤더 `.header-right`에 추가:
```html
<button class="theme-toggle" onclick="toggleTheme()" aria-label="테마 전환">🌙</button>
```
`profile.html` 메뉴에도 테마 전환 메뉴 추가.

### 4. 인라인 `<style>` 완전 삭제
`app-design.css` v2.0이 모든 컴포넌트를 정의하므로,
각 HTML의 `<style>` 블록에서 중복 선언 **전부 삭제**.
빈 `<style>` 태그도 삭제.

### 5. Samsara 핵심 차이점

| 이전 (v1) | 이후 (v2) |
|---|---|
| 헤더 = 짙은 네이비 단색 | 헤더 = 배경과 동화 (`--bg-0`) |
| 카드 = `border: 1px solid` | 카드 = `box-shadow` (테두리 없음) |
| `.section-title` = 검정 볼드 | `.section-title` = 회색 소문자 라벨 |
| `.activity-icon` = 원형 50% | `.activity-icon` = 사각 10px radius |
| 고정 라이트 테마 | 다크 기본 + 라이트 전환 |
| 디자인 토큰 13개 | 디자인 토큰 28개 (시맨틱 계층) |

### 6. 색상 매핑
| v1 변수 | v2 변수 |
|---|---|
| `--bg` | `--bg-0` |
| `--bg-card` | `--bg-1` |
| `--bg-inset` | `--bg-2` |
| `--ink` | `--text-0` |
| `--ink2` | `--text-1` |
| `--ink3` | `--text-2` |
| `--blue` | `--accent` |
| `--blue-light` | `--accent-subtle` |
| `--ok` | `--ok` (동일) |
| `--bad` | `--bad` (동일) |
| `--warn` | `--warn` (동일) |
| `--border` | `--border` |
| `--header-bg` | 삭제 → `--bg-0` 사용 |

### 7. 파일별 작업

**전 파일 공통:**
- `<html lang="ko">` → `<html lang="ko" data-theme="dark">`
- `<style>` 블록 중복 선언 삭제 (페이지 고유만 남김)
- v1 변수 참조 → v2 변수로 교체 (위 매핑표 참고)
- `--header-bg` 참조 → `var(--bg-0)` 또는 삭제

**`index.html`:**
- 헤더에 테마 토글 버튼 추가
- 인라인 스타일 전부 삭제

**`_utils.js`:**
- `toggleTheme()` 함수 추가
- 테마 복원 IIFE 추가

**`inspect.html` / `construction_inspect.html`:**
- `.check-card`, `.check-btn` 구조 유지
- v1 변수 → v2 변수 교체

**나머지 서브페이지:**
- `.sub-header` 유지
- v1 변수 → v2 변수 교체

### 8. 검증
1. 다크 모드: `safe.taieng.co.kr/app/` 접속 → 어두운 배경 확인
2. 라이트 모드: 프로필 → 테마 전환 → 밝은 배경 확인
3. 새로고침 → 선택한 테마 유지 (localStorage)
4. 점검 화면 → 정상/이상/보류 버튼 색상 다크·라이트 모두 확인

### 커밋 메시지
```
feat: 앱 디자인 시스템 v2.0 — Samsara 참고 리디자인 + 다크/라이트 테마
```
