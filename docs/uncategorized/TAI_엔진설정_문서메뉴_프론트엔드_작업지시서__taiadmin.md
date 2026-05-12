# TAI Safe 엔진설정 > 문서 메뉴 — 프론트엔드 작업지시서

> 작성일: 2026-04-02  
> 대상: Cursor (프론트엔드 창)  
> 참고: Vuexy HTML Bootstrap 5 기반

---

## 0. 작업 전 필수 확인

```
1. system_codes 전역변수 확인
   FORM_TYPE: LEGAL / STANDARD / FREE
   FORM_CATEGORY: REPORT / DOCUMENT / NOTIFY / APPOINT / INSPECT
   SUBMIT_METHOD: ONLINE / FAX / MAIL / VISIT / KEEP

2. 기존 참고 페이지: 가격설정(price-setting.html), 법령진단 관련 페이지

3. 글로벌 규칙:
   - 리스트 첫 컬럼: 체크박스(toggleAll)
   - 두 번째 컬럼: 행번호 No. = (currentPage-1)*pageSize+idx+1
   - API base: https://api.taieng.co.kr
```

---

## 1. 신규 파일 생성

### 1.1 HTML 파일

**파일명:** `engine-document.html`  
**위치:** 기존 engine-* 파일들과 동일 경로

#### 전체 구조

```html
<!-- 상단 보관현황 요약 카드 -->
<div class="row mb-4" id="docSummaryCards">
  <!-- 전체 보관 의무 / 보관 중 / 만료임박 / 만료초과 -->
</div>

<!-- 탭 -->
<ul class="nav nav-tabs" id="docTabs">
  <li><a data-bs-toggle="tab" href="#tab-legal">법정서식</a></li>
  <li><a data-bs-toggle="tab" href="#tab-standard">TAI표준서식</a></li>
  <li><a data-bs-toggle="tab" href="#tab-free">자유서식가이드</a></li>
</ul>

<div class="tab-content">
  <!-- 탭1: 법정서식 -->
  <div id="tab-legal">...</div>
  <!-- 탭2: TAI표준서식 -->
  <div id="tab-standard">...</div>
  <!-- 탭3: 자유서식가이드 -->
  <div id="tab-free">...</div>
</div>

<!-- 서식 상세 모달 -->
<div class="modal" id="formDetailModal">...</div>
```

---

### 1.2 탭1 — 법정서식 테이블

```html
<table class="table">
  <thead>
    <tr>
      <th><input type="checkbox" id="toggleAll-legal"></th> <!-- 체크박스 -->
      <th>No.</th>
      <th>서식코드</th>
      <th>서식명</th>
      <th>관련법령</th>
      <th>제출처</th>
      <th>제출방법</th> <!-- 뱃지 표시 -->
      <th>제출기한</th>
      <th>과태료</th>
      <th>관리</th>
    </tr>
  </thead>
  <tbody id="legalFormList"></tbody>
</table>
```

#### 제출방법 뱃지 색상 규칙

```javascript
const submitMethodBadge = {
  'ONLINE': '<span class="badge bg-success">전자제출</span>',
  'FAX':    '<span class="badge bg-primary">팩스</span>',
  'MAIL':   '<span class="badge bg-warning">우편</span>',
  'VISIT':  '<span class="badge bg-danger">방문</span>',
  'KEEP':   '<span class="badge bg-secondary">보관용</span>'
};
```

#### 관리 버튼

```html
<!-- 전자제출 가능한 서식 -->
<a href="{submit_url}" target="_blank" class="btn btn-sm btn-success">전자제출</a>
<!-- 다운로드 -->
<button class="btn btn-sm btn-outline-primary" onclick="downloadForm('{form_code}')">다운로드</button>
<!-- 상세 -->
<button class="btn btn-sm btn-outline-secondary" onclick="showFormDetail('{form_code}')">상세</button>
```

---

### 1.3 탭2 — TAI표준서식 테이블

```html
<table class="table">
  <thead>
    <tr>
      <th><input type="checkbox" id="toggleAll-standard"></th>
      <th>No.</th>
      <th>서식코드</th>
      <th>서식명</th>
      <th>관련법령</th>
      <th>보관기간</th>
      <th>사용시점</th>
      <th>관리</th>
    </tr>
  </thead>
  <tbody id="standardFormList"></tbody>
</table>
```

#### 보관기간 표시

```javascript
// retention_years → 표시
function retentionLabel(years) {
  if (!years) return '-';
  const colors = { 1: 'bg-secondary', 2: 'bg-info', 3: 'bg-primary', 5: 'bg-warning', 10: 'bg-danger' };
  const color = colors[years] || 'bg-secondary';
  return `<span class="badge ${color}">${years}년 보관</span>`;
}
```

#### 관리 버튼

```html
<button class="btn btn-sm btn-success" onclick="autoFillForm('{form_code}')">자동작성</button>
<button class="btn btn-sm btn-outline-primary" onclick="downloadForm('{form_code}')">다운로드</button>
<button class="btn btn-sm btn-outline-secondary" onclick="showFormDetail('{form_code}')">상세</button>
```

---

### 1.4 탭3 — 자유서식가이드 테이블

```html
<table class="table">
  <thead>
    <tr>
      <th><input type="checkbox" id="toggleAll-free"></th>
      <th>No.</th>
      <th>의무명</th>
      <th>관련법령</th>
      <th>보관기간</th>
      <th>필수기재항목</th>
      <th>TAI표준서식</th>
      <th>관리</th>
    </tr>
  </thead>
  <tbody id="freeFormList"></tbody>
</table>
```

---

### 1.5 서식 상세 모달

```html
<div class="modal fade" id="formDetailModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="formDetailTitle"></h5>
        <span id="formDetailTypeBadge"></span>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <table class="table table-bordered">
          <tr><th width="130">법적 근거</th><td id="detailLegalBasis"></td></tr>
          <tr><th>사용 시점</th><td id="detailUseCase"></td></tr>
          <tr><th>제출처</th><td id="detailSubmitAgency"></td></tr>
          <tr><th>제출방법</th><td id="detailSubmitMethod"></td></tr>
          <tr><th>제출기한</th><td id="detailSubmitTiming"></td></tr>
          <tr><th>보관기간</th><td id="detailRetention"></td></tr>
          <tr><th>과태료</th><td id="detailPenalty"></td></tr>
        </table>

        <!-- 필수 기재항목 -->
        <div class="mt-3">
          <h6>필수 기재항목</h6>
          <ul id="detailRequiredFields"></ul>
        </div>
      </div>
      <div class="modal-footer">
        <button id="btnDetailDownload" class="btn btn-outline-primary">서식 다운로드</button>
        <button id="btnDetailAutoFill" class="btn btn-success d-none">자동작성</button>
        <a id="btnDetailSubmitUrl" href="#" target="_blank" class="btn btn-success d-none">전자제출 바로가기</a>
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
      </div>
    </div>
  </div>
</div>
```

---

## 2. JS 파일 생성

**파일명:** `engine-document.page.js`

### 2.1 전체 함수 목록

```javascript
// 초기화
async function initPage()          // 페이지 로드 시 실행
async function loadSummaryCards()  // 상단 요약 카드 로드

// 탭별 데이터 로드
async function loadLegalForms()    // 법정서식 목록
async function loadStandardForms() // TAI표준서식 목록
async function loadFreeForms()     // 자유서식가이드 목록

// 렌더링
function renderLegalForm(item, idx)    // 법정서식 행 렌더링
function renderStandardForm(item, idx) // 표준서식 행 렌더링
function renderFreeForm(item, idx)     // 자유서식 행 렌더링

// 모달
async function showFormDetail(formCode) // 상세 모달 열기
function renderFormDetailModal(data)    // 모달 내용 렌더링

// 액션
function downloadForm(formCode)   // 서식 다운로드
function autoFillForm(formCode)   // 자동작성 (Phase 2)

// 유틸
function submitMethodBadge(method)  // 제출방법 뱃지
function retentionBadge(years)      // 보관기간 뱃지
function formTypeBadge(type)        // 서식유형 뱃지
```

### 2.2 API 호출 패턴

```javascript
// 법정서식 목록
const res = await fetch(`${API_BASE}/engine/forms?form_type=LEGAL&sector=BUILDING`);

// TAI표준서식 목록
const res = await fetch(`${API_BASE}/engine/forms?form_type=STANDARD&sector=BUILDING`);

// 자유서식가이드 목록
const res = await fetch(`${API_BASE}/engine/forms?form_type=FREE&sector=BUILDING`);

// 서식 상세
const res = await fetch(`${API_BASE}/engine/forms/${formCode}`);
```

### 2.3 페이지 초기화 코드 패턴

```javascript
document.addEventListener('DOMContentLoaded', async () => {
  await initPage();
});

async function initPage() {
  await loadSummaryCards();
  await loadLegalForms(); // 첫 탭 기본 로드

  // 탭 전환 시 지연 로드
  document.getElementById('tab-standard-btn').addEventListener('shown.bs.tab', async () => {
    await loadStandardForms();
  });
  document.getElementById('tab-free-btn').addEventListener('shown.bs.tab', async () => {
    await loadFreeForms();
  });
}
```

---

## 3. aside 메뉴 추가

**모든 admin 페이지의 aside 메뉴**에 '문서' 항목 추가:

```html
<!-- 엔진설정 메뉴 그룹 내 추가 -->
<li class="menu-item">
  <a href="engine-document.html" class="menu-link">
    <i class="menu-icon tf-icons bx bx-file"></i>
    <div data-i18n="문서">문서</div>
  </a>
</li>
```

**위치:** 엔진설정 그룹 내 마지막 항목으로 추가

---

## 4. 완성 기준 체크리스트

```
□ engine-document.html 생성
□ engine-document.page.js 생성
□ 탭 3개 정상 전환
□ 법정서식 리스트 API 연동
□ TAI표준서식 리스트 API 연동
□ 자유서식가이드 리스트 API 연동
□ 제출방법 뱃지 색상 구분
□ 보관기간 뱃지 년수별 색상 구분
□ 서식 상세 모달 정상 동작
□ 전자제출 URL 있을 때 버튼 표시
□ aside 메뉴 추가 (전체 admin 페이지)
□ 첫 컬럼 체크박스 (toggleAll)
□ 두 번째 컬럼 행번호 (No.)
□ 빈 데이터 시 "데이터가 없습니다" 표시
```
