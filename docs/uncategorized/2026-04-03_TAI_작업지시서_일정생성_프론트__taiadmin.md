# 작업지시서 — engine-schedule.html 전면 재설계

## 무엇을 만드는가
`engine-legal-ai.html`과 **동일한 UX 구조**로 engine-schedule.html 재구현.

```
engine-legal-ai          engine-schedule (목표)
탭1: 조문 파싱      →    탭1: 룰 → 일정 생성
   좌: 법령 목록         →       좌: INSPECT 룰 목록 (법령별)
   우: 조문+AI파싱        →       우: 룰 상세+시설 선택+생성
탭2: 초안 검토·승인   →    탭2: 일정 검토·활성화
   주햨→승인→master     →       기준일입력→활성화→마스터 일정
```

## 파일
`admin/full-version/html/horizontal-menu-template/engine-schedule.html`
(engine-legal-ai.html을 기반으로 일정 버전으로 수정)

---

## 페이지 전체 구조

### 상단 네비게이션 + 요약 카드

**4개 요약 카드** (API: `GET /inspection-schedule/sets/summary-by-rule`):
```
[전체 INSPECT 룰]   [일정생성 완료]   [미생성]   [활성 일정]
     191개             67개 (35%)    124개       1개
```

**2개 탭 네비게이션**:
```
[탭1: 파싱→생성 (룰목록 및 일정 생성)]  [탭2: 검토·활성화 (PENDING_ANCHOR 검토)]
                                          배지: PENDING 수 표시
```

---

## 탭1: INSPECT 룰 목록 → 일정 생성

### 좌측 패널 (룰 목록, w=320px)
**인터페이스 (engine-legal-ai 좌측 법령 목록과 동일 스타일)**:
- 상단: 헤더 + 섬터 필터 `<select id="fSector">` (BUILDING/MANUFACTURING/CONSTRUCTION/COMMON)
- 목록 항목마다:
```html
<div class="px-3 py-2 border-bottom rule-item" data-id="{rule_id}">
  <div class="small fw-semibold">{law_name}</div>
  <div class="d-flex gap-2 mt-1">
    <span class="badge bg-label-secondary" style="font-size:10px">{sector}</span>
    <span class="cycle-{cycle_unit}">{cycle_label}</span>
    <!-- 미생성 유제 -->
    <span class="badge bg-warning text-dark">{not_converted_for_this_rule}개 미생성</span>
    <!-- 전체 시설 생성완료시 -->
    <span class="badge bg-success">완료</span>
  </div>
</div>
```

- API: `GET /inspection-schedule/rules?page=1&page_size=50&sector={sector}`
- 룰 클릭 시 우측 패널 로드

### 우측 패널 (룰 상세 + 일정 생성)

**클릭 전 (빈 상태)**:
```html
<div class="text-center py-5">
  <div class="fs-1">📅</div>
  <p>좌측에서 점검 룰을 선택하세요.</p>
</div>
```

**클릭 후 (룰 상세카드)**:
```html
<!-- 상단: 룰 정보 -->
<div class="card mb-3">
  <div class="card-body py-2 d-flex align-items-center justify-content-between">
    <div>
      <h6 class="mb-0">{law_name} {law_article}</h6>
      <small class="text-body-secondary">{obligation_summary}</small>
    </div>
    <div class="d-flex gap-2">
      <span class="cycle-{cycle_unit}">{cycle_label}</span>
      <!-- 전체 선택 일괄 생성 버튼 -->
      <button class="btn btn-sm btn-warning" id="btnGenAll">
        <i class="ti ti-calendar-plus me-1"></i> 전체 시설 일정 생성
      </button>
    </div>
  </div>
</div>

<!-- 시설 목록: 시설별 생성 여부 -->
<div class="card">
  <div class="card-header py-2"><h6 class="mb-0">시설별 상태</h6></div>
  <div class="table-responsive">
    <table class="table table-sm align-middle mb-0">
      <thead>
        <tr>
          <th><input type="checkbox" id="chkAllFactory"></th>
          <th>시설명</th>
          <th>섬터</th>
          <th class="text-center">상태</th>
          <th class="text-center">액션</th>
        </tr>
      </thead>
      <tbody id="factoryRows">
        <!-- API: GET /inspection-schedule/rules/{rule_id}/factories -->
        <!-- 생성 완료된 시설 -->
        <tr>
          <td><input type="checkbox" class="fac-chk" data-id="{factory_id}" disabled></td>
          <td>{factory_name}</td>
          <td><span class="badge bg-label-secondary">{sector}</span></td>
          <td class="text-center">
            <span class="st-{status_code}">{status_label}</span>
          </td>
          <td class="text-center">
            <!-- 이미 생성된 경우 -->
            <a href="#" class="small text-primary" onclick="switchToDrafts('{inspection_set_id}')">...검토하기</a>
          </td>
        </tr>
        <!-- 미생성 시설 -->
        <tr>
          <td><input type="checkbox" class="fac-chk" data-id="{factory_id}"></td>
          <td>{factory_name}</td>
          <td><span class="badge bg-label-secondary">{sector}</span></td>
          <td class="text-center"><span class="st-PENDING_ANCHOR">미생성</span></td>
          <td class="text-center"><span class="text-body-secondary small">선택 후 생성</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="card-footer d-flex justify-content-between">
    <button class="btn btn-sm btn-outline-primary" id="btnGenSelected">
      선택시설 일정 생성
    </button>
    <button class="btn btn-sm btn-outline-secondary" id="btnGoReview">탭2 검토로 →</button>
  </div>
</div>
```

**생성 실행 흐름**:
```javascript
async function generateSets(ruleIds, factoryIds) {
  var r = await apiCall('POST', '/inspection-schedule/generate', {
    rule_ids: ruleIds,
    factory_ids: factoryIds,
    skip_existing: true
  });
  showToast('success', `일정 ${r.data.created}개 생성됨 (스킵 ${r.data.skipped}개)`);
  loadRuleFactories(currentRuleId);  // 우측 새로고침
  loadStats();                        // 상단 카드 새로고침
}
```

---

## 탭2: 일정 검토 & 활성화

**(engine-legal-ai의 초안 검토 탭과 동일 스타일)**

### 안내 배너 (review-banner)
```html
<div class="review-banner">
  🔍 생성된 일정세트를 검토하는 곳입니다
  ✅ <strong>기준일 확정</strong> — 일정 활성화 (마스터 일정 등록)
  ✎ <strong>수정</strong> — 주기 변경
  기준일이 없으면 일정이 작동하지 않습니다.
</div>
```

### 필터 바 (검토 탭)
```
[상태 v]  [주기 v]  [시설 검색]  [검색]
- 상태: 전체|기준일필요|활성|일정예정|연체
- 주기: 전체|연|반기|분기|월
```

### 검토 목록 (engine-legal-ai의 초안 목록 스타일)

**카드형 배치** (`.draft-card` 스타일 사용):
```html
<div class="draft-card {anchor_cls}">
  <!-- 헤더: 상태 + 엔터 발화 + 선택셀 + 주기 + 액션 버튼 -->
  <div class="d-flex align-items-start justify-content-between">
    <div class="flex-grow-1">
      <div class="d-flex gap-2 align-items-center flex-wrap mb-2">
        {statusBadge(status_code)}
        <span class="cycle-{cycle_unit}">{cycle_label}</span>
        <span class="small text-body-secondary">{law_name} {law_article}</span>
        <span class="badge bg-label-secondary">{factory_name}</span>
      </div>
      <div class="fw-semibold mb-1">{inspection_set_name}</div>
      <div class="small text-body-secondary">
        <!-- 기준일 입력 (PENDING_ANCHOR일 때 인라인 입력 UI) -->
        <span>기준일: </span>
        {anchor_confirmed
          ? schedule_anchor_date
          : '<input type="date" class="form-control form-control-sm inline-anchor" style="width:160px" ...>'
        }
        {schedule_anchor_date
          ? ' → 다음예정: ' + next_planned_date
          : ''
        }
      </div>
    </div>
    <!-- 액션 버튼 -->
    {status_code === 'PENDING_ANCHOR'
      ? '<div class="d-flex gap-1 flex-shrink-0 ms-3">'
        + '<button class="btn btn-success btn-sm _confirm">&#9989; 활성화</button>'
        + '<button class="btn btn-outline-secondary btn-sm _edit">✎</button>'
        + '</div>'
      : '<span class="small text-body-secondary">' + next_planned_date + '</span>'
    }
  </div>
</div>
```

**테마츹 (anchor_cls)**:
- PENDING_ANCHOR: `draft-card ai-medium` (주황)
- ACTIVE/UPCOMING: `draft-card ai-high` (녹색)
- OVERDUE: `draft-card needs-review` (빨간)

### 인라인 기준일 입력 + 바로 활성화
탭2의 첫 번째 커스터 액션:
```javascript
// 기준일 input엔서 날짜 선택 시 다음예정일 미리보기
card.querySelector('.inline-anchor').addEventListener('change', function() {
  var next = calcNextDate(this.value, cycleUnit, cycleValue);
  card.querySelector('.next-preview-inline').textContent = '\u2192 ' + next;
});

// 활성화 버튼
card.querySelector('._confirm').addEventListener('click', async function() {
  var anchor = card.querySelector('.inline-anchor').value;
  if(!anchor) { showToast('error', '기준일을 입력하세요.'); return; }
  await apiCall('POST', '/inspection-schedule/sets/' + id + '/confirm-anchor', {
    anchor_date: anchor,
    anchor_type: 'LAST_INSPECTION'
  });
  showToast('success', '✅ 활성화됨!');
  loadDraftSets();
  loadStats();
});
```

### 수정 모달 (클릭 시)
후엑스이를 사용하지 않고 인라인 검토를 우선하되,
`✎ 수정` 버튼 클릭 시는 기존 수정 모달 (스타일 동일하게) 열기.

---

## CSS 추가 (기존 engine-legal-ai.html 라답에 아래 추가)
```css
/* 주기 배지 (룰 목록용) */
.cycle-year     { background:rgba(115,103,240,.15); color:#7367f0; ... }
.cycle-half_year{ background:rgba(0,207,232,.15);   color:#00cfe8; ... }
.cycle-quarter  { background:rgba(255,159,67,.15);  color:#ff9f43; ... }
.cycle-month    { background:rgba(40,199,111,.15);  color:#28c76f; ... }

/* 상태 배지 */
.st-PENDING_ANCHOR { background:rgba(255,159,67,.15); color:#ff9f43; ... }
.st-ACTIVE         { background:rgba(40,199,111,.15); color:#28c76f; ... }
.st-UPCOMING       { background:rgba(29,135,249,.15); color:#1d87f9; ... }
.st-OVERDUE        { background:rgba(234,84,85,.15);  color:#ea5455; ... }

/* 일정카드 (대기 = 파란, 활성 = 녹색, 연체 = 빨간) */
.draft-card.anchor-pending  { border-left:4px solid #ff9f43; }
.draft-card.anchor-active   { border-left:4px solid #28c76f; }
.draft-card.anchor-overdue  { border-left:4px solid #ea5455; background:rgba(234,84,85,.03); }

/* 인라인 기준일 */
.next-preview-inline { font-size:12px; color:#28c76f; font-weight:600; }
```

---

## 전역 규칙 준수
1. 쳋번째 컴럼 = 전체선택 체크박스 (`toggleAll`)
2. 두번째 컴럼 = No. = `(page-1)*pageSize+idx+1`
3. 로그인 체크: `access_token` 확인
4. `apiCall()` 유틸 활용
5. `showToast()` 유틸 활용
6. `calcNextDate(anchor, unit, value)` 함수: 다음예정일 계산 (기존 engine-schedule.html에서 복사)

---

## API 연결 요약

| 동작 | API |
|------|-----|
| 상단 요약 | GET /inspection-schedule/sets/summary-by-rule |
| 룰 목록 (탭1좌) | GET /inspection-schedule/rules |
| 시설별 상태 (탭1우) | GET /inspection-schedule/rules/{rule_id}/factories |
| 일정 생성 | POST /inspection-schedule/generate |
| 일정 목록 (탭2) | GET /inspection-schedule/sets |
| 수정 모달 | GET /inspection-schedule/sets/{id} |
| 주기수정 | PATCH /inspection-schedule/sets/{id} |
| **기준일 확정 → 활성화** | POST /inspection-schedule/sets/{id}/confirm-anchor |
