# TAI Frontend MEMORY — 2026-04-03 (최종)

## 오늘 완료된 작업

### 1. engine-document.html — 완료 ✅
- 위치: `admin/full-version/html/horizontal-menu-template/engine-document.html`
- 배포 확인: admin.taieng.co.kr 정상 노출
- 탭 3개: 법정서식 / TAI표준서식 / 자유서식가이드
- API: `GET /engine/forms?form_type=LEGAL|STANDARD|FREE`
- fallback: 법정→`/report-forms`, 표준→기본10종, 자유→가이드3종
- menu-nav.js에 `엔진설정 > 문서관리` 항목 이미 포함됨

### 2. contract-kmong — 완료 ✅
- `admin/full-version/html/horizontal-menu-template/contract-kmong.html`
- `admin/full-version/assets/js/tai/contract-kmong.page.js`
- `admin/full-version/html/horizontal-menu-template/contract-kmong-edit.html`
- menu-nav.js `계약관리` 그룹에 크몽 항목 추가
- 백엔드 API 연동 확인: `GET /contract/kmong` → 200 OK

### 3. DB 적재 완료 ✅
- `document_form_master`: LEGAL 12건, STANDARD 10건, FREE 5건 (총 27건)

---

## admin 페이지 작성 규칙 (확정)

| 항목 | 값 |
|------|----|
| 레이아웃 | 수직 사이드바 (layout-compact layout-menu-fixed) |
| assets 경로 | `../../assets/` |
| 메뉴 | menu-nav.js 공통 (`.menu-inner` 동적 렌더링) |
| 인증 | `localStorage.getItem('access_token')` (menu-nav.js 자동 처리) |
| 로그아웃 | `doLogout()` (page.js에 정의) |
| API | `apiCall('GET', '/path')` (api.js 공통 함수) |
| 토큰키 | `access_token`, `refresh_token`, `role_code`, `user_name`, `user_id`, `company_id` |
| 파일구조 | `*.html` (shell) + `assets/js/tai/*.page.js` (로직) |
| 리스트규칙 | 1열=체크박스(toggleAll), 2열=No. |
| 코드값 | system_codes API 동적 조회 (하드코딩 금지) |

---

## 다음 우선순위

1. `document_form_master` → `form_code` 매핑 80건 (백엔드)
2. 건설섹터 진단 알고리즘 (하청 인원수, 공종 분리)
3. 공지예외주장 제출 마감 **2026-04-28** (patent.go.kr)
4. Cloudflare Zero Trust Access 설정 (taieng.co.kr 잠금)
