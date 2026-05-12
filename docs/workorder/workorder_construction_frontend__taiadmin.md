# 건설관리 프론트엔드 워크오더

> 작성일: 2026-04-09  
> 기준 API: `routers/construction.py` v2.1.0  
> 기준 경로: `tadmin/full-version/html/horizontal-menu-template/`  
> 메뉴 진입: `safe.taieng.co.kr` → 건설관리

---

## ★ API v2.1.0 추가 기능 (프론트엔드 구현 필수)

### 1. `POST /construction/sites/{site_id}/diagnose` — 법령진단 독립 실행

현장 등록 시 자동 실행되지만, **재실행 버튼**도 필요.

**동작:**
- CONSTRUCTION sector 173개 규칙 → 현장 조건(도급금액·인원·공종) 매칭
- `factory_diagnosis_results` 저장 (`is_latest=true`)
- `construction_sites.diagnosis_applicable_count` 자동 업데이트

**응답:**
```json
{
  "data": {
    "site_id": "...",
    "factory_id": "...",
    "total_rules": 173,
    "applicable_rules": 42,
    "diagnosis_id": "...",
    "by_obligation_type": {
      "appointment": 5,
      "inspection": 28,
      "action": 4,
      "report": 3,
      "notify": 2
    }
  }
}
```

**프론트 처리:**
```js
async function runDiagnosis(siteId) {
  setButtonLoading(diagBtn, true);
  const res = await fetch(`${API}/construction/sites/${siteId}/diagnose`, {
    method: 'POST', headers: hdr()
  });
  const j = await res.json();
  setButtonLoading(diagBtn, false);
  if (res.ok) {
    showToast('success',
      `법령진단 완료 — 적용 ${j.data.applicable_rules}건 ` +
      `(선임 ${j.data.by_obligation_type.appointment}, ` +
      `점검 ${j.data.by_obligation_type.inspection})`
    );
    refreshSiteRow(siteId); // diagnosis_applicable_count 갱신
  }
}
```

**표시 위치:** `construction-site-list.html` 사이드패널 하단 버튼

---

### 2. `POST /construction/sites/{site_id}/generate-schedules` — 작업일정 자동 생성

법령진단 후 **일정 생성 버튼** 또는 진단 직후 자동 트리거.

**동작:**
- 최신 진단 결과(`is_latest=true`)의 `inspection_required` + `action_required` 조회
- `work_schedules` 생성 (source_type=`LEGAL`)
- 중복 `rule_code`는 자동 스킵

**응답:**
```json
{
  "data": {
    "site_id": "...",
    "factory_id": "...",
    "created": 25,
    "skipped": 3,
    "total_rules": 28,
    "message": "25건 일정 생성, 3건 중복 스킵"
  }
}
```

**프론트 처리:**
```js
async function generateSchedules(siteId) {
  const res = await fetch(`${API}/construction/sites/${siteId}/generate-schedules`, {
    method: 'POST', headers: hdr()
  });
  const j = await res.json();
  if (res.ok) {
    showToast('info',
      `작업일정 생성 — ${j.data.created}건 생성, ${j.data.skipped}건 중복 스킵`
    );
  } else {
    // "법령진단을 먼저 실행하세요" 에러 처리
    showToast('warning', j.detail || '진단 후 재시도해주세요.');
  }
}
```

**표시 위치:** `construction-site-list.html` 사이드패널 — 진단 버튼 옆

**버튼 비활성화 조건:** `diagnosis_applicable_count` 가 null이거나 0이면 비활성

---

### 3. 점검 저장 → FCM 자동 발송 (백엔드 자동 처리)

`POST /construction/sites/:site_id/inspections` 시 API가 자동으로:

1. **defect_count 자동 계산:**
   - `checklist_items` 배열에서 `result`가 `bad`, `fail`, `이상`, `FAIL` 인 항목 수 집계

2. **overall_result 자동 판정:**
   - `defect_count >= 1` → `ISSUE`
   - `defect_count == 0` → `PASS`
   - 프론트에서 명시적으로 보내도 되지만, **생략 가능** (API가 계산)

3. **FCM 자동 발송:**
   - `overall_result`가 `FAIL` 또는 `ISSUE`이고 `defect_count > 0` 이면
   - `site.manager_id → users.fcm_token` 조회 → FCM 발송
   - `FCM_SERVER_KEY` 환경변수 없으면 자동 무시 (에러 발생하지 않음)

**프론트 제출 코드 패턴:**
```js
// worker-check-construction.html 및 construction-inspection-list.html 공통
async function submitInspection(siteId, items, workId) {
  const payload = {
    work_id: workId || null,
    inspection_date: new Date().toISOString(),
    inspector_id: localStorage.getItem('user_id'),
    inspection_type: 'BEFORE_WORK',
    checklist_items: items.map(i => ({
      item_name: i.name,
      result: i.result,   // 'good' | 'bad'
      note: i.note || ''
    })),
    // overall_result, defect_count 생략 가능 → API 자동 계산
  };

  const res = await fetch(
    `${API}/construction/sites/${siteId}/inspections`,
    { method: 'POST', headers: hdr(), body: JSON.stringify(payload) }
  );
  const j = await res.json();

  if (res.ok) {
    const result = j.data.overall_result;
    if (result === 'ISSUE' || result === 'FAIL') {
      // FCM은 API가 자동 발송 완료
      showResult(
        `⚠️ 이상 항목 ${j.data.defect_count}건 감지. 관리자에게 자동 보고됐습니다.`,
        'warning'
      );
    } else {
      showResult('✅ 점검 완료. 안전하게 작업해주세요!', 'success');
    }
  }
}
```

**checklist_items 배열 형식 (API 기대값):**
```json
[
  { "item_name": "PPE 착용 확인", "result": "good", "note": "" },
  { "item_name": "안전 펜스 설치", "result": "bad", "note": "우측 구간 미설치" },
  { "item_name": "장비 이상 유무", "result": "good", "note": "" }
]
```

**FCM 환경변수 설정 (Railway):**
```
Railway 대시보드 → 해당 서비스 → Variables
FCM_SERVER_KEY = [Firebase 서버 키]
```
미설정 시 FCM 발송 건너뜀, 점검 저장에는 영향 없음.

---

## 공통 사전 지식

### 건설관리 핵심 구조

```
company (회사)
  └── construction_site (건설현장)  ← 시설관리의 factory에 해당
        ├── factory_id (자동생성, 법령진단 연동)
        ├── construction_site_processes (공정)
        ├── construction_works (작업/PTW)
        ├── construction_workers (작업자)
        └── construction_inspections (점검)
```

### 시설관리와의 차이

| 항목 | 시설관리 | 건설관리 |
|------|---------|--------|
| 기준 단위 | factory (사업장) | construction_site (현장) |
| 셀렉터 | factorySelect | siteSelect |
| 법령진단 | `/factories/:id` | POST `/construction/sites/:id/diagnose` |
| 스케줄생성 | `/inspection-sets` | POST `/construction/sites/:id/generate-schedules` |
| 점검항목 | inspection_sets | inspection-anchor.html 공유 (factory_id 기반) |

### API 기본 경로
```
https://api.taieng.co.kr/construction
```

### site_id 전달 방식
모든 하위 화면은 URL 파라미터 `?site_id=xxx`로 현장 ID를 수신한다.  
`localStorage.setItem('selectedConstructionSiteId', siteId)` 병행 저장.

### status_code 공통 코드
| 코드 | 의미 |
|------|------|
| PLANNED | 계획 |
| IN_PROGRESS | 진행중 |
| DONE | 완료 |
| SUSPENDED | 중단 |

---

## 화면 목록

| 순서 | 파일명 | 방식 | 메뉴 경로 | 상태 |
|------|--------|------|----------|------|
| 1 | construction-site-list.html | 기존 파일 전면 재작성 | 건설관리 > 현장관리 | 재작성 필요 |
| 2 | construction-inspection-anchor.html | inspection-anchor.html 재활용 | 건설관리 > 점검항목관리 | 신규 생성 |
| 3 | construction-inspection-list.html | 기존 파일 전면 재작성 | 건설관리 > 점검관리 | 재작성 필요 |
| 4 | construction-process.html | 신규 | 건설관리 > 공정관리 | 신규 |
| 5 | construction-worker-list.html | worker-list.html 재활용 | 건설관리 > 작업관리 (작업자) | 재작성 필요 |
| 6 | worker-check-construction.html | worker-check.html 재활용 | 작업자 현장 점검 제출 | 신규 생성 |

---

## 1. construction-site-list.html — 현장관리

### 목적
건설현장 CRUD. 시설관리의 `factory-list.html` 역할을 건설에서 담당.  
현장 생성 시 법령진단 자동 실행 + 작업일정 자동 생성 (API 자동처리).

### 기존 파일 현황
- SHA: f00b3509 / 20,468 bytes — 기존 구조 대부분 교체 필요

### API
```
GET    /construction/sites?company_id=&status_code=&search=&page=&size=
POST   /construction/sites
GET    /construction/sites/:site_id
PATCH  /construction/sites/:site_id
DELETE /construction/sites/:site_id
GET    /construction/sites/:site_id/stats       ← 현장 통계 (오른쪽 사이드 패널용)
POST   /construction/sites/:site_id/diagnose    ← 법령진단 재실행 버튼 (v2.1.0)
POST   /construction/sites/:site_id/generate-schedules  ← 일정 생성 버튼 (v2.1.0)
```

### 화면 구성

#### 상단 헤더
```
[🏗 건설현장 관리]  법령진단·일정 자동 생성
                                        [+ 현장 등록]
```

#### 필터 바
```
[전체 상태 ▼] [건물/토목 ▼] [검색: 현장명...] [🔍]
```

#### 목록 테이블
| # | 체크 | No. | 현장명 | 유형 | 도급금액(억) | 상태 | 안전관리자 | 진행율 | 기간 | 진단 | 액션 |
|---|------|-----|--------|------|------------|------|----------|--------|------|------|------|
- 안전관리자 열: `safety_manager_required=true` 시 뱃지 표시
- 진단 열: `diagnosis_applicable_count` 값, 없으면 `진단 필요` 버튼
- 행 클릭 → `?site_id=xxx`로 이동 없이, 통계 사이드 패널 오픈

#### 사이드 패널 (stats 기반)
```
현장 이름 / 주소
─────────────────────
공정: 전체 N / 진행중 N
작업: 전체 N / PTW승인 N
작업자: 전체 N / 현장내 N
점검: 전체 N / 이상 N
─────────────────────
[법령진단 재실행]  [일정 생성]  [현장 수정]
```
※ `diagnosis_applicable_count`가 0이면 `일정 생성` 버튼 비활성화

#### 등록 모달 필드
```
현장명 *       사업장유형 (BUILDING/CIVIL) *
도급금액(억) * 시작일        종료일
주소           현장소장 (users 드롭다운)
직영 근로자 수  하도급 근로자 수
비고
```

### 코드 포인트
```js
// company_id는 localStorage에서
const cid = localStorage.getItem('company_id');

// 현장 목록 로드
GET /construction/sites?company_id={cid}&page=1&size=50

// 현장 등록 후 auto 결과 표시
const { data, auto } = await res.json();
if (auto?.diagnosis) showToast('success', `법령 ${auto.diagnosis.applicable_count}건 적용`);
if (auto?.schedules) showToast('info', `작업일정 ${auto.schedules.created}건 생성`);

// 법령진단 재실행 (v2.1.0)
POST /construction/sites/{site_id}/diagnose

// 작업일정 생성 (v2.1.0)
POST /construction/sites/{site_id}/generate-schedules
```

---

## 2. construction-inspection-anchor.html — 점검항목관리

### 목적
`inspection-anchor.html`을 건설현장 전용으로 재활용.  
사업장 셀렉터 → **현장 셀렉터**로 교체.  
API 경로 `/inspection-sets?factory_id=` 그대로 사용 (현장 생성 시 factory_id 자동 생성됨).

### 재활용 원본
- `inspection-anchor.html` SHA: 5afb9f1b (49,121 bytes)

### 변경 사항 (원본 대비 diff)

#### 변경 1: 페이지 타이틀 및 헤더
```html
<!-- 원본 -->
<title>TAI - 점검항목관리</title>
<h4>점검항목관리</h4>
<small>언제 · 누가 · 무엇을 · 어떻게</small>

<!-- 건설 버전 -->
<title>TAI - 건설 점검항목관리</title>
<h4><i class="ti tabler-building-community me-2 text-warning"></i>건설 점검항목관리</h4>
<small>건설현장 법령 기반 — 언제 · 누가 · 무엇을 · 어떻게</small>
```

#### 변경 2: 사업장 배너 → 현장 셀렉터
```html
<!-- 원본: factorySelect -->
<select id="factorySelect" onchange="onFactoryChange()">
  <option value="">사업장을 선택하세요</option>
</select>

<!-- 건설 버전: siteSelect -->
<select id="siteSelect" onchange="onSiteChange()">
  <option value="">건설현장을 선택하세요</option>
</select>
```

#### 변경 3: 배너 컬러 (파란색 → 주황/건설 컬러)
```html
<!-- 원본 -->
<div class="card mb-3" style="background:linear-gradient(135deg,#1a5fd4,#0c2d5c)">

<!-- 건설 버전 -->
<div class="card mb-3" style="background:linear-gradient(135deg,#d97706,#92400e)">
```

#### 변경 4: JS — 현장 목록 로드 함수
```js
// 건설 버전: loadSites()
async function loadSites() {
  const url = `${API}/construction/sites?company_id=${cid}&page=1&size=100`;
  const items = j.data?.items || [];
  const sel = document.getElementById('siteSelect');
  sel.innerHTML = '<option value="">건설현장을 선택하세요</option>';
  items.forEach(s => {
    const o = document.createElement('option');
    o.value = s.factory_id; // ← factory_id를 사용 (inspection-sets API가 factory_id 기반)
    o.textContent = `${s.site_name} (${s.site_type === 'BUILDING' ? '건축' : '토목'})`;
    o.dataset.siteId = s.id; // ← 원본 site_id도 보관
    sel.appendChild(o);
  });
}
```

#### 변경 5: onSiteChange() — factory_id 기준 유지
```js
window.onSiteChange = function() {
  const sel = document.getElementById('siteSelect');
  _factoryId = sel.value; // factory_id
  const selectedOpt = sel.options[sel.selectedIndex];
  _siteId = selectedOpt?.dataset?.siteId || '';
  ...
};
```

#### 변경 6: localStorage key
```js
localStorage.setItem('selectedConstructionSiteId', _siteId);
localStorage.setItem('selectedConstructionFactoryId', _factoryId);
```

#### 그 외 로직
- 점검항목 탭, 4조건 패널, 법령원문 모달 등 **원본 그대로 유지**
- URL 파라미터: `?site_id=xxx` 수신 시 해당 현장 자동 선택

---

## 3. construction-inspection-list.html — 점검관리

### 목적
건설현장 안전점검 이력 목록 + 신규 점검 등록.  
이상 항목 감지 시 관리자 FCM 알림 자동 발송 (API 자동처리 — v2.1.0).

### 기존 파일 현황
- SHA: 1630775e (21,710 bytes) — 구조 재작성 필요

### API
```
GET    /construction/sites/:site_id/inspections?inspection_type=&overall_result=&page=&size=
POST   /construction/sites/:site_id/inspections
GET    /construction/inspections/:inspection_id
PATCH  /construction/inspections/:inspection_id
PATCH  /construction/inspections/:inspection_id/corrective  ← 시정조치 상태 변경
DELETE /construction/inspections/:inspection_id
```

### 화면 구성

#### 상단 헤더
```
[🔍 건설 안전점검]  이상 감지 시 관리자 자동 알림 (v2.1.0)
현장 선택 배너 (construction/sites 기반)
                                        [+ 점검 등록]
```

#### 필터 탭
```
[전체] [작업전점검] [정기점검] [특별점검]
[결과: 전체 ▼] [시정: 전체 ▼] [검색] [새로고침]
```

#### 목록 테이블
| # | No. | 점검일시 | 점검유형 | 점검자 | 결과 | 이상항목수 | 시정조치 | 마감일 | 액션 |
|---|-----|---------|---------|--------|------|----------|---------|--------|------|
- 결과 배지: PASS=초록, ISSUE=주황, FAIL=빨강
- 시정조치: PENDING/IN_PROGRESS/DONE 배지 + 인라인 변경 버튼
- 행 클릭 → 상세 모달

#### 통계 카드 (목록 상단)
```
[전체 N건] [이상 N건] [시정완료율 N%] [이번달 N건]
```

#### 등록 모달 필드
```
점검일시 *     점검유형 * (BEFORE_WORK/REGULAR/SPECIAL)
점검자         관련 작업 (works 드롭다운, 선택사항)
체크리스트 항목 (동적 행 추가: 항목명 + 결과 양호/이상)
              ※ overall_result, defect_count 생략 → API 자동 계산 (v2.1.0)
시정조치 내용   시정 마감일
비고
```

### 코드 포인트
```js
// inspection_type 코드
const INSP_TYPE = {
  BEFORE_WORK: '작업 전 점검',
  REGULAR: '정기점검',
  SPECIAL: '특별점검',
};

// 제출 시 overall_result 생략 가능 (API v2.1.0이 자동 계산)
const payload = {
  inspection_type: 'BEFORE_WORK',
  checklist_items: items.map(i => ({
    item_name: i.name,
    result: i.result,  // 'good' | 'bad'
    note: i.note || ''
  })),
  // overall_result 생략 → API가 bad 항목 수 기준으로 자동 판정
};

// 시정조치 상태 변경
PATCH /construction/inspections/{id}/corrective
body: { corrective_status: 'DONE', corrective_action: '...' }
```

---

## 4. construction-process.html — 공정관리

### 목적
건설 공정 목록 + CRUD. 현장별 공정 단계를 관리.  
기존 `construction-process-list.html` (47b9964a) 대체.

### API
```
GET    /construction/sites/:site_id/processes?status_code=&page=&size=
POST   /construction/sites/:site_id/processes
GET    /construction/processes/:process_id
PATCH  /construction/processes/:process_id
DELETE /construction/processes/:process_id

# KCSC 마스터 (공정 선택 드롭다운용)
GET    /construction/kcsc/processes?search=&construction_type=&size=50
GET    /construction/kcsc/works?is_hazardous=true&work_type_code=   ← 위험작업 목록
```

### 화면 구성

#### 목록 테이블
| # | No. | 공정명 | KCSC코드 | 계획시작 | 계획종료 | 진행율 | 투입인원 | 위험작업 | 상태 | 액션 |
|---|-----|--------|---------|---------|---------|--------|---------|---------|------|------|
- 진행율: 프로그레스 바 (`progress_rate` 0~100)
- 위험작업: `is_high_risk=true` 시 뱃지 `⚠️ 위험`
- 상태 배지: PLANNED/IN_PROGRESS/DONE
- 행 드래그: `sort_order` PATCH

#### KCSC 공정 연동
```js
GET /construction/kcsc/processes?search={q}&size=20
// → 선택 시 kcsc_process_id, work_type_code 자동 세팅
```

### 코드 포인트
```js
// 진행율 인라인 수정 (슬라이더)
async function updateProgress(processId, rate) {
  await fetch(`${API}/construction/processes/${processId}`, {
    method: 'PATCH', headers: hdr(),
    body: JSON.stringify({ progress_rate: rate })
  });
}

// 실제 시작일 자동 세팅 (상태 IN_PROGRESS 변경 시)
if (newStatus === 'IN_PROGRESS' && !row.actual_start) {
  body.actual_start = new Date().toISOString().slice(0, 10);
}
```

---

## 5. construction-worker-list.html — 작업자관리

### 목적
`worker-list.html`(eba689f0, 35,165 bytes)을 건설현장 작업자 전용으로 재활용.  
시설관리 `worker_registry` 기반 → 건설 `construction_workers` 기반으로 교체.

### API
```
GET    /construction/sites/:site_id/workers?worker_type=&entry_status=&search=&page=&size=
POST   /construction/sites/:site_id/workers
GET    /construction/workers/:worker_id
PATCH  /construction/workers/:worker_id
PATCH  /construction/workers/:worker_id/entry   ← 출입 상태 변경 (IN/OUT/OFFSITE)
DELETE /construction/workers/:worker_id
```

### 변경 사항 (원본 worker-list.html 대비)

#### 테이블 컬럼
| # | No. | 이름 | 구분 | 소속(하도급) | 역할 | 출입상태 | 안전교육일 | 입사일 | 출입변경 | 액션 |
|---|-----|------|------|------------|------|---------|----------|--------|---------|------|
- 구분 배지: `DIRECT`=직영(파란), `SUBCON`=하도급(회색)
- 출입상태 뱃지: `IN`=초록, `OUT`=회색, `OFFSITE`=주황
- 출입변경: 인라인 버튼 → PATCH `/entry`

#### 통계 카드
```
[전체 N] [현장내(IN) N] [직영 N] [하도급 N]
```

### 코드 포인트
```js
// 출입 상태 변경
async function changeEntry(workerId, status) {
  await fetch(`${API}/construction/workers/${workerId}/entry`, {
    method: 'PATCH', headers: hdr(),
    body: JSON.stringify({ entry_status: status })
  });
  refreshRow(workerId);
  showToast('success', status === 'IN' ? '입장 처리됐습니다.' : '퇴장 처리됐습니다.');
}

const ENTRY = { IN: '현장내', OUT: '퇴장', OFFSITE: '현장외' };
```

---

## 6. worker-check-construction.html — 작업자 건설점검

### 목적
`worker-check.html`(2535ab23, 10,794 bytes)을 건설 작업자 점검용으로 재활용.  
작업자가 **작업 전 체크리스트를 직접 제출**하는 모바일 우선 화면.  
제출 → `POST /construction/sites/:site_id/inspections` 호출.  
이상 감지 시 관리자 FCM 자동 발송 (API v2.1.0 자동 처리).

### 변경 사항 (원본 대비)

#### 변경 1: URL 파라미터
```
원본: ?factory_id=xxx&set_id=xxx
건설: ?site_id=xxx&work_id=xxx  (work_id는 선택사항)
```

#### 변경 2: 기본 체크리스트
```js
const DEFAULT_CHECKLIST = [
  { id: 'c1', name: 'PPE(안전모/조끼/안전화) 착용 확인' },
  { id: 'c2', name: '작업구역 안전 펜스 설치 확인' },
  { id: 'c3', name: '위험물질 취급 안전 절차 확인' },
  { id: 'c4', name: '비상연락망 및 소화기 위치 확인' },
  { id: 'c5', name: '장비/공구 이상 유무 확인' },
];
```

#### 변경 3: 제출 API (v2.1.0 기준)
```js
const payload = {
  work_id: workId || null,
  inspection_date: new Date().toISOString(),
  inspector_id: localStorage.getItem('user_id'),
  inspection_type: 'BEFORE_WORK',
  checklist_items: items.map(i => ({
    item_name: i.name,
    result: i.result,  // 'good' | 'bad'
    note: i.note || ''
  })),
  // overall_result 생략 → API가 자동 계산 + FCM 자동 발송
};
POST /construction/sites/{site_id}/inspections
```

#### 변경 4: 제출 후 처리
```js
if (j.data.overall_result === 'ISSUE') {
  // FCM은 API가 이미 자동 발송 완료
  showResult('⚠️ 이상 항목이 감지됐습니다. 관리자에게 자동 보고됐습니다.', 'warning');
} else {
  showResult('✅ 점검 완료. 안전하게 작업해주세요!', 'success');
}
```

---

## 공통 개발 가이드

### 현장 셀렉터 공통 패턴
```html
<div class="card mb-3" style="background:linear-gradient(135deg,#d97706,#92400e);border:none;">
  <div class="card-body py-3">
    <label class="form-label text-white small mb-1" style="opacity:.8">현장 선택</label>
    <select id="siteSelect" class="form-select" style="max-width:480px" onchange="onSiteChange()">
      <option value="">현장을 선택하세요</option>
    </select>
  </div>
</div>
```

### localStorage 키 규칙
```js
localStorage.getItem('company_id')                       // 회사 ID
localStorage.getItem('selectedConstructionSiteId')        // 현장 ID (construction_sites.id)
localStorage.getItem('selectedConstructionFactoryId')     // factory ID (inspection-sets 연동용)
```

### 상태코드 배지 컬러
```js
const STATUS_CLR = {
  PLANNED: 'secondary', IN_PROGRESS: 'primary',
  DONE: 'success',      SUSPENDED: 'warning',
};
const ENTRY_CLR  = { IN: 'success', OUT: 'secondary', OFFSITE: 'warning' };
const RESULT_CLR = { PASS: 'success', ISSUE: 'warning', FAIL: 'danger' };
const WORKER_CLR = { DIRECT: 'primary', SUBCON: 'secondary' };
```

### 테이블 공통 규칙 (전사 표준)
- 1번 컬럼: 전체선택 체크박스
- 2번 컬럼: No. (1부터 순번)
- 이후 데이터 컬럼

---

## 개발 순서 권장

```
1. construction-site-list.html  ← 나머지 화면의 site_id 공급자
2. construction-process.html    ← 공정이 있어야 작업관리 연결 가능
3. construction-worker-list.html
4. construction-inspection-list.html
5. construction-inspection-anchor.html  ← factory_id 생성 후 가능
6. worker-check-construction.html       ← 가장 마지막 (작업자 facing)
```

---

## 참고 파일 SHA (작성 시점)

| 파일 | SHA | 크기 |
|------|-----|------|
| inspection-anchor.html | 5afb9f1b | 49,121 |
| worker-list.html | eba689f0 | 35,165 |
| worker-check.html | 2535ab23 | 10,794 |
| construction-site-list.html (기존) | f00b3509 | 20,468 |
| construction-inspection-list.html (기존) | 1630775e | 21,710 |
| construction-process-list.html (기존) | 47b9964a | 20,292 |
| construction-worker-list.html (기존) | f3a87abd | 16,850 |
