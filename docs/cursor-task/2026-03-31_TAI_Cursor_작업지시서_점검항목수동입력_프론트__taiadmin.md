# TAI Cursor 작업지시서 — 점검항목 수동 입력 페이지 (프론트)

> 우선순위: 🔴 긴급  
> 작성일: 2026-03-31  
> 레포: taiengineering/tai-admin  
> 대상 파일: **신규** `site/full-version/html/tadmin/inspection-custom.html`

---

## 개요

SaaS 고객이 법령엔진 외에 자체 점검항목을 직접 정의하고 점검 세트로 등록하는 페이지입니다.  
예: 직접 만든 찬반하목 체크리스트, 설비 전용 점검표, 일일 안전점검표

**기존 파일 참고:**
```
site/full-version/html/tadmin/factory-list.html  ← 레이아웃
site/full-version/html/tadmin/inspection-anchor.html ← 점검 UI 패턴
```

**공통 규칙 (반드시 준수):**
- 로그인 체크, BASE_URL, Vuexy Bootstrap 5
- Global Rule: **1번=체크박스(toggleAll), 2번=No.**

---

## 페이지 전체 구조

```
inspection-custom.html
├── 좌측: 점검 템플릿 목록 패널 (1/3 너비)
└── 우측: 템플릿 상세 / 신규 생성 판널 (2/3 너비)
```

---

## 1. 좌측: 템플릿 목록 패널

```html
<div class="col-md-4">
  <!-- 시설 선택 -->
  <div class="mb-3">
    <select class="form-select" id="factorySelect" onchange="loadTemplates()">
      <option value="">-- 시설 선택 --</option>
    </select>
  </div>

  <!-- 신규 템플릿 버튼 -->
  <div class="d-flex justify-content-between align-items-center mb-2">
    <span class="fw-semibold">점검 템플릿</span>
    <button class="btn btn-sm btn-primary" onclick="showCreatePanel()">
      <i class="bx bx-plus"></i> 새 템플릿
    </button>
  </div>

  <!-- 템플릿 목록 -->
  <div id="templateList" class="list-group">
    <!-- 동적 렌더 -->
  </div>
</div>
```

### 템플릿 리스트 아이템
```javascript
function renderTemplateItem(t, isActive) {
  return `
  <a href="#" class="list-group-item list-group-item-action ${
    isActive ? 'active' : ''}"
    onclick="loadTemplateDetail('${t.id}');return false">
    <div class="d-flex justify-content-between">
      <span class="fw-semibold">${t.template_name}</span>
      <span class="badge bg-secondary">${t.item_count || 0}항목</span>
    </div>
    ${t.description ? `<small class="text-muted">${t.description}</small>` : ''}
  </a>`;
}
```

---

## 2. 우측: 신규 템플릿 생성 판널

### 2-1. 헤더
```html
<div id="panel-create" class="d-none">
  <div class="card mb-3">
    <div class="card-header">
      <h6 class="mb-0">신규 템플릿</h6>
    </div>
    <div class="card-body">
      <div class="row g-3 mb-3">
        <div class="col-md-6">
          <label class="form-label">템플릿명 <span class="text-danger">*</span></label>
          <input type="text" class="form-control" id="newTemplateName"
            placeholder="예: 소화기 월간점검">
        </div>
        <div class="col-md-6">
          <label class="form-label">점검 유형</label>
          <select class="form-select" id="newCategory">
            <option value="FIRE">소방</option>
            <option value="ELEC">전기</option>
            <option value="SAFETY">안전</option>
            <option value="ENV">환경</option>
            <option value="MACHINERY">기계설비</option>
            <option value="GENERAL">기타</option>
          </select>
        </div>
        <div class="col-12">
          <label class="form-label">설명</label>
          <input type="text" class="form-control" id="newDescription" placeholder="선택사항">
        </div>
      </div>

      <!-- 항목 입력 영역 -->
      <div class="d-flex justify-content-between align-items-center mb-2">
        <span class="fw-semibold small">점검 항목</span>
        <button class="btn btn-sm btn-outline-primary" onclick="addItemRow()">
          <i class="bx bx-plus"></i> 항목 추가
        </button>
      </div>

      <table class="table table-sm" id="itemsTable">
        <thead class="table-light">
          <tr>
            <th>항목명</th>
            <th>유형</th>
            <th>주기</th>
            <th>위험도</th>
            <th>기준값</th>
            <th>점검방법</th>
            <th style="width:40px"></th>
          </tr>
        </thead>
        <tbody id="itemsBody">
          <!-- 항목 행 동적 생성 -->
        </tbody>
      </table>

      <div class="d-flex gap-2 mt-3">
        <button class="btn btn-success" onclick="saveTemplate()">
          <i class="bx bx-save me-1"></i>템플릿 저장
        </button>
        <button class="btn btn-outline-secondary" onclick="cancelCreate()">취소</button>
      </div>
    </div>
  </div>
</div>
```

### 2-2. 항목 행 템플릿 (JS)
```javascript
let itemRowIndex = 0;
function addItemRow(prefill = {}) {
  const idx = itemRowIndex++;
  const row = document.createElement('tr');
  row.id = `item-row-${idx}`;
  row.innerHTML = `
    <td><input type="text" class="form-control form-control-sm item-name"
      value="${prefill.item_name||''}" placeholder="항목명"></td>
    <td>
      <select class="form-select form-select-sm item-type">
        <option value="boolean" ${prefill.item_type==='boolean'?'selected':''}>O/X</option>
        <option value="text" ${prefill.item_type==='text'?'selected':''}>\ud14d\uc2a4\ud2b8</option>
        <option value="numeric" ${prefill.item_type==='numeric'?'selected':''}>\uc218\uce58</option>
        <option value="photo" ${prefill.item_type==='photo'?'selected':''}>\uc0ac\uc9c4</option>
        <option value="select" ${prefill.item_type==='select'?'selected':''}>\uc120\ud0dd</option>
      </select>
    </td>
    <td>
      <select class="form-select form-select-sm item-cycle">
        <option value="daily" ${prefill.cycle==='daily'?'selected':''}>일일</option>
        <option value="weekly" ${prefill.cycle==='weekly'?'selected':''}>주간</option>
        <option value="monthly" ${prefill.cycle==='monthly'?'selected':''}>월간</option>
        <option value="quarterly" ${prefill.cycle==='quarterly'?'selected':''}>분기</option>
        <option value="yearly" ${prefill.cycle==='yearly'?'selected':''}>연간</option>
      </select>
    </td>
    <td>
      <select class="form-select form-select-sm item-risk">
        <option value="HIGH" ${prefill.risk_level==='HIGH'?'selected':''}>높음</option>
        <option value="MEDIUM" ${prefill.risk_level==='MEDIUM'?'selected':''}>중간</option>
        <option value="LOW" ${prefill.risk_level==='LOW'?'selected':''}>낙음</option>
      </select>
    </td>
    <td><input type="text" class="form-control form-control-sm item-std"
      value="${prefill.standard_value||''}" placeholder="예: 0.5MPa"></td>
    <td><input type="text" class="form-control form-control-sm item-method"
      value="${prefill.check_method||''}" placeholder="육안/계측"></td>
    <td>
      <button class="btn btn-xs btn-outline-danger"
        onclick="document.getElementById('item-row-${idx}').remove()">
        <i class="bx bx-x"></i>
      </button>
    </td>`;
  document.getElementById('itemsBody').appendChild(row);
}
```

---

## 3. 템플릿 저장 + 점검세트 등록 JS

```javascript
async function saveTemplate() {
  const factoryId     = document.getElementById('factorySelect').value;
  const templateName  = document.getElementById('newTemplateName').value.trim();
  const category      = document.getElementById('newCategory').value;
  const description   = document.getElementById('newDescription').value.trim();

  if (!factoryId || !templateName) {
    showToast('warning', '시설과 템플릿명은 필수입니다.');
    return;
  }

  // 항목 수집
  const items = [];
  let sortOrder = 0;
  document.querySelectorAll('#itemsBody tr').forEach(row => {
    const name = row.querySelector('.item-name')?.value?.trim();
    if (!name) return;
    items.push({
      item_name:      name,
      item_type:      row.querySelector('.item-type')?.value,
      cycle:          row.querySelector('.item-cycle')?.value,
      risk_level:     row.querySelector('.item-risk')?.value,
      standard_value: row.querySelector('.item-std')?.value?.trim() || null,
      check_method:   row.querySelector('.item-method')?.value?.trim() || null,
      sort_order:     sortOrder++,
    });
  });

  if (!items.length) {
    showToast('warning', '항목을 1개 이상 입력해주세요.');
    return;
  }

  // 1) 템플릿 + 항목 저장
  const tplRes = await apiCall('POST', '/safety-templates', {
    factory_id:    factoryId,
    template_name: templateName,
    description,
    items,
  });
  const templateId = tplRes.data?.template_id;

  // 2) inspection_sets MANUAL 등록 (주기가 같은 항목의 대표 주기로 설정)
  const cycles = items.map(i => i.cycle).filter(Boolean);
  const repCycle = cycles[0] || 'monthly';
  const CYCLE_MAP = {
    'daily': {value: 1, unit: 'month'},   // 일일 항목도 월 1회 점검세트
    'weekly': {value: 1, unit: 'month'},
    'monthly': {value: 1, unit: 'month'},
    'quarterly': {value: 1, unit: 'quarter'},
    'yearly': {value: 1, unit: 'year'},
  };
  const cycleInfo = CYCLE_MAP[repCycle] || {value: 1, unit: 'month'};

  await apiCall('POST', '/inspection-sets/manual', {
    factory_id:           factoryId,
    inspection_set_name:  templateName,
    inspection_category:  category,
    template_id:          templateId,
    cycle_value:          cycleInfo.value,
    cycle_unit:           cycleInfo.unit,
    description:          description || null,
  });

  showToast('success', `"${templateName}" 템플릿과 점검세틘가 등록되었습니다.`);
  cancelCreate();
  loadTemplates();
}

async function loadTemplates() {
  const factoryId = document.getElementById('factorySelect').value;
  if (!factoryId) return;
  const data = await apiCall('GET', `/safety-templates/${factoryId}`);
  const list = data.data || [];
  document.getElementById('templateList').innerHTML =
    list.map((t, i) => renderTemplateItem(t, i === 0)).join('');
  if (list.length) loadTemplateDetail(list[0].id);
}

async function loadTemplateDetail(templateId) {
  const data = await apiCall('GET', `/safety-templates/detail/${templateId}`);
  const t = data.data;
  // 우측 상세 판널에 표시
  renderTemplateDetail(t);
}

function renderTemplateDetail(t) {
  const panel = document.getElementById('panel-detail');
  // 항목 리스트 표시
  const CYCLE_KO = {daily:'일일', weekly:'주간', monthly:'월간', quarterly:'분기', yearly:'연간'};
  const RISK_BADGE = {HIGH:'bg-danger', MEDIUM:'bg-warning', LOW:'bg-success'};

  const rows = (t.items || []).map((item, i) => `
    <tr>
      <td class="text-muted">${i+1}</td>
      <td class="fw-semibold">${item.item_name}</td>
      <td>${CYCLE_KO[item.cycle] || item.cycle || '-'}</td>
      <td><span class="badge ${RISK_BADGE[item.risk_level] || 'bg-secondary'}">${item.risk_level || '-'}</span></td>
      <td class="text-muted small">${item.standard_value || '-'}</td>
      <td class="text-muted small">${item.check_method || '-'}</td>
      <td>
        <button class="btn btn-xs btn-outline-danger"
          onclick="deleteItem('${t.id}','${item.id}')">
          <i class="bx bx-x"></i>
        </button>
      </td>
    </tr>`);

  panel.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h6 class="mb-0">${t.template_name}</h6>
        ${t.description ? `<small class="text-muted">${t.description}</small>` : ''}
      </div>
      <button class="btn btn-sm btn-outline-danger" onclick="deleteTemplate('${t.id}')">
        <i class="bx bx-trash me-1"></i>템플릿 삭제
      </button>
    </div>
    <table class="table table-sm">
      <thead class="table-light">
        <tr>
          <th>No.</th><th>항목명</th><th>주기</th><th>위험도</th>
          <th>기준값</th><th>점검방법</th><th></th>
        </tr>
      </thead>
      <tbody>${rows.join('')}</tbody>
    </table>
    <div class="text-muted small">* 점검 세트를 통해 실제 작업일정에 연결됩니다.</div>`;
}
```

---

## 완료 체크리스트

```
□ inspection-custom.html 파일 생성 (Vuexy tadmin 레이아웃)
□ 좌측: 시설선택 + 템플릿 목록 (GET /safety-templates/{factory_id})
□ 신규 템플릿 판널
  □ 템플릿명/유형/설명 입력
  □ 항목 추가 버튼 → 햜 동적 추가
  □ 항목행: 항목명/유형/주기/위험도/기준값/점검방법
  □ 저장 버튼 → POST /safety-templates + POST /inspection-sets/manual
□ 우측: 템플릿 상세 보기
  □ 항목목록 테이블
  □ 단건 항목 삭제 (DELETE /safety-templates/{id}/items/{item_id})
  □ 템플릿 삭제 (DELETE /safety-templates/{id})
□ GitHub push
```
