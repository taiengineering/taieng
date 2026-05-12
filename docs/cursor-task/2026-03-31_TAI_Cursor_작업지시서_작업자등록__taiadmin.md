# TAI 작업지시서 — 작업자 등록 (수동 + 파일 업로드)

> 우선순위: 🔴 긴급  
> 작성일: 2026-03-31  
> 관련 레포: tai-admin (프론트) + tai-api (백엔드)

---

## 결정된 설계 원칙

- 안전관리자가 직접 등록 (수동 or 파일 업로드)
- **포지션(직종) 필수 입력** → 법령 기반 필수 교육 자동 도출에 사용
- 작업자는 로그인 없이 앱 초대 문자 → 간편 가입
- DB: `worker_registry` 테이블 (migration 완료)
- 직종 코드: `system_codes.worker_job_type` (WJT001~WJT020, 20건 등록 완료)

---

## DB 현황 (migration 완료)

```
worker_registry       — 작업자 명부
education_assignment  — 교육 발령
system_codes          — worker_job_type 직종 20건 추가
```

---

## 작업 1 (백엔드): worker_registry API

### 1-1. 수동 등록
```
POST /worker-registry
{
  "factory_id": "uuid",
  "name": "홍길동",          -- 필수
  "phone": "010-1234-5678", -- 필수
  "job_type_code": "WJT003",-- 필수 (포지션)
  "contractor_name": "(주)ABC건설",
  "start_date": "2026-04-01"
}
```

### 1-2. 파일 업로드 (엑셀 일괄 등록)
```
POST /worker-registry/bulk-import
Content-Type: multipart/form-data
  file: workers.xlsx
  factory_id: uuid

-- 엑셀 컬럼 순서 (첫 행 = 헤더)
이름 | 연락처 | 직종 | 소속업체 | 입사일
홍길동 | 010-1234-5678 | 용접공 | (주)ABC | 2026-04-01

-- 처리 로직:
1. 직종명 → WJT 코드 자동 매핑 (job_type_name ILIKE 매칭)
2. 직종 매핑 실패 시 → WJT020(기타) 처리 + 검토 목록 반환
3. 중복 전화번호 → 업데이트 (INSERT ON CONFLICT)
4. 결과 반환: { created: n, updated: n, failed: [...] }
```

### 1-3. 목록 조회
```
GET /worker-registry?factory_id=&job_type_code=&is_active=&keyword=&page=&size=
```

### 1-4. 수정 / 비활성화
```
PATCH /worker-registry/{id}
DELETE /worker-registry/{id}  -- soft delete (is_active=false)
```

### 1-5. 앱 초대 문자 발송
```
POST /worker-registry/{id}/invite
→ 문자 발송: "[TAI Safe] 홍길동님, 앱을 설치해 주세요. https://w.taieng.co.kr"
→ invite_sent_at 업데이트
```

### 1-6. 엑셀 템플릿 다운로드
```
GET /worker-registry/template
→ workers_template.xlsx 반환
→ 컬럼: 이름(*), 연락처(*), 직종(*), 소속업체, 입사일
```

---

## 작업 2 (프론트): `worker-list.html` 신규

### 위치
`tadmin/full-version/html/horizontal-menu-template/worker-list.html`

### 화면 구성

```
┌─────────────────────────────────────────────────┐
│ 작업자 관리                    [+ 수동 등록]       │
│                               [↑ 파일 업로드]     │
│                               [📥 템플릿 다운로드] │
├─────────────────────────────────────────────────┤
│ 시설 [전체▼] 직종 [전체▼] 상태 [전체▼] [검색]     │
├─────────────────────────────────────────────────┤
│ □ No. │ 이름 │ 연락처 │ 직종 │ 소속업체 │ 앱설치 │ 상태 │ 등록일 │
│ □  1  │ 홍길동│ 010-... │ 용접공 │ ABC건설 │ ✅ │ 재직 │ 2026.4.1 │
│ □  2  │ 김철수│ 010-... │ 철근공 │ ABC건설 │ ❌ │ 재직 │ 2026.4.1 │
└─────────────────────────────────────────────────┘
```

### 수동 등록 패널 (사이드 패널)

```html
<!-- 필수 필드 -->
<input id="wp-name"  placeholder="이름 *" required>
<input id="wp-phone" placeholder="연락처 * (010-0000-0000)" required>
<select id="wp-job-type" required>
  <!-- system_codes.worker_job_type 목록 -->
  <option value="">직종 선택 * (필수)</option>
  <option value="WJT001">사무직</option>
  <option value="WJT003">용접공</option>
  ...
</select>

<!-- 선택 필드 -->
<input id="wp-contractor" placeholder="소속 업체명">
<input id="wp-start-date" type="date" placeholder="입사일">
<select id="wp-factory"><!-- 시설 선택 --></select>
```

### 파일 업로드 모달

```html
<div class="modal" id="bulkUploadModal">
  <h5>작업자 일괄 등록</h5>
  
  <!-- 1단계: 템플릿 안내 -->
  <div class="alert alert-info">
    <a href="javascript:downloadTemplate()">📥 엑셀 템플릿 다운로드</a>
    후 작성하여 업로드하세요.
    <br>필수 컬럼: <strong>이름, 연락처, 직종</strong>
  </div>
  
  <!-- 2단계: 파일 선택 -->
  <input type="file" id="bulkFile" accept=".xlsx,.xls,.csv">
  
  <!-- 3단계: 미리보기 테이블 (업로드 후) -->
  <div id="previewArea" style="display:none">
    <p>총 <span id="previewCount">0</span>건 확인됨</p>
    <table id="previewTable"><!-- 미리보기 --></table>
    <!-- 직종 매핑 실패 항목 경고 -->
    <div id="mappingWarning" class="alert alert-warning d-none">
      ⚠️ 직종을 찾을 수 없는 항목이 있습니다. 확인 후 등록하세요.
    </div>
  </div>
  
  <button onclick="confirmBulkUpload()">등록하기</button>
</div>
```

### 파일 업로드 JS 핵심 로직

```javascript
// SheetJS(XLSX) 로 파일 파싱 후 미리보기
async function previewFile(file) {
  const data = await file.arrayBuffer();
  const wb = XLSX.read(data);
  const rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]]);
  
  // 컬럼명 정규화 (한글 컬럼명 허용)
  const normalized = rows.map(r => ({
    name:            r['이름'] || r['name'] || '',
    phone:           r['연락처'] || r['phone'] || '',
    job_type_name:   r['직종'] || r['job_type'] || '',
    contractor_name: r['소속업체'] || r['contractor'] || '',
    start_date:      r['입사일'] || r['start_date'] || ''
  }));
  
  renderPreview(normalized);
}

// 등록 확정
async function confirmBulkUpload() {
  const formData = new FormData();
  formData.append('file', document.getElementById('bulkFile').files[0]);
  formData.append('factory_id', selectedFactoryId);
  
  const res = await apiCall('POST', '/worker-registry/bulk-import', formData);
  showToast('success', `등록 완료: ${res.data.created}건, 수정: ${res.data.updated}건`);
  
  if (res.data.failed?.length) {
    showToast('warning', `처리 실패 ${res.data.failed.length}건 — 확인 필요`);
  }
  loadList();
}
```

### 앱 초대 버튼

```javascript
// 개별 초대
async function sendInvite(workerId) {
  await apiCall('POST', `/worker-registry/${workerId}/invite`);
  showToast('success', '초대 문자가 발송됐습니다.');
}

// 미설치자 일괄 초대
async function sendBulkInvite() {
  const ids = getCheckedIds();
  await Promise.all(ids.map(id => apiCall('POST', `/worker-registry/${id}/invite`)));
  showToast('success', `${ids.length}명에게 초대 문자를 발송했습니다.`);
}
```

---

## 작업 3: 엑셀 템플릿 파일

`tadmin/full-version/assets/templates/workers_template.xlsx`

헤더 행:
```
A1: 이름(필수)  B1: 연락처(필수)  C1: 직종(필수)  D1: 소속업체  E1: 입사일
```

직종 참고 시트 추가:
```
WJT001: 사무직
WJT002: 생산직(일반)
WJT003: 용접공
... 20종
```

---

## 직종 → 필수교육 자동 도출 (향후 연동)

작업자 등록 시 직종이 입력되면, 아래 교육이 자동 배정됩니다:

| 직종 | 필수 교육 |
|------|----------|
| 전체 | 채용시교육, 정기교육(분기) |
| 용접공 | 특별교육(유해·위험작업) 16h |
| 고소작업자 | 특별교육(고소작업) 16h |
| 밀폐공간 작업자 | 특별교육(밀폐공간) 16h |
| 지게차 운전원 | 특별교육 16h |
| 관리감독자 | 관리감독자 정기교육 16h/년 |

→ `education_assignment` 자동 생성 (추후 구현)

---

## 완료 체크리스트

```
백엔드 (tai-api)
□ POST   /worker-registry                — 수동 등록
□ POST   /worker-registry/bulk-import    — 엑셀 일괄 등록
□ GET    /worker-registry                — 목록 조회
□ GET    /worker-registry/template       — 엑셀 템플릿 다운로드
□ PATCH  /worker-registry/{id}           — 수정
□ DELETE /worker-registry/{id}           — 비활성화
□ POST   /worker-registry/{id}/invite    — 앱 초대 문자 발송

프론트 (tai-admin)
□ worker-list.html 신규 생성
□ 수동 등록 사이드 패널
□ 파일 업로드 모달 (SheetJS 파싱 + 미리보기)
□ 엑셀 템플릿 다운로드
□ 앱 초대 버튼 (개별 + 일괄)
□ menu-tadmin.js 메뉴 연결 확인
□ GitHub push
```
