# TAI 프론트엔드 세션 메모리 — 2026-03-28

## 작업 대상 레포
- **repo**: taiengineering/tai-admin (main 브랜치)
- **배포**: Cloudflare Pages → admin.taieng.co.kr
- **API**: https://api.taieng.co.kr

---

## 완료된 작업 목록

### 1. personnel-list.html 신규 생성
**파일**: `admin/full-version/html/horizontal-menu-template/personnel-list.html`  
**커밋**: `aa4121c`

- 탭1 선임 연결 현황: `GET /personnel/requests`, 통계카드 4개(`GET /personnel/stats`)
  - 상태 배지: PENDING(검토중) / MATCHED(매칭완료) / CONTRACTED(계약성사) / CANCELLED(취소)
  - [매칭] 버튼: PENDING 상태만 활성 → `PATCH /personnel/requests/{id}`
- 탭2 기술자 목록: `GET /personnel/list?search=&verified_status=`
  - TAI등급 배지 T1~T5, 인증상태 배지 4종
  - [기술자 등록] 슬라이드패널 → `POST /personnel/create`
  - 담당지역 17개 시도 체크박스
- 탭3 안전관리전문기관: `GET /personnel/agencies?search=`
  - [기관 등록] 슬라이드패널 → `POST /personnel/agencies`
- active: 선임연결 > 선임연결 관리

---

### 2. role_code 001 전체 권한 부여
**DB**: role_permissions 테이블  
**누락 10개 추가**:
`COMPANY_DELETE`, `COMPANY_UPDATE`, `FACTORY_CREATE`, `FACTORY_DELETE`, `FACTORY_UPDATE`,
`INSPECTION_CREATE`, `INSPECTION_VIEW`, `LEGAL_APPLY`, `LEGAL_VIEW`, `SYSTEM_VIEW`  
→ role_code 001 권한 45개 = permissions 테이블 전체 45개 (100%)

---

### 3. globals.js 핵심 버그 수정
**파일**: `admin/full-version/assets/js/tai/globals.js`  
**커밋**: `ac78152`

**수정 내용**:
```js
// 기존 (버그)
if (!data) return;
categories.forEach(cat => { G[cat] = data[cat] || []; });

// 수정 ✅
if (!res || !res.data) return;
categories.forEach(cat => { G[cat] = res.data[cat] || []; });
```
- apiCall 응답 구조: `{ status, data: { user_role: [...] } }` → `data.data[cat]`으로 접근
- `renderPagination` 6번째 파라미터 `paginationId` 추가 (하위 호환)
- **영향**: loadGlobals + fillSelect를 사용하는 모든 페이지의 전역변수 셀렉트 정상화

---

### 4. member-list.html 대규모 수정
**파일**: `admin/full-version/html/horizontal-menu-template/member-list.html`  
**커밋**: `81ff819`

| 항목 | 변경 |
|---|---|
| 회원코드 컬럼 | 제거 (8컬럼) |
| 관리 버튼 라인 | 완전 제거 |
| 행 클릭 | 상세 슬라이드 패널 열림 |
| 부서 입력 | `<input list="dl-department">` datalist (선택+직접입력) |
| 직책 입력 | `<input list="dl-position">` datalist (선택+직접입력) |
| 전역변수 로드 | `user_role, user_status, department, position` 동시 로드 |
| 필터 셀렉트 | globals.js 버그 우회 → 직접 apiCall 후 `res.data.xxx` 접근 |

---

### 5. department 전역변수 DB 등록
**DB**: system_codes 테이블, category='department', category_name='부서'  
12개 등록: 경영지원/안전관리/생산/품질관리/설비관리/영업/구매/물류/인사총무/재무회계/기술연구/현장

---

### 6. 탑메뉴 협력사관리 이동 — Cursor 작업지시서 작성
**내용** (Cursor에 전달 필요):
- 회원관리 서브메뉴에서 "협력사관리" 항목 제거
- 수선관리 서브메뉴 제일 위에 "협력사관리" 추가
- 대상: 23개 HTML 파일 (auth-*.html, report-v1-viewer.html 제외)
- active 클래스 수정 금지
- 커밋: `"refactor(menu): 협력사관리 회원관리→수선관리 상단 이동"`

---

### 7. company-list.html 회사코드 컬럼 미노출
**커밋**: `450b770`
- 테이블 헤더: `회사코드` th 제거, 다음 컬럼 `회사유형`에 ps-4 이동
- tbody 렌더링: `company_code` 배지 td 제거
- colspan 11 → 10

---

### 8. company-list.html 등록/수정 폼 전면 개편
**커밋**: `e9bd16b`

**필드 변경**:
| 항목 | 변경 |
|---|---|
| 회사유형 | 맨 위로 이동, 필수 |
| 회사명 | 필수 |
| 사업자번호 | 필수 |
| 법인번호 | 삭제 |
| 대표자 | 필수 |
| 연락처 | 필수 |
| 이메일 | 필수 |
| 설립일 | 삭제 |
| 주소 | 필수 |
| 상태 | DB 순서대로 출력 |

**담당자 탭**: 이름/연락처/이메일 필수 표시 + 저장 전 검증  
**서류 탭**: 사업자등록증 필수 표시 + 미업로드 시 저장 차단

---

### 9. contract_status DB 재정렬
**DB**: system_codes 테이블

| code | code_name | sort_order | is_active |
|---|---|---|---|
| REQUESTED | 견적요청중 | 1 | true |
| CONFIRMED | 견적확정 | 2 | true |
| ACTIVE | 계약중 | 3 | true |
| SUSPENDED | 일시정지 | 4 | true |
| 나머지 4개 | - | - | false |

---

### 10. factory-list.html 회사 셀렉트 전체 목록 로드 수정
**파일**: `admin/full-version/html/horizontal-menu-template/factory-list.html`  
**커밋**: `276ba42`

**원인**: `/companies?size=500` → API `size <= 100` 제한 → 422 오류 → catch → `companiesList = []`

**수정**: `loadAllCompanies()` 함수 신규 추가
```js
async function loadAllCompanies() {
  let all = [], page = 1;
  while (true) {
    const data = await apiCall('GET', '/companies?size=100&page=' + page + '&sort=company_name&order=asc');
    const items = (data && data.data && data.data.items) || [];
    const total = (data && data.data && data.data.total) || 0;
    all = all.concat(items);
    if (all.length >= total || items.length === 0) break;
    page++;
  }
  return all;
}
```
- size=100 페이지네이션 루프로 전체 회사 로드
- 회사명 오름차순 정렬
- 시설 등록/수정 폼의 회사 선택에 전체 회사 표시

---

## 미완료 / 보류 항목

### 로그아웃 무한루프 이슈 (미해결)
- 증상: 로그아웃 후 auth-login-cover.html에서 무한루프 발생 가능성
- 추정 원인: api.js의 401 핸들러가 location.replace 실행 → 이미 로그인 페이지에서 또 redirect
- auth-login-cover.html 상단 스크립트는 token 있을 때만 redirect → 이론상 루프 불가
- **미해결 상태** — 추가 디버깅 필요

### Cursor 작업지시 (전달 필요)
협력사관리 메뉴 이동 건 — 위 6번 항목 참조

---

## API 제한사항
- `/companies?size=` 최대 100 (500 불가)
- `/factories?size=` 최대 100
- `/system-codes/multi` 응답: `{ status, data: { category: [...] } }` 구조

## 공통 패턴
- 인증: `localStorage.getItem('access_token')` → 없으면 auth-login-cover.html 리다이렉트
- globals.js: `loadGlobals(['cat'])` → `G['cat']` 배열 (data.data.cat 접근, 수정 완료)
- `fillSelect(el, 'category', '전체')` 정상 동작 (globals.js 수정 후)
- `renderPagination(total, page, size, cb, null, 'pagination-id')` — 6번째 파라미터로 id 지정

## 파일별 현재 SHA
| 파일 | SHA |
|---|---|
| globals.js | 4f3a6d5 |
| member-list.html | 0def018 |
| company-list.html | 9a5b112 |
| factory-list.html | 4b12a0b |
| personnel-list.html | c2c2d5b |
