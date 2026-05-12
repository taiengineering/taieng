# TAI 작업지시서 — 교육 발령·이수 관리 Phase 1

> 우선순위: 🟡  
> 작성일: 2026-03-31  
> 관련 레포: tai-admin (프론트) + tai-api (백엔드)

---

## 전략 방향

콘텐츠 없이 **관리 플랫폼**으로 즉시 서비스

```
안전관리자 → 교육 발령 (누구에게, 어떤 교육, 언제까지)
           ↓
작업자 → 회사별 교육 링크로 이동하여 수강 → 이수증 사진 업로드
           ↓
시스템 → 이수 완료 자동 기록 + 법적 증빙 보관
           ↓
안전관리자 → 전체 이수 현황 대시보드 확인
```

---

## 교육 링크 우선순위 (핵심 설계)

**회사마다 자체 교육 시스템을 사용하므로 링크를 회사별로 관리합니다.**

```
교육 링크 표시 우선순위:
1순위: company_education_setting.custom_url  (회사 직접 설정)
2순위: education_master.source_url           (KOSHA 등 기본값)
3순위: 없음 → "이수증만 업로드" 안내
```

---

## DB 현황 (이미 완료)

```
education_master            20건 (교육 종류 + KOSHA 기본 URL)
education_assignment        발령 관리 테이블
worker_registry             작업자 명부 테이블
company_education_setting   회사별 교육 링크 재정의 테이블 ← NEW
```

### company_education_setting 구조
```
company_id       회사 ID (FK)
education_id     교육 항목 ID (FK)
custom_url       회사 자체 교육 시스템 URL
custom_url_label 링크 표시명 (예: "삼성 안전교육 포털")
custom_note      추가 안내 메시지
is_active        이 교육 항목 활성 여부
UNIQUE(company_id, education_id)
```

---

## 작업 1 (백엔드): 교육 설정 API (회사별 링크)

### 1-1. 회사별 교육 링크 조회
```python
# GET /education/company-settings?company_id=
# Response: education_master 목록 + 회사별 custom_url merge
# {
#   "education_code": "OSH_REG_NONOFFICE",
#   "education_name": "근로자 정기안전보건교육(비사무직)",
#   "source_url": "https://kosha.or.kr/...",       # 기본값
#   "effective_url": "https://company-lms.co.kr",  # 실제 사용 URL
#   "effective_url_label": "회사 교육 포털",
#   "has_custom": true
# }
```

### 1-2. 회사별 교육 링크 저장/수정
```python
# PUT /education/company-settings/{education_id}
# company_id는 토큰에서 자동 추출
{
  "custom_url": "https://company-lms.co.kr/course/12",
  "custom_url_label": "회사 안전교육 포털",
  "custom_note": "사내 LMS 로그인 후 수강하세요.",
  "is_active": true
}
# → UPSERT (company_id + education_id 기준)
```

### 1-3. 교육 링크 초기화 (기본값으로 복원)
```python
# DELETE /education/company-settings/{education_id}
# → company_education_setting 행 삭제 → KOSHA 기본 URL 사용
```

### 1-4. 교육 발령 (단건/다건)
```python
# POST /education/assign
{
  "factory_id": "uuid",
  "education_id": "uuid",
  "due_date": "2026-04-30",
  "worker_ids": ["uuid", ...],
  "user_ids": ["uuid", ...],
  "note": "분기 정기교육"
}
# 처리:
# 1. education_assignment rows 생성 (1인 1행)
# 2. 앱 푸시 알림 발송 (push_token 있는 경우)
```

### 1-5. 이수 완료 처리
```python
# PATCH /education/assignment/{id}/complete
{
  "completed_at": "2026-04-15T10:00:00",
  "completed_hours": 8.0,
  "certificate_url": "https://...",
  "note": "사내 LMS 이수"
}
```

### 1-6. 이수증 파일 업로드
```python
# POST /education/assignment/{id}/certificate
# Content-Type: multipart/form-data
# → Supabase Storage 업로드 → certificate_url 저장
```

### 1-7. 목록/요약 조회
```python
# GET /education/assignments?factory_id=&status_code=&page=&size=
# GET /education/assignments/summary?factory_id=
```

### 1-8. 만료 처리 크론 (daily)
```python
# due_date < today AND status_code = 'PENDING'
# → status_code = 'OVERDUE'
```

---

## 작업 2 (프론트): `education-setting.html` — 교육 설정

### 위치
`tadmin/full-version/html/horizontal-menu-template/education-setting.html`

### 화면 구성

```
┌─────────────────────────────────────────────────────────────┐
│ 교육 설정                                                    │
│ 각 교육 항목별로 회사 자체 교육 링크를 설정할 수 있습니다.     │
├──────────────┬──────┬──────┬─────────────────────┬──────────┤
│ 교육명       │ 시간 │ 주기 │ 교육 링크            │ 관리     │
├──────────────┼──────┼──────┼─────────────────────┼──────────┤
│ 정기교육     │  6h  │ 분기 │ [KOSHA 기본] ←회색  │ [설정]   │
│ 특별교육(용접│ 16h  │ 신규 │ 회사 LMS ←파란색    │ [수정]   │
│ 채용시교육   │  8h  │채용시│ [KOSHA 기본] ←회색  │ [설정]   │
└──────────────┴──────┴──────┴─────────────────────┴──────────┘
```

### 교육 링크 설정 모달

```html
<div class="modal" id="eduSettingModal">
  <h5 id="modal-edu-name">교육 링크 설정</h5>

  <!-- 현재 기본값 표시 -->
  <div class="alert alert-secondary mb-3">
    <small>기본 링크 (KOSHA/고용노동부)</small><br>
    <a id="default-url" href="#" target="_blank" class="small"></a>
  </div>

  <!-- 회사 자체 링크 입력 -->
  <div class="mb-3">
    <label class="form-label">
      회사 교육 링크
      <span class="text-muted small ms-1">(비워두면 기본 링크 사용)</span>
    </label>
    <input type="url" id="custom-url" class="form-control"
           placeholder="https://company-lms.co.kr/course/...">
  </div>

  <div class="mb-3">
    <label class="form-label">링크 표시명</label>
    <input type="text" id="custom-url-label" class="form-control"
           placeholder="예: 사내 안전교육 포털">
  </div>

  <div class="mb-3">
    <label class="form-label">추가 안내 메시지</label>
    <textarea id="custom-note" class="form-control" rows="2"
              placeholder="예: 사내 LMS 로그인 후 '안전교육' 카테고리에서 수강하세요."></textarea>
  </div>

  <div class="d-flex gap-2">
    <button class="btn btn-primary flex-grow-1" onclick="saveEduSetting()">저장</button>
    <button class="btn btn-outline-secondary" onclick="resetEduSetting()">기본값으로</button>
  </div>
</div>
```

---

## 작업 3 (프론트): `education-list.html` — 교육 이수 현황

### 위치
`tadmin/full-version/html/horizontal-menu-template/education-list.html`

### 화면 구성

```
┌─────────────────────────────────────────────────────┐
│ 교육 이수 관리              [+ 교육 발령하기]         │
├─────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│ │ 전체 100 │ │완료 65 ✅│ │대기 30 ⏳│ │초과 5 🔴│ │
│ │          │ │  65%     │ │          │ │         │ │
│ └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
├─────────────────────────────────────────────────────┤
│ 시설[전체▼] 교육[전체▼] 상태[전체▼] [검색]          │
├─────────────────────────────────────────────────────┤
│ □ No. │ 이름 │ 직종 │ 교육명 │ 기한 │ 이수증 │ 상태 │
│ □  1  │홍길동│용접공│특별교육│4/30  │  ✅   │ 완료 │
│ □  2  │김철수│철근공│정기교육│4/30  │  ❌   │ 대기 │
│ □  3  │이영희│사무직│채용교육│3/31  │  ❌   │ 초과 │
└─────────────────────────────────────────────────────┘
```

### 교육 발령 모달

```javascript
// 교육 선택 시 → effective_url 표시
// custom_url 있으면 파란색, 없으면 회색으로 KOSHA 기본 링크 표시
async function onEduSelect(educationId) {
  const res = await apiCall('GET',
    `/education/company-settings?company_id=${companyId}&education_id=${educationId}`);
  const edu = res.data;

  const infoEl = document.getElementById('edu-info');
  if (edu.has_custom) {
    infoEl.innerHTML = `
      <span class="badge bg-label-primary">회사 설정 링크</span>
      <a href="${edu.effective_url}" target="_blank" class="ms-2 small">
        ${edu.effective_url_label || '교육 링크'} →
      </a>
      ${edu.custom_note ? `<br><small class="text-muted">${edu.custom_note}</small>` : ''}`;
  } else {
    infoEl.innerHTML = `
      <span class="badge bg-label-secondary">KOSHA 기본 링크</span>
      <a href="${edu.effective_url}" target="_blank" class="ms-2 small">
        교육 링크 →
      </a>`;
  }
}
```

### 이수 처리 사이드 패널 (교육 링크 표시)

```html
<!-- 교육 링크 (회사 설정 or KOSHA 기본) -->
<div id="edu-link-area" class="alert mb-3" style="display:none">
  <div class="d-flex align-items-center justify-content-between">
    <div>
      <span class="badge me-2" id="edu-link-badge"></span>
      <small id="edu-link-note" class="text-muted d-block mt-1"></small>
    </div>
    <a id="edu-link" href="#" target="_blank" class="btn btn-sm btn-outline-primary">
      <i class="ti tabler-external-link me-1"></i>수강하기
    </a>
  </div>
</div>
```

```javascript
// 사이드 패널 열 때 교육 링크 세팅
function setEduLink(assignment) {
  const area = document.getElementById('edu-link-area');
  const badge = document.getElementById('edu-link-badge');
  const link = document.getElementById('edu-link');
  const note = document.getElementById('edu-link-note');

  const url = assignment.effective_url;
  if (!url) { area.style.display = 'none'; return; }

  area.style.display = 'block';
  area.className = assignment.has_custom
    ? 'alert alert-primary mb-3'
    : 'alert alert-secondary mb-3';
  badge.className = assignment.has_custom
    ? 'badge bg-primary'
    : 'badge bg-secondary';
  badge.textContent = assignment.has_custom
    ? (assignment.effective_url_label || '회사 교육 링크')
    : 'KOSHA 기본 링크';
  link.href = url;
  note.textContent = assignment.custom_note || '';
}
```

---

## 완료 체크리스트

```
백엔드 (tai-api)
□ GET    /education/company-settings     회사별 교육 링크 목록
□ PUT    /education/company-settings/{id} 교육 링크 저장/수정 (UPSERT)
□ DELETE /education/company-settings/{id} 기본값으로 초기화
□ POST   /education/assign               교육 발령 (다건)
□ PATCH  /education/assignment/{id}/complete  이수 완료
□ POST   /education/assignment/{id}/certificate  이수증 업로드
□ GET    /education/assignments          목록 조회 (effective_url 포함)
□ GET    /education/assignments/summary  요약 통계
□ GET    /education/master               교육 마스터 목록
□ 크론: 만료 상태 자동 처리 (PENDING → OVERDUE)

프론트 (tai-admin)
□ education-setting.html — 교육 설정 (회사별 링크 설정 모달)
□ education-list.html — 교육 이수 현황 (요약카드 + 목록 + 사이드패널)
□ 교육 발령 모달 — 교육 선택 시 effective_url 즉시 표시
□ 이수 사이드패널 — 회사 링크 or KOSHA 기본 링크 표시
□ GitHub push
```
