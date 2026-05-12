# Cursor 작업지시서 — 건설 법령진단 프론트 재설계

> 작성일: 2026-04-01
> 대상 파일: diagnosis-step1.html (수정), construction-diagnosis-step2.html (신규), construction-diagnosis-step3.html (신규), diagnosis-result.html (수정)

---

## 작업 1. diagnosis-step1.html — CONSTRUCTION 폼 개선

### 현재 문제
- 근로자수 1개 필드 → 직접근로자/하도급근로자 구분 없음
- construction_summary 미리보기 없음
- 진단 후 건설 전용 결과 화면으로 이동 안 됨

### 수정 내용

#### 1-1. CONSTRUCTION 폼 교체 (id="form-CONSTRUCTION")
```html
<div id="form-CONSTRUCTION" class="card mb-4 sector-form d-none">
  <div class="card-header d-flex justify-content-between align-items-center">
    <h5 class="mb-0">🏗️ 건설현장</h5>
    <span class="badge bg-label-danger">건설 섹터</span>
  </div>
  <div class="card-body">
    <div class="row g-3">
      <!-- 공사종류 -->
      <div class="col-md-4">
        <label class="form-label fw-semibold">공사종류 <span class="text-danger">*</span></label>
        <select class="form-select" id="c-type">
          <option value="">선택</option>
          <!-- system_codes에서 로드 -->
        </select>
      </div>

      <!-- 공사금액 -->
      <div class="col-md-4">
        <label class="form-label fw-semibold">공사금액 (억 원) <span class="text-danger">*</span></label>
        <input type="number" class="form-control" id="c-eok" min="0" step="0.01" value="0"/>
        <div class="form-text" id="c-eok-hint">—</div>
      </div>

      <!-- 터널·교량 -->
      <div class="col-md-4 d-flex align-items-center pt-3">
        <div class="form-check form-switch mt-2">
          <input class="form-check-input" type="checkbox" id="c-tunnel"/>
          <label class="form-check-label" for="c-tunnel">터널·교량 포함</label>
        </div>
      </div>

      <!-- 근로자 구분 -->
      <div class="col-12"><hr class="my-0"/></div>
      <div class="col-md-4">
        <label class="form-label fw-semibold">직접 근로자수</label>
        <input type="number" class="form-control" id="c-direct" min="0" value="0"/>
      </div>
      <div class="col-md-4">
        <label class="form-label fw-semibold">하도급 근로자수</label>
        <input type="number" class="form-control" id="c-subcon" min="0" value="0"/>
        <div class="form-text text-body-secondary">산안법 시행령 제16조③ — 하도급 포함</div>
      </div>
      <div class="col-md-4 d-flex align-items-end pb-1">
        <div class="p-2 rounded bg-light w-100 text-center">
          합계: <strong id="c-workers-total" class="text-primary">0</strong>명
        </div>
      </div>

      <!-- 안전관리자 선임 미리보기 -->
      <div class="col-12" id="c-sm-preview-wrap" style="display:none;">
        <div class="alert mb-0" id="c-sm-alert">
          <!-- JS로 채움 -->
        </div>
      </div>
    </div>
  </div>
</div>
```

#### 1-2. JavaScript에 실시간 선임 판정 추가 (기존 스크립트 내부에 추가)
```javascript
// CONSTRUCTION 실시간 판정
function updateConsmPreview() {
  var siteType = (document.getElementById('c-type') || {}).value || '';
  var eok = parseFloat((document.getElementById('c-eok') || {}).value) || 0;
  var direct = parseInt((document.getElementById('c-direct') || {}).value, 10) || 0;
  var subcon = parseInt((document.getElementById('c-subcon') || {}).value, 10) || 0;
  var total = direct + subcon;
  var totalEl = document.getElementById('c-workers-total');
  if (totalEl) totalEl.textContent = total;

  var wrap = document.getElementById('c-sm-preview-wrap');
  var alert = document.getElementById('c-sm-alert');
  if (!wrap || !alert || !siteType) return;

  var threshold = siteType === 'CIVIL' ? 120 : 150;
  var smByAmt = eok >= threshold;
  var smByWorker = total >= 50;
  var smRequired = smByAmt || smByWorker;

  wrap.style.display = '';
  var hintEl = document.getElementById('c-eok-hint');

  if (smRequired) {
    alert.className = 'alert alert-warning mb-0';
    var reasons = [];
    if (smByAmt) reasons.push('공사금액 ' + threshold + '억원 이상');
    if (smByWorker) reasons.push('근로자 ' + total + '명(하도급 포함) ≥ 50명');
    alert.innerHTML = '<i class="ti tabler-alert-triangle me-1"></i><strong>안전관리자 선임 의무 발생</strong> — ' + reasons.join(', ');
    if (hintEl) hintEl.className = 'form-text text-warning';
    if (hintEl) hintEl.textContent = '⚠️ ' + threshold + '억 이상 → 안전관리자 선임 의무';
  } else {
    alert.className = 'alert alert-success mb-0';
    alert.innerHTML = '<i class="ti tabler-check me-1"></i>현재 조건에서 안전관리자 선임 의무 없음 (기타 산안법 의무는 1단계 진단 후 확인)';
    if (hintEl) hintEl.className = 'form-text text-body-secondary';
    if (hintEl) hintEl.textContent = threshold + '억 미만';
  }

  // key thresholds 안내
  var hints = [];
  if (eok >= 1) hints.push('✓ 산안관리비 계상(1억↑)');
  if (eok >= 50) hints.push('✓ 유해위험방지계획서(50억↑)');
  if (eok >= 100) hints.push('✓ 안전관리계획서(100억↑)');
  if (eok >= 200) hints.push('✓ 안전보건관리책임자(200억↑)');
  if (eok >= 1000) hints.push('✓ 건설안전판정사(1000억↑)');
  if (hints.length) {
    alert.innerHTML += '<div class="small mt-1 text-body-secondary">' + hints.join(' | ') + '</div>';
  }
}

// 이벤트 바인딩
['c-eok', 'c-direct', 'c-subcon', 'c-type'].forEach(function(id) {
  var el = document.getElementById(id);
  if (el) el.addEventListener('input', updateConsmPreview);
  if (el) el.addEventListener('change', updateConsmPreview);
});
```

#### 1-3. getFormInput CONSTRUCTION 분기 수정
```javascript
if (sector === 'CONSTRUCTION') return {
  contract_amount_eok: parseFloat(document.getElementById('c-eok').value) || 0,
  construction_type: (document.getElementById('c-type') && document.getElementById('c-type').value) || 'BUILDING',
  worker_count: parseInt(document.getElementById('c-direct').value, 10) || 0,
  direct_workers: parseInt(document.getElementById('c-direct').value, 10) || 0,
  subcon_workers: parseInt(document.getElementById('c-subcon').value, 10) || 0,
  has_tunnel_bridge: !!(document.getElementById('c-tunnel') && document.getElementById('c-tunnel').checked)
};
```

#### 1-4. 진단 완료 후 분기 처리
```javascript
// 기존 runDiagnosis() 내부 location.href 분기 수정
if (selectedSector === 'CONSTRUCTION') {
  // 건설 전용: construction-diagnosis-step2.html로 이동
  var q = new URLSearchParams({ sector: 'CONSTRUCTION' });
  if (factoryId) q.set('factory_id', factoryId);
  if (did) q.set('diagnosis_id', did);
  location.href = 'construction-diagnosis-step2.html?' + q.toString();
} else {
  location.href = 'diagnosis-result.html?' + q.toString();
}
```

---

## 작업 2. construction-diagnosis-step2.html — 공정 선택 & 2단계 진단 (신규)

### 화면 구조
```
[스테퍼] ✓1단계 → ②공정선택 → ③작업/설비 → ④결과

[Hero 헤더]
  "건설 법령진단 · 2단계"
  "현장에서 진행하는 KCSC 공정을 선택하세요. 공종별 법령 의무가 자동 판정됩니다."

[construction_summary 카드] — step1 결과에서 가져옴
  공사금액: 200억 | 공사종류: 건축 | 근로자: 80명
  안전관리자 선임: ⚠️ 필요 (150억↑)
  [달성 임계값 배지들]

[공정 선택 영역]
  [필터] 공사구분: 전체 | 건축 | 토목 | 공통
         검색창: 공정명 검색
  [공정 목록] - 체크박스 + 공정명 + risk_level 배지 + work_type_label
    □ 가설공사        HIGH  | 고소작업(2m이상)
    □ 거푸집 및 동바리 HIGH  | 거푸집/동바리
    □ 일반콘크리트    MEDIUM | 콘크리트타설작업
    ...
  [선택된 공정] 하단 요약: N개 선택됨

[2단계 진단 실행 버튼]
[이전 단계] 링크
```

### API
```javascript
// 공정 목록 로드
GET /construction/kcsc/processes?construction_type=&search=&page=1&size=100

// 2단계 진단 실행
POST /legal-engine/diagnose/step2
body: {
  factory_id,
  diagnosis_id,  // step1 결과
  kcsc_process_ids: [선택된 공정 UUID 배열]
}

// 완료 후 이동
→ construction-diagnosis-step3.html?factory_id=&diagnosis_id=&sector=CONSTRUCTION
```

### 핵심 코드
```javascript
// URL params에서 step1 결과 읽기
var params = new URLSearchParams(location.search);
var factoryId = params.get('factory_id');
var diagnosisId = params.get('diagnosis_id');

// step1 결과 sessionStorage에서 가져오기
var step1Cache = {};
try {
  var cached = sessionStorage.getItem('tai_diagnosis_step1');
  if (cached) step1Cache = JSON.parse(cached).data || {};
} catch(e) {}

// construction_summary 카드 렌더링
var cs = step1Cache.construction_summary || {};
// site_type, contract_amount_eok, total_workers, safety_manager_required
// key_thresholds_met 배지들 표시

// 공정 로드 & 필터링
async function loadProcesses(constructionType, search) {
  var q = '/construction/kcsc/processes?page=1&size=100';
  if (constructionType && constructionType !== 'ALL') q += '&construction_type=' + constructionType;
  if (search) q += '&search=' + encodeURIComponent(search);
  var res = await apiCall('GET', q);
  return (res.data && res.data.items) || (res.data) || [];
}

// 공정 카드 렌더링
function renderProcess(p) {
  var riskBadge = { HIGH: 'bg-danger', MEDIUM: 'bg-warning', LOW: 'bg-success' };
  var riskLabel = { HIGH: '고위험', MEDIUM: '중위험', LOW: '저위험' };
  return '<div class="col-md-6 col-lg-4">' +
    '<label class="d-block border rounded p-2 cursor-pointer process-card" data-id="' + p.id + '">' +
    '<input type="checkbox" class="form-check-input me-2 process-chk" value="' + p.id + '"/>' +
    '<span class="fw-semibold">' + esc(p.process_name) + '</span>' +
    (p.risk_level ? '<span class="badge ' + (riskBadge[p.risk_level]||'bg-secondary') + ' ms-1">' + (riskLabel[p.risk_level]||p.risk_level) + '</span>' : '') +
    (p.work_type_label ? '<div class="small text-body-secondary mt-1">' + esc(p.work_type_label) + '</div>' : '<div class="small text-warning mt-1">법령 미매핑</div>') +
    '</label></div>';
}

// 2단계 실행
async function runStep2() {
  var checked = Array.from(document.querySelectorAll('.process-chk:checked')).map(function(el){ return el.value; });
  if (!checked.length) { showToast('warning', '공정을 하나 이상 선택하세요.'); return; }

  var res = await apiCall('POST', '/legal-engine/diagnose/step2', {
    factory_id: factoryId,
    diagnosis_id: diagnosisId,
    kcsc_process_ids: checked
  });
  var d = res.data || res;
  // sessionStorage에 step2 결과 저장
  try { sessionStorage.setItem('tai_diagnosis_step2', JSON.stringify({ data: d, saved_at: Date.now() })); } catch(e) {}

  var newDiagId = d.diagnosis_id || diagnosisId;
  var q = new URLSearchParams({ factory_id: factoryId, diagnosis_id: newDiagId, sector: 'CONSTRUCTION' });
  location.href = 'construction-diagnosis-step3.html?' + q.toString();
}
```

---

## 작업 3. construction-diagnosis-step3.html — 작업/설비 선택 & 3단계 진단 (신규)

### 화면 구조
```
[스테퍼] ✓1단계 → ✓공정선택 → ③작업/설비 → ④결과

[Hero 헤더]
  "건설 법령진단 · 3단계"
  "현장 위험작업과 설비를 선택하면 법정검사 의무가 자동 판정됩니다."

[2단계 요약 카드] — step2 결과에서
  적용 공종: FORMWORK | REINFORCEMENT | CONCRETE_POUR
  추가 룰 수: N건

[탭] ① 등록된 PTW 작업  |  ② KCSC 작업 마스터 검색

[탭①: PTW 작업 목록]
  현장에 등록된 작업(PTW) 목록
  GET /construction/sites/{site_id}/works?ptw_status=APPROVED
  체크박스로 선택
  작업명 | 작업일 | PTW상태 | KCSC연결여부

[탭②: KCSC 작업 검색]
  위험작업(is_hazardous=true) 자동 필터
  공정명 검색 + is_hazardous 토글
  체크박스로 선택
  작업명 | 위험유형 | 연결 설비코드

[설비코드 미리보기]
  선택된 작업에서 추출된 설비 코드 배지
  예) TCR (타워크레인), WMC (용접기), SCF (비계)

[3단계 진단 실행 버튼]
[이전 단계] | [건너뛰기 (결과 바로보기)]
```

### API
```javascript
// PTW 작업 목록
GET /construction/sites/{site_id}/works?page=1&size=100

// KCSC 작업 마스터 (위험작업)
GET /construction/kcsc/works/{process_id}  // 공정별 작업 목록
// 또는 전체: GET /construction/kcsc/works?is_hazardous=true

// 3단계 실행
POST /legal-engine/diagnose/step3
body: {
  factory_id,
  diagnosis_id,
  construction_work_ids: [PTW 작업 UUID 배열],  // 탭①
  kcsc_work_ids: [KCSC 작업 UUID 배열]          // 탭②
}

// 완료 후
→ diagnosis-result.html?factory_id=&diagnosis_id=&sector=CONSTRUCTION
```

### 설비코드 미리보기
```javascript
// KCSC 작업 체크 시 equipment_type_codes 미리 표시
const EQUIP_LABELS = {
  TCR: '타워크레인', MCR: '이동식크레인', LFT: '건설용리프트',
  GDL: '곤돌라', HST: '호이스트', CPR: '공기압축기',
  CCP: '콘크리트펌프카', WMC: '용접기', SCF: '가설비계', EXC: '굴삭기'
};

function updateEquipPreview(selectedWorks) {
  var codes = new Set();
  selectedWorks.forEach(function(w) {
    (w.equipment_type_codes || []).forEach(function(c) { codes.add(c); });
  });
  var wrap = document.getElementById('equip-preview');
  if (!codes.size) { wrap.innerHTML = '<span class="text-body-secondary small">설비 없음</span>'; return; }
  wrap.innerHTML = Array.from(codes).map(function(c) {
    return '<span class="badge bg-label-primary me-1">' + c + ' ' + (EQUIP_LABELS[c] || '') + '</span>';
  }).join('');
}
```

---

## 작업 4. diagnosis-result.html — construction_summary 블록 추가

기존 diagnosis-result.html의 결과 표시 영역에 건설 전용 블록 추가.

### 추가 위치
결과 카드 상단 (applicable_count 카드들 위)에 아래 블록 조건부 표시:
```javascript
// step1 결과에 construction_summary가 있으면 표시
var cs = (data && data.construction_summary) || null;
if (cs) {
  renderConstructionSummary(cs);
}

function renderConstructionSummary(cs) {
  var el = document.getElementById('construction-summary-block');
  if (!el) return;
  el.classList.remove('d-none');

  var smClass = cs.safety_manager_required ? 'alert-warning' : 'alert-success';
  var smIcon = cs.safety_manager_required ? 'tabler-alert-triangle' : 'tabler-check';
  var smText = cs.safety_manager_required
    ? '안전관리자 선임 의무 발생 — ' + (cs.safety_manager_basis || '')
    : '현재 조건: 안전관리자 선임 의무 없음';

  var thresholds = cs.key_thresholds_met || {};
  var badges = Object.entries(thresholds)
    .filter(function(e){ return e[1]; })
    .map(function(e){
      return '<span class="badge bg-label-primary me-1 mb-1">' + e[0].replace(/_/g,' ') + '</span>';
    }).join('');

  el.innerHTML =
    '<div class="card mb-4 border-warning">' +
    '  <div class="card-header bg-label-warning d-flex gap-3 flex-wrap">' +
    '    <span><strong>공사종류:</strong> ' + esc(cs.site_type || '—') + '</span>' +
    '    <span><strong>공사금액:</strong> ' + esc(cs.contract_amount_eok || 0) + '억원</span>' +
    '    <span><strong>근로자:</strong> ' + esc(cs.total_workers || 0) + '명 (직접 ' + esc(cs.direct_workers||0) + ' + 하도급 ' + esc(cs.subcon_workers||0) + ')</span>' +
    '  </div>' +
    '  <div class="card-body">' +
    '    <div class="alert ' + smClass + ' mb-2 py-2"><i class="ti ' + smIcon + ' me-1"></i>' + esc(smText) + '</div>' +
    '    <div>' + (badges || '<span class="text-body-secondary small">해당 임계값 없음</span>') + '</div>' +
    '  </div>' +
    '</div>';
}
```

### HTML에 블록 삽입
결과 컨테이너 최상단(요약 카드 위)에 추가:
```html
<!-- 건설 섹터 전용 -->
<div id="construction-summary-block" class="d-none"></div>
```

---

## 완료 체크

```
□ diagnosis-step1.html
  □ CONSTRUCTION 폼: 직접/하도급 분리 (c-direct, c-subcon)
  □ 실시간 선임 판정 미리보기 (updateConsmPreview)
  □ getFormInput CONSTRUCTION 분기: direct_workers, subcon_workers 포함
  □ 진단 완료 후 CONSTRUCTION → construction-diagnosis-step2.html로 이동

□ construction-diagnosis-step2.html 신규
  □ 스테퍼 (4단계 표시)
  □ construction_summary 카드 (step1 sessionStorage에서)
  □ KCSC 공정 목록 (GET /construction/kcsc/processes)
  □ 공사구분 필터 (BUILDING/CIVIL/COMMON)
  □ 체크박스 선택 + risk_level 배지 + work_type_label
  □ 법령 미매핑 공정 안내 표시
  □ POST /legal-engine/diagnose/step2 with kcsc_process_ids
  □ 완료 → construction-diagnosis-step3.html

□ construction-diagnosis-step3.html 신규
  □ 스테퍼 (4단계)
  □ step2 요약 카드
  □ 탭①: PTW 등록 작업 목록
  □ 탭②: KCSC 위험작업 검색 (is_hazardous 강조)
  □ 설비코드 미리보기 (equipment_type_codes)
  □ POST /legal-engine/diagnose/step3 with construction_work_ids/kcsc_work_ids
  □ 건너뛰기 버튼 → diagnosis-result.html 직접 이동
  □ 완료 → diagnosis-result.html

□ diagnosis-result.html
  □ construction-summary-block div 추가
  □ renderConstructionSummary() 함수 추가
  □ step1 결과에 construction_summary 있으면 자동 렌더링

□ GitHub push
```
