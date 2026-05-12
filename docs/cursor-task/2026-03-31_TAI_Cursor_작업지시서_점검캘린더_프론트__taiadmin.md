# TAI 프론트 작업지시서 — 점검 캘린더 + Rolling 생성 방식 전환

> 우선순위: 🔴 긴급  
> 작성일: 2026-03-31  
> 레포: taiengineering/tai-admin  
> Vuexy Bootstrap 5 기반

---

## 배경

1. **일정 생성 방식 변경**: 1년치 일괄 생성 → Rolling 방식 (다음 1회차만 DB 저장, 이후는 완료 시 자동 생성)
2. **캘린더 뷰 신규**: 상단 달력 아이콘으로 접근, 법정점검·정밀점검 등 구분 보기
3. **시설 필터**: 다중 시설 운영 시 시설별 분리 조회

---

## 작업 1: 전역 네비게이션 — 상단 달력 아이콘 추가

### 대상 파일
모든 tadmin 페이지의 `<nav>` 상단 우측 아이콘 영역 (기존 알림벨 옆)

### 추가할 HTML
```html
<!-- 알림벨 옆에 추가 -->
<li class="nav-item">
  <a class="nav-link" href="inspection-calendar.html" title="점검 캘린더">
    <i class="bx bx-calendar-check bx-sm"></i>
    <!-- 미완료 일정 수 배지 -->
    <span class="badge bg-danger badge-dot badge-notifications" id="calendarBadge" style="display:none"></span>
  </a>
</li>
```

### 배지 업데이트 JS (공통 초기화 시 실행)
```javascript
// 오늘 기준 SCHEDULED이면서 planned_date가 지난 일정 수 조회
async function updateCalendarBadge() {
  const factoryId = getCurrentFactoryId(); // localStorage 또는 전역변수
  if (!factoryId) return;
  const today = new Date().toISOString().split('T')[0];
  const res = await apiCall('GET',
    `/work-schedules/factory/${factoryId}?status_code=SCHEDULED&planned_date_to=${today}&size=1`
  );
  const overdue = res.data?.total || 0;
  const badge = document.getElementById('calendarBadge');
  if (badge && overdue > 0) {
    badge.textContent = overdue > 99 ? '99+' : overdue;
    badge.style.display = '';
  }
}
```

---

## 작업 2: 신규 페이지 — `inspection-calendar.html`

### 위치
`tadmin/full-version/html/horizontal-menu-template/inspection-calendar.html`

### 전체 구조
```
inspection-calendar.html
├── 상단: 시설 선택 드롭다운 + 점검유형 필터 탭
├── 중단: 월간 캘린더 뷰
└── 하단: 선택 날짜의 일정 상세 목록
```

---

### 2-1. 상단 컨트롤 영역

```html
<div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">

  <!-- 시설 선택 -->
  <div class="d-flex align-items-center gap-2">
    <i class="bx bx-building text-primary fs-5"></i>
    <select class="form-select form-select-sm w-auto" id="factoryFilter" onchange="loadCalendar()">
      <option value="">전체 시설</option>
      <!-- JS로 동적 로드 -->
    </select>
  </div>

  <!-- 월 이동 -->
  <div class="d-flex align-items-center gap-2">
    <button class="btn btn-sm btn-outline-secondary" onclick="changeMonth(-1)">
      <i class="bx bx-chevron-left"></i>
    </button>
    <h6 class="mb-0 fw-semibold" id="currentMonthLabel">2026년 4월</h6>
    <button class="btn btn-sm btn-outline-secondary" onclick="changeMonth(1)">
      <i class="bx bx-chevron-right"></i>
    </button>
    <button class="btn btn-sm btn-outline-primary ms-2" onclick="goToday()">오늘</button>
  </div>

  <!-- 점검 유형 필터 탭 -->
  <div class="btn-group btn-group-sm" id="categoryFilter">
    <button class="btn btn-outline-secondary active" data-cat="" onclick="setCat(this,'')">전체</button>
    <button class="btn btn-outline-danger"  data-cat="FIRE"      onclick="setCat(this,'FIRE')">소방</button>
    <button class="btn btn-outline-warning" data-cat="ELEC"      onclick="setCat(this,'ELEC')">전기</button>
    <button class="btn btn-outline-success" data-cat="SAFETY"    onclick="setCat(this,'SAFETY')">안전</button>
    <button class="btn btn-outline-info"    data-cat="ENV"       onclick="setCat(this,'ENV')">환경</button>
    <button class="btn btn-outline-dark"    data-cat="MACHINERY" onclick="setCat(this,'MACHINERY')">기계</button>
    <button class="btn btn-outline-secondary" data-cat="GENERAL" onclick="setCat(this,'GENERAL')">수동</button>
  </div>

</div>
```

---

### 2-2. 범례 (캘린더 위)

```html
<div class="d-flex gap-3 mb-3 flex-wrap small">
  <span><span class="badge bg-primary me-1">●</span>법정점검 (LEGAL_ENGINE)</span>
  <span><span class="badge bg-warning me-1">●</span>수동점검 (MANUAL)</span>
  <span><span class="badge bg-success me-1">●</span>완료</span>
  <span><span class="badge bg-danger me-1">●</span>기한초과</span>
  <span><span class="badge bg-light text-muted border me-1">●</span>예정 (미생성)</span>
</div>
```

---

### 2-3. 월간 캘린더 그리드

```html
<div class="card">
  <div class="card-body p-2">
    <table class="table table-bordered mb-0" id="calendarTable" style="table-layout:fixed">
      <thead class="table-light">
        <tr>
          <th class="text-center small">일</th>
          <th class="text-center small">월</th>
          <th class="text-center small">화</th>
          <th class="text-center small">수</th>
          <th class="text-center small">목</th>
          <th class="text-center small">금</th>
          <th class="text-center small">토</th>
        </tr>
      </thead>
      <tbody id="calendarBody">
        <!-- JS로 동적 렌더 -->
      </tbody>
    </table>
  </div>
</div>
```

### 캘린더 셀 렌더링 JS

```javascript
// 셀 하나 구조
function renderCell(dateStr, schedules, previews) {
  const isToday = dateStr === todayStr;
  const isPast  = dateStr < todayStr;

  // 실제 DB 일정 (work_schedules)
  const dots = schedules.map(s => {
    const color = s.status_code === 'COMPLETED' ? 'success'
                : s.status_code === 'SCHEDULED' && isPast ? 'danger'
                : s.source_type === 'LEGAL' ? 'primary' : 'warning';
    return `<span class="badge bg-${color} p-1 me-1" style="cursor:pointer"
              onclick="showDetail('${s.id}')" title="${s.summary}">●</span>`;
  }).join('');

  // 가상 예정일 (preview — DB 미생성, 점선 표시)
  const previewDots = previews.map(p =>
    `<span class="border border-secondary rounded-circle d-inline-block me-1"
       style="width:8px;height:8px;opacity:.4" title="${p.inspection_set_name} (예정)"></span>`
  ).join('');

  return `
    <td class="p-1 ${isToday ? 'bg-primary bg-opacity-10' : ''}"
        style="height:80px;vertical-align:top;cursor:pointer"
        onclick="selectDate('${dateStr}')">
      <div class="text-end small ${isPast ? 'text-muted' : ''} fw-${isToday ? 'bold' : 'normal'}">
        ${new Date(dateStr).getDate()}
      </div>
      <div class="mt-1">${dots}${previewDots}</div>
    </td>`;
}
```

---

### 2-4. 하단 선택 날짜 상세 목록

```html
<div class="card mt-4" id="detailPanel" style="display:none">
  <div class="card-header d-flex justify-content-between align-items-center">
    <h6 class="mb-0" id="detailDateLabel">2026년 4월 1일 점검 일정</h6>
    <span class="badge bg-secondary" id="detailCount">0건</span>
  </div>
  <div class="card-body p-0">
    <table class="table table-hover mb-0">
      <thead class="table-light">
        <tr>
          <th>점검명</th>
          <th>유형</th>
          <th>시설</th>
          <th>출처</th>
          <th>상태</th>
          <th>담당자</th>
          <th>관리</th>
        </tr>
      </thead>
      <tbody id="detailBody"></tbody>
    </table>
  </div>
</div>
```

### 상세 행 렌더링

```javascript
function renderDetailRow(s, idx) {
  const statusBadge = {
    'SCHEDULED':  '<span class="badge bg-label-primary">예정</span>',
    'COMPLETED':  '<span class="badge bg-label-success">완료</span>',
    'SUSPENDED':  '<span class="badge bg-label-secondary">정지</span>',
  }[s.status_code] || '<span class="badge bg-label-secondary">-</span>';

  const sourceBadge = s.source_type === 'LEGAL'
    ? '<span class="badge bg-primary">법정</span>'
    : '<span class="badge bg-warning text-dark">수동</span>';

  const isPast = s.planned_date < todayStr;
  const isOverdue = s.status_code === 'SCHEDULED' && isPast;

  return `
  <tr class="${isOverdue ? 'table-danger' : ''}">
    <td>
      <span class="fw-semibold">${s.summary || '-'}</span>
      ${isOverdue ? '<span class="badge bg-danger ms-1">기한초과</span>' : ''}
    </td>
    <td><span class="small text-muted">${s.obligation_type || '-'}</span></td>
    <td><span class="small">${s.factory_name || '-'}</span></td>
    <td>${sourceBadge}</td>
    <td>${statusBadge}</td>
    <td><span class="small">${s.inspector_name || '<span class="text-danger">미배정</span>'}</span></td>
    <td>
      ${s.status_code === 'SCHEDULED'
        ? `<button class="btn btn-xs btn-outline-success" onclick="completeSchedule('${s.id}')">완료처리</button>`
        : ''}
    </td>
  </tr>`;
}
```

---

### 2-5. 핵심 JS 로직

```javascript
const BASE_URL = 'https://api.taieng.co.kr';
let currentYear, currentMonth, selectedCat = '', selectedFactory = '';
let calendarData = {}; // { '2026-04-01': [schedules...] }
let previewData  = {}; // { '2026-04-01': [previews...] }

// 초기화
async function init() {
  const now = new Date();
  currentYear  = now.getFullYear();
  currentMonth = now.getMonth() + 1;
  await loadFactories();
  await loadCalendar();
}

// 시설 목록 로드
async function loadFactories() {
  const res = await apiCall('GET', '/factories');
  const sel = document.getElementById('factoryFilter');
  (res.data?.items || []).forEach(f => {
    sel.innerHTML += `<option value="${f.id}">${f.name}</option>`;
  });
}

// 캘린더 데이터 로드
async function loadCalendar() {
  selectedFactory = document.getElementById('factoryFilter').value;
  const monthStr = `${currentYear}-${String(currentMonth).padStart(2,'0')}`;

  // 1. 실제 DB 일정 조회
  let url = `/work-schedules?planned_date_from=${monthStr}-01&planned_date_to=${monthStr}-31&size=100`;
  if (selectedFactory) url += `&factory_id=${selectedFactory}`;
  if (selectedCat)     url += `&obligation_type=${selectedCat}`;

  const res = await apiCall('GET', url);
  calendarData = {};
  (res.data?.items || []).forEach(s => {
    if (!calendarData[s.planned_date]) calendarData[s.planned_date] = [];
    calendarData[s.planned_date].push(s);
  });

  // 2. 가상 예정일 조회 (preview — DB 미생성)
  let previewUrl = `/inspection-sets/${selectedFactory || 'all'}/preview-schedule?months=3`;
  if (selectedFactory) previewUrl = `/inspection-sets/factory-preview?factory_id=${selectedFactory}&months=3`;
  try {
    const prev = await apiCall('GET', previewUrl);
    previewData = {};
    (prev.data?.preview || []).filter(p => !p.is_actual).forEach(p => {
      if (!previewData[p.planned_date]) previewData[p.planned_date] = [];
      previewData[p.planned_date].push(p);
    });
  } catch(e) { previewData = {}; }

  renderCalendar();
}

// 완료 처리 → Rolling: 다음 회차 자동 생성은 백엔드에서 처리
async function completeSchedule(scheduleId) {
  if (!confirm('이 점검을 완료 처리하시겠습니까?')) return;
  await apiCall('PATCH', `/work-schedules/${scheduleId}`, { status_code: 'COMPLETED' });
  showToast('success', '완료 처리됐습니다. 다음 회차 일정이 자동 생성됩니다.');
  await loadCalendar(); // 캘린더 새로고침
}

// 월 이동
function changeMonth(delta) {
  currentMonth += delta;
  if (currentMonth > 12) { currentMonth = 1;  currentYear++; }
  if (currentMonth < 1)  { currentMonth = 12; currentYear--; }
  document.getElementById('currentMonthLabel').textContent =
    `${currentYear}년 ${currentMonth}월`;
  loadCalendar();
}

// 카테고리 필터
function setCat(btn, cat) {
  document.querySelectorAll('#categoryFilter .btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  selectedCat = cat;
  loadCalendar();
}
```

---

## 작업 3: `my-inspection.html` — Rolling 방식 전환에 따른 변경

### 변경 1: "1년치 일정" 표현 제거

기존에 "1년치 일정 생성됨" 또는 "총 12건" 등으로 표시한 부분을 모두 삭제.

대신:
```html
<!-- 변경 전 -->
<span>총 12개 일정 생성</span>

<!-- 변경 후 -->
<span>다음 점검일: <strong id="nextDate">-</strong></span>
```

### 변경 2: 일정 목록 — 실제 건수만 표시

```javascript
// 변경 전: 1년치 가정한 12건 목록
// 변경 후: DB의 실제 SCHEDULED 1건 + 가상 preview 목록 병합 표시

function renderInspectionList(sets) {
  return sets.map((s, i) => `
    <tr>
      <td><input type="checkbox" class="row-check" value="${s.id}"></td>
      <td>${i+1}</td>
      <td>
        ${s.inspection_set_name}
        ${s.source === 'LEGAL_ENGINE'
          ? '<span class="badge bg-primary ms-1">법정</span>'
          : '<span class="badge bg-warning text-dark ms-1">수동</span>'}
      </td>
      <td>${s.inspection_category || '-'}</td>
      <td>${s.cycle_value}${CYCLE_KO[s.cycle_unit] || s.cycle_unit}</td>
      <td>${s.next_planned_date || '기준일 미설정'}</td>
      <td>${s.status_code === 'ACTIVE'
          ? '<span class="badge bg-success">운영중</span>'
          : '<span class="badge bg-warning">기준일 대기</span>'}</td>
      <td>
        <a href="inspection-calendar.html?set=${s.id}" class="btn btn-xs btn-outline-primary">
          <i class="bx bx-calendar"></i>
        </a>
      </td>
    </tr>`).join('');
}
```

### 변경 3: 기준일 미설정 세트 강조

PENDING_ANCHOR 상태인 세트가 있으면 상단에 경고 배너 표시:

```html
<div class="alert alert-warning d-flex align-items-center gap-2" id="pendingBanner" style="display:none!important">
  <i class="bx bx-error-circle fs-5"></i>
  <span>기준일이 설정되지 않은 점검세트가 <strong id="pendingCount">0</strong>건 있습니다.
    <a href="inspection-anchor.html" class="alert-link">기준일 설정하기 →</a>
  </span>
</div>
```

---

## 작업 4: `inspection-anchor.html` — Rolling 방식 설명 문구 변경

기존 "1년치 일정이 생성됩니다" 문구를 변경:

```html
<!-- 변경 전 -->
<p class="text-muted small">기준일 설정 시 1년치 반복 일정이 자동 생성됩니다.</p>

<!-- 변경 후 -->
<p class="text-muted small">
  기준일 설정 시 <strong>다음 1회차 점검일정</strong>이 즉시 생성됩니다.<br>
  이후 각 점검 완료 시마다 다음 회차가 자동으로 생성됩니다.
</p>
```

anchor 설정 완료 응답 처리:
```javascript
// 변경 전: "12개 일정이 생성됐습니다"
// 변경 후:
function onAnchorSuccess(data) {
  showToast('success', `기준일이 설정됐습니다. 첫 점검일: ${data.next_planned_date}`);
  // 캘린더로 이동
  setTimeout(() => location.href = `inspection-calendar.html?factory=${currentFactoryId}`, 1500);
}
```

---

## 완료 체크리스트

```
□ 전역 nav에 달력 아이콘 추가 (모든 tadmin 페이지)
□ 배지: 기한초과 SCHEDULED 건수 표시
□ inspection-calendar.html 신규 생성
  □ 시설 필터 드롭다운
  □ 점검유형 탭 (소방/전기/안전/환경/기계/수동)
  □ 월간 캘린더 그리드 (실제 dot + 가상 preview dot)
  □ 선택 날짜 상세 목록 (법정/수동 구분, 기한초과 빨강)
  □ 완료 처리 버튼 (→ 다음 회차 자동 생성 toast)
□ my-inspection.html
  □ "1년치 생성" 문구 제거
  □ next_planned_date 표시로 변경
  □ PENDING_ANCHOR 경고 배너 추가
□ inspection-anchor.html
  □ 설명 문구 변경
  □ 완료 후 캘린더 페이지로 이동
□ GitHub push
```

---

## API 참고

| API | 설명 |
|-----|------|
| `GET /work-schedules?planned_date_from=&planned_date_to=` | 월간 실제 일정 조회 |
| `GET /inspection-sets/factory/{id}/preview-schedule?months=3` | 가상 예정일 (미생성) |
| `PATCH /work-schedules/{id}` | 완료 처리 |
| `GET /inspection-sets/factory/{factory_id}` | 점검세트 목록 |
| `GET /factories` | 시설 목록 |
