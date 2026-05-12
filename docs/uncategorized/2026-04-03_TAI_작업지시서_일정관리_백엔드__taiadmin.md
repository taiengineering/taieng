# 작업지시서 — 엔진설정 > 일정관리 백엔드

## 목적
`inspection_sets` 테이블의 데이터를 조회·수정할 수 있는 API 신규 생성.
반복주기(cycle)와 기준시점(anchor)을 관리하는 것이 핵심.

## 파일
`routers/inspection_schedule.py` (신규 생성)
`main.py` 에 라우터 등록

---

## API 목록

### 1. GET /inspection-schedule/sets
**설명**: inspection_sets 전체 목록 (페이지네이션, 필터)

**Query Params**:
- `page` int default=1
- `page_size` int default=30 max=100
- `factory_id` str optional
- `status_code` str optional (PENDING_ANCHOR | ACTIVE | INACTIVE)
- `source` str optional (LEGAL_ENGINE | MANUAL)
- `anchor_confirmed` bool optional
- `cycle_unit` str optional (year | month | quarter | half_year | week | day)

**Response**:
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "factory_id": "uuid",
        "factory_name": "string",  // factories.name JOIN
        "inspection_set_name": "string",
        "law_name": "string",
        "law_article": "string",
        "source": "LEGAL_ENGINE | MANUAL",
        // ★ 반복 (주기)
        "cycle_unit": "year | month | quarter | half_year | week | day",
        "cycle_value": 1,
        "cycle_label": "연 1회 | 반기 1회 | 분기 1회 | 월 1회 ...",  // 계산값
        "cycle_base_type": "LAST_INSPECTION | FIXED_DATE",
        "cycle_base_guide": "string",
        // ★ 시점 (anchor)
        "last_inspection_date": "2024-01-01",
        "schedule_anchor_date": "2024-01-01",
        "next_planned_date": "2024-07-01",
        "schedule_end_date": null,
        "anchor_confirmed": false,
        "status_code": "PENDING_ANCHOR"
      }
    ],
    "total": 68,
    "page": 1,
    "page_size": 30
  }
}
```

**cycle_label 계산 로직** (Python):
```python
def get_cycle_label(cycle_unit: str, cycle_value: int) -> str:
    UNIT_MAP = {
        "year":      lambda v: f"연 {v}회" if v == 1 else f"{v}년마다",
        "half_year": lambda v: "반기 1회",
        "quarter":   lambda v: "분기 1회",
        "month":     lambda v: f"월 {v}회" if v == 1 else f"{v}개월마다",
        "week":      lambda v: f"주 {v}회" if v == 1 else f"{v}주마다",
        "day":       lambda v: f"일 {v}회" if v == 1 else f"{v}일마다",
    }
    fn = UNIT_MAP.get(cycle_unit)
    return fn(cycle_value) if fn else f"{cycle_value} {cycle_unit}"
```

---

### 2. GET /inspection-schedule/sets/{set_id}
**설명**: 단건 상세 조회 (수정 모달용)

**Response**: 위 items 단건

---

### 3. PATCH /inspection-schedule/sets/{set_id}
**설명**: 반복주기 및 기준시점 수정

**Request Body** (수정 가능한 필드만):
```json
{
  "cycle_unit": "month",
  "cycle_value": 1,
  "cycle_base_type": "LAST_INSPECTION",
  "last_inspection_date": "2024-03-15",
  "schedule_anchor_date": "2024-03-15",
  "schedule_end_date": null,
  "anchor_confirmed": true,
  "status_code": "ACTIVE",
  "description": "메모"
}
```

**처리 로직**:
1. 허용 필드만 필터링
2. `anchor_confirmed = true` 이고 `schedule_anchor_date` 있으면 `next_planned_date` 자동 계산:
   ```python
   from datetime import date
   from dateutil.relativedelta import relativedelta

   def calc_next_date(anchor: date, unit: str, value: int) -> date:
       DELTA = {
           "year":      relativedelta(years=value),
           "half_year": relativedelta(months=6),
           "quarter":   relativedelta(months=3),
           "month":     relativedelta(months=value),
           "week":      relativedelta(weeks=value),
           "day":       relativedelta(days=value),
       }
       return anchor + DELTA.get(unit, relativedelta(years=1))
   ```
3. `status_code` = `ACTIVE` 자동 설정 (anchor_confirmed=true일 때)
4. `updated_at` = now()

**Response**:
```json
{"status": "success", "data": {/* 수정된 row */}}
```

---

### 4. POST /inspection-schedule/sets/{set_id}/confirm-anchor
**설명**: 기준일 확정 (anchor_confirmed=true + next_planned_date 계산)

**Request Body**:
```json
{
  "anchor_date": "2024-03-15",  // 기준일 (마지막 점검일 또는 설치일)
  "anchor_type": "LAST_INSPECTION"  // LAST_INSPECTION | INSTALL_DATE | FIXED_DATE
}
```

**처리**: schedule_anchor_date 저장, next_planned_date 계산, anchor_confirmed=true, status_code=ACTIVE

---

### 5. GET /inspection-schedule/summary
**설명**: 전체 현황 요약 (페이지 상단 카드용)

**Response**:
```json
{
  "status": "success",
  "data": {
    "total": 68,
    "pending_anchor": 67,  // 기준일 미설정
    "active": 1,           // 일정 활성
    "by_cycle": {
      "year": 45, "half_year": 9, "quarter": 8, "month": 6
    },
    "by_source": {
      "LEGAL_ENGINE": 67, "MANUAL": 1
    }
  }
}
```

---

## main.py 등록
```python
from routers import inspection_schedule
app.include_router(inspection_schedule.router)
```

## 의존성
- `python-dateutil` (이미 설치되어 있을 가능성 높음, 없으면 requirements.txt 추가)
- DB: factories 테이블과 JOIN 필요 (`factories.name`)
