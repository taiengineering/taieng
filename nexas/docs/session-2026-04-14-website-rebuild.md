# 세션 작업내역 — 2026-04-14

> repo: taiengineering/taieng | 작업 폴더: nexas/
> 기획서: docs/workorder-website-rebuild-v5.md 기준

---

## 완료 작업 목록

### 잔여 수정 3건 (이전 세션 후속)

| # | 파일 | 내용 | 커밋 |
|---|------|------|------|
| 1 | `service/repair.html` | 구 navbar-area 하드코딩 제거 → `<div id="tai-header">` + header.js 교체 | fix: 웹사이트 잔여 수정 |
| 2 | `service/consulting.html` | "맞욤 콘설팅" → "맞춤 컨설팅" 전체 7곳 교체 | fix: 웹사이트 잔여 수정 |
| 3 | `site-map.html` | 이전 세션에서 이미 완료 확인 (레거시 섹션 없음) | — |

---

### 단계 0: 정리 작업

| # | 항목 | 상태 |
|---|------|------|
| 0-1 | `nexas/.gitignore` — `node_modules/`, `.DS_Store`, `Nexas.zip`, `prepros.config` 추가 | ✅ |
| 0-2 | 레거시 파일 20개 삭제 (index-1~6, blog*, team*, construction, service, demo, diagnosis-start, tai-fix, Nexas.zip, prepros.config, .DS_Store) | ⏳ GitHub UI/CLI 필요 |
| 0-3 | `node_modules/` git rm --cached | ⏳ CLI 필요 |
| 0-4 | `site-map.html` 레거시 섹션 제거 | ✅ (이전 세션 완료) |

---

### 단계 1: header.js + footer.js 통일

| 파일 | 변경 내용 | 버전 |
|------|----------|------|
| `assets/js/header.js` | Nexas 원본 `navbar-area` 구조 유지, `btn btn-base` → **`btn btn-white`** (무료 진단 버튼) | v2.0.0 |
| `assets/js/footer.js` | 자체 CSS(`tai-footer`, `footer-grid`) → **원본 Nexas `footer-area style-1`** 구조로 완전 교체. 특허 안내 바 추가 | v2.1.0 |

footer.js 주요 내용:
- 상단: "특허 출원 중 (Patent Pending) · 제10-2026-0056330 외 5건"
- 5컬럼: 회사정보 / 서비스(7개) / 대상별+역할별 / 시작하기 / 회사
- 하단: © 2026 TAI Engineering + 특허 출원 중 + 사이트맵 링크

> 전 페이지 이미 `<div id="tai-header/footer">` + JS 로드 적용 완료 → JS 2개 파일 업데이트만으로 전체 자동 반영

---

### 단계 2~3: 페이지 리빌드

#### for-safety-manager.html (단계 3)
- 기반: `nexas_sample/index-2.html` (`body class="sc5 home-2"`)
- 섹션: 히어로 → Pain Points 5개 → TAI 기능 6개 카드 → 도입 전/후 비교 → 현장 앱 → CTA
- 커밋: `rebuild: for-safety-manager.html — 안전관리자용 랜딩 리빌드`

#### service/saas.html (단계 5)
- 기반: `nexas_sample/index-4.html` (`body class="home-4 sc5"`)
- 섹션: 히어로 → 설계철학 한줄 → 기능 10개 (about/work-area 좌우 교차) → 가격 미리보기 → 강조 배너 → CTA
- "안전관리자와 현장의 입장에서 설계하고 만들었습니다" 문구 포함
- "이 시스템으로 관리한다면, 중대재해처벌법은 어림없습니다." 강조 배너
- 커밋: `rebuild: service/saas.html — SaaS 구독 페이지 리빌드`

#### service/repair.html (단계 8)
- 기반: `nexas_sample/service.html` (`body class="sc5"`)
- 양면 마켓: 사업장(수요자) + 수선업체(공급자) 별도 섹션
- 연결 가능 분야 5개 (기계·전기·소방·건축·법정검사)
- **【절대 금지】** 소개비/소개수수료 → 플랫폼 이용료 사용
- 커밋: `rebuild: service/repair.html — 수선 연결 페이지 리빌드`

#### service/consulting.html (단계 9)
- 기반: `nexas_sample/service.html` (`body class="sc5"`)
- 섹션: 히어로 → 현실 3단 → 컨설팅 분야 5개 → TAI 차이점 → 전문가 유치 배너 → CTA
- 공급자(전문가) 유치 섹션 포함 → `mypage/expert-application/` 링크
- **【절대 금지】** 소개비 → 플랫폼 이용료/매칭 서비스료 사용
- 커밋: `rebuild: service/consulting.html — 컨설팅 페이지 리빌드`

#### target/ 3개 페이지 (단계 12)
공통 구조: 히어로 → 적용 법령 → 주요 점검 의무 → TAI 자동화 → CTA

| 파일 | 히어로 | 법령 수 | 의무 카드 | 자동화 블록 | 색상 |
|------|--------|---------|----------|------------|------|
| `target/building.html` | 건물·시설 안전관리, TAI가 자동화합니다 | 5개 | 5개 | 3개 | 보라 |
| `target/factory.html` | 제조공장 안전관리, 이제 혼자가 아닙니다 | 4개 | 5개 | 3개 | 초록 |
| `target/construction.html` | 건설현장 안전관리, TBM부터 신고까지 | 4개 | 5개 | 4개 | 주황 |

- 텍스트 전수 검수 완료 (이전의 깨진 텍스트 없음)
- construction.html: 기상청 API 연동 작업중지 경고 자동화 블록 포함 (이미 구현된 기능)
- 커밋: `rebuild: target/ 3개 페이지 — 건물·공장·건설 대상별 리빌드`

---

## 현재 nexas/ 리빌드 진행률

| 순서 | 작업 | 상태 |
|------|------|------|
| 0 | nexas/ 정리 (.gitignore, 파일삭제) | 🔶 부분완료 (삭제는 별도 CLI) |
| 1 | header.js + footer.js | ✅ |
| 2 | index.html 리빌드 | ⏳ |
| 3 | for-safety-manager.html | ✅ |
| 4 | for-business-owner.html | ⏳ |
| 5 | service/saas.html | ✅ |
| 6 | service/diagnosis.html | ⏳ |
| 7 | service/appointment.html | ⏳ |
| 8 | service/repair.html | ✅ |
| 9 | service/consulting.html | ✅ |
| 10 | service/education.html | ⏳ |
| 11 | service/inapp.html | ⏳ |
| 12 | target/ 3개 | ✅ |
| 13 | pricing.html | ⏳ |
| 14 | about.html | ⏳ |
| 15 | faq, safety-news, contact | ⏳ |

완료: 7 / 15 단계 (약 47%)

---

## 다음 작업 우선순위

1. **index.html 리빌드** (메인홈, index-1 템플릿 기반) — 가장 중요
2. **for-business-owner.html** (사업주/현장소장용, index-3 기반)
3. **service/appointment.html** (선임 연결, 양면 마켓)
4. **service/education.html**, **service/inapp.html**
5. **service/diagnosis.html**
6. **0-2 레거시 파일 삭제** — GitHub UI 또는 `git rm` CLI 필요

---

## 기술 메모

### 페이지 구조 패턴 (확립됨)
- 루트 페이지: `body class="sc5"` 또는 `sc5 home-2` 등, CSS/JS `assets/...`
- 서비스 서브폴더: CSS/JS `../assets/...`, 링크 `../pagename.html`
- header.js 자동 경로 감지: `/service/` 또는 `/target/` 포함 시 `../` prefix 자동 적용
- 이미지 placeholder: 원본 Nexas 템플릿 이미지 사용 + alt/caption에 실제 설명

### JS 로드 순서 (표준)
```html
jquery → bootstrap → imageloded → magnific → fontawesome → wow → main
→ header.js → footer.js
→ WOW().init()
```

### 클래스 레퍼런스 (Nexas 원본)
| 페이지 템플릿 | body class | 주요 섹션 |
|---|---|---|
| index-1 | `sc5` | `banner-area`, `featured-area`, `management-area` |
| index-2 | `sc5 home-2` | `banner-area style-2`, `single-app-service-inner-2` |
| index-3 | `sc5 home-3` | `banner-area style-3` |
| index-4 | `home-4 sc5` | `banner-area style-4`, `section-title style-2`, `about-area`, `work-area` |
| index-5 | `home-5 sc5` | `banner-area style-5`, `pricing` |
| index-6 | `home-6 sc5` | `banner-area style-6` |
| service.html | `sc5` | `breadcrumb-area`, `service-area`, `single-service-inner` |
