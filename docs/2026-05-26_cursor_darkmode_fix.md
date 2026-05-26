# 다크모드 가독성 일괄 수정 — Cursor 작업지시서

> 작성일: 2026-05-26
> 대상: `tai-admin/tadmin/full-version/` 전체
> 문제: 커스텀 CSS에 hex 색상 하드코딩 → 다크모드에서 가독성 저하
> 해결: Vuexy CSS 변수로 교체

---

## 근본 원인

각 HTML 파일의 `<style>` 블록과 JS에서 생성하는 인라인 스타일에서
배경색/텍스트색/보더색을 hex 값으로 직접 지정하고 있음.
Vuexy는 `[data-bs-theme="dark"]` 전환 시 CSS 변수를 자동 전환하지만,
하드코딩된 hex 값은 전환되지 않아 다크모드에서 가독성이 떨어짐.

---

## 교체 규칙 (전체 파일 공통)

### 배경색

| 현재 (하드코딩) | 교체 대상 |
|---|---|
| `background: #fff` | `background: var(--bs-card-bg)` |
| `background: #ffffff` | `background: var(--bs-card-bg)` |
| `background: white` | `background: var(--bs-card-bg)` |
| `background: #f8fafc` | `background: var(--bs-secondary-bg)` |
| `background: #f8f9fa` | `background: var(--bs-secondary-bg)` |
| `background: #f1f5f9` | `background: var(--bs-tertiary-bg)` |
| `background: #e9ecef` | `background: var(--bs-tertiary-bg)` |
| `background: #f0f4ff` | `background: var(--bs-secondary-bg)` |

### 텍스트색

| 현재 (하드코딩) | 교체 대상 |
|---|---|
| `color: #0f172a` | `color: var(--bs-body-color)` |
| `color: #1a1a1a` | `color: var(--bs-body-color)` |
| `color: #333` / `#333333` | `color: var(--bs-body-color)` |
| `color: #475569` | `color: var(--bs-secondary-color)` |
| `color: #64748b` | `color: var(--bs-secondary-color)` |
| `color: #94a3b8` | `color: var(--bs-tertiary-color)` |
| `color: #6c757d` | `color: var(--bs-secondary-color)` |

### 보더색

| 현재 (하드코딩) | 교체 대상 |
|---|---|
| `border-color: #e2e8f0` | `border-color: var(--bs-border-color)` |
| `border-color: #dee2e6` | `border-color: var(--bs-border-color)` |
| `border: 1px solid #e2e8f0` | `border: 1px solid var(--bs-border-color)` |
| `border: 1.5px solid #e2e8f0` | `border: 1.5px solid var(--bs-border-color)` |
| `border-bottom: 1px solid #f1f5f9` | `border-bottom: 1px solid var(--bs-border-color-translucent)` |

### 시맨틱 배경 (상태별 색상)

이 항목들은 `[data-bs-theme="dark"]` 별도 오버라이드로 처리:

| 현재 | 라이트모드 | 다크모드 오버라이드 |
|---|---|---|
| `.sel-ACTIVE { background:#dcfce7 }` | 그대로 | `[data-bs-theme="dark"] .sel-ACTIVE { background:rgba(22,163,74,0.2); color:#4ade80 }` |
| `.sel-BROKEN { background:#fee2e2 }` | 그대로 | `[data-bs-theme="dark"] .sel-BROKEN { background:rgba(220,38,38,0.2); color:#f87171 }` |
| `.sel-INACTIVE { background:#f1f5f9 }` | 그대로 | `[data-bs-theme="dark"] .sel-INACTIVE { background:rgba(148,163,184,0.15); color:#94a3b8 }` |
| `.eq-selected-box { background:#f0fdf4 }` | 그대로 | `[data-bs-theme="dark"] .eq-selected-box { background:rgba(22,163,74,0.1); border-color:#166534 }` |
| `.band-must { background:#fff1f2; color:#e11d48 }` | 그대로 | `[data-bs-theme="dark"] .band-must { background:rgba(225,29,72,0.2); color:#fb7185 }` |
| `.band-core { background:#eff6ff; color:#2563eb }` | 그대로 | `[data-bs-theme="dark"] .band-core { background:rgba(37,99,235,0.2); color:#60a5fa }` |

---

## custom.css 수정

### placeholder 색상

변경 전:
```css
::placeholder {
  color: #b0b8c4 !important;
  opacity: 1 !important;
}
```

변경 후:
```css
::placeholder {
  color: var(--bs-secondary-color) !important;
  opacity: 0.65 !important;
}
```

---

## 대상 파일 목록

`tadmin/full-version/html/horizontal-menu-template/` 내 모든 HTML 파일.
특히 `<style>` 블록이 있는 파일들을 우선 처리:

### 우선순위 1 — 확인된 문제 파일
| 파일 | 크기 | 하드코딩 수준 |
|---|---|---|
| `my-equipment.html` | 38KB | 심각 — 20개+ hex 값 |
| `safety-dashboard.html` | 37KB | 중간 — 날씨/미이행 위젯 CSS |
| `inspection-anchor.html` | 49KB | 높음 — 모달/카드 커스텀 |
| `tbm-setting.html` | 47KB | 높음 |
| `factory-list.html` | 45KB | 높음 |
| `construction-inspection-anchor.html` | 45KB | 높음 |
| `process-manage.html` | 30KB | 중간 |
| `process-select.html` | 34KB | 중간 |

### 우선순위 2 — 공통 CSS
| 파일 | 설명 |
|---|---|
| `assets/css/tai/custom.css` | placeholder 색상 |

### 우선순위 3 — JS 파일에서 생성하는 인라인 스타일
JS에서 `innerHTML`로 생성하는 HTML에 인라인 `style="color:#0f172a"` 같은 하드코딩이 있을 수 있음.
이 경우 인라인 스타일 대신 CSS 클래스를 사용하도록 변경.

---

## 작업 방법

### 단계 1: 전역 검색

`tadmin/full-version/` 디렉토리에서 아래 패턴 검색:

```bash
# 배경색 하드코딩 검색
grep -rn 'background.*#f8fafc\|background.*#fff[^f]\|background.*#f1f5f9\|background.*#e9ecef\|background.*#f8f9fa' tadmin/full-version/html/

# 텍스트색 하드코딩 검색
grep -rn 'color.*#0f172a\|color.*#475569\|color.*#64748b\|color.*#94a3b8\|color.*#333' tadmin/full-version/html/

# 보더 하드코딩 검색
grep -rn 'border.*#e2e8f0\|border.*#dee2e6\|border.*#f1f5f9' tadmin/full-version/html/
```

### 단계 2: `<style>` 블록 내 교체

각 파일의 `<style>` 블록에서 위 교체 규칙에 따라 sed/수동 교체.

**주의: 아래 항목은 교체 금지**
- `linear-gradient(...)` 내부 색상 — 그라디언트는 CSS 변수로 대체 불가 (보류)
- `rgba(...)` — 이미 투명도 처리되어 있으므로 유지
- `.wx-*` 클래스 (날씨 위젯) — 의도적 다크 배경, 유지
- Vuexy 기본 클래스 (`bg-label-*`, `text-*`, `badge`) — 이미 다크모드 대응, 유지
- `.tai-factory-banner` — 의도적 gradient 배너, 유지

### 단계 3: 시맨틱 색상 다크모드 오버라이드 추가

각 파일의 `<style>` 블록 끝에 다크모드 오버라이드 섹션 추가:

```css
/* === 다크모드 대응 === */
[data-bs-theme="dark"] .oc-section { background: var(--bs-secondary-bg); }
[data-bs-theme="dark"] .status-btn { background: var(--bs-card-bg); border-color: var(--bs-border-color); color: var(--bs-secondary-color); }
[data-bs-theme="dark"] .sel-ACTIVE { background: rgba(22,163,74,0.2); color: #4ade80; border-color: #166534; }
[data-bs-theme="dark"] .sel-BROKEN { background: rgba(220,38,38,0.2); color: #f87171; border-color: #991b1b; }
[data-bs-theme="dark"] .sel-INACTIVE { background: rgba(148,163,184,0.15); color: #94a3b8; border-color: #475569; }
[data-bs-theme="dark"] .eq-selected-box { background: rgba(22,163,74,0.1); border-color: #166534; }
[data-bs-theme="dark"] .band-must { background: rgba(225,29,72,0.2); color: #fb7185; }
[data-bs-theme="dark"] .band-core { background: rgba(37,99,235,0.2); color: #60a5fa; }
[data-bs-theme="dark"] .eq-result-item:hover { background: var(--bs-tertiary-bg); }
[data-bs-theme="dark"] .proc-eq-item.already { background: var(--bs-tertiary-bg); }
[data-bs-theme="dark"] .add-tab-btn { background: var(--bs-secondary-bg); border-color: var(--bs-border-color); color: var(--bs-secondary-color); }
```

### 단계 4: JS innerHTML 내 인라인 스타일 제거

각 JS 파일에서 `style="color:#` 또는 `style="background:#` 패턴을 검색.
발견되면 CSS 클래스로 대체:

```js
// 변경 전
'<div style="color:#0f172a; font-weight:700">' + name + '</div>'

// 변경 후
'<div class="fw-bold">' + name + '</div>'
```

---

## 검증 방법

1. 브라우저에서 safe.taieng.co.kr 접속
2. Vuexy 테마 토글 (우측 하단 톱니바퀴 버튼) → Dark 선택
3. 아래 페이지들 순회 확인:
   - [ ] 내 설비 (my-equipment) → 설비 등록 모달
   - [ ] 안전대시보드 (safety-dashboard)
   - [ ] 점검관리 (inspection-anchor)
   - [ ] TBM 설정 (tbm-setting)
   - [ ] 시설관리 (factory-list)
   - [ ] 공정관리 (process-manage)
4. 각 페이지에서:
   - 텍스트가 배경에 묻히지 않는지
   - 카드/보더가 식별 가능한지
   - 입력 필드의 placeholder가 보이는지
   - 뱃지/태그 색상이 적절한지

---

## 주의사항

- `tadmin/` 경로만 수정 — `admin/` 경로 절대 혼동 금지
- `tai-admin`에는 `dev` 브랜치 없음 → `main` 직접 커밋
- Cloudflare Pages 자동배포 (push 시 즉시 반영)
- 파일당 `<style>` 블록 + JS 인라인 스타일 모두 확인
- 수정 후 라이트모드에서도 동일하게 보이는지 확인 (변수 사용 시 양쪽 모두 정상)
