# TAI Backend Memory — 2026-04-01

## 배포 마지막 버전
- v5.0.0 (Railway, 2026-04-01)

## 구현된 신규 라우터

### TBM (`routers/tbm.py`)
```
POST   /tbm
GET    /tbm?factory_id=&page=&size=
GET    /tbm/{id}
PATCH  /tbm/{id}
POST   /tbm/{id}/complete
POST   /tbm/transcribe           ← STT (Web Speech API 결과 저장)
GET    /tbm/{id}/attendees
POST   /tbm/{id}/attendees
PATCH  /tbm/{id}/attendees/{aid}/sign
```

### 안전보건회의 (`routers/safety_meetings.py`)
```
POST   /safety-meetings
GET    /safety-meetings?company_id=&meeting_type=&page=
GET    /safety-meetings/schedule?company_id=
GET    /safety-meetings/{id}
PATCH  /safety-meetings/{id}
POST   /safety-meetings/{id}/files
POST   /safety-meetings/{id}/complete
```

### 위험성평가 (`routers/risk_assessments.py`)
```
POST   /risk-assessments
GET    /risk-assessments?factory_id=&assessment_type=&page=
GET    /risk-assessments/dashboard?factory_id=
GET    /risk-assessments/{id}
PATCH  /risk-assessments/{id}
POST   /risk-assessments/{id}/files
POST   /risk-assessments/{id}/complete
```

### 법령진단 (`routers/diagnosis.py`)
```
GET    /diagnosis/access-check?factory_id=&step=
  → diagnosis_purchases 단건 결제 기록만 확인
  → SaaS contract_level 무시
  → Response: { has_access: bool }

POST   /diagnosis/purchases (v1.1.0)
  → payment_method=card:     status=PAID, paid_at=now() 즉시
  → payment_method=transfer: status=PENDING
  → payment_method=invoice:  status=PENDING
  → 가격 검증: SECTOR_PRICES 불일치 시 422
```

## SECTOR_PRICES (백엔드 검증 기준)
```python
SECTOR_PRICES = {
  'BUILDING':         {'s2': 29000,  's3': 59000,  'report': 99000},
  'MANUFACTURING':    {'s2': 49000,  's3': 99000,  'report': 249000},
  'SPECIAL_FACILITY': {'s2': 49000,  's3': 99000,  'report': 199000},
  'CONSTRUCTION':     {'s2': 79000,  's3': 149000, 'report': 399000},
}
```

## 주의사항
- factory_id: UUID 형식만 허용 (cc000003 형식 금지)
- 목록 API: factory_id or company_id 필수 (company_id 토큰에서 자동 추출)
- diagnosis_purchases: status 필드에 PAID/PENDING 관리자 화면 필요
