# Browser Synthetic Coverage 관리

## Coverage 기준

| 우선순위 | Flow | Browser | API | 상태 |
|:---:|------|:---:|:---:|------|
| P0 | login_browser | ✅ | ✅ | 운영 중 |
| P0 | process_registration_browser | ✅ | ✅ | 운영 중 |
| P1 | law_diagnosis_browser | ❌ | ✅ | 계획 |
| P1 | approval_browser | ❌ | ❌ | 계획 |
| P2 | export_download_browser | ❌ | ❌ | 미정 |

## data-testid Selector 규약

프론트엔드에 아래 `data-testid` 속성 추가 필요:

### 로그인 페이지
```html
<input data-testid="login-email-input" type="email" />
<input data-testid="login-password-input" type="password" />
<button data-testid="login-submit-btn" type="submit">로그인</button>
```

### 공정등록 페이지
```html
<select data-testid="process-type-select" name="source">
<input data-testid="process-name-input" name="process_name" />
<button data-testid="process-submit-btn" type="submit">저장</button>
<div data-testid="process-success-modal" class="success-modal">
<span data-testid="process-type-display" data-field="source">
```

### Naming 규칙
`{page}-{role}-{type}`

예: `login-submit-btn`, `process-type-select`, `diagnosis-submit-btn`

## Timeout 표준

| 구분 | 시간 |
|------|------|
| 페이지 로드 | 15초 |
| Selector 대기 | 10초 |
| Submit 결과 대기 | 20초 |
| 기본 retry | 2회 |

## Railway 요구사항

```
pip install playwright
playwright install chromium
```

메모리: 최소 1GB 권장 (Chromium headless ~200MB)

환경변수:
- `PLAYWRIGHT_HEADLESS=true`
- `PLAYWRIGHT_BASE_URL=https://taieng.co.kr`
