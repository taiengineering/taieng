# 가격설정 페이지 — 프론트엔드 작업지시서

> 백엔드 API 완료 (012cd3d 커밋, Railway 배포 완료)  
> 이 문서는 프론트엔드 작업만 기술합니다.

---

## 0. 작업 전 확인

```
백엔드 API 베이스: https://api.taieng.co.kr

사용 가능한 API (모두 정상):
  GET  /price-setting/saas-plans              → 플랜 3건
  GET  /price-setting/saas-plans/{id}         → 플랜 상세
  PATCH /price-setting/saas-plans/{id}        → 플랜 수정
  GET  /price-setting/diagnosis-reports       → 진단 요금 6건
  PATCH /price-setting/diagnosis-reports/{id} → 진단 요금 수정
  GET  /price-setting/change-logs             → 변경 이력
```

---

## 1. 생성할 파일

| 파일 | 경로 | 작업 |
|------|------|------|
| HTML | `admin/full-version/html/horizontal-menu-template/price-setting.html` | **신규** |
| JS | `admin/full-version/assets/js/tai/pages/price-setting.page.js` | **신규** |
| 메뉴 수정 | 기존 모든 admin HTML 파일 | **수정** |

---

## 2. HTML 파일 (price-setting.html)

### 2.1 기본 구조

`education-setting.html` 완전 동일 패턴 사용.
- `<head>`, navbar, aside 메뉴, scripts 부분 그대로 복사
- `<title>TAI - 가격설정</title>` 변경
- active 메뉴 항목만 price-setting으로 변경
- content 영역만 아래 내용으로 교체

### 2.2 content 영역 구조

```html
<div class="container-xxl flex-grow-1 container-p-y" id="priceSettingRoot">

  <!-- 페이지 헤더 -->
  <div class="d-flex flex-wrap align-items-start justify-content-between gap-3 mb-3">
    <div>
      <h4 class="mb-1">가격설정</h4>
      <p class="text-muted small mb-0">서비스별·등급별·추가옵션별 요금을 설정합니다.</p>
    </div>
  </div>

  <!-- 안내 박스 -->
  <div class="alert alert-primary py-2 small mb-3">
    💡 여기서 설정한 요금은 서비스에 즉시 반영됩니다.
    가격 변경 시 변경 이력이 자동으로 기록됩니다.
  </div>

  <!-- 탭 -->
  <ul class="nav nav-tabs mb-3" role="tablist">
    <li class="nav-item">
      <button class="nav-link active" id="tabBtnPlan"
        data-bs-toggle="tab" data-bs-target="#tabPanePlan" type="button">
        SaaS 구독 플랜
      </button>
    </li>
    <li class="nav-item">
      <button class="nav-link" id="tabBtnDiagnosis"
        data-bs-toggle="tab" data-bs-target="#tabPaneDiagnosis" type="button">
        법령진단 단건 요금
      </button>
    </li>
    <li class="nav-item">
      <button class="nav-link" id="tabBtnLog"
        data-bs-toggle="tab" data-bs-target="#tabPaneLog" type="button">
        변경 이력
      </button>
    </li>
  </ul>

  <!-- 탭 컨텐츠 -->
  <div class="tab-content">

    <!-- 탭1: SaaS 플랜 -->
    <div class="tab-pane fade show active" id="tabPanePlan">
      <div id="planCardsRoot" class="row g-4">
        <!-- JS로 렌더링 -->
        <div class="col-12 text-center py-4 text-body-secondary">로딩 중…</div>
      </div>
    </div>

    <!-- 탭2: 법령진단 단건 요금 -->
    <div class="tab-pane fade" id="tabPaneDiagnosis">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">시설 유형별 단건 진단 요금</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle" id="tableDiagnosis">
              <thead>
                <tr>
                  <th style="width:36px">
                    <input type="checkbox" class="form-check-input"
                      id="chkAllDiag" onchange="toggleAll(this, '.diag-chk')">
                  </th>
                  <th class="text-center text-muted small" style="width:52px">No.</th>
                  <th>시설 유형</th>
                  <th class="text-end">기초진단</th>
                  <th class="text-end">공정/공종 진단</th>
                  <th class="text-end">설비/기계 진단</th>
                  <th class="text-end">종합 리포트</th>
                  <th class="text-center">활성</th>
                  <th class="text-center">저장</th>
                </tr>
              </thead>
              <tbody id="diagTbody">
                <tr><td colspan="9" class="text-center py-4 text-body-secondary">로딩 중…</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 탭3: 변경 이력 -->
    <div class="tab-pane fade" id="tabPaneLog">
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">가격 변경 이력</h5>
          <button class="btn btn-outline-secondary btn-sm" onclick="loadChangeLogs()">
            <i class="ti tabler-refresh me-1"></i>새로고침
          </button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
              <thead>
                <tr>
                  <th style="width:36px">
                    <input type="checkbox" class="form-check-input"
                      id="chkAllLog" onchange="toggleAll(this, '.log-chk')">
                  </th>
                  <th class="text-center text-muted small" style="width:52px">No.</th>
                  <th>변경일시</th>
                  <th>구분</th>
                  <th>필드</th>
                  <th>변경 전</th>
                  <th>변경 후</th>
                </tr>
              </thead>
              <tbody id="logTbody">
                <tr><td colspan="7" class="text-center py-4 text-body-secondary">로딩 중…</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>
```

### 2.3 scripts

기존 페이지와 동일한 스크립트 로드 순서 유지 후 마지막에 추가:

```html
<script src="../../assets/js/tai/pages/price-setting.page.js"></script>
```

---

## 3. JS 파일 (price-setting.page.js)

### 3.1 전체 구조

```javascript
// price-setting.page.js
'use strict';

// ── 초기화 ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadGlobals().then(() => initPage());
});

async function initPage() {
  await loadSaasPlans();
  await loadDiagnosisReports();
  // 탭3 클릭 시 이력 로드 (lazy)
  document.getElementById('tabBtnLog')
    .addEventListener('click', loadChangeLogs);
}
```

### 3.2 탭1 — SaaS 플랜 카드

```javascript
async function loadSaasPlans() {
  const res = await apiCall('GET', '/price-setting/saas-plans');
  const root = document.getElementById('planCardsRoot');
  if (!res?.data?.length) {
    root.innerHTML = '<div class="col-12 text-center text-muted py-4">플랜 데이터 없음</div>';
    return;
  }
  root.innerHTML = res.data.map(plan => renderPlanCard(plan)).join('');
}

function renderPlanCard(plan) {
  const isEnterprise = plan.plan_code === 'ENTERPRISE';
  const badgeClass = { secondary: 'bg-label-secondary', primary: 'bg-label-primary', dark: 'bg-label-dark' }[plan.badge_color] || 'bg-label-primary';

  return `
  <div class="col-12 col-md-4">
    <div class="card border-2">
      <div class="card-header d-flex align-items-center justify-content-between">
        <div>
          <span class="badge ${badgeClass} me-2">${plan.plan_code}</span>
          <strong>${plan.display_name || plan.plan_name}</strong>
        </div>
        <div class="form-check form-switch mb-0">
          <input class="form-check-input" type="checkbox" role="switch"
            id="activeSwitch_${plan.id}"
            ${plan.is_active ? 'checked' : ''}
            onchange="savePlanField('${plan.id}', 'is_active', this.checked)">
          <label class="form-check-label small" for="activeSwitch_${plan.id}">활성</label>
        </div>
      </div>
      <div class="card-body">
        <p class="text-muted small mb-3">${plan.description || ''}</p>

        <!-- 기본 요금 -->
        <h6 class="small fw-semibold text-uppercase text-muted mb-2">기본 요금</h6>
        <div class="row g-2 mb-3">
          <div class="col-6">
            <label class="form-label small">월 기본료 (원)</label>
            <input type="number" class="form-control form-control-sm"
              id="monthly_${plan.id}"
              value="${plan.monthly_base_fee}"
              ${isEnterprise ? 'disabled placeholder="협의"' : ''}>
          </div>
          <div class="col-6">
            <label class="form-label small">연간 기본료 (원)</label>
            <input type="number" class="form-control form-control-sm"
              id="annual_${plan.id}"
              value="${plan.annual_base_fee}"
              ${isEnterprise ? 'disabled placeholder="협의"' : ''}>
          </div>
          <div class="col-6">
            <label class="form-label small">연간 무료 개월</label>
            <input type="number" class="form-control form-control-sm"
              id="freemonth_${plan.id}"
              value="${plan.annual_free_months}" min="0" max="12"
              ${isEnterprise ? 'disabled' : ''}>
          </div>
        </div>

        <!-- 사용자 설정 -->
        <h6 class="small fw-semibold text-uppercase text-muted mb-2">사용자 설정</h6>
        <div class="row g-2 mb-3">
          <div class="col-6">
            <label class="form-label small">포함 인원 (명)</label>
            <input type="number" class="form-control form-control-sm"
              id="included_${plan.id}"
              value="${plan.included_users === -1 ? '' : plan.included_users}"
              placeholder="${plan.included_users === -1 ? '무제한' : ''}"
              ${isEnterprise ? 'disabled' : ''}>
          </div>
          <div class="col-6">
            <label class="form-label small">초과 1인당 (원)</label>
            <input type="number" class="form-control form-control-sm"
              id="extrauser_${plan.id}"
              value="${plan.extra_user_fee_v2}"
              ${isEnterprise ? 'disabled placeholder="협의"' : ''}>
          </div>
        </div>

        <!-- 시설/이력 -->
        <h6 class="small fw-semibold text-uppercase text-muted mb-2">시설 / 이력</h6>
        <div class="row g-2 mb-3">
          <div class="col-6">
            <label class="form-label small">최대 시설 수</label>
            <input type="number" class="form-control form-control-sm"
              id="maxsites_${plan.id}"
              value="${plan.max_sites === -1 ? '' : plan.max_sites}"
              placeholder="${plan.max_sites === -1 ? '무제한' : ''}"
              ${isEnterprise ? 'disabled' : ''}>
          </div>
          <div class="col-6">
            <label class="form-label small">이력 보관 개월</label>
            <input type="number" class="form-control form-control-sm"
              id="storage_${plan.id}"
              value="${plan.storage_history_month === -1 ? '' : plan.storage_history_month}"
              placeholder="${plan.storage_history_month === -1 ? '무제한' : ''}">
          </div>
        </div>

        <!-- 기능 포함 -->
        <h6 class="small fw-semibold text-uppercase text-muted mb-2">기능 포함</h6>
        <div class="d-flex flex-column gap-2 mb-3">
          ${[
            ['include_task_assign', '업무 할당·분산'],
            ['include_group_mgmt', '그룹 관리'],
            ['include_miss_alert', '누락 알림'],
            ['include_api_v2', 'API 연동'],
          ].map(([field, label]) => `
          <div class="form-check form-switch">
            <input class="form-check-input" type="checkbox" role="switch"
              id="${field}_${plan.id}"
              ${plan[field] ? 'checked' : ''}>
            <label class="form-check-label small" for="${field}_${plan.id}">${label}</label>
          </div>
          `).join('')}
        </div>

        <!-- 등급 select -->
        <div class="row g-2 mb-3">
          <div class="col-6">
            <label class="form-label small">안전콘텐츠 등급</label>
            <select class="form-select form-select-sm" id="safetycontent_${plan.id}">
              <option value="basic" ${plan.include_safety_content === 'basic' ? 'selected' : ''}>기본</option>
              <option value="advanced" ${plan.include_safety_content === 'advanced' ? 'selected' : ''}>고급</option>
              <option value="custom" ${plan.include_safety_content === 'custom' ? 'selected' : ''}>커스텀</option>
            </select>
          </div>
          <div class="col-6">
            <label class="form-label small">대시보드 등급</label>
            <select class="form-select form-select-sm" id="dashboard_${plan.id}">
              <option value="basic" ${plan.include_dashboard === 'basic' ? 'selected' : ''}>기본</option>
              <option value="advanced" ${plan.include_dashboard === 'advanced' ? 'selected' : ''}>고급</option>
              <option value="custom" ${plan.include_dashboard === 'custom' ? 'selected' : ''}>커스텀</option>
            </select>
          </div>
        </div>

      </div>
      <div class="card-footer">
        <button class="btn btn-primary btn-sm w-100"
          id="btnSavePlan_${plan.id}"
          onclick="savePlan('${plan.id}')">
          <i class="ti tabler-device-floppy me-1"></i>이 플랜 저장
        </button>
      </div>
    </div>
  </div>`;
}
```

### 3.3 savePlan 함수

```javascript
async function savePlan(planId) {
  const btn = document.getElementById(`btnSavePlan_${planId}`);
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>저장 중…';

  const toNum  = id => { const v = document.getElementById(id)?.value; return v === '' ? -1 : Number(v); };
  const toBool = id => document.getElementById(id)?.checked ?? false;
  const toStr  = id => document.getElementById(id)?.value ?? '';

  const body = {
    monthly_base_fee:       toNum(`monthly_${planId}`),
    annual_base_fee:        toNum(`annual_${planId}`),
    annual_free_months:     toNum(`freemonth_${planId}`),
    included_users:         toNum(`included_${planId}`),
    extra_user_fee_v2:      toNum(`extrauser_${planId}`),
    max_sites:              toNum(`maxsites_${planId}`),
    storage_history_month:  toNum(`storage_${planId}`),
    include_task_assign:    toBool(`include_task_assign_${planId}`),
    include_group_mgmt:     toBool(`include_group_mgmt_${planId}`),
    include_miss_alert:     toBool(`include_miss_alert_${planId}`),
    include_api_v2:         toBool(`include_api_v2_${planId}`),
    include_safety_content: toStr(`safetycontent_${planId}`),
    include_dashboard:      toStr(`dashboard_${planId}`),
  };

  try {
    await apiCall('PATCH', `/price-setting/saas-plans/${planId}`, body);
    showToast('플랜이 저장되었습니다.', 'success');
  } catch (e) {
    showToast('저장 중 오류가 발생했습니다.', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="ti tabler-device-floppy me-1"></i>이 플랜 저장';
  }
}

async function savePlanField(planId, field, value) {
  // toggle 즉시 저장용 (is_active 등)
  try {
    await apiCall('PATCH', `/price-setting/saas-plans/${planId}`, { [field]: value });
    showToast('저장되었습니다.', 'success');
  } catch (e) {
    showToast('저장 실패', 'error');
  }
}
```

### 3.4 탭2 — 법령진단 단건 요금

```javascript
async function loadDiagnosisReports() {
  const res = await apiCall('GET', '/price-setting/diagnosis-reports');
  const tbody = document.getElementById('diagTbody');
  if (!res?.data?.length) {
    tbody.innerHTML = '<tr><td colspan="9" class="text-center py-4">데이터 없음</td></tr>';
    return;
  }
  tbody.innerHTML = res.data.map((row, idx) => `
    <tr>
      <td class="ps-3">
        <input type="checkbox" class="form-check-input diag-chk">
      </td>
      <td class="text-center text-muted small">${idx + 1}</td>
      <td><strong>${row.facility_type_name}</strong></td>
      <td class="text-end">
        <input type="number" class="form-control form-control-sm text-end"
          style="width:100px"
          id="basic_${row.id}" value="${row.basic_fee}">
      </td>
      <td class="text-end">
        <input type="number" class="form-control form-control-sm text-end"
          style="width:110px"
          id="process_${row.id}" value="${row.process_fee}">
      </td>
      <td class="text-end">
        <input type="number" class="form-control form-control-sm text-end"
          style="width:110px"
          id="equipment_${row.id}" value="${row.equipment_fee}">
      </td>
      <td class="text-end">
        <input type="number" class="form-control form-control-sm text-end"
          style="width:120px"
          id="total_${row.id}" value="${row.total_report_fee}">
      </td>
      <td class="text-center">
        <div class="form-check form-switch d-flex justify-content-center mb-0">
          <input class="form-check-input" type="checkbox" role="switch"
            id="diagActive_${row.id}" ${row.is_active ? 'checked' : ''}>
        </div>
      </td>
      <td class="text-center">
        <button class="btn btn-primary btn-sm" id="btnDiag_${row.id}"
          onclick="saveDiagnosisRow('${row.id}')">
          저장
        </button>
      </td>
    </tr>
  `).join('');
}

async function saveDiagnosisRow(id) {
  const btn = document.getElementById(`btnDiag_${id}`);
  btn.disabled = true;
  btn.textContent = '…';

  const body = {
    basic_fee:        Number(document.getElementById(`basic_${id}`).value),
    process_fee:      Number(document.getElementById(`process_${id}`).value),
    equipment_fee:    Number(document.getElementById(`equipment_${id}`).value),
    total_report_fee: Number(document.getElementById(`total_${id}`).value),
    is_active:        document.getElementById(`diagActive_${id}`).checked,
  };

  try {
    await apiCall('PATCH', `/price-setting/diagnosis-reports/${id}`, body);
    showToast('저장되었습니다.', 'success');
  } catch (e) {
    showToast('저장 실패', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '저장';
  }
}
```

### 3.5 탭3 — 변경 이력

```javascript
async function loadChangeLogs() {
  const tbody = document.getElementById('logTbody');
  tbody.innerHTML = '<tr><td colspan="7" class="text-center py-3">로딩 중…</td></tr>';

  const res = await apiCall('GET', '/price-setting/change-logs');
  if (!res?.data?.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">변경 이력 없음</td></tr>';
    return;
  }
  tbody.innerHTML = res.data.map((log, idx) => `
    <tr>
      <td class="ps-3"><input type="checkbox" class="form-check-input log-chk"></td>
      <td class="text-center text-muted small">${idx + 1}</td>
      <td class="small">${formatDatetime(log.changed_at)}</td>
      <td><span class="badge bg-label-secondary">${formatTableName(log.table_name)}</span></td>
      <td class="small">${formatFieldName(log.field_name)}</td>
      <td class="small text-body-secondary">${formatValue(log.old_value)}</td>
      <td class="small fw-semibold text-primary">${formatValue(log.new_value)}</td>
    </tr>
  `).join('');
}

// ── 유틸 함수 ──────────────────────────────────────────
function formatTableName(t) {
  return { price_saas_plan: 'SaaS 플랜', price_diagnosis_report: '진단 요금' }[t] || t;
}

function formatFieldName(f) {
  const map = {
    monthly_base_fee: '월 기본료', annual_base_fee: '연간 기본료',
    annual_free_months: '연간 무료 개월', included_users: '포함 인원',
    extra_user_fee_v2: '초과 1인당', max_sites: '최대 사이트',
    storage_history_month: '이력 보관 개월', include_task_assign: '업무 할당',
    include_group_mgmt: '그룹 관리', include_miss_alert: '누락 알림',
    include_api_v2: 'API 연동', include_safety_content: '안전콘텐츠 등급',
    include_dashboard: '대시보드 등급', is_active: '활성 여부',
    basic_fee: '기초진단 요금', process_fee: '공정진단 요금',
    equipment_fee: '설비진단 요금', total_report_fee: '종합 리포트 요금',
  };
  return map[f] || f;
}

function formatValue(v) {
  if (v === null || v === undefined || v === '') return '—';
  if (v === 'true') return '✅';
  if (v === 'false') return '❌';
  if (v === '-1') return '무제한';
  // 숫자면 천단위 콤마
  const n = Number(v);
  if (!isNaN(n) && n > 0) return n.toLocaleString() + '원';
  return v;
}

function formatDatetime(dt) {
  if (!dt) return '—';
  return new Date(dt).toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short' });
}
```

---

## 4. 메뉴 추가 (기존 모든 admin HTML)

모든 admin 페이지의 aside 메뉴에서 **설정** 관련 menu-item을 찾아 아래 항목 추가:

```html
<li class="menu-item">
  <a class="menu-link" href="price-setting.html">
    <div>가격설정</div>
  </a>
</li>
```

**위치**: 기존 메뉴 구조에서 설정/시스템 관련 메뉴 하위.
설정 메뉴가 없다면 아래와 같이 신규 메뉴 추가:

```html
<li class="menu-item">
  <a class="menu-link menu-toggle" href="javascript:void(0)">
    <i class="menu-icon icon-base ti tabler-settings"></i>
    <div>설정</div>
  </a>
  <ul class="menu-sub">
    <li class="menu-item">
      <a class="menu-link" href="price-setting.html">
        <div>가격설정</div>
      </a>
    </li>
  </ul>
</li>
```

---

## 5. 완료 체크리스트

- [ ] `price-setting.html` 생성 (탭 3개 구조)
- [ ] `price-setting.page.js` 생성 (함수 7개)
- [ ] 탭1 플랜 카드 3개 정상 렌더링
- [ ] 플랜 저장 버튼 → PATCH 정상 호출
- [ ] 탭2 진단 요금 테이블 6행 렌더링
- [ ] 진단 요금 행별 저장 버튼 작동
- [ ] 탭3 클릭 시 변경 이력 로드
- [ ] 모든 admin 페이지 메뉴에 '가격설정' 추가
- [ ] ENTERPRISE 플랜 필드 disabled + '협의' placeholder 표시
- [ ] -1 값 → '무제한' placeholder 표시

---

## 6. 주의사항

- `loadGlobals()` 완료 후 `initPage()` 호출 (기존 패턴 동일)
- `apiCall()` 함수 사용 (`assets/js/tai/api.js`)
- `showToast()` 사용 (`assets/js/tai/toast.js`)
- 테이블 첫 컬럼: 전체선택 체크박스 / 두 번째 컬럼: No. (전역 규칙)
- access_token 없으면 로그인 페이지로 redirect
