# TAI Safe 앱 UI 리디자인 — Cursor 워크오더

## 작업 대상
`tadmin/full-version/app/` 폴더 전체 (17개 HTML 파일)

## 디자인 원칙
1. **5초 점검** — 작업자가 최소 터치로 점검 완료
2. **1클릭 완료** — 같은 기능에 여러 경로 금지, 가장 짧은 경로 하나
3. **스크롤 최소화** — 홈 화면은 스크롤 없이 핵심 액션 노출
4. **절제된 색감** — 블루 하나만 강조, 상태색은 텍스트·아이콘에만
5. **촌스럽지 않은 도구** — 공사현장·공장 남성 기술자가 쓰는 전문 도구 느낌

## 신규 CSS 파일
`app-design.css` 가 이미 커밋됨. 각 HTML `<head>`에 아래 추가:
```html
<link rel="stylesheet" href="app-design.css">
```
기존 인라인 `<style>` 블록에서 `app-design.css`와 중복되는 선언을 제거.
중복 판단 기준: 같은 셀렉터가 `app-design.css`에 이미 정의되어 있으면 인라인에서 삭제.

---

## 파일별 작업

### 1. `index.html` (48KB) — 메인 홈
- `<style>` 블록에서 `app-design.css`와 중복되는 모든 선언 제거
- `<link rel="stylesheet" href="app-design.css">` 추가
- 색상 변수 `:root` 블록 → `app-design.css`로 이관 완료이므로 삭제
- `.worker-card` 배경: `linear-gradient(135deg,var(--navy),var(--navy2))` → `var(--header-bg)` 단색
- `.hero-btn` 배경: 그라데이션 제거 → `var(--blue)` 단색
- `.quick-grid`, `.quick-btn` 코드 삭제 (사용되지 않음, `sub-grid`로 대체 완료)
- `.status-row`, `.status-card` 코드 삭제 (`.status-mini`로 대체 완료)
- 홈 탭에서 프로그레스 카드 아래 `margin-top` 줄이기: `10px` → `8px`
- box-shadow 값: `0 2px 12px rgba(0,0,0,.1)` → `var(--shadow-sm)` 또는 `var(--shadow-md)`

### 2. `inspect.html` (23KB) — 산업 점검
- `app-design.css` 링크 추가
- 점검 항목 UI → `.check-card` + `.check-actions` + `.check-btn` 구조 적용
- 정상/이상/보류 3버튼: `.check-btn.selected-ok`, `.check-btn.selected-bad`, `.check-btn.selected-hold`
- 헤더 → `.sub-header` + `.back-btn` 구조
- 색상 하드코딩 제거 → CSS 변수 참조

### 3. `construction_inspect.html` (32KB) — 건설 점검
- `inspect.html`과 동일한 구조 적용

### 4. `tbm.html` (17KB)
- `app-design.css` 링크 추가
- 헤더 → `.sub-header`
- 버튼 → `.btn-primary`, `.btn-secondary`
- 색상 하드코딩 제거

### 5~17. 나머지 파일 공통
- `app-design.css` 링크 추가
- 인라인 스타일에서 중복 선언 제거
- 헤더 → `.sub-header` 통일
- 버튼 → `.btn-primary` / `.btn-secondary` / `.btn-danger`
- 그라데이션 배경 → 단색으로 교체
- 색상 하드코딩 → CSS 변수 참조

---

## 색상 매핑 (기존 → 신규)
| 기존 | 신규 변수 |
|---|---|
| `#0d1b2a` | `var(--header-bg)` 또는 `var(--ink)` |
| `#1a2e42` | 삭제 (그라데이션 제거) |
| `#1565c0` | `var(--blue)` |
| `#00875a` | `var(--ok)` |
| `#de350b` | `var(--bad)` |
| `#ff8b00` | `var(--warn)` |
| `#172b4d` | `var(--ink)` |
| `#5e6c84` | `var(--ink2)` |
| `#dfe1e6` | `var(--border)` |
| `#f4f5f7` | `var(--bg)` |
| `linear-gradient(135deg,...)` | 단색으로 교체 |

## 규칙
- 200줄 이상 파일 MCP 수정 금지 → 이 워크오더는 Cursor에서 실행
- 한 파일 최대 400줄(15KB) 유지
- 기능 로직(JS) 변경 없음 — CSS·HTML 구조만 변경
- `app-design.css`가 정의한 셀렉터와 동일한 인라인 선언만 삭제
- 인라인에만 있는 페이지 고유 스타일은 유지
