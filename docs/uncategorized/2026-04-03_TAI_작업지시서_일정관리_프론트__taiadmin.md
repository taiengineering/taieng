# 작업지시서 — 엔진설정 > 일정관리 프론트

## 파일
`admin/full-version/html/horizontal-menu-template/engine-schedule.html` (신규)

## 메뉴 등록
모든 admin 페이지의 `엔진설정` 메뉴 `<ul class="menu-sub">` 안에 추가:
```html
<li class="menu-item"><a href="engine-schedule.html" class="menu-link"><div>일정관리</div></a></li>
```
위치: `check-education.html` 메뉴 아이템 바로 위

---

## 페이지 구성

### 상단 요약 카드 (4개)
```
[전체 일정세트]  [기준일 미설정]  [활성]  [법령엔진생성]
    68개            67개          1개       67개
```
- 미설정(PENDING_ANCHOR)은 bg-label-warning, 숫자 강조
- API: `GET /inspection-schedule/summary`

---

### 필터 바
```
[시설 검색] [주기 v] [상태 v] [출처 v] [검색 버튼]
```
- 시설: text input (factory 이름 검색)
- 주기: 전체 | 연 | 반기 | 분기 | 월 | 주
- 상태: 전체 | 기준일 미설정 | 활성 | 비활성
- 출처: 전체 | 법령엔진 | 수동등록

---

### 목록 테이블

**컬럼 (전체선택 체크박스 포함):**
```
[No.] [No.] [시설명] [점검명] [법령] [반복주기] [기준일] [다음예정일] [상태] [액션]
```

**상세 컬럼:**
- **No.**: (page-1)*pageSize + idx + 1
- **시설명**: factory_name
- **점검명**: inspection_set_name
- **법령**: law_name + law_article (없으면 '-')
- **반복주기**: cycle_label 배지로 표시
  ```
  [연 1회] [반기 1회] [분기 1회] [월 1회]
  ```
  주기별 색상:
  - year: bg-label-primary
  - half_year: bg-label-info  
  - quarter: bg-label-warning
  - month: bg-label-success
  - week/day: bg-label-danger
- **기준일**: schedule_anchor_date (없으면 `<span class="text-danger">미설정</span>`)
- **다음예정일**: next_planned_date (없으면 '-')
- **상태** 배지:
  - PENDING_ANCHOR: `<span class="badge bg-warning text-dark">기준일 필요</span>`
  - ACTIVE: `<span class="badge bg-success">활성</span>`
  - INACTIVE: `<span class="badge bg-secondary">비활성</span>`
- **액션**: `✎ 수정` 버튼 (수정 모달 오픈)

---

### 수정 모달 (`#editScheduleModal`)

**모달 크기**: modal-lg

**상단 정보 (읽기전용):**
- 시설명, 점검명, 법령명+조문, 출처(법령엔진/수동)

**수정 가능 섹션 1: 반복 주기**
```
[주기 단위 select]  [주기 값 input]  → cycle_label 미리보기 자동 표시

주기 단위 options:
  year = 년
  half_year = 반기(6개월)
  quarter = 분기(3개월)
  month = 개월
  week = 주
  day = 일

주기 값: number input min=1
예시 자동 표시: "→ 연 1회" or "→ 3개월마다"
```

**수정 가능 섹션 2: 기준 시점 (★ 핵심)**
```
기준일 유형:
  [● 마지막 점검일 기준]  [○ 설치일/고정일 기준]

기준일 입력:
  [날짜 input]  ← schedule_anchor_date
  예: 2024-03-15

기준 안내문:
  readonly textarea ← cycle_base_guide
  예: "마지막 점검일로부터 1개월마다"

[다음 예정일 미리보기]
  anchor_date + cycle 계산해서 자동 표시
  예: "→ 다음 예정일: 2024-04-15"
```

**수정 가능 섹션 3: 종료일 (선택)**
```
[종료일 input] ← schedule_end_date (없으면 무기한)
```

**수정 가능 섹션 4: 메모**
```
[textarea] ← description
```

**모달 하단 버튼:**
```
[비활성화]  [취소]  [저장]  [기준일 확정 → 활성화]
```
- `저장`: PATCH /inspection-schedule/sets/{id} — 수정만
- `기준일 확정 → 활성화`: POST /inspection-schedule/sets/{id}/confirm-anchor — anchor 설정 + ACTIVE 전환

---

### 다음 예정일 자동 계산 (JS)
```javascript
function calcNextDate(anchorDate, cycleUnit, cycleValue) {
  if (!anchorDate) return null;
  var d = new Date(anchorDate);
  switch(cycleUnit) {
    case 'year':      d.setFullYear(d.getFullYear() + cycleValue); break;
    case 'half_year': d.setMonth(d.getMonth() + 6); break;
    case 'quarter':   d.setMonth(d.getMonth() + 3); break;
    case 'month':     d.setMonth(d.getMonth() + cycleValue); break;
    case 'week':      d.setDate(d.getDate() + cycleValue * 7); break;
    case 'day':       d.setDate(d.getDate() + cycleValue); break;
  }
  return d.toISOString().split('T')[0];
}
```

---

## 전역 규칙 준수
1. 첫 컬럼: 전체선택 체크박스 (`toggleAll`)
2. 두 번째 컬럼: 순번 No. = `(currentPage-1)*pageSize + idx + 1`
3. 로그인 체크: `if (!localStorage.getItem('access_token')) location.replace(...)`
4. API 호출: `apiCall()` 유틸 사용
5. 토스트: `showToast()` 사용

---

## API 연결 요약
| 동작 | API |
|------|-----|
| 목록 조회 | GET /inspection-schedule/sets |
| 요약 카드 | GET /inspection-schedule/summary |
| 단건 조회(모달) | GET /inspection-schedule/sets/{id} |
| 수정 저장 | PATCH /inspection-schedule/sets/{id} |
| 기준일 확정 | POST /inspection-schedule/sets/{id}/confirm-anchor |
