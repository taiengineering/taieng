# Cursor 작업지시서 — 건설 tadmin 관리 페이지 5개

> 작성일: 2026-04-01  
> 레포: tai-admin (프론트)  
> 경로: `tadmin/full-version/html/horizontal-menu-template/`

---

## 공통 규칙

- auth-guard.js HEAD 삽입 필수
- apiCall() + globals.js 사용
- 목록 첫 컬럼: 체크박스(toggleAll), 두 번째 컬럼: No. (1-based)
- 페이지네이션: renderPagination() 사용
- 시설 선택: localStorage의 `current_factory_id` 사용
- API base: TAI_API (globals.js)
- company_id: 토큰에서 자동 추출

---

## 페이지 1: `construction-site-list.html` (건설현장 목록)

### 화면 구조
```
[Hero 헤더] 건설현장 관리 (녹색 그라디언트)
[요약 카드 4개] 전체 / 진행중 / 완료 / 예정
[필터] 현장명 검색 | 공사종류(전체/건축/토목/전문) | 상태(전체/PLANNED/IN_PROGRESS/COMPLETED)
[등록 버튼] + 현장 등록
[목록 테이블]
  No | 현장명 | 공사종류 | 공사금액 | 근로자 | 안전관리자 선임 | 상태 | 등록일
  → 행 클릭: 우측 상세/수정 사이드패널 오픈
```

### 등록 사이드패널 필드
```
현장명* | 현장코드
공사종류* (BUILDING=건축 / CIVIL=토목 / SPECIALTY=전문 / PLANT=플랜트)
공사금액(억원)* → 입력 시 실시간 안전관리자 선임 기준 안내
  - 건축 150억↑: ⚠️ 안전관리자 선임 의무
  - 토목 120억↑: ⚠️ 안전관리자 선임 의무
직접 근로자수 | 하도급 근로자수 → 합계 자동 계산
  - 합계 50명↑: ⚠️ 안전관리자 선임 의무
현장 주소
착공일 | 준공예정일
현장 소장(manager_id) - users 목록에서 선택
메모
```

### API
```
GET  /construction/sites?company_id=&status_code=&site_type=&search=&page=&size=
POST /construction/sites
GET  /construction/sites/{id}
PATCH /construction/sites/{id}
POST /construction/engine/safety-manager  ← 실시간 선임 판정
  body: { site_type, contract_amount, total_workers }
```

### 안전관리자 선임 배지
```javascript
// 목록에서 표시
if (safety_manager_required) {
  '<span class="badge bg-danger">선임필요</span>'
} else {
  '<span class="badge bg-success">해당없음</span>'
}
```

---

## 페이지 2: `construction-process-list.html` (공정 관리)

### 화면 구조
```
[상단 바] 현장 선택 드롭다운 (company_id 기준 현장 목록)
[Hero] 공정 관리
[KCSC 공정 추가 버튼] + 공정 추가
[목록 테이블]
  No | 공정명 | 공사구분 | 계획 시작 | 계획 종료 | 진행률 | 위험여부 | 상태
  → 행 클릭: 수정 사이드패널
```

### 공정 추가 모달 (2단계)
```
Step 1: KCSC 공정 선택
  GET /construction/kcsc/processes?construction_type=&search=
  construction_type 필터: BUILDING(건축) / CIVIL(토목) / COMMON(공통)
  공정 검색 + 선택 (체크박스)

Step 2: 상세 정보 입력
  계획 시작일 | 계획 종료일
  근로자수 | 위험작업여부(toggle)
  메모
```

### API
```
GET  /construction/sites/{site_id}/processes?page=&size=
POST /construction/sites/{site_id}/processes
GET  /construction/kcsc/processes?construction_type=&search=&page=&size=
GET  /construction/kcsc/works/{process_id}
PATCH /construction/processes/{id}
DELETE /construction/processes/{id}
```

---

## 페이지 3: `construction-work-list.html` (위험작업/PTW)

### 화면 구조
```
[상단 바] 현장 선택
[Hero] 위험작업 · PTW 관리
[요약 카드] 전체 | 승인대기(DRAFT) | 승인완료(APPROVED) | 진행중
[필터] 작업일 | PTW상태 | 공정 선택
[등록 버튼] + 작업 등록
[목록 테이블]
  No | PTW번호 | 작업명 | 작업일 | 작업시간 | 근로자수 | PTW상태 | 담당자
  → 행 클릭: 상세 패널 (PTW 승인/반려 버튼 포함)
```

### PTW 상태 배지
```javascript
const PTW_BADGE = {
  DRAFT:    'bg-secondary',   // 임시저장
  PENDING:  'bg-warning',     // 승인요청
  APPROVED: 'bg-success',     // 승인완료
  REJECTED: 'bg-danger',      // 반려
  CLOSED:   'bg-dark',        // 종료
};
```

### 등록 모달
```
작업명* | 작업일* | 시작시간 | 종료시간
작업 위치
공정 연결 (construction_site_processes 목록)
KCSC 작업 마스터 연결 (선택)
  GET /construction/kcsc/works/{process_id}
  is_hazardous=true 항목 강조 표시
특수작업유형 | 위험코드 | PPE 요구사항
작업자수
```

### PTW 승인 패널
```
[승인] 버튼 → PATCH /construction/works/{id}/ptw
  body: { ptw_status: 'APPROVED', ptw_approved_by: current_user_id }
[반려] 버튼 → ptw_status: 'REJECTED'
승인자 / 승인일시 표시
```

### API
```
GET  /construction/sites/{site_id}/works?page=&size=&ptw_status=&work_date=
POST /construction/sites/{site_id}/works
GET  /construction/works/{id}
PATCH /construction/works/{id}
PATCH /construction/works/{id}/ptw
```

---

## 페이지 4: `construction-worker-list.html` (작업자 출입)

### 화면 구조
```
[상단 바] 현장 선택
[Hero] 작업자 출입 관리
[실시간 카드] 현재 현장 내: N명 (IN) | 퇴장: N명 (OUT) | 미출근: N명
[필터] 이름 검색 | 구분(직접/하도급) | 출입상태(IN/OUT/OFFSITE)
[등록 버튼] + 작업자 등록
[목록 테이블]
  No | 이름 | 연락처 | 구분 | 직종 | 안전교육일 | 출입상태 | 최종입장
  → 행 클릭: 수정 패널 + [입장] / [퇴장] 버튼
```

### 출입 상태 버튼
```javascript
// 현재 상태에 따라 버튼 전환
if (entry_status === 'IN') {
  // [퇴장 처리] 버튼 → PATCH /construction/workers/{id}/entry { entry_status: 'OUT' }
} else {
  // [입장 처리] 버튼 → PATCH /construction/workers/{id}/entry { entry_status: 'IN' }
}
```

### 등록 패널
```
이름* | 연락처
구분* (DIRECT=직접 / SUBCON=하도급)
직종 | 하도급업체
입사일 | 안전교육일 | 안전교육시간
자격증 코드
메모
```

### API
```
GET  /construction/sites/{site_id}/workers?page=&size=&worker_type=&entry_status=&search=
POST /construction/sites/{site_id}/workers
GET  /construction/workers/{id}
PATCH /construction/workers/{id}
PATCH /construction/workers/{id}/entry   ← 출입처리
DELETE /construction/workers/{id}
```

---

## 페이지 5: `construction-inspection-list.html` (안전점검)

### 화면 구조
```
[상단 바] 현장 선택
[Hero] 안전점검 관리
[요약 카드] 전체 | 합격(PASS) | 불합격(FAIL) | 시정조치중
[필터] 점검유형 | 점검결과 | 기간
[등록 버튼] + 점검 등록
[목록 테이블]
  No | 점검유형 | 점검일시 | 점검자 | 결함수 | 결과 | 시정조치 상태
  → 행 클릭: 상세 패널
```

### 점검 유형
```javascript
const INSPECTION_TYPES = {
  BEFORE_WORK:  '작업 전 점검',
  DAILY:        '일상 점검',
  WEEKLY:       '주간 점검',
  MONTHLY:      '월간 점검',
  SPECIAL:      '특별 점검',
  AFTER_INCIDENT: '사고 후 점검',
};
```

### 등록 모달
```
점검유형* | 점검일시*
점검자 (users 목록)
공정 연결 | 작업 연결 (선택)
체크리스트 항목 (JSON 동적 추가)
  [+ 항목 추가] → 항목명 + 결과(OK/NG/N/A)
전체 결과 (PASS / FAIL / PARTIAL)
결함수 | 결함 상세 내용
시정조치 내용 | 시정기한
사진 URL (텍스트 입력 - 추후 업로드 연동)
```

### 시정조치 처리
```javascript
// FAIL 또는 결함 있을 때 표시
// PATCH /construction/inspections/{id}/corrective
// body: { corrective_status: 'DONE', corrective_action: '내용' }
```

### API
```
GET  /construction/sites/{site_id}/inspections?page=&size=&inspection_type=&overall_result=
POST /construction/sites/{site_id}/inspections
GET  /construction/inspections/{id}
PATCH /construction/inspections/{id}
PATCH /construction/inspections/{id}/corrective
DELETE /construction/inspections/{id}
```

---

## 메뉴 추가 (menu-tadmin.js)

기존 '건설관리' 또는 '작업관리' 그룹에 아래 5개 추가:
```javascript
{ label: '건설현장',    href: 'construction-site-list.html',       icon: 'tabler-building-community' },
{ label: '공정관리',    href: 'construction-process-list.html',    icon: 'tabler-timeline' },
{ label: '위험작업/PTW', href: 'construction-work-list.html',      icon: 'tabler-alert-triangle' },
{ label: '작업자출입',  href: 'construction-worker-list.html',     icon: 'tabler-user-check' },
{ label: '안전점검',    href: 'construction-inspection-list.html', icon: 'tabler-checklist' },
```

---

## 완료 체크리스트

```
□ construction-site-list.html
  □ 현장 목록 + 실시간 선임 기준 안내
  □ 공사금액 입력 시 POST /construction/engine/safety-manager 호출
□ construction-process-list.html
  □ KCSC 공정 검색 모달
  □ construction_type 필터 (BUILDING/CIVIL/COMMON)
□ construction-work-list.html
  □ PTW 상태 배지
  □ PTW 승인/반려 버튼
  □ is_hazardous 위험작업 강조 표시
□ construction-worker-list.html
  □ 출입 실시간 카드 (IN 인원 수)
  □ 입장/퇴장 버튼
□ construction-inspection-list.html
  □ 체크리스트 동적 추가
  □ 시정조치 처리 버튼
□ menu-tadmin.js 메뉴 5개 추가
□ GitHub push
```
