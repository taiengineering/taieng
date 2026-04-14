# pricing API 엔드포인트 구현 — 백엔드 작업지시서

> 2026-04-14 기획창 작성  
> 대상 레포: taiengineering/tai-api  
> 대상 파일: app/routers/public_pricing.py (신규 생성)  
> 브랜치: dev → PR → main

---

## 목적

`new.taieng.co.kr/nexas/pricing.html` 에서 가격을 API로 가져와 렌더링.  
어드민 화면에서 가격 수정 → 사이트 자동 반영 구조.

---

## 구현할 엔드포인트 2개

### 1. GET /public/pricing/saas-plans

**설명:** SaaS 구독 플랜 목록 (is_active=true 만)

**응답 구조:**
```json
{
  "data": [
    {
      "plan_code": "BUILDING_BASIC",
      "display_name": "건물 BASIC",
      "sector_code": "BUILDING",
      "monthly_base_fee": 59000,
      "is_active": true
    },
    {
      "plan_code": "BUILDING_STANDARD",
      "display_name": "건물 STANDARD",
      "sector_code": "BUILDING",
      "monthly_base_fee": 99000,
      "is_active": true
    },
    {
      "plan_code": "INDUSTRY_STARTER",
      "sector_code": "INDUSTRY",
      "monthly_base_fee": 79000,
      ...
    },
    ...
  ]
}
```

**plan_code 목록 (DB에 없으면 시드 데이터 삽입):**
| plan_code | sector_code | monthly_base_fee |
|-----------|-------------|------------------|
| BUILDING_BASIC | BUILDING | 59000 |
| BUILDING_STANDARD | BUILDING | 99000 |
| INDUSTRY_STARTER | INDUSTRY | 79000 |
| INDUSTRY_BUSINESS | INDUSTRY | 149000 |
| INDUSTRY_PRO | INDUSTRY | 249000 |
| CONSTRUCTION_STANDARD | CONSTRUCTION | 199000 |
| CONSTRUCTION_PREMIUM | CONSTRUCTION | 399000 |

---

### 2. GET /public/pricing/diagnosis-reports

**설명:** 법령진단 리포트 단건 가격 목록 (is_active=true 만)

**응답 구조:**
```json
{
  "data": [
    {
      "facility_type_code": "BUILDING_V2",
      "basic_fee": 0,
      "process_fee": 0,
      "equipment_fee": 0,
      "total_report_fee": 299000,
      "is_active": true
    },
    {
      "facility_type_code": "INDUSTRY_V2",
      "basic_fee": 99000,
      "process_fee": 0,
      "equipment_fee": 199000,
      "total_report_fee": 249000,
      "is_active": true
    },
    {
      "facility_type_code": "CONSTRUCTION_V2",
      "basic_fee": 0,
      "process_fee": 0,
      "equipment_fee": 0,
      "total_report_fee": 299000,
      "is_active": true
    }
  ]
}
```

**facility_type_code 매핑:**
| facility_type_code | 설명 | basic_fee | equipment_fee | total_report_fee |
|--------------------|------|-----------|---------------|------------------|
| BUILDING_V2 | 건물·시설 | 0 | 0 | 299000 |
| INDUSTRY_V2 | 제조·산업 | 99000 | 199000 | 249000 |
| CONSTRUCTION_V2 | 건설현장 | 0 | 0 | 299000 |

프론트엔드 키 매핑 (pricing.js v2 기준):
- `BUILDING_V2.total_report_fee` → `diag-building-total`
- `INDUSTRY_V2.basic_fee` → `diag-industry-basic` (표준 99K)
- `INDUSTRY_V2.equipment_fee` → `diag-industry-equipment` (설비 199K)
- `INDUSTRY_V2.total_report_fee` → `diag-industry-total` (종합 249K)
- `CONSTRUCTION_V2.total_report_fee` → `diag-construction-total`

---

## DB 테이블 확인

먼저 Supabase MCP로 기존 테이블 구조 확인:

```sql
-- 관련 테이블 존재 여부 확인
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'saas_subscription_plans',
    'diagnosis_pricing',
    'pricing_plans',
    'public_pricing'
  );
```

### 케이스 A: 기존 테이블 사용
기존에 `saas_subscription_plans` 또는 유사 테이블이 있으면 해당 컬럼 구조로 쿼리 작성.

### 케이스 B: 테이블 없음 → 신규 생성

```sql
-- SaaS 플랜 테이블
CREATE TABLE IF NOT EXISTS public.saas_subscription_plans (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  plan_code TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  sector_code TEXT NOT NULL,  -- BUILDING / INDUSTRY / CONSTRUCTION
  monthly_base_fee INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 시드 데이터
INSERT INTO public.saas_subscription_plans
  (plan_code, display_name, sector_code, monthly_base_fee)
VALUES
  ('BUILDING_BASIC',        '건물 BASIC',              'BUILDING',      59000),
  ('BUILDING_STANDARD',     '건물 STANDARD',           'BUILDING',      99000),
  ('INDUSTRY_STARTER',      '산업 STARTER',            'INDUSTRY',      79000),
  ('INDUSTRY_BUSINESS',     '산업 BUSINESS',           'INDUSTRY',      149000),
  ('INDUSTRY_PRO',          '산업 PRO',                'INDUSTRY',      249000),
  ('CONSTRUCTION_STANDARD', '건설 STANDARD',           'CONSTRUCTION',  199000),
  ('CONSTRUCTION_PREMIUM',  '건설 PREMIUM',            'CONSTRUCTION',  399000)
ON CONFLICT (plan_code) DO NOTHING;

-- 법령진단 가격 테이블
CREATE TABLE IF NOT EXISTS public.diagnosis_pricing (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  facility_type_code TEXT NOT NULL UNIQUE,  -- BUILDING_V2 / INDUSTRY_V2 / CONSTRUCTION_V2
  basic_fee INTEGER NOT NULL DEFAULT 0,
  process_fee INTEGER NOT NULL DEFAULT 0,
  equipment_fee INTEGER NOT NULL DEFAULT 0,
  total_report_fee INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 시드 데이터
INSERT INTO public.diagnosis_pricing
  (facility_type_code, basic_fee, process_fee, equipment_fee, total_report_fee)
VALUES
  ('BUILDING_V2',      0,      0, 0,      299000),
  ('INDUSTRY_V2',      99000,  0, 199000, 249000),
  ('CONSTRUCTION_V2',  0,      0, 0,      299000)
ON CONFLICT (facility_type_code) DO NOTHING;
```

---

## 라우터 구현 (app/routers/public_pricing.py)

```python
"""
TAI Safe — Public Pricing API
GET /public/pricing/saas-plans
GET /public/pricing/diagnosis-reports
인증 불필요 (공개 엔드포인트)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.response import success_response  # 기존 response 유틸 사용

router = APIRouter(prefix="/public/pricing", tags=["public-pricing"])


@router.get("/saas-plans")
def get_saas_plans(db: Session = Depends(get_db)):
    """SaaS 구독 플랜 목록 (is_active=true, 인증 불필요)"""
    rows = db.execute("""
        SELECT plan_code, display_name, sector_code, monthly_base_fee, is_active
        FROM public.saas_subscription_plans
        WHERE is_active = true
        ORDER BY monthly_base_fee ASC
    """).fetchall()
    return success_response(data=[dict(r) for r in rows])


@router.get("/diagnosis-reports")
def get_diagnosis_reports(db: Session = Depends(get_db)):
    """법령진단 리포트 단건 가격 (is_active=true, 인증 불필요)"""
    rows = db.execute("""
        SELECT facility_type_code, basic_fee, process_fee,
               equipment_fee, total_report_fee, is_active
        FROM public.diagnosis_pricing
        WHERE is_active = true
        ORDER BY facility_type_code ASC
    """).fetchall()
    return success_response(data=[dict(r) for r in rows])
```

> response 유틸이 없으면 직접 `{"success": True, "data": [...]}` 딕셔너리 리턴.

---

## main.py 라우터 등록

기존 main.py에 아래 추가:

```python
from app.routers import public_pricing
app.include_router(public_pricing.router)
```

라우터 순서 주의: `/public/pricing/saas-plans` 같은 구체적 경로가 파라미터 경로보다 앞에 있어야 함.

---

## CORS 확인

`new.taieng.co.kr` 도메인에서 호출하므로 CORS origins에 포함 여부 확인:

```python
# main.py의 CORSMiddleware origins에 포함되어야 할 도메인
"https://new.taieng.co.kr"
```

---

## 테스트

```bash
# 로컬 또는 Fly.io
curl https://api.taieng.co.kr/public/pricing/saas-plans
curl https://api.taieng.co.kr/public/pricing/diagnosis-reports
```

예상 응답:
```json
{"success": true, "data": [{"plan_code": "BUILDING_BASIC", "monthly_base_fee": 59000, ...}, ...]}
```

---

## 완료 조건

- [ ] DB 테이블 확인 또는 신규 생성 (Supabase MCP apply_migration)
- [ ] 시드 데이터 삽입
- [ ] app/routers/public_pricing.py 생성
- [ ] main.py에 라우터 등록
- [ ] CORS 확인
- [ ] dev 브랜치 push → PR 생성
- [ ] curl 테스트 통과
