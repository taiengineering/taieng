# TAI Cursor 작업지시서 — 법정점검 기준일 설정 페이지 (tadmin)

> 우선순위: 🔴 긴급  
> 작성일: 2026-03-31  
> 레포: taiengineering/tai-admin  
> 대상 파일: **신규 생성**

---

## 개요

법령진단으로 자동 생성된 점검세트의 **기준일을 SaaS 사용자가 직접 입력**하는 tadmin 페이지를 생성합니다.  
괁호 안에 업체마다 다른 기준일 (마지막 점검일, 사용승인일, 설치일 등)을 입력하권 합니다.  
법령이 요구하는 **기준점 안내 문구**를 표시하여 사용자가 어떤 날짜를 넣어야 하는지 알 수 있게 합니다.

**파일 위치:** `site/full-version/html/tadmin/inspection-anchor.html`

---

## 기존 파일 참고

```
site/full-version/html/tadmin/factory-list.html  ← 전체 레이아웃 참고
site/full-version/html/tadmin/index.html         ← 상단 카드 스타일 참고
```

**공통 규칙 (반드시 준수):**
- 로그인 체크: `if (!localStorage.getItem('access_token')) { location.href = '../auth-login-cover.html'; }`
- API 베이스: `const BASE_URL = 'https://api.taieng.co.kr';`
- apiCall() 함수: `assets/js/tai/api.js` 가져와 사용
- 목록 체크박스 Global Rule: **1번 컨럼 = 체크박스(toggleAll), 2번 = No.**
- Vuexy Bootstrap 5 기반

---

## 페이지 전체 구조

```
inspection-anchor.html
├── 상단: 시설 선택 + 진행상태 요약
└── 하단: 목록 테이블 (점검 세트별 기준일 입력)
```

---

## 1. 상단 요약 영역

### 1-1. 시설 선택 드롭다운 (필수)
```html
<select class="form-select w-auto" id="factorySelect" onchange="loadInspectionSets()">
  <option value="">-- 시설 선택 --</option>
</select>
```
- 페이지 로드 시 `GET /factories` 호출하여 드롭다운 자동 포함

### 1-2. 진행상태 낔 카드 (시설 선택 후 표시)
```html
<div class="row g-3 mb-4" id="statCards" style="display:none">
  <div class="col-6 col-md-3">
    <div class="card border-danger">
      <div class="card-body py-3 text-center">
        <div class="text-muted small">미설정</div>
        <h3 class="text-danger mb-0" id="statUnset">-</h3>
        <small class="text-muted">기준일 입력 필요</small>
      </div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card border-success">
      <div class="card-body py-3 text-center">
        <div class="text-muted small">설정 완료</div>
        <h3 class="text-success mb-0" id="statDone">-</h3>
      </div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card border-warning">
      <div class="card-body py-3 text-center">
        <div class="text-muted small">임박 (30일)</div>
        <h3 class="text-warning mb-0" id="statSoon">-</h3>
      </div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card border-danger">
      <div class="card-body py-3 text-center">
        <div class="text-muted small">기간 초과</div>
        <h3 class="text-danger mb-0" id="statOver">-</h3>
      </div>
    </div>
  </div>
</div>
```

### 1-3. 필터 탭 + 일괄저장 버튼
```html
<div class="d-flex align-items-center gap-2 mb-3">
  <!-- 탭 필터 -->
  <ul class="nav nav-pills" id="filterTab">
    <li class="nav-item"><button class="nav-link active" data-filter="all" onclick="applyFilter('all')">  전체</button></li>
    <li class="nav-item"><button class="nav-link" data-filter="unset" onclick="applyFilter('unset')">  미설정</button></li>
    <li class="nav-item"><button class="nav-link" data-filter="done" onclick="applyFilter('done')">  설정완료</button></li>
    <li class="nav-item"><button class="nav-link" data-filter="soon" onclick="applyFilter('soon')">  임박</button></li>
    <li class="nav-item"><button class="nav-link" data-filter="over" onclick="applyFilter('over')">  초과</button></li>
  </ul>
  <!-- 일괄저장 버튼 (선택된 항목 있을 때 활성화) -->
  <button class="btn btn-primary btn-sm ms-auto" id="btnBulkSave" onclick="bulkSave()" disabled>
    일괄 저장
  </button>
</div>
```

---

## 2. 목록 테이블

### 2-1. 테이블 구조
```html
<table class="table table-hover mb-0">
  <thead class="table-light">
    <tr>
      <th style="width:40px"><input type="checkbox" id="checkAll" onclick="toggleAll(this)"></th>  <!-- 1번 -->
      <th style="width:50px">No.</th>  <!-- 2번 -->
      <th>법령명</th>
      <th>조문</th>
      <th>점검주기</th>
      <th>평가단위 안내</th>  <!-- 핵심: cycle_base_guide -->
      <th>기준일 입력</th>
      <th>직전점검일 (선택)</th>
      <th>다음점검 예정</th>  <!-- 자동 계산 -->
      <th>상태</th>
    </tr>
  </thead>
  <tbody id="tableBody"></tbody>
</table>
```

### 2-2. 행 렌더링 (JS)
```javascript
function renderRow(item, index) {
  // 상태 판정
  const today = new Date();
  const nextDate = item.next_planned_date ? new Date(item.next_planned_date) : null;
  const daysLeft = nextDate ? Math.ceil((nextDate - today) / 86400000) : null;

  let statusBadge = '';
  let filterClass = '';
  if (!item.anchor_confirmed || !item.schedule_anchor_date) {
    statusBadge = '<span class="badge bg-danger">미설정</span>';
    filterClass = 'unset';
  } else if (daysLeft !== null && daysLeft < 0) {
    statusBadge = '<span class="badge bg-danger">기간초과</span>';
    filterClass = 'over';
  } else if (daysLeft !== null && daysLeft <= 30) {
    statusBadge = `<span class="badge bg-warning">D-${daysLeft}</span>`;
    filterClass = 'soon';
  } else {
    statusBadge = '<span class="badge bg-success">설정완료</span>';
    filterClass = 'done';
  }

  // 주기 표시
  const unitLabel = {
    'year': '년', 'month': '개월',
    'half_year': '반기', 'quarter': '분기'
  };
  const cycleText = `${item.cycle_value}${unitLabel[item.cycle_unit] || ''}마다`;

  return `
  <tr data-id="${item.id}" data-filter="${filterClass}">
    <td><input type="checkbox" class="form-check-input row-check" value="${item.id}"></td>
    <td class="text-muted">${index + 1}</td>
    <td class="fw-semibold">${item.law_name || '-'}</td>
    <td class="text-muted small">${item.law_article || '-'}</td>
    <td>${cycleText}</td>
    <!-- 핵심: 기준점 안내 -->
    <td>
      <span class="text-info small">
        <i class="ti tabler-info-circle me-1"></i>${item.cycle_base_guide || '-'}
      </span>
    </td>
    <!-- 기준일 입력 (date input) -->
    <td>
      <input type="date"
        class="form-control form-control-sm anchor-input"
        style="width:150px"
        data-id="${item.id}"
        data-cycle-value="${item.cycle_value}"
        data-cycle-unit="${item.cycle_unit}"
        value="${item.schedule_anchor_date || ''}"
        onchange="onAnchorChange(this)">
    </td>
    <!-- 직전 점검일 (선택) -->
    <td>
      <input type="date"
        class="form-control form-control-sm last-input"
        style="width:150px"
        data-id="${item.id}"
        value="${item.last_inspection_date || ''}">
    </td>
    <!-- 다음 점검 예정 (자동 계산) -->
    <td class="next-date text-muted" id="next-${item.id}">
      ${item.next_planned_date || '-'}
    </td>
    <td>${statusBadge}</td>
  </tr>`;
}
```

### 2-3. 기준일 입력 시 다음점검일 실시간 계산 (JS)
```javascript
function onAnchorChange(input) {
  const id = input.dataset.id;
  const cycleValue = parseInt(input.dataset.cycleValue) || 1;
  const cycleUnit  = input.dataset.cycleUnit || 'year';
  const anchorDate = input.value;
  if (!anchorDate) return;

  // 다음 점검일 계산
  const d = new Date(anchorDate);
  if (cycleUnit === 'year')       d.setFullYear(d.getFullYear() + cycleValue);
  else if (cycleUnit === 'month') d.setMonth(d.getMonth() + cycleValue);
  else if (cycleUnit === 'half_year') d.setMonth(d.getMonth() + 6);
  else if (cycleUnit === 'quarter')   d.setMonth(d.getMonth() + 3);

  const nextStr = d.toISOString().split('T')[0];
  document.getElementById(`next-${id}`).textContent = nextStr;

  // 일괄저장 버튼 활성화
  document.getElementById('btnBulkSave').disabled = false;
}
```

---

## 3. 저장 로직 (JS)

### 3-1. 단건 저장
```javascript
async function saveSingle(id) {
  const anchorInput = document.querySelector(`.anchor-input[data-id="${id}"]`);
  const lastInput   = document.querySelector(`.last-input[data-id="${id}"]`);
  const body = {
    schedule_anchor_date: anchorInput.value,
    last_inspection_date: lastInput.value || undefined
  };
  if (!body.schedule_anchor_date) {
    showToast('warning', '기준일을 입력해주세요.');
    return;
  }
  await apiCall('PATCH', `/inspection-sets/${id}/anchor`, body);
  showToast('success', '저장되었습니다.');
  loadInspectionSets(); // 목록 재로드
}
```

### 3-2. 일괄 저장 (체크된 항목 전체)
```javascript
async function bulkSave() {
  const checked = document.querySelectorAll('.row-check:checked');
  if (!checked.length) {
    showToast('warning', '저장할 항목을 선택해주세요.');
    return;
  }
  const items = [];
  checked.forEach(cb => {
    const id = cb.value;
    const anchor = document.querySelector(`.anchor-input[data-id="${id}"]`)?.value;
    const last   = document.querySelector(`.last-input[data-id="${id}"]`)?.value;
    if (anchor) items.push({ id, schedule_anchor_date: anchor, last_inspection_date: last || undefined });
  });
  if (!items.length) { showToast('warning', '기준일이 입력된 항목이 없습니다.'); return; }

  const res = await apiCall('PATCH', '/inspection-sets/anchor/bulk', { items });
  showToast('success', `${res.data.updated}건 저장되었습니다.`);
  loadInspectionSets();
}
```

---

## 4. API 명세 (사용)

```
# 시설 목록
GET  /factories

# 점검세트 목록
GET  /inspection-sets?factory_id={uuid}&source=LEGAL_ENGINE&page=1&size=100
→ 응답 필드: id, law_name, law_article, cycle_value, cycle_unit,
              cycle_base_type, cycle_base_guide,
              schedule_anchor_date, last_inspection_date,
              next_planned_date, anchor_confirmed

# 단건 저장
PATCH /inspection-sets/{id}/anchor
body: { schedule_anchor_date, last_inspection_date? }

# 일괄 저장
PATCH /inspection-sets/anchor/bulk
body: { items: [{id, schedule_anchor_date, last_inspection_date?}] }
```

---

## 5. 페이지 헤더

```html
<h4 class="mb-1">법정점검 기준일 설정</h4>
<p class="text-muted small mb-0">
  법령이 요구하는 기준일을 입력하면 다음 점검 예정일이 자동 계산됩니다.
</p>
```

---

## 완료 체크리스트

```
□ inspection-anchor.html 파일 생성 (Vuexy tadmin 레이아웃)
□ 시설 선택 드롭다운 (GET /factories)
□ 시설 선택 후 점검세트 목록 로드
□ 요약 카드 4개 (미설정/설정완료/임박/초과)
□ Global Rule: 1번=체크박스(toggleAll), 2번=No.
□ 목록에 cycle_base_guide 안내문구 표시
□ date input 입력 시 next_planned_date 실시간 계산으로 표시
□ 관부 상태 배지 (미설정=빨강/완료=초록/임박=주황/초과=빨강)
□ 필터 탭 (전체/미설정/완료/임박/초과)
□ 단건 저장 동작 (PATCH /inspection-sets/{id}/anchor)
□ 일괄 저장 버튼 동작 (PATCH /inspection-sets/anchor/bulk)
□ GitHub push
```
