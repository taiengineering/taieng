# TAI 프론트엔드 메모리 — 2026-03-28

## 서버/레포 정보
- 레포: taiengineering/tai-admin (main)
- 배포: Cloudflare Pages 자동배포
- admin: admin.taieng.co.kr
- tadmin: tadmin.taieng.co.kr
- API: https://api.taieng.co.kr
- 스택: Vuexy HTML Bootstrap 5, Vanilla JS

---

## 오늘 완료된 작업

### 1. engine-equipment.html 신규 생성 ✅
- 경로: `admin/full-version/html/horizontal-menu-template/engine-equipment.html`
- 통계카드 4개 (GET /engine-equipment/stats)
- 탭1 설비마스터 (GET /engine-equipment/list)
- 탭2 모델마스터 (GET /engine-equipment/models)
- 버그: `renderPaginationTo()` 인라인 함수 추가 (utils.js #pagination 고정 ID 문제)
- 버그: 패널 footer onclick → addEventListener 교체
- 커밋: `1f54bc0` → 버그수정 `e02b088`

### 2. company-list.html NTS 국세청 검증 완성 ✅
- **최종 API 응답 필드 확정:**
  - `valid_yn: true` = 대표자명 진위 일치
  - `is_active: true` = 계속사업자
- 헬퍼 함수:
  ```javascript
  function _ntsActiveOk(c){ return c.is_active !== undefined ? !!c.is_active : true; }
  function _ntsCeoOk(c)   { return c.valid_yn  !== undefined ? !!c.valid_yn  : true; }
  function _ntsVerified(c){ return !!(c.nts_verified_at || c.verified_at); }
  ```
- 리스트: NTS검증 컬럼 (미검증/일치/불일치 배지)
- 상세: 계속사업자·대표자 진위 ✔/✘ 결과 카드 + [재검증] 버튼
- 불일치 태그: 사업자번호 옆 `⚠ 휴업/폐업`, 대표자명 옆 `⚠ 국세청 불일치`
- 경고 배너: 패널 상단 alert-danger
- 사업자등록증 필수 해제 (선택)
- NTS API 경로 상수:
  ```javascript
  const NTS_VERIFY_PATH     = '/companies/nts-verify';
  const NTS_REVERIFY_PREFIX = '/companies';
  const NTS_REVERIFY_SUFFIX = '/nts-verify';
  ```
- 최종 커밋: `4744c77`

### 3. 전체 리스트 페이지 전체선택+순번 일괄 적용 ✅
- **규칙:** 모든 리스트 페이지 1번째 컬럼 전체선택 체크박스 + 2번째 컬럼 No. 순번
- **순번 계산:** `(currentPage-1)*pageSize + idx + 1`
- **프론트창 직접 수정:** member-list.html, admin/factory-list.html
- **Cursor 작업 완료 (커밋 9928064):**
  - admin: company-list, contract-list, quote-list, inquiry-list, equipment-list(checkAll1/2), personnel-list(3탭), system-codes, inspection-list, repair-list, education-list, engine-equipment, engine-model
  - tadmin: factory-list, my-contract, my-equipment, my-inspection, notification-list, education-list
- **스킵:** education-setting.html(설정화면), process-select.html(테이블 없음)

### 4. site/ front-pages 경로 정리 ✅ (Claude Code)
- `html/contact.html` → `html/front-pages/contact.html`
- `html/survey.html` → `html/front-pages/survey.html`
- `html/survey_pro.html` → `html/front-pages/survey_pro.html`
- `html/tai_survey_v5.html` → `html/front-pages/tai_survey_v5.html`
- 내부 경로 수정: `../assets/` → `../../assets/`
- 기존 18개 HTML: contact.html 참조 → front-pages/contact.html 업데이트
- 커밋: push 완료 (`2a87535`)

### 5. Claude Code 작업지시서 — loadGlobals 버그수정 ✅
- 경로: `docs/TAI_ClaudeCode_작업지시서_loadGlobals_버그수정.md`
- 대상: admin 17개 + tadmin 9개 파일
- 커밋: `0faccfa`

---

## 영구 규칙 (변경 금지)

1. **모든 리스트 페이지 필수 2가지:**
   - 1번째 컬럼: 전체선택 체크박스 (`id="checkAll"`, `toggleAll(this)`)
   - 2번째 컬럼: 순번 No. (`(currentPage-1)*pageSize+idx+1`)
2. 새 페이지: maps-leaflet.html 복사 후 콘텐츠만 교체
3. 로고: height:110px 고정
4. autocomplete span 유지 필수
5. 모든 alert() → showToast(type, message)
6. 절대 URL + location.replace()
7. Supabase 직접 연결 금지 → FastAPI 경유
8. 코드값 하드코딩 금지 → system_codes API
9. `utils.js`의 `renderPagination`은 #pagination 고정 → 별도 ID 필요 시 `renderPaginationTo()` 인라인 정의
10. onclick 인라인 문자열에 JS 객체 주입 금지 → `addEventListener` + `data-*` 속성
11. init() 내 loadGlobals는 반드시 try-catch → loadList() 항상 실행

---

## 완성된 파일 현황

### admin (/admin/full-version/html/horizontal-menu-template/)
| 파일 | 상태 | 비고 |
|------|------|------|
| auth-login-cover.html | ✅ | |
| auth-register.html | ✅ | |
| auth-find-id.html | ✅ | |
| index.html | ✅ | 대시보드 |
| member-list.html | ✅ | 전체선택+순번 |
| company-list.html | ✅ | NTS 검증 포함 |
| factory-list.html | ✅ | 전체선택+순번 |
| contract-list.html | ✅ | 전체선택+순번 |
| quote-list.html | ✅ | 전체선택+순번 |
| inquiry-list.html | ✅ | 전체선택+순번 |
| equipment-list.html | ✅ | checkAll1/2 |
| personnel-list.html | ✅ | 3탭 |
| inspection-list.html | ✅ | 전체선택+순번 |
| repair-list.html | ✅ | 전체선택+순번 |
| education-list.html | ✅ | 전체선택+순번 |
| system-codes.html | ✅ | 전체선택+순번 |
| engine-equipment.html | ✅ | 오늘 신규 |
| engine-model.html | ✅ | 전체선택+순번 |
| notification-setting.html | ✅ | |
| education-setting.html | ✅ | |
| permission.html | ✅ | |
| facility-process.html | ✅ | |
| facility-equipment.html | ✅ | |
| process-list.html | ✅ | v3 |
| report-v1.html | ✅ | |

### tadmin (/tadmin/full-version/html/horizontal-menu-template/)
| 파일 | 상태 | 비고 |
|------|------|------|
| index.html | ✅ | |
| factory-list.html | ✅ | 전체선택+순번 |
| my-contract.html | ✅ | 전체선택+순번 |
| my-equipment.html | ✅ | 전체선택+순번 |
| my-inspection.html | ✅ | 전체선택+순번 |
| notification-list.html | ✅ | 전체선택+순번 |
| education-list.html | ✅ | 전체선택+순번 |
| education-setting.html | ✅ | |
| manager-permission.html | ✅ | |
| my-diagnosis.html | ✅ | |
| process-select.html | ✅ | |
| contact.html | ✅ | |

---

## 미완료 이슈

| 이슈 | 우선순위 | 비고 |
|------|---------|------|
| /contracts 503 오류 | 🔴 | 백엔드 창 |
| NTS API 실제 경로 확인 | 🔴 | 백엔드 창 확인 필요 |
| loadGlobals 버그 전체 수정 | 🟡 | 작업지시서 전달됨 |
| system-codes.html CRUD API | 🟡 | 백엔드 미구현 |
| 엔진설정 서브메뉴 HTML 미생성 (engine-factory 등) | 🟢 | |
| 설정 서브메뉴 HTML 미생성 (quote-setting 등) | 🟢 | |
| 탑바 알림 드롭다운 위치 (우측으로 열림) | 🟡 | |
| 법령 판정 결과 탭5 | 🟡 | 프론트 미작업 |
| 공정 4단계 셀렉트 (tadmin) | 🟡 | |
| 신고서식 HTML 입력폼 구현 (tadmin) | 🟡 | 백엔드 API 완성 후 |

---

## API 현황

| 엔드포인트 | 상태 |
|-----------|------|
| POST /auth/login | ✅ |
| GET /system-codes/multi | ✅ |
| GET /building-register/juso-search | ✅ |
| GET /engine-equipment/stats | ✅ (느림→집계 테이블 필요) |
| GET /engine-equipment/list | ✅ (느림) |
| GET /engine-equipment/models | ✅ |
| POST /companies/nts-verify | ⚠️ 경로 미확인 |
| POST /companies/{id}/nts-verify | ⚠️ 경로 미확인 |
| GET /report-forms/obligations | ✅ (오늘 추가) |
| POST /report-forms/submissions/preview-pdf | ✅ (오늘 추가) |
| GET /contracts | 🔴 503 |
| POST/PATCH/DELETE /system-codes | 🔴 미구현 |

---

## 절대 URL 표
| 목적 | URL |
|------|-----|
| admin 로그인 | https://admin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html |
| tadmin 로그인 | https://tadmin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html |
| admin 대시보드 | https://admin.taieng.co.kr/html/horizontal-menu-template/index.html |
| tadmin 대시보드 | https://tadmin.taieng.co.kr/html/horizontal-menu-template/index.html |
