# 프론트 작업지시서 — 안전관리자 대시보드 + 담당자 배정 UI
**날짜: 2026-04-07 | 담당: 프론트 창 | 저장소: tai-admin**

---

## 배경

법령엔진이 진단을 완료하더라도 안전관리자가 보는 화면이 없다.
- "오늘 해야 하는 일" 한 줄짜리 뷰 없음
- work_assignments 1,161건 중 1,071건(92%)이 담당자 미배정
- 법령 진단 결과가 관리자 화면에서 소비되지 않음

---

## 작업 1: 안전관리자 대시보드 페이지

### 파일
- HTML: `site/full-version/html/safety-dashboard.html`
- JS: `site/full-version/html/assets/js/pages/safety-dashboard.page.js`

### 화면 구성 (3 영역)

#### 영역 1: 오늘 할 일 요약 (상단 카드 4개)
```
[ D-0 마감 N건 ]  [ D-3 이내 N건 ]  [ 이번달 N건 ]  [ 미배정 N건 ]
```
- 각 카드 클릭 시 하단 목록이 해당 필터로 전환
- API: `GET /work-schedules?factory_id=...&due_within=0` 등
- 미배정: `GET /work-assignments?assigned_user_id=null`

#### 영역 2: 할 일 목록 테이블
| 항목명 | 법령 | 마감일 | 담당자 | 상태 |
|---|---|---|---|---|
| 전기안전점검 | 전기사업법 23조 | 2026-04-10 | [미배정] | PENDING |

- 담당자 셀: 미배정이면 보라색 배지 `[미배정]` → 클릭 시 배정 모달 오픈
- 배정된 경우: 이름 표시
- 행 클릭: 해당 일정 상세 모달

#### 영역 3: 법령 진단 현황 (우측 사이드바)
```
[적용 법령 N건]  [선임의무 N건]  [점검의무 N건]  [신고의무 N건]
```
- API: `GET /legal-engine/result/{factory_id}` → summary 필드 사용
- 숫자 클릭 시 해당 카테고리 상세 목록 (별도 모달 또는 페이지)

### API 연결
```javascript
const BASE = 'https://api.taieng.co.kr';

async function loadDashboard(factoryId) {
  const [schedules, assignments, legalResult] = await Promise.all([
    fetch(`${BASE}/work-schedules?factory_id=${factoryId}&status=PENDING`).then(r => r.json()),
    fetch(`${BASE}/work-assignments?factory_id=${factoryId}`).then(r => r.json()),
    fetch(`${BASE}/legal-engine/result/${factoryId}`).then(r => r.json())
  ]);
  renderCards(schedules, assignments);
  renderTable(schedules);
  renderLegalSummary(legalResult);
}
```

### 디자인 가이드
- Vuexy Bootstrap 5 템플릿 기반
- 상단 카드: `card border-0 shadow-sm` + 아이콘 (ti-calendar, ti-alert-circle 등)
- 위험도 배지: HIGH=빨강, MEDIUM=주황, LOW=초록
- 테이블 첫 번째 컬럼: 체크박스 없음 (대시보드이므로), 번호 컬럼 포함

---

## 작업 2: 담당자 배정 모달

### 위치
`safety-dashboard.html` 내부 모달 또는 기존 일정관리 페이지에 추가

### 모달 구성
```html
<div class="modal fade" id="assignModal">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5>담당자 배정</h5>
      </div>
      <div class="modal-body">
        <div class="mb-3">
          <label class="form-label">담당 그룹</label>
          <select class="form-select" id="assignGroup"></select>
        </div>
        <div class="mb-3">
          <label class="form-label">담당자</label>
          <select class="form-select" id="assignUser"></select>
        </div>
        <div class="mb-3">
          <label class="form-label">완료예정일</label>
          <input type="date" class="form-control" id="assignDueDate">
          <!-- 필수 아님 -->
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary" onclick="submitAssign()">배정하기</button>
      </div>
    </div>
  </div>
</div>
```

### API 연결
```javascript
// 그룹 목록 로드
GET /groups?factory_id={id}

// 그룹 선택 시 해당 그룹 작업자 로드
GET /users?group_id={id}

// 배정 저장
PATCH /work-assignments/{assignment_id}
{
  "assigned_user_id": "uuid",
  "assigned_group_id": "uuid",
  "due_date": "2026-04-30"  // 선택
}
```

### UX 흐름
1. 테이블에서 `[미배정]` 배지 클릭
2. 모달 오픈 + 현재 일정 정보 표시 (제목, 법령, 마감일)
3. 그룹 선택 → 작업자 드롭다운 갱신
4. 배정하기 클릭 → PATCH 호출 → 성공 시 모달 닫기 + 테이블 갱신
5. 배정된 셀: 이름으로 교체

---

## 메뉴 등록

`menu-nav.js` 또는 `menu-tadmin.js`에 추가:
```javascript
{
  label: '안전대시보드',
  url: '/safety-dashboard.html',
  icon: 'ti-shield-check'
}
```

---

## 완료 기준
- [ ] 대시보드 로드 시 D-0 / D-3 / 이번달 / 미배정 카드 4개 표시
- [ ] 카드 클릭 시 하단 목록 필터 전환
- [ ] `[미배정]` 클릭 시 배정 모달 오픈
- [ ] 그룹 선택 시 작업자 목록 갱신
- [ ] 배정 후 테이블 즉시 반영
- [ ] 우측 법령 진단 요약 숫자 표시
- [ ] 메뉴에서 직접 접근 가능
