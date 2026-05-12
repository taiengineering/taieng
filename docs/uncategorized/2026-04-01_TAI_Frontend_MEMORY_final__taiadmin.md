# TAI Frontend MEMORY — 2026-04-01 최종마감

> 작성: Claude (CTO/Architect 창)
> 커밋 범위: ae6095c → e34fe56

---

## 1. 건설 법령진단 프론트 재설계 (작업지시서: TAI_Cursor_작업지시서_건설진단_프론트_재설계_20260401.md)

### 완료 파일 (커밋 ae6095c)

#### diagnosis-step1.html 수정
- CONSTRUCTION 폼 전면 교체
  - `c-direct` (직접 근로자수) + `c-subcon` (하도급 근로자수) 분리
  - `c-workers-total` 합계 실시간 표시
  - `c-sm-preview-wrap` / `c-sm-alert` 선임의무 미리보기 박스 추가
- `updateConsmPreview()` 함수 추가
  - 토목 120억 / 기타 150억 기준 선임의무 판정
  - 1억/50억/100억/200억/1000억 임계값 달성 시 안내 텍스트 표시
  - c-eok, c-direct, c-subcon, c-type 이벤트 바인딩
- `getFormInput('CONSTRUCTION')` 수정
  - `direct_workers`, `subcon_workers` 분리 포함
  - `worker_count` = direct + subcon 합계
- `runDiagnosis()` 완료 후 분기
  - CONSTRUCTION → `construction-diagnosis-step2.html?factory_id=&diagnosis_id=&sector=CONSTRUCTION`
  - 나머지 섹터 → 기존 `diagnosis-result.html` 유지
- `localStorage.setItem('current_factory_id', factoryId)` 추가

#### construction-diagnosis-step2.html 신규
- 4단계 스테퍼 (1단계 완료 ✓, 2단계 active)
- `renderSummary()`: sessionStorage `tai_diagnosis_step1`에서 construction_summary 카드 렌더링
  - 공사종류 / 공사금액 / 근로자수 / 선임의무 여부 / key_thresholds_met 배지
- KCSC 공정 목록: `GET /construction/kcsc/processes?page=1&size=100`
  - 공사구분 필터 (전체/BUILDING/CIVIL/COMMON)
  - 공정명 검색 (300ms debounce)
  - risk_level 배지 (HIGH/MEDIUM/LOW)
  - work_type_label 없으면 "법령 미매핑" 표시 + 주황 테두리
- 체크박스 선택 → `sel-count` 카운터 업데이트
- `runStep2()`: `POST /legal-engine/diagnose/step2` body: `{factory_id, diagnosis_id, kcsc_process_ids}`
  - 응답 sessionStorage `tai_diagnosis_step2` 저장
  - → `construction-diagnosis-step3.html` 이동

#### construction-diagnosis-step3.html 신규
- 4단계 스테퍼 (1·2단계 완료 ✓, 3단계 active)
- `renderStep2Summary()`: sessionStorage `tai_diagnosis_step2`에서 적용 공종 배지 + 추가 룰 수 표시
- 탭① PTW 작업: 현장 드롭다운 → `GET /construction/sites/{id}/works?page=1&size=100`
  - is_hazardous 빨간 좌측 보더, KCSC 연결여부 배지
- 탭② KCSC 위험작업: `GET /construction/kcsc/works?is_hazardous=true&page=1&size=100`
  - 검색 + is_hazardous 토글
  - `data-item` 속성에 JSON 저장 → 체크 시 `selectedKcscWorks` 배열 관리
- 설비코드 미리보기: `selectedKcscWorks`에서 `equipment_type_codes` 추출 → 배지 표시
  - TCR/MCR/LFT/GDL/HST/CPR/CCP/WMC/SCF/EXC 10종 한글 레이블
- `runStep3()`: `POST /legal-engine/diagnose/step3` body: `{factory_id, diagnosis_id, construction_work_ids, kcsc_work_ids}`
  - → `diagnosis-result.html?factory_id=&diagnosis_id=&sector=CONSTRUCTION`
- 건너뛰기 버튼: `skipToResult()` → diagnosis-result.html 직접 이동

#### diagnosis-result.html 수정
- `<div id="construction-summary-block" class="d-none">` — resultMain 최상단에 삽입
- `renderConstructionSummary(cs)` 함수 추가
  - 공사종류/금액/근로자(직접+하도급) 헤더
  - 안전관리자 선임 의무 발생/미발생 alert
  - key_thresholds_met true 항목 배지
- `paint()` 내부: `data.construction_summary` 우선, 없으면 sessionStorage `tai_diagnosis_step1` 에서 추출

---

## 2. taieng.co.kr 리다이렉트 이슈 — 상세 분석 및 해결 기록

### 2-1. 문제 현상
- `taieng.co.kr/request/v1/` → 법령진단 신청 페이지 대신 메인사이트 표시
- `taieng.co.kr/request/v1/login.html` → 무한루프 발생
- `taieng.co.kr/` → 디렉토리 목록("선택화면") 표시

### 2-2. 진단 과정 (브라우저 직접 확인)

#### 1단계: ETag 동일 현상 발견
```
fetch('/request/v1/')   → ETag: W/"2906fb6..."
fetch('/home/')         → ETag: W/"2906fb6..."
fetch('/zzz-nonexistent/') → ETag: W/"2906fb6..." (존재하지 않는 경로도 동일!)
```
→ 모든 URL에서 동일한 파일이 서빙됨 = **완전한 SPA 폴백 상태**

#### 2단계: 서빙되는 파일 내용 확인
```javascript
// 실제 브라우저에 서빙된 HTML 소스 확인
document.documentElement.outerHTML.substring(0, 500)
// 결과: '<!-- 로그인 게이트: 토큰 없으면 login.html로 즉시 redirect -->'
// 결과: function doLogout(){ ... location.replace('login.html'); }  ← 구버전!
```
→ GitHub에 없는 구버전 코드가 서빙 중

#### 3단계: 무한루프 원인 파악
```
/request/v1/login.html 접속
→ 파일 없음 → SPA 폴백 → 구버전 메인사이트 서빙
→ 구버전 JS: location.replace('login.html')  ← 상대경로!
→ 다시 /request/v1/login.html 로 리디렉트
→ 무한루프
```

#### 4단계: 근본 원인 확정
**Cloudflare Pages Build output directory 미설정**
- Cloudflare Pages가 레포 루트(/)를 서빙하는 설정
- `site/full-version/html/` 폴더를 인식하지 못함
- 결과: 모든 URL → 레포 루트의 단일 fallback 파일 서빙
- `_redirects` 규칙도 무효화 (올바른 디렉토리를 기반으로 동작하지 않음)

### 2-3. 해결 과정

#### 시도 1: `_redirects` 경로 수정 (커밋 baca744)
```
기존: /tadmin → /tadmin/auth-login-cover.html  (파일 없는 경로)
수정: /tadmin → /tadmin/full-version/html/.../auth-login-cover.html
+ 루트 / → tadmin 대시보드 직접 이동
```
→ 실패 (Build output directory 문제가 근본 원인)

#### 시도 2: home/index.html 코드 수정 (커밋 929788f)
```javascript
// 기존 (구버전 — 무한루프 원인)
function doLogout(){ location.replace('login.html'); }

// 수정 (최신)
function doHomeLogout(){
  [...키목록].forEach(k => localStorage.removeItem(k));
  location.reload();  // redirect 없음, 무한루프 없음
}
```
→ GitHub 코드는 최신이나 Cloudflare가 구버전 서빙 중 → 여전히 실패

#### 시도 3: 캐시 버스팅 push (커밋 929788f)
```html
<!-- cache-bust: 20260401-v2 -->
```
→ ETag 변화 없음 → Build output directory 문제 재확인

#### 시도 4: Cloudflare Pages 재배포 (사용자 직접)
→ ETag 동일 (`2906fb6...`) → Build output directory 미변경 확인

#### 최종 해결: Build output directory 변경
```
Cloudflare Pages → Settings → Build & deployments → Build output directory
: (비어있음 또는 잘못된 값) → site/full-version/html
→ 저장 → 재배포
```
→ ETag 변경 확인 → 모든 URL 정상 서빙

### 2-4. 해결 후 상태 검증 (브라우저 테스트)

| URL | 결과 |
|-----|------|
| `taieng.co.kr/` | ✅ `/home/` 리디렉트 → 메인사이트 |
| `taieng.co.kr/home/` | ✅ 최신 메인사이트 (`doHomeLogout` + `location.reload()`) |
| `taieng.co.kr/request/v1/` | ✅ 법령진단 신청 페이지 (타이틀: "법령진단 신청 \| TAI 산업안전") |
| `taieng.co.kr/request/v2/` | ✅ 공정진단 신청 페이지 |
| `taieng.co.kr/request/v3/` | ✅ 설비진단 신청 페이지 |
| `taieng.co.kr/request/v1/login.html` | ✅ `/request/v1/` 302 (무한루프 없음) |
| `taieng.co.kr/login.html` | ✅ tadmin 로그인으로 리디렉트 |
| 콘솔 에러 | ✅ 없음 |

### 2-5. 핵심 교훈

1. **Cloudflare Pages Build output directory는 반드시 명시해야 함**
   - 빈 값이면 레포 루트 기준 서빙 → 모든 URL이 동일한 fallback 파일 반환
   - ETag 동일 여부로 이 상태를 즉시 진단 가능

2. **`_redirects`는 Build output directory 설정 후에만 유효**
   - 파일이 올바른 디렉토리에 위치해야 규칙이 적용됨
   - Build output directory 미설정 상태에서는 _redirects 수정이 무의미

3. **구버전 코드 + SPA 폴백 = 무한루프 패턴**
   - `location.replace('login.html')` — 절대경로가 아닌 상대경로 사용 금지
   - 로그아웃은 반드시 `location.reload()` 또는 절대경로 사용

4. **재배포(Retry deployment)와 Build output directory 변경은 다른 작업**
   - 설정 변경 없이 재배포하면 동일한 결과
   - 반드시 Settings → Build output directory 수정 → 저장 → 재배포 순서

### 2-6. 최종 _redirects 규칙 (site/full-version/html/_redirects)
```
/request/v1   /request/v1/index.html  200  (SPA 폴백 차단)
/request/v1/  /request/v1/index.html  200
/request/v2   /request/v2/index.html  200
/request/v2/  /request/v2/index.html  200
/request/v3   /request/v3/index.html  200
/request/v3/  /request/v3/index.html  200
/login.html         → tadmin 로그인  302
/request/v1/login.html → /request/v1/  302  (무한루프 방지)
/request/v2/login.html → /request/v2/  302
/request/v3/login.html → /request/v3/  302
/             /home/  302
/index.html   /home/  302
```

### 2-7. tadmin 로그인 게이트 제거 (커밋 104f8ad)
- **배경**: 대표가 taieng.co.kr 접속 시 로그인 없이 대시보드 바로 접근 원함
- **수정**: `tadmin/full-version/html/horizontal-menu-template/index.html`에서 `<script src="auth-guard.js">` 제거
- **_redirects**: `/ → tadmin/full-version/html/.../index.html 302`
- **결과**: taieng.co.kr → 로그인 없이 대시보드 접근 가능

---

## 3. request v1/v2/v3 주소검색 API + 건축물대장 자동입력

### 구현 내용 (커밋 765d232, be6f933)

**적용 파일**: `site/full-version/html/request/v1/v2/v3/index.html`

**사용 API** (기존 TAI 백엔드 — factory-list.html과 동일)
- 주소 검색: `GET /building-register/juso-search?keyword=...&page=1&size=20`
- 건축물대장: `GET /building-register/search?address=...`

**동작 흐름**
1. 주소 필드 클릭 or "주소 검색" 버튼 → Bootstrap Modal 오픈
2. 검색어 입력 → `searchJuso()` → 결과 목록 (`div.juso-item`)
3. 결과 클릭 → `selectJusoItem(idx)`:
   - `address` 필드에 도로명주소 자동입력 (readonly)
   - `addressDetail` 필드에 건물명 자동입력
   - 즉시 `GET /building-register/search` 호출
4. 건축물대장 조회 성공 시 `renderBldgInfo(d)` → 정보 박스 표시
   - 연면적 / 지상층수 / 승강기 수 / 주 용도 / 사용승인일
5. v1에서만 "시설조건 자동입력" 버튼 → `floorArea` 필드에 건축물대장 연면적 자동입력 + `autofilled` 클래스

**색상 테마별 구분**
- v1 (법령진단): 파란색 (`#0d6efd`)
- v2 (공정진단): 보라색 (`#6610f2`)
- v3 (설비진단): 초록색 (`#0f9d6a`)

**테스트 결과 (브라우저 목업 테스트)**
- 공장·제조 (MANUFACTURING): 주소검색 2건 반환 → 건축물대장 `공장(제조시설)` 4820.5㎡ 정상 표시 → 설비 3개 선택 → 접수번호 `TAI-2026-MFG-00142` 정상
- 건설현장 (CONSTRUCTION): 주소검색 2건 반환 → 건축물대장 `가설건축물(현장사무소)` 148.5㎡ 정상 표시 → 설비 3개 선택 → 접수번호 `TAI-2026-CON-00089` 정상

---

## 4. F-FEAT-001 Feature Flag 시스템 (커밋 e34fe56)

### feature-flags.js 신규 생성
**파일**: `tadmin/full-version/assets/js/feature-flags.js`

```javascript
// 공개 API
TAIFeatureFlags.load(sector, plan)  // GET /feature-flags/?sector=&plan=
TAIFeatureFlags.apply()             // [data-feature] 요소 제어
TAIFeatureFlags.isOpen(code)        // boolean
TAIFeatureFlags.setFlags(flags)     // 테스트/오프라인용 직접 주입
```

**블록 제어 로직**
- `open`: `d-none` 제거, lock overlay 제거
- `locked`: lock overlay 삽입 (required_plan + 업그레이드 버튼 → `my-contract.html`)
- `hidden`: `d-none` 추가 (섹터 불일치)
- API 실패 폴백: 모두 표시 (숨기지 않음, 낙관적 허용)

**자동 초기화**
- DOMContentLoaded 시 `sessionStorage.active_sector/plan` → `localStorage.contract_sector/plan_code` 순으로 읽어 자동 `load()` 실행

### menu-tadmin.js v2.6.0 — data-feature 속성 적용

**전체 메뉴 feature code 매핑**

| 메뉴 그룹 | 그룹 feature | 주요 서브 feature |
|-----------|-------------|------------------|
| 대시보드 | `DASHBOARD` | — |
| 시설관리 | `FACILITY_BASIC` | 공정→`FACILITY_PROCESS`, 설비→`FACILITY_EQUIPMENT` |
| 작업자관리 | `WORK_ASSIGN` | 전체 `WORK_ASSIGN` |
| 작업관리 | `WORK_TBM` | TBM→`WORK_TBM`, 위험성평가→`WORK_RISK` |
| TBM관리 | `WORK_TBM` | 전체 `WORK_TBM` |
| 건설관리 | `CONSTRUCTION_SITE` | PTW→`CONSTRUCTION_PTW`, 공정→`CONSTRUCTION_PROCESS`, 출입→`CONSTRUCTION_ENTRY`, 안전점검→`CONSTRUCTION_SAFETY` |
| 교육관리 | `EDUCATION_BASIC` | 전체 `EDUCATION_BASIC` |
| 위험관리 | `WORK_RISK` | 전체 `WORK_RISK` |
| 문서관리 | `REPORT_FORM` | 신고관리→`REPORT_AUTO` |
| FREE 법령진단 | `LEGAL_DIAGNOSIS_BASIC` | — |

**renderMenuItem 수정사항**
```javascript
// 그룹 li에 data-feature 출력
'<li class="menu-item"' + (def.feature ? ' data-feature="'+def.feature+'"' : '') + '>'

// 서브 li에도 개별 data-feature 출력
'<li class="menu-item"' + (s.feature ? ' data-feature="'+s.feature+'"' : '') + '>'

// buildMenu() 완료 후 자동 apply()
if (window.TAIFeatureFlags) window.TAIFeatureFlags.apply();
```

---

## 5. 오늘 세션 커밋 요약

| 커밋 | 내용 |
|------|------|
| `ae6095c` | 건설진단 프론트 재설계 4개 파일 |
| `baca744` | _redirects 경로 수정 (1차) |
| `104f8ad` | tadmin index.html auth-guard 제거 + _redirects tadmin→dashboard |
| `929788f` | cache-bust 20260401-v2, home/index.html doHomeLogout + reload |
| `765d232` | request/v1 주소검색+건축물대장 자동입력 |
| `be6f933` | request/v2/v3 주소검색+건축물대장 적용 |
| `e34fe56` | feature-flags.js 신규 + menu-tadmin.js v2.6.0 data-feature |

---

## 6. 다음 세션 PENDING

| 항목 | 비고 |
|------|------|
| `POST /diagnosis/request-quote` 백엔드 구현 | 프론트 완료, API만 없음 |
| Cloudflare Zero Trust Access 설정 | taieng.co.kr hetto@kakao.com only |
| **공지예외주장 제출 (2026-04-28 필수)** | patent.go.kr |
| 건설 섹터 알고리즘 백엔드 | 하도급 포함, 150억/120억 분기 |
| 12개 법령 수집 (data.go.kr) | 근로기준법 등 |
| feature-flags API 백엔드 구현 | `/feature-flags/?sector=&plan=` |
| home/index.html 최신화 | 현재 site/full-version/html/home/index.html은 구버전 스타일 — 신버전으로 교체 필요 |
