# 사이트 점검 — 메뉴 트리 상태 (2026-05-05)

## 점검 도구 제약

이 점검은 **GitHub repo HTML/JS 정적 분석**으로 수행됨. 라이브 사이트 (taieng.co.kr) 직접 fetch 불가 환경. 따라서:

- ✅ **확인 가능**: 헤더/풋터 5종 포함, `<img src>` 경로, `<a href>` 경로, 외부 supabase URL 사용 일관성, body class 위험 (home-N), 헤더 링크 `.html` 누락
- ❌ **확인 불가**: 이미지 실제 로딩 여부 (HTTP 200), Supabase Storage 객체 실제 존재, JS 동작 후 화면 상태, CSS 렌더링 결과

라이브 페이지 직접 점검은 사용자가 브라우저에서 확인하거나, Cloudflare Pages 빌드 로그/런타임 모니터링이 필요함.

---

## 색상 범례

- 🟢 **정상**: 직접 검증됨 또는 정적 분석 통과
- 🟡 **주의**: 정적 분석으로 발견된 위험 요소 있음 (작동은 가능)
- 🔴 **문제**: 깨진 자원/링크 명확히 식별됨
- ⚪ **미점검**: 본 세션에서 확인 안 됨

---

## 헤더 메뉴 트리

### 로고 / 홈

```
TAI Engineering 로고                            🟢
└── index.html                                 🟢 (검증: 직접 작업, supabase 이미지 사용)
```

### 메뉴 1. 서비스

```
서비스 ▼
├── 법령진단 → service/diagnosis.html          🟢 (검증: 직접 작업, KG이니시스 결제 정상)
├── SaaS 구독 → service/saas.html              🟡 (정적 분석 통과 / body class="sc5 home-2" — 주의 사항)
└── 인앱 서비스 → service/inapp.html           ⚪ (미점검)
```

**의견**:
- saas.html에서 `body class="sc5 home-2"` 사용 — 메모리 원칙 "Bootstrap theme body class(home-2~6) 사용 금지" 위반 가능성. tai-brand.css 변수 오버라이드 발생 시 색상/폰트 어긋날 수 있음. 라이브에서 색상 정상이면 보류, 어긋나면 home-2 제거.

### 메뉴 2. 업종별

```
업종별 ▼
├── 건물·시설 → target/building.html           ⚪ (미점검)
├── 제조공장 → target/factory.html             🟡 (검증: 깨진 로컬 이미지 4개 잔존)
└── 건설현장 → target/construction.html        ⚪ (미점검)
```

**factory.html 잔존 이슈**:
- `../assets/img/factory/risk-assessment-workers.jpg` 🔴
- `../assets/img/factory/before-paper-safety.jpg` 🔴
- `../assets/img/factory/after-digital-safety.jpg` 🔴
- `../assets/img/factory/tai-safety-flow.jpg` 🔴

→ 해당 디렉토리 존재 여부 미확인. supabase로 옮기거나 새 이미지 제작 필요.

### 메뉴 3. 역할별

```
역할별 ▼
├── 안전관리자 → for-safety-manager            🔴 (.html 확장자 누락 - header.js)
└── 사업주 → for-business-owner                🔴 (.html 확장자 누락 - header.js)
```

**즉각 수정 필요**:
- `nexas/assets/js/header.js` v3.5.5에서:
  - `for-safety-manager` → `for-safety-manager.html`
  - `for-business-owner` → `for-business-owner.html`
- Cloudflare Pages가 자동 fallback 처리해 우회되고 있을 수 있지만, 명시적 .html 권장.

페이지 본문은 미점검 (⚪).

### 메뉴 4. 안전정보

```
안전정보 ▼
├── 안전자료 → safety-news.html                ⚪ (미점검)
├── 재해사례 → accident-cases.html             ⚪ (미점검)
├── 개정법령 → law-updates.html                ⚪ (미점검)
└── 판례검색 → precedent-search.html           ⚪ (미점검)
```

### 우측 인증 영역

```
[로그인 시]
├── 마이페이지 → mypage/                       ⚪ (미점검)
└── 로그아웃 (JS 처리)                         🟢 (header.js 검증)

[비로그인 시]
├── 로그인 → log-in.html?redirect=...          ⚪ (미점검)
└── 회원가입 → sign-up.html                    ⚪ (미점검)
```

---

## 헤더에 노출되지 않는 페이지 (참고)

루트 디렉토리에 존재하지만 헤더 메뉴에 없는 HTML:

| 페이지 | 용도 | 상태 |
|---|---|---|
| `free-diagnosis.html` | 무료 법령진단 폼 (히어로 CTA) | ⚪ |
| `free-diagnosis-result.html` | 무료 진단 결과 | ⚪ |
| `paid-diagnosis-result.html` | 유료 진단 결과 | ⚪ |
| `fix-request.html` | 도입 문의 폼 | ⚪ |
| `pricing.html` | (가격 페이지) | ⚪ |
| `faq.html` | FAQ | ⚪ |
| `about.html` | 회사소개 | ⚪ |
| `patents.html` | TAI 기술력/특허 | ⚪ |
| `terms.html` | 이용약관 | ⚪ |
| `privacy.html` | 개인정보처리방침 | ⚪ |
| `delete-account.html` | 회원탈퇴 | ⚪ |
| `connect.html` | 연결 서비스 | ⚪ |
| `provider-register.html` | 공급자 등록 | ⚪ |
| `for-agency.html` | 대행기관 (역할별 미노출) | ⚪ |
| `for-consultant.html` | 컨설턴트 (역할별 미노출) | ⚪ |
| `for-expert.html` | 전문가 (역할별 미노출) | ⚪ |
| `for-repair.html` | 수선업체 (역할별 미노출) | ⚪ |
| `safety-news-detail.html` | 안전자료 상세 | ⚪ |
| `accident-case-detail.html` | 재해사례 상세 | ⚪ |
| `law-update-detail.html` | 개정법령 상세 | ⚪ |
| `precedent-detail.html` | 판례 상세 | ⚪ |
| `safety-post-detail.html` | (안전 포스트 상세) | ⚪ |
| `law-view.html` | 법령 본문 뷰어 | ⚪ |
| `team.html`, `team-details.html` | (팀 페이지) | ⚪ |
| `showcase.html` | (쇼케이스) | ⚪ |
| `site-map.html` | 사이트맵 | ⚪ |

**레거시/템플릿 잔존 (정리 후보)**:

| 파일 | 크기 | 비고 |
|---|---|---|
| `index-1.html` ~ `index-6.html` | 각 1.5KB | Nexas 템플릿 변형 잔존 — 삭제 검토 |
| `app.html`, `demo.html` | ~1.5KB | 템플릿 잔존 |
| `service.html`, `service-details.html` | 1.5KB | 빈 stub (메뉴는 `service/` 디렉토리 사용) |
| `blog.html`, `blog-2.html`, `blog-3.html`, `blog-single*.html` | 1.5~24KB | 사용 안 하는 블로그 템플릿 |
| `contact.html` | 9.7KB | (`fix-request.html`로 대체됐는지 확인) |
| `construction.html` (루트) | 1.5KB | `target/construction.html`과 충돌 가능 — 삭제 검토 |
| `tai-fix.html` | 1.5KB | 빈 stub |
| `mypage.html` (루트) | 1.7KB | `mypage/` 디렉토리와 별개 |
| `diagnosis-start.html` | 1.5KB | (사용처 확인 필요) |

---

## 즉각 수정 권장 (우선순위)

### 🔴 P0 — 명확히 깨진 항목

1. **header.js 역할별 메뉴 .html 누락** (`for-safety-manager`, `for-business-owner`)
   - 위치: `nexas/assets/js/header.js` line 280~289
   - 5분 작업

2. **factory.html 깨진 로컬 이미지 4개**
   - risk-assessment-workers, before-paper-safety, after-digital-safety, tai-safety-flow
   - supabase로 옮기거나 새 이미지 제작 필요

### 🟡 P1 — 위험 요소

3. **saas.html body class home-2 제거**
   - 메모리 원칙 위반. tai-brand.css 변수 오버라이드 가능성.
   - 단, 라이브에서 정상이면 보류 가능 — 우선 라이브 확인 필요

### ⚪ P2 — 미점검 페이지 일괄 점검 필요

4. 헤더 메뉴 노출되는 9개 페이지 점검:
   - service/inapp.html
   - target/building.html, target/construction.html
   - for-safety-manager.html, for-business-owner.html
   - safety-news.html, accident-cases.html, law-updates.html, precedent-search.html
   - log-in.html, sign-up.html
   - 점검 항목: 헤더/풋터 5종 포함, supabase 이미지 사용, 깨진 로컬 이미지, 가격/결제 보호 영역 (해당 시)

### 🟢 P3 — 정리 작업

5. 레거시/템플릿 잔존 파일 삭제
   - index-1~6.html, app.html, demo.html, service.html, service-details.html, blog*.html, tai-fix.html, contact.html, construction.html(루트), mypage.html(루트)
   - 약 15~20개 파일

---

## 다음 작업 권고

라이브 점검은 본 환경 도구 한계로 불가. 다음 두 가지 방법 중 선택:

**A. 사용자가 라이브 직접 확인**
- 헤더 4그룹 메뉴 클릭하면서 페이지별 이미지 깨짐, 폰트, 컬러, CTA 작동 확인
- 깨진 곳 스크린샷 공유 → 본 세션에서 즉시 수정

**B. 본 세션에서 파일별 정적 분석 추가**
- 미점검 9개 페이지 fetch 후 P0~P1 이슈 추출
- 단, 도구 한계로 라이브 렌더링 결과는 알 수 없음 — 정적 코드 레벨 점검만

**즉시 실행 가능한 자동 수정 (사용자 승인 시)**:
- P0-1: header.js 역할별 메뉴 `.html` 추가 (5분)
- P3: 레거시 파일 삭제 (10분)

---

## 본 세션 핸드오프

- 이 보고서: `docs/site-audit/2026-05-05-menu-status.md`
- 작업 일지: `docs/work-log/2026-05-05.md`
- 다음 세션 시 두 파일 읽으면 컨텍스트 즉시 복원
