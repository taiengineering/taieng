# TAI 작업 세션 — 2026-04-09

## 완료 작업 (tai-admin repo)

### 1. 파비콘 SVG 3종 생성 및 업로드
업로드된 TAI 로고 이미지에서 색상 추출 후 각 사이트별 SVG 파비콘 제작.

| 사이트 | 색상 | 파일 경로 | 주입 방식 |
|---|---|---|---|
| new.taieng.co.kr | 파란+회색 (#1e4d7a/#6b6b6b) | nexas/assets/img/favicon.svg (taieng repo) | footer.js |
| admin.taieng.co.kr | 주황+어두운 (#d49030/#383838) | site/full-version/html/favicon.svg | menu-nav.js |
| safe.taieng.co.kr | 초록+어두운 (#1a5c30/#383838) | front-pages/assets/favicon.svg | tai-footer.js |

### 2. tai-footer.js v3 업데이트 (safe.taieng.co.kr)
- 파비콘 자동 설정 코드 추가 (`front-pages/assets/favicon.svg` 경로)
- 회사명: `주식회사 TAI엔지니어링` → `TAI엔지니어링` (개인사업자 표기)
- Copyright: `© 2026` → `©` (연도 삭제)

### 3. menu-nav.js 파비콘 주입 추가 (admin.taieng.co.kr)
- 파일: `admin/full-version/assets/js/tai/menu-nav.js`
- `/favicon.svg` 절대경로 사용 (배포 루트 기준)
- 코드 위치: `guardAdminAccess()` 호출 바로 위

---

## 변경된 파일 목록 (tai-admin)

| 파일 | 변경 내용 |
|---|---|
| `site/full-version/html/favicon.svg` | admin 파비콘 SVG 신규 (주황+어두운) |
| `site/full-version/html/front-pages/assets/favicon.svg` | safe 파비콘 SVG 신규 (초록+어두운) |
| `site/full-version/html/front-pages/assets/tai-footer.js` | 파비콘 주입 + 개인사업자 수정 + copyright 정리 |
| `admin/full-version/assets/js/tai/menu-nav.js` | 파비콘 자동 설정 코드 추가 |

---

## 참고: taieng repo 작업 (같은 세션)

| 항목 | 완료 |
|---|---|
| Footer 특허문구 색상 → 흰색(#fff) | ✅ |
| Copyright 2026 삭제 / 이걸왜몰랐지 삭제 | ✅ |
| 파비콘 SVG (new, 파란+회색) + footer.js 주입 | ✅ |
| 홈페이지 히어로 2단 레이아웃 (좌텍스트+우목업이미지) | ✅ |
| hero-mockup.webp 32KB 연결 | ✅ |
| nav 로고 흰색 반전 (filter: brightness(0) invert(1)) | ✅ |
| 안전정보 API(/posts) 점검 → 정상, 데이터 0건 확인 | ✅ |

---

## 내일 진행 예정

### 안전정보 데이터 채우기
`posts` 테이블 현재 0건. 방향 결정 필요:
- **A안) 크롤러 구축** — 고용노동부/KOSHA/안전보건공단 자동 수집
- **B안) 어드민 등록 UI** — admin.taieng.co.kr에서 수동 등록 화면 제작
