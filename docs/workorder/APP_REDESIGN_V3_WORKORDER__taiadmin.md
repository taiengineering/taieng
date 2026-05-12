# TAI Safe 앱 전면 재작성 — Cursor 워크오더 v3 (최종)

## ⚠️ 절대 규칙
**`app-design.css`를 수정하지 마세요.** Claude MCP가 관리합니다.

## 작업 순서

### Step 1: 자동 정리 스크립트 실행
```bash
cd /path/to/tai-admin
node scripts/clean-app-html.js
```
이 스크립트가:
- 모든 `<style>` 블록 제거
- `data-theme="dark"` 보장
- `app-design.css` 링크 보장
- v1 변수를 v2로 치환

### Step 2: `_utils.js` 테마 토글 추가

파일 맨 아래에 추가 (기존 코드 삭제하지 말 것):
```javascript
// ═══════════════════════════════
// 테마 전환
// ═══════════════════════════════
function toggleTheme() {
  var html = document.documentElement;
  var current = html.getAttribute('data-theme') || 'dark';
  var next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  try { localStorage.setItem('tai_theme', next); } catch(e) {}
  var btns = document.querySelectorAll('.theme-toggle');
  btns.forEach(function(b) { b.textContent = next === 'dark' ? '☀️' : '🌙'; });
}

function initTheme() {
  var saved = 'dark';
  try { saved = localStorage.getItem('tai_theme') || 'dark'; } catch(e) {}
  document.documentElement.setAttribute('data-theme', saved);
  var btns = document.querySelectorAll('.theme-toggle');
  btns.forEach(function(b) { b.textContent = saved === 'dark' ? '☀️' : '🌙'; });
}

initTheme();
```

⚠️ 이미 `toggleTheme`/`initTheme` 함수가 있다면 기존 것 삭제 후 위 코드로 교체.

### Step 3: 헤더에 테마 토글 버튼 배치

`index.html`의 `.header-right` 안에:
```html
<button class="theme-toggle" onclick="toggleTheme()" aria-label="테마 전환">☀️</button>
```

`profile.html`의 메뉴에:
```html
<div class="menu-item" onclick="toggleTheme()">
  <div class="menu-item-icon">🌓</div>
  <div class="menu-item-text">
    <div class="menu-item-label">테마 전환</div>
    <div class="menu-item-sub">다크 / 라이트 모드</div>
  </div>
  <div class="menu-item-arrow">›</div>
</div>
```

### Step 4: 수동 검증

스크립트 실행 후 남아있을 수 있는 문제:
1. JS 코드 내에서 `--header-bg` 등 v1 변수를 참조하는 경우 → v2로 교체
2. 인라인 `style` 속성에서 `color: #fff`가 헤더 내부에 하드코딩된 경우 → 삭제 (CSS에서 처리)
3. `linear-gradient(...)` 잔존 → 단색으로 교체

### Step 5: 검증 명령어
```bash
# <style> 잔존 확인
grep -c '<style>' tadmin/full-version/app/*.html
# 전부 0이어야 함

# v1 변수 잔존 확인
grep -rn 'var(--header-bg)\|var(--ink)\|var(--bg-card)\|var(--blue)' tadmin/full-version/app/*.html
# 결과 0건이어야 함

# app-design.css 변경 없음 확인
git diff tadmin/full-version/app/app-design.css
# 변경 없어야 함
```

### 커밋 메시지
```
feat: 앱 전면 재작성 — 인라인 style 제거 + 다크 테마 + 테마 토글

⚠️ app-design.css 변경 없음 (Claude MCP 관리)
```
