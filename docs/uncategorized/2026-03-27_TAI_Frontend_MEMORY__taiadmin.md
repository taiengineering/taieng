# TAI Frontend 메모리 — 2026-03-27

---

## 오늘 완료 작업

### 1. engine-equipment.html 신규 생성 ✅
- 커밋: `1f54bc0`
- 경로: `admin/full-version/html/horizontal-menu-template/engine-equipment.html`
- 탑메뉴: 엔진설정 > 설비 active

**구성:**
- 통계 카드 4개: 매핑 전체 건수 / 고유 설비 수 / 검토필요 / 모델 마스터
  - API: `GET /engine-equipment/stats`
- 탭1 설비 마스터
  - API: `GET /engine-equipment/list?search=&category=&band=&needs_review=&page=&page_size=50`
  - 필터: 설비명 검색, 카테고리(13종), 밴드(4종), 검토상태
  - 테이블: 체크박스 + 설비명/카테고리/경로/밴드/공정수/검토상태/관리
  - 배지: MUST(빨강) / CORE(주황) / OPTIONAL(파랑) / REFERENCE(회색)
  - 일괄 승인: `POST /engine-equipment/review/approve`
  - 슬라이드 패널: 기본정보 + 밴드분포 진행바 + 연결공정(max 50) + 메타수정 폼
    - 수정 API: `PATCH /engine-equipment/update/{name}`
- 탭2 모델 마스터
  - API: `GET /engine-equipment/models?search=&equipment_std=&manufacturer=&page=&page_size=30`
  - 수정 모달: `PATCH /engine-equipment/models/{id}` (6개 필드)

---

### 2. engine-equipment.html 버그 수정 ✅
- 커밋: `e02b088`

**수정 내용:**

| 버그 | 원인 | 해결 |
|------|------|------|
| 페이지네이션 미출력 | `utils.js`의 `renderPagination`이 `#pagination` 고정 ID만 참조 | `renderPaginationTo(total, page, size, cb, targetId)` 인라인 함수 추가 |
| 패널 수정 저장 버튼 미동작 | onclick 문자열 내 JS 이스케이프 오류 | `addEventListener('click', ...)` + 클로저 방식으로 교체 |
| 모델 수정 버튼 미동작 | 동일 원인 | `data-model-id` 속성 + `window._moCache` 전역 캐시로 교체 |

---

### 3. 성능 이슈 기획안 작성 ✅

**현재 문제:** `process_equipment_map` (118만 row, 증가 중) 실시간 GROUP BY 집계

**해결 방향:**

| 순위 | 작업 | 담당 | 효과 |
|------|------|------|------|
| 1 | `engine_equipment_summary` 집계 테이블 생성 + list/stats API 교체 | 백엔드 | ★★★★★ |
| 2 | 인덱스 추가 (facility_name / facility_category / needs_review / top_band) | 백엔드 | ★★★★ |
| 3 | 기본 page_size 축소 / 검색 디바운스 300ms / 세션 캐시 | 프론트 | ★★ |

→ 백엔드 창에 집계 테이블 설계 및 API 교체 요청 필요

---

## 현재 파일 목록 (전체)

### Admin (총관리자)
| 파일 | 상태 |
|------|------|
| auth-login-cover.html | ✅ 완료 |
| auth-register.html | ✅ 완료 |
| auth-find-id.html | ✅ 완료 |
| index.html | ✅ 완료 (대시보드) |
| member-list.html | ✅ 완료 |
| company-list.html | ✅ 완료 |
| factory-list.html | ✅ 완료 |
| contract-list.html | ✅ 완료 (503 이슈 별도) |
| quote-list.html | ✅ Mock |
| permission.html | ✅ Mock |
| notification-setting.html | ✅ 완료 |
| education-setting.html | ✅ 완료 |
| education-list.html | ✅ 완료 |
| process-list.html | ✅ 완료 (v3) |
| system-codes.html | ✅ 완료 |
| engine-equipment.html | ✅ 완료 (오늘 신규) |

### tadmin (안전관리자)
| 파일 | 상태 |
|------|------|
| index.html | ✅ 완료 |
| my-contract.html | ✅ 완료 |
| manager-permission.html | ✅ 완료 |
| notification-list.html | ✅ 완료 |
| education-list.html | ✅ 완료 |
| education-setting.html | ✅ 완료 |
| process-select.html | ✅ 완료 |

### 공통 모듈
- `assets/js/tai/api.js` — FastAPI 공통 호출
- `assets/js/tai/toast.js` — Toast 알럿
- `assets/js/tai/globals.js` — 전역변수 로드
- `assets/js/tai/notification.js` — 탑바 알림
- `assets/css/tai/custom.css` — 슬라이드 패널, Toast
- `assets/js/utils.js` — setButtonLoading, showToast, confirmModal, formatMoney, renderPagination

---

## 핵심 작업 규칙 (변경 없음)

1. 새 페이지: maps-leaflet.html 복사 후 콘텐츠만 교체
2. 로고: height:110px 고정
3. autocomplete span 유지 필수
4. 모든 alert() → showToast(type, message) 교체
5. 페이지 진입 시 closePanel() 호출
6. Supabase 직접 연결 전면 제거 → FastAPI 경유
7. 코드값 하드코딩 금지 → system_codes API 동적 조회
8. 모든 HTML 로그인 리다이렉트: **절대 URL 필수** + `location.replace()`
9. **`utils.js`의 `renderPagination`은 `#pagination` 고정 ID 사용** → 별도 ID 필요 시 `renderPaginationTo()` 인라인 정의할 것
10. onclick 인라인 문자열에 JS 객체/변수 주입 금지 → `addEventListener` + `data-*` 속성 사용

---

## 절대 URL 규칙

| 목적 | URL |
|------|-----|
| admin 로그인 | `https://admin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html` |
| tadmin 로그인 | `https://tadmin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html` |
| admin 대시보드 | `https://admin.taieng.co.kr/html/horizontal-menu-template/index.html` |
| tadmin 대시보드 | `https://tadmin.taieng.co.kr/html/horizontal-menu-template/index.html` |

---

## API 현황

| 엔드포인트 | 상태 |
|-----------|------|
| POST /auth/login | ✅ |
| GET /system-codes/multi | ✅ |
| GET /building-register/juso-search | ✅ |
| GET /engine-equipment/stats | ✅ (느림 → 집계 테이블 도입 필요) |
| GET /engine-equipment/list | ✅ (느림 → 집계 테이블 도입 필요) |
| GET /engine-equipment/detail/{name} | ✅ |
| PATCH /engine-equipment/update/{name} | ✅ |
| POST /engine-equipment/review/approve | ✅ |
| GET /engine-equipment/models | ✅ |
| PATCH /engine-equipment/models/{id} | ✅ |
| GET /contracts | 🔴 503 (백엔드 수정 필요) |
| POST /system-codes | 🔴 미완성 |
| PATCH /system-codes/{id} | 🔴 미완성 |
| DELETE /system-codes/{id} | 🔴 미완성 |

---

## PENDING 이슈

| 이슈 | 우선순위 |
|------|----------|
| engine-equipment 성능: 집계 테이블 도입 필요 (백엔드) | 🔴 |
| `/contracts` 503 (백엔드) | 🔴 |
| system-codes CRUD API 미완성 (백엔드) | 🔴 |
| 엔진설정 서브메뉴 HTML 미생성 (engine-factory, engine-model, engine-legal 등) | 🟢 |
| 설정 서브메뉴 HTML 미생성 (quote-setting, repair-setting, doc-setting) | 🟢 |
| 탑바 알림 드롭다운 위치 (우측으로 열림) | 🟡 |
| 대시보드 TAI 전용 통계 카드 구성 | 🟡 |
