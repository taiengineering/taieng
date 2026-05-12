# 법정점검 기준일 설정 페이지 작업지시서
## 작성일: 2026-03-31 | 담당: 프론트엔드 창

---

## 배경 및 목적

법령진단 완료 후 `inspection_sets`가 자동 생성되지만,
**기준일(`schedule_anchor_date`)이 비어 있어** 실제 일정 계산이 불가능합니다.

업체마다 기준일이 다르기 때문에 (마지막 점검일, 설치일, 사용승인일 등)
SaaS 사용자가 **직접 기준일을 입력**하는 tadmin 전용 페이지가 필요합니다.

법령이 요구하는 기준점 유형을 **안내 문구로 표시**하여
사용자가 어떤 날짜를 입력해야 하는지 알 수 있게 합니다.

---

## 파일 정보

**생성 파일:** `tadmin/html/inspection-anchor.html`  
**메뉴 위치:** 점검관리 > 법정점검 기준일 설정

---

## DB 구조 (참고)

### inspection_sets (핵심 테이블)
```
id                  UUID
factory_id          UUID → factories
inspection_set_name TEXT  (예: "산업안전보건법 점검")
law_name            TEXT  (예: "산업안전보건법")
law_article         TEXT  (예: "제36조")
cycle_value         INT   (예: 1)
cycle_unit          TEXT  (예: "year")
cycle_base_type     TEXT  기준점유형 (NEW: LAST_INSPECTION/APPROVAL_DATE/INSTALL_DATE/MANUFACTURE_DATE)
cycle_base_guide    TEXT  안내문구  (NEW: "마지막 점검일로부터 1년마다")
schedule_anchor_date DATE  ← 사용자가 입력해야 하는 값 (기준일)
last_inspection_date DATE  ← 직전 점검 완료일 (선택 입력)
next_planned_date   DATE  ← 자동 계산 (anchor + cycle)
anchor_confirmed    BOOL  ← 입력 완료 여부
source              TEXT  = 'LEGAL_ENGINE'
is_active           BOOL
```

### cycle_base_type 값 설명
| 코드 | 의미 | 입력 안내 |
|------|------|----------|
| LAST_INSPECTION | 마지막 점검일 | "마지막으로 점검한 날짜를 입력하세요" |
| APPROVAL_DATE | 건물 사용승인일 | "건축물 사용승인일을 입력하세요" |
| INSTALL_DATE | 설비/시설 설치일 | "해당 시설의 설치일을 입력하세요" |
| MANUFACTURE_DATE | 제조/등록일 | "장비 등록일(제조일)을 입력하세요" |
| CUSTOM | 직접 지정 | "기준일을 직접 입력하세요" |

---

## 페이지 구조

### 1. 상단 구성
- **시설 선택 드롭다운** (필수) → 선택 시 하단 목록 로드
- 완료 현황 뱃지: `기준일 설정 완료 N건 / 전체 N건`
- [일괄 저장] 버튼

### 2. 진행 상태 바 (상단 요약)
```
[미설정 N건 🔴] [설정 완료 N건 🟢] [다음 점검 임박 N건 🟡]
```

### 3. 메인 카드 목록 (inspection_sets 항목별)

각 카드 구성:
```
┌─────────────────────────────────────────────────────────┐
│ 🔴 [미설정] 산업안전보건법 제36조          연 1회 점검  │
│                                                          │
│ 📌 기준점 안내                                          │
│ " 마지막 점검일로부터 1년마다 "                         │
│                                                          │
│ 마지막 점검일  [ 2024-03-15  📅 ]                       │
│ 다음 점검 예정: 2025-03-15 (자동계산)                   │
│                                                          │
│ 직전 점검 완료일 (선택)  [ _________ 📅 ]               │
│                                                          │
│                              [저장]                     │
└─────────────────────────────────────────────────────────┘
```

**기준점 유형별 입력 필드명 변경:**
| cycle_base_type | 필드 라벨 |
|---|---|
| LAST_INSPECTION | 마지막 점검일 |
| APPROVAL_DATE | 건물 사용승인일 |
| INSTALL_DATE | 설치일 |
| MANUFACTURE_DATE | 장비 등록일 |

---

## API 명세

### 목록 조회
```
GET /inspection-sets?factory_id={id}&source=LEGAL_ENGINE&page=1&size=50

응답 항목 (필요 필드):
- id, inspection_set_name
- law_name, law_article
- cycle_value, cycle_unit
- cycle_base_type, cycle_base_guide  ← 안내 문구
- schedule_anchor_date               ← 기준일 (NULL이면 미설정)
- last_inspection_date
- next_planned_date
- anchor_confirmed
```

### 기준일 저장
```
PATCH /inspection-sets/{id}/anchor
Body:
{
  "schedule_anchor_date": "2024-03-15",  // 기준일 (필수)
  "last_inspection_date": "2024-03-15"   // 직전 점검일 (선택, 보통 같음)
}

백엔드 처리:
1. schedule_anchor_date 저장
2. next_planned_date 자동 계산:
   - cycle_unit = 'month'  → anchor + cycle_value months
   - cycle_unit = 'year'   → anchor + cycle_value years
   - cycle_unit = 'half_year' → anchor + 6 months
   - cycle_unit = 'quarter'   → anchor + 3 months
3. anchor_confirmed = true 저장
4. last_inspection_date 저장 (있을 경우)
```

### 일괄 저장
```
PATCH /inspection-sets/anchor/bulk
Body:
{
  "items": [
    { "id": "uuid1", "schedule_anchor_date": "2024-03-15", "last_inspection_date": "2024-03-15" },
    { "id": "uuid2", "schedule_anchor_date": "2023-07-01" }
  ]
}
```

---

## UI 상세 동작

### 상태 표시
- `anchor_confirmed = false` AND `schedule_anchor_date = null` → 🔴 빨간 뱃지 "미설정"
- `anchor_confirmed = true` → 🟢 초록 뱃지 "설정 완료"
- `next_planned_date` - 오늘 <= 30일 → 🟡 "D-{N}" 임박 뱃지 추가
- `next_planned_date` < 오늘 → 🔴 "기간 초과" 뱃지

### 다음 점검일 실시간 계산
- 날짜 입력 시 `next_planned_date` 즉시 계산하여 화면에 표시 (저장 전 미리보기)
- 계산 로직 (JS):
```javascript
function calcNext(anchorDate, cycleValue, cycleUnit) {
  const d = new Date(anchorDate);
  if (cycleUnit === 'month')     d.setMonth(d.getMonth() + cycleValue);
  else if (cycleUnit === 'year') d.setFullYear(d.getFullYear() + cycleValue);
  else if (cycleUnit === 'half_year') d.setMonth(d.getMonth() + 6);
  else if (cycleUnit === 'quarter')   d.setMonth(d.getMonth() + 3);
  return d.toISOString().split('T')[0];
}
```

### 필터 탭
```
[전체] [미설정] [설정완료] [임박(30일 이내)] [기간초과]
```

---

## 목록 컬럼 (Global Rule 적용)

리스트형 보조 테이블 (카드 하단 접이식):
1. 체크박스 (toggleAll)
2. No.
3. 법령명 + 조문
4. 점검 주기 (예: 연 1회)
5. 기준점 유형 뱃지
6. 기준일 (설정 시 날짜, 미설정 시 [-])
7. 다음 점검 예정일
8. 상태 뱃지

---

## menu-nav.js 수정

`tadmin`의 점검관리 메뉴에 항목 추가:
```javascript
{ label: '법정점검 기준일 설정', href: 'inspection-anchor.html' }
```

---

## 백엔드 작업 (별도 지시서)

`/inspection-sets/{id}/anchor` PATCH 엔드포인트 구현 필요.
현재 `inspection_sets.py`에 없으므로 추가 필요.

처리 로직:
```python
# cycle_unit → 개월 수 변환
UNIT_TO_MONTHS = {
    'month': 1, 'quarter': 3, 'half_year': 6, 'year': 12
}
# year 계산 시 월 변환 대신 timedelta 대신 dateutil.relativedelta 사용
```

---

## 완료 기준

- [ ] 시설 선택 후 inspection_sets 목록 로드
- [ ] 각 항목에 cycle_base_guide 안내 문구 표시
- [ ] 날짜 입력 시 next_planned_date 실시간 계산 표시
- [ ] 개별 저장 동작 (PATCH /inspection-sets/{id}/anchor)
- [ ] 상태 뱃지 (미설정/완료/임박/초과) 표시
- [ ] 필터 탭 동작
- [ ] 일괄 저장 버튼 동작
