# TAI Cursor 작업지시서 — 공정 수동 등록 페이지 (프론트)

> 우선순위: 🔴 긴급  
> 작성일: 2026-03-31  
> 레포: taiengineering/tai-admin  
> 대상 파일: **신규** `site/full-version/html/tadmin/process-manage.html`

---

## 개요

SaaS 고객이 자신의 시설에 어떤 공정이 있는지 등록하는 페이지입니다.  
KCSC 표준 공정 검색으로 추가하거나, DB에 없는 공정은 직접 입력합니다.

**기존 파일 참고:**
```
site/full-version/html/tadmin/factory-list.html  ← 레이아웃 참고
```

**공통 규칙 (반드시 준수):**
- 로그인 체크: `if (!localStorage.getItem('access_token')) { location.href = '../auth-login-cover.html'; }`
- API 베이스: `const BASE_URL = 'https://api.taieng.co.kr';`
- Global Rule: **1번 컨럼 = 체크박스(toggleAll), 2번 = No.**
- Vuexy Bootstrap 5 기반

---

## 페이지 전체 구조

```
process-manage.html
├── 상단: 시설 선택 + 요약 카드
├── 중단: 공정 검색/등록 영역
└── 하단: 등록된 공정 목록 테이블
```

---

## 1. 상단: 시설 선택 + 요약

```html
<!-- 시설 선택 -->
<div class="d-flex align-items-center gap-3 mb-4">
  <label class="fw-semibold mb-0">시설</label>
  <select class="form-select w-auto" id="factorySelect" onchange="loadProcesses()">
    <option value="">-- 시설 선택 --</option>
  </select>
</div>

<!-- 요약 카드 3개 -->
<div class="row g-3 mb-4" id="statCards" style="display:none">
  <div class="col-md-4">
    <div class="card">
      <div class="card-body py-3 text-center">
        <div class="text-muted small">전체 공정</div>
        <h3 class="mb-0" id="statTotal">-</h3>
      </div>
    </div>
  </div>
  <div class="col-md-4">
    <div class="card border-primary">
      <div class="card-body py-3 text-center">
        <div class="text-muted small">KCSC 표준</div>
        <h3 class="text-primary mb-0" id="statKcsc">-</h3>
      </div>
    </div>
  </div>
  <div class="col-md-4">
    <div class="card border-warning">
      <div class="card-body py-3 text-center">
        <div class="text-muted small">수동 등록</div>
        <h3 class="text-warning mb-0" id="statManual">-</h3>
      </div>
    </div>
  </div>
</div>
```

---

## 2. 중단: 공정 추가 영역

### 2-1. 탭 선택 (KCSC 검색 vs 직접 입력)
```html
<ul class="nav nav-tabs mb-3" id="addTab">
  <li class="nav-item">
    <button class="nav-link active" id="tab-search" onclick="switchTab('search')">
      <i class="bx bx-search me-1"></i>KCSC 공정 검색
    </button>
  </li>
  <li class="nav-item">
    <button class="nav-link" id="tab-manual" onclick="switchTab('manual')">
      <i class="bx bx-edit me-1"></i>직접 입력
    </button>
  </li>
</ul>
```

### 2-2. KCSC 검색 판널
```html
<div id="panel-search">
  <div class="input-group mb-3" style="max-width:500px">
    <input type="text" class="form-control" id="searchInput"
      placeholder="공종명 검색 (예: 철근, 목공)" onkeyup="onSearchKey(event)">
    <button class="btn btn-outline-primary" onclick="searchProcess()">검색</button>
  </div>
  <div id="searchResults" class="d-none">
    <table class="table table-sm table-hover">
      <thead class="table-light">
        <tr><th>공종코드</th><th>공종명</th><th>분류</th><th>등록</th></tr>
      </thead>
      <tbody id="searchBody"></tbody>
    </table>
  </div>
</div>
```

### 2-3. 직접 입력 판널 (수동 등록 패널)
```html
<div id="panel-manual" class="d-none">
  <div class="card">
    <div class="card-body">
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">공정명 <span class="text-danger">*</span></label>
          <input type="text" class="form-control" id="manualProcessName"
            placeholder="예: 스테인레스 도장 공정">
        </div>
        <div class="col-md-3">
          <label class="form-label">대분류</label>
          <input type="text" class="form-control" id="manualLv1"
            placeholder="예: 표면처리">
        </div>
        <div class="col-md-3">
          <label class="form-label">중분류</label>
          <input type="text" class="form-control" id="manualLv2"
            placeholder="예: 금속 표면">
        </div>
        <div class="col-12">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" id="manualIsPrimary">
            <label class="form-check-label">주요 공정으로 설정</label>
          </div>
        </div>
        <div class="col-12">
          <button class="btn btn-warning" onclick="addManualProcess()">
            <i class="bx bx-plus me-1"></i>직접 등록
          </button>
        </div>
      </div>
    </div>
  </div>
</div>
```

---

## 3. 하단: 등록된 공정 목록 테이블

```html
<table class="table table-hover">
  <thead class="table-light">
    <tr>
      <th style="width:40px"><input type="checkbox" id="checkAll" onclick="toggleAll(this)"></th>
      <th style="width:50px">No.</th>
      <th>공정명</th>
      <th>분류</th>
      <th>출처</th>
      <th>주요공정</th>
      <th>관리</th>
    </tr>
  </thead>
  <tbody id="processTableBody"></tbody>
</table>
```

### 행 렌더링 (JS)
```javascript
function renderProcessRow(p, index) {
  const sourceBadge = p.is_manual
    ? '<span class="badge bg-warning">직접등록</span>'
    : '<span class="badge bg-primary">KCSC</span>';
  const primaryBadge = p.is_primary
    ? '<span class="badge bg-success ms-1">주요</span>' : '';

  return `
  <tr data-id="${p.id}">
    <td><input type="checkbox" class="form-check-input row-check" value="${p.id}"></td>
    <td class="text-muted">${index + 1}</td>
    <td>
      <span class="fw-semibold">${p.display_name}</span>${primaryBadge}
      ${p.process_path ? `<br><small class="text-muted">${p.process_path}</small>` : ''}
    </td>
    <td class="text-muted small">${p.process_lv1 || '-'}</td>
    <td>${sourceBadge}</td>
    <td>
      ${p.is_primary
        ? '<span class="text-success"><i class="bx bx-check-circle"></i></span>'
        : `<button class="btn btn-xs btn-outline-secondary" onclick="setPrimary('${p.id}')">\uc8fc요설정</button>`}
    </td>
    <td>
      ${p.is_manual
        ? `<button class="btn btn-xs btn-outline-danger" onclick="deleteProcess('${p.id}')"><i class="bx bx-trash"></i></button>`
        : '<span class="text-muted small">-</span>'}
    </td>
  </tr>`;
}
```

---

## 4. 핵심 JS 함수

```javascript
const BASE_URL = 'https://api.taieng.co.kr';

// 공정 목록 로드
async function loadProcesses() {
  const factoryId = document.getElementById('factorySelect').value;
  if (!factoryId) return;

  const data = await apiCall('GET', `/factory-process/${factoryId}/processes`);
  const list = data.data || [];

  // 요약 카드
  const total  = list.length;
  const kcsc   = list.filter(p => !p.is_manual).length;
  const manual = list.filter(p => p.is_manual).length;
  document.getElementById('statTotal').textContent  = total;
  document.getElementById('statKcsc').textContent   = kcsc;
  document.getElementById('statManual').textContent = manual;
  document.getElementById('statCards').style.display = '';

  // 테이블 렌더
  const tbody = document.getElementById('processTableBody');
  tbody.innerHTML = list.map((p, i) => renderProcessRow(p, i)).join('');
}

// KCSC 검색
async function searchProcess() {
  const q = document.getElementById('searchInput').value.trim();
  if (!q) return;
  const data = await apiCall('GET', `/factory-process/search?q=${encodeURIComponent(q)}&size=20`);
  renderSearchResults(data.data || []);
}

function onSearchKey(e) {
  if (e.key === 'Enter') searchProcess();
}

function renderSearchResults(results) {
  const tbody = document.getElementById('searchBody');
  tbody.innerHTML = results.map(r => `
    <tr>
      <td class="text-muted small">${r.kcs_code || r.process_id || '-'}</td>
      <td class="fw-semibold">${r.title || r.process_name || '-'}</td>
      <td class="text-muted small">${r.level || '-'}</td>
      <td>
        <button class="btn btn-xs btn-primary"
          onclick="addKcscProcess('${r.id}', '${(r.title||'').replace(/'/g,"\\'")}')">+ 등록</button>
      </td>
    </tr>`).join('');
  document.getElementById('searchResults').classList.remove('d-none');
}

// KCSC 공정 등록
async function addKcscProcess(workMasterId, processName) {
  const factoryId = document.getElementById('factorySelect').value;
  if (!factoryId) { showToast('warning', '시설을 선택해주세요.'); return; }
  await apiCall('POST', `/factory-process/${factoryId}/processes`, {
    process_id: workMasterId,
    source: 'DB'
  });
  showToast('success', `"${processName}" 공정이 등록되었습니다.`);
  loadProcesses();
}

// 직접 등록
async function addManualProcess() {
  const factoryId = document.getElementById('factorySelect').value;
  const name      = document.getElementById('manualProcessName').value.trim();
  const lv1       = document.getElementById('manualLv1').value.trim();
  const lv2       = document.getElementById('manualLv2').value.trim();
  const isPrimary = document.getElementById('manualIsPrimary').checked;

  if (!factoryId) { showToast('warning', '시설을 선택해주세요.'); return; }
  if (!name) { showToast('warning', '공정명을 입력해주세요.'); return; }

  await apiCall('POST', `/factory-process/${factoryId}/processes`, {
    source: 'MANUAL',
    process_name_manual: name,
    process_lv1: lv1 || '기타',
    process_lv2: lv2 || null,
    is_primary: isPrimary
  });
  showToast('success', `"${name}" 공정이 등록되었습니다.`);
  document.getElementById('manualProcessName').value = '';
  loadProcesses();
}

// 직접 등록 공정 삭제
async function deleteProcess(id) {
  if (!confirm('이 공정을 삭제할까요?')) return;
  const factoryId = document.getElementById('factorySelect').value;
  await apiCall('DELETE', `/factory-process/${factoryId}/processes/${id}`);
  showToast('success', '삭제되었습니다.');
  loadProcesses();
}

// 탭 전환
function switchTab(tab) {
  document.getElementById('panel-search').classList.toggle('d-none', tab !== 'search');
  document.getElementById('panel-manual').classList.toggle('d-none', tab !== 'manual');
  document.querySelectorAll('#addTab .nav-link').forEach(el => el.classList.remove('active'));
  document.getElementById(`tab-${tab}`).classList.add('active');
}
```

---

## 5. 페이지 헤더
```html
<h4 class="mb-1">공정 관리</h4>
<p class="text-muted small mb-0">시설의 공정을 등록합니다. KCSC 표준 공종 검색 또는 직접 입력으로 추가할 수 있습니다.</p>
```

---

## 완료 체크리스트

```
□ process-manage.html 파일 생성 (Vuexy tadmin 레이아웃)
□ 시설 선택 드롭다운 (GET /factories)
□ 요약 카드 3개 (전체/KCSC/직접)
□ KCSC 검색 탭 — 입력 후 검색 버튼 or Enter
□ 직접 입력 탭 — 공정명/대분류/중분류/주요공정체크
□ 목록 테이블: 1=체크박스, 2=No., 공정명, 외 치 배지·KCSC배지, 삭제(직접등록만)
□ GitHub push
```
