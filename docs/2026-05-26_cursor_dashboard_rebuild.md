# 안전관리자 대시보드 개편 — Cursor 작업지시서

> 작성일: 2026-05-26
> 대상 파일: `tadmin/full-version/html/horizontal-menu-template/index.html` (28KB → 전체 교체)
> 디자인 레퍼런스: Vuexy Analytics Dashboard (horizontal-menu-template-dark)
> 목적: 안전관리자가 "오늘의 안전관리 상태"를 한눈에 관제하는 화면

---

## 핵심 원칙

- TAI는 작업자가 직접 점검을 수행하는 구조 → **일별 단위**가 기본 시간축
- 안전관리자 = 배정/모니터링/예외처리 역할 → 대시보드는 "지금 뭐가 문제인가"에 집중
- Vuexy 디자인 톤: 깔끔한 카드 + ApexCharts + 최소 커스텀 CSS
- 이모지 사용 금지, Tabler 아이콘(ti ti-xxx) 사용
- gradient 배경 금지, Vuexy 기본 카드(card/card-body) 사용

---

## 전체 삭제 대상 (현재 index.html에서)

1. `.dash-hero` — gradient 인사말 영역 전체 삭제
2. 통계 카드 4개 (내 시설/활성 계약/법령진단 신청/법령판정 완료) — 전체 삭제
3. `#unassigned-wrap` — 미배정 경고 카드 + pulse 애니메이션 전체 삭제
4. `#insp-status-wrap` — 미점검 현황 위젯 전체 삭제
5. `#shortcut-grid` — 빠른 바로가기 전체 삭제
6. `#upcoming-list` — 다가오는 점검 전체 삭제
7. `<style>` 블록 내 커스텀 CSS 전체 삭제 (`.dash-hero`, `.shortcut-card`, `.unassigned-alert`, `.insp-stat-*`, `.insp-row`, `.sch-badge` 등)
8. `<script>` 블록 내 `loadDashStats`, `loadUnassigned`, `loadInspectionStatus`, `loadUpcoming` 함수 전체 삭제
9. SHORTCUTS 객체 전체 삭제

---

## 신규 레이아웃 (4단 구조)

### ■ 유지 항목
- `<head>` 내 Vuexy 기본 CSS/JS 임포트 — 그대로 유지
- `auth-guard.js` — 그대로 유지
- `#onboarding-checklist` — 그대로 유지 (온보딩 체크리스트)
- 하단 공통 JS (jquery, bootstrap, menu.js, main.js, api.js, toast.js, globals.js, menu-tadmin.js, nav-tadmin.js, notification.js, onboarding-checklist.js, footer-nav.js) — 그대로 유지
- `buildMenu('layout-menu')` — 그대로 유지

### ■ 추가 라이브러리
- ApexCharts — `<link>` + `<script>` 추가 필요
- Vuexy에 이미 포함: `../../assets/vendor/libs/apex-charts/apexcharts.js` + `../../assets/vendor/libs/apex-charts/apex-charts.css`

---

### ROW 0: 간결 인사 + 플랜 뱃지 (1줄)

Vuexy 스타일 1줄 인사. gradient 배경 없이, `<h5>` 텍스트만.

```html
<div class="d-flex align-items-center justify-content-between mb-4">
  <div>
    <h5 class="mb-1">안녕하세요, <span id="hero-username">관리자</span>님</h5>
    <p class="text-body-secondary mb-0">오늘의 안전관리 현황입니다.</p>
  </div>
  <span class="badge bg-label-primary" id="plan-chip">로딩 중...</span>
</div>
```

플랜 뱃지 로직은 기존과 동일 (localStorage contract_sector/contract_level 읽기).

---

### ROW 1: 핵심 KPI 카드 4개 (col-6 col-lg-3)

Vuexy 카드 패턴: avatar-lg 아이콘 + 숫자 + 서브텍스트 + progress bar.

| # | 카드 | 아이콘 | 색상 | 숫자 | 서브텍스트 | API |
|---|------|--------|------|------|------------|-----|
| 1 | 오늘 점검 이행률 | ti ti-clipboard-check | success | N% | 완료 X/Y건 | 아래 참조 |
| 2 | 기한 초과 | ti ti-alert-triangle | danger | N건 | 즉시 조치 필요 | 아래 참조 |
| 3 | 등록 근로자 | ti ti-users | info | N명 | 교육 미이수 N명 | `GET /workers` |
| 4 | 생성 문서 | ti ti-file-text | warning | N건 | 만료 임박 N건 | `GET /documents` |

각 카드 하단에 Vuexy `progress` 바 (height: 4px, rounded).

**점검 이행률 + 기한 초과 데이터 소스:**
```js
// factory_id = localStorage.getItem('factory_id')
// 이번 달 스케줄 가져오기
var now = new Date();
var monthStr = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0');
var r = await apiCall('GET', '/inspection/schedules/' + factoryId + '?month=' + monthStr);
var items = r?.data?.items || r?.data || [];
// 오늘 날짜 기준 완료/미완료/기한초과 분류
var today = new Date(); today.setHours(0,0,0,0);
var completed = 0, total = 0, overdue = 0;
items.forEach(s => {
  total++;
  if(s.status === 'COMPLETED' || s.status === 'completed') completed++;
  var pd = s.planned_date || s.scheduled_date;
  if(pd && new Date(pd) < today && s.status !== 'COMPLETED' && s.status !== 'completed') overdue++;
});
```

**근로자 데이터:**
```js
var companyId = localStorage.getItem('company_id');
var wr = await apiCall('GET', '/workers?page=1&size=1' + (companyId ? '&company_id=' + companyId : ''));
var workerTotal = wr?.data?.total || 0;
```

**문서 데이터:**
```js
var dr = await apiCall('GET', '/documents?page=1&size=1' + (companyId ? '&company_id=' + companyId : ''));
var docTotal = dr?.data?.total || 0;
```

---

### ROW 2: 차트 2단 (col-lg-8 + col-lg-4)

#### 왼쪽 (8칸): 일별 점검 이행 현황 — ApexCharts bar chart

**핵심 변경: 월별이 아닌 일별 표시**

X축 = 최근 14일 (날짜 라벨: "5/13", "5/14", ..., "5/26")
Y축 = 점검 건수
시리즈 2개: 완료(success색) / 미완료(danger색) — stacked bar

```js
// 최근 14일 스케줄 데이터 집계
var end = new Date();
var start = new Date(); start.setDate(start.getDate() - 13);
// items 배열에서 planned_date 기준으로 일별 그룹핑
var dailyMap = {}; // { '2026-05-13': { completed: 3, incomplete: 1 }, ... }
items.forEach(s => {
  var pd = (s.planned_date || s.scheduled_date || '').slice(0,10);
  if(!pd) return;
  if(!dailyMap[pd]) dailyMap[pd] = { completed: 0, incomplete: 0 };
  if(s.status === 'COMPLETED' || s.status === 'completed') {
    dailyMap[pd].completed++;
  } else {
    dailyMap[pd].incomplete++;
  }
});

// 14일 배열 생성
var categories = [], completedData = [], incompleteData = [];
for(var d = new Date(start); d <= end; d.setDate(d.getDate()+1)) {
  var key = d.toISOString().slice(0,10);
  var label = (d.getMonth()+1) + '/' + d.getDate();
  categories.push(label);
  completedData.push(dailyMap[key]?.completed || 0);
  incompleteData.push(dailyMap[key]?.incomplete || 0);
}

var chart = new ApexCharts(document.getElementById('daily-chart'), {
  chart: { type: 'bar', height: 260, stacked: true, toolbar: { show: false } },
  plotOptions: { bar: { columnWidth: '45%', borderRadius: 4 } },
  series: [
    { name: '완료', data: completedData },
    { name: '미완료', data: incompleteData }
  ],
  colors: ['#28c76f', '#ea5455'],
  xaxis: { categories: categories },
  yaxis: { title: { text: '건수' }, forceNiceScale: true },
  legend: { position: 'top' },
  tooltip: { y: { formatter: v => v + '건' } },
  grid: { borderColor: '#f1f1f1' }
});
chart.render();
```

카드 헤더:
```html
<div class="card-header d-flex align-items-center justify-content-between">
  <h5 class="card-title mb-0">일별 점검 현황</h5>
  <span class="text-body-secondary small">최근 14일</span>
</div>
<div class="card-body">
  <div id="daily-chart"></div>
</div>
```

#### 오른쪽 (4칸): 의무사항 분류 — ApexCharts donut

법령진단 결과의 `summary` 데이터 사용.

```js
// factory_diagnosis_results 또는 anonymous_diagnosis_results에서
// full_result.summary.appointment / report / action 사용
var factoryId = localStorage.getItem('factory_id');
var diagR = await apiCall('GET', '/diagnosis/results?factory_id=' + factoryId + '&page=1&size=1');
var summary = diagR?.data?.items?.[0]?.full_result?.summary || null;

// 데이터 없으면 inspection_sets에서 카테고리별 집계로 대체
if(!summary) {
  var setR = await apiCall('GET', '/inspection/sets?factory_id=' + factoryId + '&page=1&size=200');
  var sets = setR?.data?.items || [];
  // inspection_category_code 기준 집계
}
```

도넛 차트:
```js
new ApexCharts(document.getElementById('obligation-chart'), {
  chart: { type: 'donut', height: 260 },
  labels: ['선임/신고', '보고 의무', '조치 의무', '기타'],
  series: [appointment, report, action, etc],
  colors: ['#7367f0', '#28c76f', '#ff9f43', '#82868b'],
  legend: { position: 'bottom' },
  plotOptions: { pie: { donut: { size: '70%',
    labels: { show: true, total: { show: true, label: '전체', formatter: w => w.globals.seriesTotals.reduce((a,b)=>a+b,0) + '건' } }
  }}}
}).render();
```

**데이터 없을 때 처리:**
진단 결과가 없으면 도넛 차트 대신 안내 메시지 표시:
```html
<div class="text-center py-5">
  <i class="ti ti-clipboard-list" style="font-size: 3rem; color: var(--bs-secondary-color);"></i>
  <p class="text-body-secondary mt-2 mb-0">법령진단을 실행하면<br>의무사항 분류가 표시됩니다.</p>
</div>
```

---

### ROW 3: 리스트 2단 (col-lg-6 + col-lg-6)

#### 왼쪽: 기한 초과 점검 (최대 5건)

Vuexy 리스트 카드 스타일. 각 항목에 D+N 뱃지.

```html
<div class="card">
  <div class="card-header d-flex align-items-center justify-content-between">
    <h5 class="card-title mb-0">
      <i class="ti ti-alert-circle text-danger me-1"></i>기한 초과 점검
    </h5>
    <span class="badge bg-label-danger" id="overdue-badge">0건</span>
  </div>
  <div class="card-body" id="overdue-list">
    <!-- JS 렌더링 -->
  </div>
</div>
```

각 항목 HTML:
```html
<div class="d-flex align-items-center justify-content-between py-2 border-bottom">
  <div>
    <div class="fw-semibold small">{점검명}</div>
    <small class="text-body-secondary">{법령명} {조문} · {예정일}</small>
  </div>
  <span class="badge bg-label-danger">D+{N}</span>
</div>
```

기한 초과 없으면:
```html
<div class="text-center py-3">
  <span class="text-success fw-semibold"><i class="ti ti-check me-1"></i>기한 초과 항목이 없습니다</span>
</div>
```

API: `GET /inspection/schedules/{factoryId}?month={monthStr}` → planned_date < today && status !== COMPLETED 필터링.

#### 오른쪽: 이번 주 일정

Vuexy 타임라인 스타일. 날짜 + 컬러 바 + 점검명 + 담당자.

```html
<div class="card">
  <div class="card-header d-flex align-items-center justify-content-between">
    <h5 class="card-title mb-0">
      <i class="ti ti-calendar text-primary me-1"></i>이번 주 일정
    </h5>
    <a href="inspection-calendar.html" class="btn btn-sm btn-outline-primary">캘린더</a>
  </div>
  <div class="card-body" id="week-schedule">
    <!-- JS 렌더링 -->
  </div>
</div>
```

이번 주 = 오늘부터 7일간 스케줄 필터링.

각 항목 HTML:
```html
<div class="d-flex align-items-center gap-3 py-2 border-bottom">
  <div class="text-center" style="min-width:40px;">
    <div class="text-body-secondary" style="font-size:.7rem;">{요일}</div>
    <div class="fw-semibold">{일}</div>
  </div>
  <div style="width:3px; height:32px; border-radius:2px; background:{색상};"></div>
  <div>
    <div class="fw-semibold small">{점검명/교육명}</div>
    <small class="text-body-secondary">{담당자} · {시간}</small>
  </div>
</div>
```

색상 규칙: 점검=primary(#7367f0), 교육=success(#28c76f), 보고마감=warning(#ff9f43).

---

### ROW 4: 최근 활동 타임라인

Vuexy 가로 스크롤 카드. 최근 활동 이벤트를 카드로 표시.

```html
<div class="card">
  <div class="card-header">
    <h5 class="card-title mb-0"><i class="ti ti-activity text-info me-1"></i>최근 활동</h5>
  </div>
  <div class="card-body">
    <div class="d-flex gap-3 overflow-auto pb-2" id="activity-feed">
      <!-- JS 렌더링 -->
    </div>
  </div>
</div>
```

각 활동 카드:
```html
<div class="flex-shrink-0 bg-lighter rounded p-3" style="min-width:200px;">
  <small class="text-body-secondary">{시간}</small>
  <div class="fw-semibold small mt-1">{이벤트 제목}</div>
  <small class="text-body-secondary">{상세}</small>
</div>
```

데이터 소스 후보:
- `GET /inspection/results?page=1&size=5&sort=-created_at` (최근 점검 완료)
- `GET /documents?page=1&size=3&sort=-created_at` (최근 문서 생성)
- 현재 활동 로그 API가 없으면 → 점검 결과 + 문서 생성 시간순 병합
- 데이터 없으면: "아직 활동 기록이 없습니다" 표시

---

## CSS 규칙

- `<style>` 블록 최소화 — Vuexy 기본 클래스 우선 사용
- 커스텀 CSS는 아래 항목만 허용:
  ```css
  .customizer-btn { display: none !important; }
  #brand-logo { height: 110px !important; width: auto !important; }
  [data-bs-theme="dark"] #brand-logo { filter: brightness(0) invert(1); }
  ```
- gradient, animation, keyframes 금지
- 모든 색상은 Vuexy 변수 또는 BS5 변수 사용

---

## JS 구조

```js
// === 유틸 ===
function esc(s) { /* HTML escape — 기존과 동일 */ }

// === 데이터 로드 ===
async function loadDashboard() {
  var companyId = localStorage.getItem('company_id');
  var factoryId = localStorage.getItem('factory_id');
  
  // 병렬 로드
  await Promise.allSettled([
    loadKPICards(companyId, factoryId),
    loadDailyChart(factoryId),
    loadObligationChart(factoryId),
    loadOverdueList(factoryId),
    loadWeekSchedule(factoryId),
    loadActivityFeed(companyId)
  ]);
}

async function loadKPICards(companyId, factoryId) { /* ... */ }
async function loadDailyChart(factoryId) { /* ApexCharts bar */ }
async function loadObligationChart(factoryId) { /* ApexCharts donut */ }
async function loadOverdueList(factoryId) { /* ... */ }
async function loadWeekSchedule(factoryId) { /* ... */ }
async function loadActivityFeed(companyId) { /* ... */ }

// === 플랜 뱃지 (기존 로직 유지) ===
(function() {
  var un = localStorage.getItem('user_name');
  if(un) document.getElementById('hero-username').textContent = un;
  // plan-chip 로직 기존과 동일
})();

// === 초기화 ===
loadDashboard();
```

---

## factory_id 없을 때 처리

사업장이 아직 등록되지 않은 신규 유저의 경우:
- KPI 카드: 전부 "-" 또는 "0" 표시
- 차트: "사업장을 등록하면 점검 현황이 표시됩니다" + 사업장 등록 버튼
- 리스트: 빈 상태 메시지

```html
<div class="text-center py-5">
  <i class="ti ti-building-factory" style="font-size:3rem; color:var(--bs-secondary-color);"></i>
  <p class="text-body-secondary mt-2">사업장을 등록하면 점검 현황이 표시됩니다.</p>
  <a href="factory-list.html" class="btn btn-primary btn-sm">사업장 등록하기</a>
</div>
```

---

## 배포 후 확인

- [ ] safe.taieng.co.kr 로그인 → 대시보드 정상 렌더링
- [ ] KPI 4개 카드 숫자 표시 (또는 0/빈 상태)
- [ ] 일별 점검 차트 렌더링 (ApexCharts)
- [ ] 의무사항 도넛 차트 또는 빈 상태 메시지
- [ ] 기한 초과 리스트 표시
- [ ] 이번 주 일정 표시
- [ ] 다크 모드 정상 (Vuexy 테마 토글)
- [ ] 모바일 반응형 (col-6 col-lg-3 등)
- [ ] onboarding-checklist 정상 표시
- [ ] 메뉴 정상 렌더링 (buildMenu)

---

## 주의사항

- 이 파일은 `tadmin/` 경로 (safe.taieng.co.kr) — `admin/` 경로와 혼동 금지
- `tai-admin` 레포에는 `dev` 브랜치 없음 → `main`에 직접 커밋
- ApexCharts import 경로: `../../assets/vendor/libs/apex-charts/` (Vuexy 내장)
- `apiCall` 함수는 `../../assets/js/tai/api.js`에 정의됨 — 그대로 사용
- `buildMenu`, `auth-guard.js`, `notification.js`, `onboarding-checklist.js` — 건드리지 않음
- 서비스 레이어 분리 불필요 (프론트엔드 HTML 파일)
