# FN-07: 점검 미이행 대시보드 + 작업자 경고 UI

> **작성일**: 2026-04-17
> **대상 레포**: taiengineering/tai-admin (safe.taieng.co.kr)
> **의존**: BE-10 완료 ✅ (main 배포 완료)
> **API base**: `https://api.taieng.co.kr`

---

## 법적 근거 (마케팅 + UI 표시용)

| 위반 | 법령 | 과태료 |
|---|---|---|
| 안전점검 미실시 | 산안법 §36 | 500만원 |
| 정기점검 미실시 | 산안법 §93 | 1,000만원 |
| 작업 전 점검 미실시 | 안전보건규칙 §35 | 300만원 |
| 점검기록 미보존 | 산안법 §164 | 300만원 |
| 미실시 + 사고 발생 | 산안법 §167 | 7년 징역 / 1억 벌금 |
| 사망사고(50인+) | 중대재해법 §6 | 1년+ 징역 / 법인 50억 벌금 |

---

## 작업 1: 안전관리자 대시보드 — 미이행 위젯

### 파일 위치
`tadmin/full-version/app/dashboard/home.html` (또는 기존 대시보드 파일)

### API 호출
```javascript
const res = await apiCall('GET', '/overdue/summary');
const s = res.summary;
```

### UI 카드 구조
```
┌─────────────────────────────────────────────┐
│ 🔴 점검 미이행 현황                    [상세] │
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ 경고     │ │에스컬레이션│ │ OVERDUE │       │
│  │ {warn}건 │ │ {mgr}건  │ │ {ovd}건  │       │
│  │ (D+1)   │ │ (D+2)   │ │ (D+7+)  │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│                                             │
│  ⚠️ 법적 리스크: 과태료 최대 {금액}원 노출     │
│                                             │
│  최근 미이행 TOP 3:                          │
│  • 김작업 — 타이어 점검 (D+3) [독촉]          │
│  • 박안전 — 소화기 점검 (D+1) [독촉]          │
│  • 이현장 — 전기 점검 (D+5) [독촉]            │
└─────────────────────────────────────────────┘
```

### 매핑
```javascript
const warn = s.warn_d1 || 0;           // Level 2: 작업자 경고
const mgr  = s.manager_d2 || 0;        // Level 3: 관리자 알림
const ovd  = s.overdue_d7 || 0;        // Level 4: OVERDUE
const total = warn + mgr + ovd;

// 과태료 추정 (건당 300만원 × 미이행 총건수)
const penaltyEstimate = total * 3000000;
```

### [독촉] 버튼
클릭 시 해당 작업자에게 즉시 SMS 발송 (별도 API 필요 — BE-10 확장):
```
POST /overdue/check?factory_id={}&limit=1
```
또는 단순히 notifications INSERT + MessageMi 호출

---

## 작업 2: 미이행 상세 페이지

### 파일
`tadmin/full-version/app/overdue/overdue-list.html`

### 페이지 구성

**필터 바:**
- 기간 선택 (최근 7일 / 30일 / 전체)
- 시설 드롭다운
- 에스컬레이션 레벨 (전체 / 경고 / 에스컬레이션 / OVERDUE)
- 해소 여부 (전체 / 미해소 / 해소)

**테이블 (필수 컬럼):**
| No. | 작업자 | 점검 내용 | 기한 | 경과일 | 레벨 | 상태 | 액션 |
|---|---|---|---|---|---|---|---|
| ☐ | 김작업 | 타이어 점검 | 04-14 | D+3 | 관리자알림 | 미해소 | [독촉] [재배정] [해소] |

**API:**
```javascript
// 목록 조회
const list = await apiCall('GET', '/overdue/history?page=1&size=20&resolved=false');

// 해소 처리
await apiCall('POST', `/overdue/resolve/${historyId}`, {
  resolved_by: currentUserId,
  resolve_note: '전화 독촉 후 완료 확인'
});
```

**하단 카드:**
```
⚠️ 법적 리스크 요약
현재 미해소 {N}건 — 산안법 §36 위반 시 건당 과태료 300~500만원
사고 발생 시 7년 이하 징역 또는 1억원 이하 벌금 (산안법 §167)
```

---

## 작업 3: 작업자 홈 — 미이행 경고 배너

### 파일
`tadmin/full-version/app/worker/worker-home.html`

### 조건
work_assignments에서 본인(assigned_user_id)의:
- status_code = 'OVERDUE' 또는
- status_code = 'PENDING' AND scheduled_date < today

### UI
```html
<div class="alert alert-danger d-flex align-items-center mb-3">
  <i class="ti ti-alert-triangle me-2 fs-4"></i>
  <div>
    <strong>⚠️ 미완료 점검 {N}건</strong>
    <p class="mb-1">기한이 경과한 점검이 있습니다. 즉시 완료해주세요.</p>
    <ul class="mb-0">
      <li>타이어 상태 점검 (D+3) <a href="#">지금 하기 →</a></li>
      <li>소화기 월간 점검 (D+1) <a href="#">지금 하기 →</a></li>
    </ul>
    <small class="text-muted">
      미이행 시 안전관리자에게 자동 보고됩니다. (산안법 §36)
    </small>
  </div>
</div>
```

### API
```javascript
// 작업자 본인의 미완료 작업 조회
const overdue = await apiCall('GET', `/work-assignments?assigned_user_id=${userId}&status=PENDING,OVERDUE&overdue_only=true`);
```
또는 worker-home.html의 기존 API에 overdue 필터 추가

---

## 작업 4: 메뉴 연결

`assets/js/tai/menu-tadmin.js`에 추가:
```javascript
{
  name: '미이행 관리',
  icon: 'ti ti-alert-triangle',
  slug: 'overdue-list',
  url: '/app/overdue/overdue-list.html',
  // sector: 'ALL' (모든 섹터 공통)
}
```
위치: 안전관리 하위 메뉴

---

## 체크리스트

- [ ] 안전관리자 대시보드 미이행 위젯
- [ ] overdue-list.html 상세 페이지 (필터 + 테이블)
- [ ] 작업자 홈 미이행 경고 배너
- [ ] [독촉] 버튼 동작
- [ ] [재배정] 모달 (작업자 선택 → assignment 수정)
- [ ] [해소] 확인 모달 (POST /overdue/resolve)
- [ ] 메뉴 연결 (menu-tadmin.js)
- [ ] 법적 리스크 카드 (과태료 금액 표시)
- [ ] 모바일 반응형
- [ ] 첫 번째 열: select-all 체크박스, 두 번째 열: No.

---

## 🔴 금지사항

1. legal_engine API 직접 호출 금지 → /overdue API만 사용
2. 과태료 금액 하드코딩 금지 → 건당 3,000,000원 상수 사용
3. 엔진 스키마 직접 접근 금지
