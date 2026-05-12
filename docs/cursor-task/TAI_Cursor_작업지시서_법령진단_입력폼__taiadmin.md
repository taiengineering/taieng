# TAI Cursor 작업지시서 — 법령진단 1단계 입력폼

> 우선순위: 🔴 긴급  
> 작성일: 2026-03-29  
> 레포: taiengineering/tai-admin  
> 대상: **신규 파일** `site/full-version/html/horizontal-menu-template/diagnosis-step1.html`

---

## 개요

법령진단 1단계 입력폼 페이지입니다.  
기존 `factory-list.html` 레이아웃을 기반으로 신규 생성합니다.

- **파일 위치:** `site/full-version/html/horizontal-menu-template/diagnosis-step1.html`
- **API:** `POST https://api.taieng.co.kr/legal-engine/diagnose/step1`
- **인증:** localStorage `access_token` 확인

---

## 페이지 전체 요건

```
1. 섹터 선택 카드 4개 (클릭 시 해당 폼만 표시)
2. 섹터별 입력폼 (아래 상세 참고)
3. [진단하기] 버튼 → API 호출
4. 결과 섹션 (법령 배지 / 의무 목록 / 룰 테이블 / 2단계 유도)
```

---

## 1. 섹터 선택 카드

```html
<div class="row g-3 mb-4" id="sectorCards">
  <div class="col-6 col-md-3">
    <div class="card sector-card h-100 cursor-pointer border-2" data-sector="BUILDING" onclick="selectSector('BUILDING')">
      <div class="card-body text-center py-4">
        <i class="bx bx-building-house bx-lg text-primary mb-2 d-block"></i>
        <h6 class="mb-1">건물·시설</h6>
        <small class="text-muted">소방·전기·산안법</small>
      </div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card sector-card h-100 cursor-pointer border-2" data-sector="MANUFACTURING" onclick="selectSector('MANUFACTURING')">
      <div class="card-body text-center py-4">
        <i class="bx bx-factory bx-lg text-warning mb-2 d-block"></i>
        <h6 class="mb-1">공장·제조업</h6>
        <small class="text-muted">산안법·위험물·화관법</small>
      </div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card sector-card h-100 cursor-pointer border-2" data-sector="CONSTRUCTION" onclick="selectSector('CONSTRUCTION')">
      <div class="card-body text-center py-4">
        <i class="bx bx-hard-hat bx-lg text-danger mb-2 d-block"></i>
        <h6 class="mb-1">건설현장</h6>
        <small class="text-muted">공사금액 기준</small>
      </div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card sector-card h-100 cursor-pointer border-2" data-sector="SPECIAL_FACILITY" onclick="selectSector('SPECIAL_FACILITY')">
      <div class="card-body text-center py-4">
        <i class="bx bx-plus-medical bx-lg text-success mb-2 d-block"></i>
        <h6 class="mb-1">특수시설</h6>
        <small class="text-muted">병원·학교·복지시설</small>
      </div>
    </div>
  </div>
</div>
```

선택 로직:
```javascript
let selectedSector = null;
function selectSector(sector) {
  selectedSector = sector;
  // 모든 카드 기본 스타일
  document.querySelectorAll('.sector-card').forEach(c => {
    c.classList.remove('border-primary', 'bg-light');
  });
  // 선택 카드 강조
  document.querySelector(`[data-sector="${sector}"]`).classList.add('border-primary', 'bg-light');
  // 폼 표시 제어
  document.querySelectorAll('.sector-form').forEach(f => f.classList.add('d-none'));
  document.getElementById(`form-${sector}`).classList.remove('d-none');
}
```

---

## 2. 섹터별 입력폼

### BUILDING 폼 (`id="form-BUILDING"`)

| 필드명 | 타입 | name 속성 | 단위 |
|-------|------|---------|------|
| 건물 용도 | select | building_use_category | - |
| 연면적 | number | gross_floor_area | ㎡ |
| 지상 층수 | number | above_ground_floors | 층 |
| 상시 근로자수 | number | worker_count | 명 |
| 수전용량 | number | electric_capacity_kw | kW |
| 고압가스 사용 | checkbox | has_high_pressure_gas | Y/N |
| 위험물 취급 | checkbox | has_hazardous_material | Y/N |

건물 용도 select 옵션:
```
업무시설, 판매시설, 의료시설, 노유자시설,
숙박시설, 교육연구시설, 창고시설, 공장, 위락시설, 기타
```

### MANUFACTURING 폼 (`id="form-MANUFACTURING"`)

| 필드명 | 타입 | name |
|-------|------|------|
| KSIC 대분류 | select | ksic_lv1_code |
| 상시 근로자수 | number | worker_count |
| 수전용량 (kW) | number | electric_capacity_kw |
| 위험물 취급 | checkbox | has_hazardous_material |
| 고압가스 사용 | checkbox | has_high_pressure_gas |
| 화학물질 취급 | checkbox | has_chemical_substance |
| 보일러 설치 | checkbox | has_boiler |

KSIC select 옵션:
```
C10 음식료품, C13 섬유, C17 종이?,
C19 석유정제, C20 화학제품, C21 의약품,
C24 1차금속, C25 금속가공,
C28 기계, C29 자동차, C30 항공우주, 기타
```

### CONSTRUCTION 폼 (`id="form-CONSTRUCTION"`)

| 필드명 | 타입 | name | 단위 |
|-------|------|------|------|
| 공사금액 (억) | number | contract_amount_eok | 억원 |
| 공사 종류 | select | construction_type | - |
| 상시 근로자수 | number | worker_count | 명 |
| 터널·교량 포함 | checkbox | has_tunnel_bridge | Y/N |

⚠️ 공사금액 억 단위 입력 → API 호출 시 ×100000000 변환:
```javascript
// 억 단위 입력 필드
const eok = parseFloat(document.getElementById('contract_amount_eok').value || 0);
const wonValue = eok * 100000000;
// API body에는 contract_amount: wonValue 로 전달
```

공사 종류: `건축공사 / 토목공사 / 전문공사`

### SPECIAL_FACILITY 폼 (`id="form-SPECIAL_FACILITY"`)

| 필드명 | 타입 | name |
|-------|------|------|
| 시설 유형 | select | facility_type |
| 연면적 (㎡) | number | gross_floor_area |
| 병상수 (병원) | number | hospital_beds |
| 학생수 (학교) | number | student_count |
| 상시 근로자수 | number | worker_count |

시설 유형: `병원 / 요양병원 / 학교 / 복지시설 / 다중이용업소 / 어린이집 / 위험물창고`

---

## 3. API 호출 함수

```javascript
const BASE_URL = 'https://api.taieng.co.kr';

async function runDiagnosis() {
  if (!selectedSector) {
    showToast('danger', '섹터를 먼저 선택해주세요.');
    return;
  }
  const factory_id = new URLSearchParams(location.search).get('factory_id')
                  || localStorage.getItem('selected_factory_id');
  if (!factory_id) {
    showToast('warning', '시설을 먼저 선택해주세요.');
    return;
  }

  const input = getFormInput();
  showLoadingOverlay(true);

  try {
    const token = localStorage.getItem('access_token');
    const resp = await fetch(`${BASE_URL}/legal-engine/diagnose/step1`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ factory_id, sector: selectedSector, input })
    });
    const data = await resp.json();
    if (data.status === 'success') showResult(data);
    else showToast('danger', data.detail || '오류가 발생했습니다.');
  } catch(e) {
    showToast('danger', '네트워크 오류가 발생했습니다.');
  } finally {
    showLoadingOverlay(false);
  }
}

function getFormInput() {
  const form = document.getElementById(`form-${selectedSector}`);
  const inputs = form.querySelectorAll('input, select');
  const obj = {};
  inputs.forEach(el => {
    if (!el.name) return;
    if (el.type === 'checkbox') obj[el.name] = el.checked;
    else if (el.name === 'contract_amount_eok') {
      obj['contract_amount'] = parseFloat(el.value || 0) * 100000000;
    } else {
      const v = parseFloat(el.value);
      obj[el.name] = isNaN(v) ? el.value : v;
    }
  });
  return obj;
}
```

---

## 4. 결과 표시 함수

```javascript
function showResult(data) {
  const s = data.summary || {};
  document.getElementById('resultSection').classList.remove('d-none');

  // 리스크 배지
  const badge = document.getElementById('riskBadge');
  const level = s.risk_level || 'LOW';
  badge.textContent = level;
  badge.className = 'badge ' + (level==='HIGH'?'bg-danger':level==='MEDIUM'?'bg-warning':'bg-success');

  // 적용 법령 배지
  const lawDiv = document.getElementById('lawCategories');
  lawDiv.innerHTML = (s.applicable_law_categories || []).map(
    l => `<span class="badge bg-label-primary me-1 mb-1">${l}</span>`
  ).join('');

  // 선임 의무
  document.getElementById('appointmentAlert').classList.toggle('d-none', !s.appointment_required);

  // 주요 의무 목록
  const ul = document.getElementById('obligationList');
  ul.innerHTML = (s.key_obligations || []).map(
    o => `<li class="list-group-item"><i class="bx bx-check-circle text-success me-2"></i>${o}</li>`
  ).join('');

  // 룰 테이블
  const tbody = document.getElementById('rulesBody');
  tbody.innerHTML = (data.rules || []).map(r =>
    `<tr><td>${r.law_name||''}</td><td><small class="text-muted">${r.law_article||''}</small></td><td>${r.obligation||r.rule_name||''}</td></tr>`
  ).join('');

  // 스크롤
  document.getElementById('resultSection').scrollIntoView({behavior:'smooth'});
}
```

---

## 5. 공통 주의사항

- **Navbar/Footer**: `factory-list.html` 내용 그대로 인라인 삽입
- **BASE_URL**: `const BASE_URL = 'https://api.taieng.co.kr';` 스크립트 상단
- **로그인 체크**: `if (!localStorage.getItem('access_token')) location.href = 'auth-login-cover.html';`
- **system_codes**: 기존 패턴대로 GET /system-codes 로드
- **showToast**: 기존 factory-list.html showToast() 함수 동일하게
- **미리보기**: 커서를 이용한 로컠 브라우저에서 확인

---

## 완료 체크리스트

```
□ diagnosis-step1.html 파일 생성
   (경로: site/full-version/html/horizontal-menu-template/diagnosis-step1.html)
□ 섹터 선택 카드 4개
□ 카드 클릭 → 선택 강조 + 폼 표시
□ BUILDING 입력폼
□ MANUFACTURING 입력폼
□ CONSTRUCTION 입력폼 (억 단위 편의 구현)
□ SPECIAL_FACILITY 입력폼
□ [진단하기] 다음 점 확인:
   - factory_id: URL 파라미터 또는 localStorage
   - 앥세스 토큰 헤더 포함
   - POST /legal-engine/diagnose/step1 정상 호출
□ 결과 섹션:
   - 리스크 레벨 배지
   - 적용 법령 배지 목록
   - 선임 의무 경고
   - 주요 의무 목록
   - 룰 테이블
   - 2단계 유도 바너
□ GitHub push 완료
```
