# TAI 작업지시서 — 법령진단 결제 흐름 수정 (백엔드)

> 작성일: 2026-04-01
> 대상: tai-api

---

## 배경 및 핵심 결정

```
기존 (잘못된 방향):
  POST /diagnosis/purchases → 즉시 has_access=true (B2C 직접결제)

올바른 방향 (B2B 플로우):
  견적(quotes) 신청
    → 관리자 확인·승인
    → 계약(contracts) 생성
    → has_access 체크는 contracts 기준
```

---

## 작업 1: quotes.service_type 확장

### 현재 사용 중인 service_type
```
SAAS       → SaaS 구독
CONSULTING → 컨설팅
```

### 추가
```sql
-- service_type 'DIAGNOSIS' 추가 (DB 컬럼은 text라 migration 불필요)
-- quotes 생성 시 service_type='DIAGNOSIS' 사용
-- items JSONB 구조:
-- [
--   {
--     "sector": "MANUFACTURING",
--     "step": 2,
--     "step_label": "2단계 공정진단",
--     "factory_id": "uuid",
--     "factory_name": "1호 공장",
--     "unit_price": 49000,
--     "quantity": 1
--   }
-- ]
```

---

## 작업 2: POST /quotes — DIAGNOSIS 견적 생성 엔드포인트 추가

`routers/quotes.py` 또는 `routers/diagnosis.py`에 추가

```python
# POST /diagnosis/request-quote
# 기존 POST /quotes와 동일한 로직, service_type='DIAGNOSIS' 고정

class DiagnosisQuoteRequest(BaseModel):
    factory_id: str
    sector: str          # BUILDING / MANUFACTURING / CONSTRUCTION / SPECIAL_FACILITY
    step: int            # 2 or 3
    contact_name: str
    contact_phone: str
    contact_email: Optional[str]
    memo: Optional[str]

@router.post("/diagnosis/request-quote")
async def request_diagnosis_quote(
    body: DiagnosisQuoteRequest,
    current_user = Depends(get_current_user)
):
    # SECTOR_PRICES 기준 금액 계산
    SECTOR_PRICES = {
        'BUILDING':         {'s2': 29000,  's3': 59000,  'report': 99000},
        'MANUFACTURING':    {'s2': 49000,  's3': 99000,  'report': 249000},
        'SPECIAL_FACILITY': {'s2': 49000,  's3': 99000,  'report': 199000},
        'CONSTRUCTION':     {'s2': 79000,  's3': 149000, 'report': 399000},
    }
    step_key = f's{body.step}'
    unit_price = SECTOR_PRICES[body.sector][step_key]
    supply_amount = unit_price
    vat_amount = int(supply_amount * 0.1)
    total_amount = supply_amount + vat_amount

    # factory 정보 조회
    factory = supabase.table('factories').select('name').eq('id', body.factory_id).single().execute()

    items = [{
        'sector': body.sector,
        'step': body.step,
        'step_label': f'{body.step}단계 진단',
        'factory_id': body.factory_id,
        'factory_name': factory.data.get('name', ''),
        'unit_price': unit_price,
        'quantity': 1
    }]

    quote_data = {
        'company_id': current_user['company_id'],
        'service_type': 'DIAGNOSIS',
        'status_code': 'REQUESTED',
        'contact_name': body.contact_name,
        'contact_phone': body.contact_phone,
        'contact_email': body.contact_email,
        'supply_amount': supply_amount,
        'vat_amount': vat_amount,
        'total_amount': total_amount,
        'items': items,
        'memo': body.memo,
        'created_by': current_user['id']
    }

    result = supabase.table('quotes').insert(quote_data).execute()
    return {'status': 'success', 'data': result.data[0]}
```

---

## 작업 3: /diagnosis/access-check 로직 변경

```python
# 기존: diagnosis_purchases 테이블 확인
# 변경: contracts 테이블에서 DIAGNOSIS 활성 계약 확인

@router.get("/diagnosis/access-check")
async def check_diagnosis_access(
    factory_id: str,
    step: int,
    current_user = Depends(get_current_user)
):
    company_id = current_user['company_id']

    # contracts에서 DIAGNOSIS 계약 확인
    # items JSONB에 factory_id + step 포함 여부 체크
    result = supabase.table('contracts').select('id, items').eq(
        'company_id', company_id
    ).eq(
        'service_type', 'DIAGNOSIS'
    ).eq(
        'status_code', 'ACTIVE'
    ).eq(
        'is_active', True
    ).execute()

    has_access = False
    for contract in result.data:
        items = contract.get('items') or []
        for item in items:
            if (
                item.get('factory_id') == factory_id and
                item.get('step') == step
            ):
                has_access = True
                break
        if has_access:
            break

    return {'status': 'success', 'data': {'has_access': has_access}}
```

---

## 작업 4: diagnosis_purchases 테이블 처리

```
기존 POST /diagnosis/purchases 는 deprecated 처리
→ 내부 관리 로그 용도로만 유지 (삭제 금지)
→ 해당 엔드포인트에 deprecation 주석 추가
→ 프론트에서 더 이상 호출 안 함
```

---

## 작업 5: contracts 생성 시 DIAGNOSIS items 저장

기존 admin에서 견적 → 계약 전환 로직(`POST /contracts`)에
service_type='DIAGNOSIS'일 때 quotes.items를 contracts.items로 복사하는 로직 확인/추가

```python
# contracts 생성 시 (admin에서 승인 처리)
if quote['service_type'] == 'DIAGNOSIS':
    contract_data['items'] = quote['items']  # factory_id, step 정보 유지
    contract_data['service_type'] = 'DIAGNOSIS'
    contract_data['status_code'] = 'ACTIVE'
    # end_date: 진단 결과는 영구 (None or 1년 후)
```

---

## Railway 배포 후 확인

```
1. POST /diagnosis/request-quote
   → 200, quotes 테이블에 service_type='DIAGNOSIS' 행 생성

2. GET /diagnosis/access-check?factory_id={uuid}&step=2
   → 계약 없을 때: { has_access: false }
   → 계약 있을 때: { has_access: true }

3. 기존 GET /diagnosis/access-check 호환성 유지
```
