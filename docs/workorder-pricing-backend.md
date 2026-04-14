# 가격체계 백엔드 작업지시서

> 2026-04-14 기획창 작성
> 대상: tai-api (api.taieng.co.kr)
> 브랜치: dev → PR → main

---

## 개요

어드민에서 가격을 수정하면 pricing.html(new.taieng.co.kr)에 즉시 반영되는 구조.
법령진단은 리포트만 제공 (일정생성·TBM·신고서식은 SaaS 기능).

---

## 1. DB 마이그레이션

### 1-1. price_saas_plan 새 데이터

기존 데이터 is_active=false 처리 후, 섹터별 신규 INSERT.

```sql
UPDATE price_saas_plan SET is_active = false;

ALTER TABLE price_saas_plan
  ADD COLUMN IF NOT EXISTS sector TEXT,
  ADD COLUMN IF NOT EXISTS billing_unit TEXT DEFAULT 'FACILITY',
  ADD COLUMN IF NOT EXISTS sms_included INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS kakao_included INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS doc_included INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS include_tbm BOOLEAN DEFAULT false;

-- 건물
INSERT INTO price_saas_plan (plan_code, display_name, sector, billing_unit, monthly_base_fee, sms_included, kakao_included, doc_included, storage_history_month, include_tbm, badge_color, sort_order, is_active)
VALUES
  ('BUILDING_BASIC', 'BASIC', 'BUILDING', 'FACILITY', 59000, 50, 50, 5, 6, false, 'secondary', 1, true),
  ('BUILDING_STANDARD', 'STANDARD', 'BUILDING', 'FACILITY', 99000, 150, 150, 15, -1, false, 'primary', 2, true),
  ('BUILDING_CUSTOM', 'CUSTOM', 'BUILDING', 'FACILITY', 0, 0, 0, 0, -1, false, 'dark', 3, true);

-- 산업
INSERT INTO price_saas_plan (plan_code, display_name, sector, billing_unit, monthly_base_fee, sms_included, kakao_included, doc_included, storage_history_month, include_tbm, badge_color, sort_order, is_active)
VALUES
  ('INDUSTRY_STARTER', 'STARTER', 'INDUSTRY', 'FACILITY', 79000, 100, 100, 10, 6, false, 'secondary', 10, true),
  ('INDUSTRY_BUSINESS', 'BUSINESS', 'INDUSTRY', 'FACILITY', 149000, 300, 300, 30, -1, false, 'primary', 11, true),
  ('INDUSTRY_PRO', 'PRO', 'INDUSTRY', 'FACILITY', 249000, 500, 500, 50, -1, true, 'info', 12, true),
  ('INDUSTRY_CUSTOM', 'CUSTOM', 'INDUSTRY', 'FACILITY', 350000, 0, 0, 0, -1, true, 'dark', 13, true);

-- 건설
INSERT INTO price_saas_plan (plan_code, display_name, sector, billing_unit, monthly_base_fee, sms_included, kakao_included, doc_included, storage_history_month, include_tbm, badge_color, sort_order, is_active)
VALUES
  ('CONSTRUCTION_STANDARD', 'STANDARD', 'CONSTRUCTION', 'SITE', 199000, 300, 300, 30, -1, true, 'primary', 20, true),
  ('CONSTRUCTION_PREMIUM', 'PREMIUM', 'CONSTRUCTION', 'SITE', 399000, 500, 500, 50, -1, true, 'warning', 21, true),
  ('CONSTRUCTION_CUSTOM', 'CUSTOM', 'CONSTRUCTION', 'SITE', 500000, 0, 0, 0, -1, true, 'dark', 22, true);
```

### 1-2. price_diagnosis_report 새 데이터

```sql
UPDATE price_diagnosis_report SET is_active = false;

-- 건물: 무료 + 299K (2단계)
INSERT INTO price_diagnosis_report (facility_type_code, facility_type_name, basic_fee, process_fee, equipment_fee, total_report_fee, is_active, sort_order)
VALUES ('BUILDING_V2', '건물', 0, 299000, 0, 0, true, 1);

-- 산업: 무료 + 99K + 199K + 249K (4단계)
INSERT INTO price_diagnosis_report (facility_type_code, facility_type_name, basic_fee, process_fee, equipment_fee, total_report_fee, is_active, sort_order)
VALUES ('INDUSTRY_V2', '산업(제조·공장)', 0, 99000, 199000, 249000, true, 2);

-- 건설: 무료 + 299K (2단계)
INSERT INTO price_diagnosis_report (facility_type_code, facility_type_name, basic_fee, process_fee, equipment_fee, total_report_fee, is_active, sort_order)
VALUES ('CONSTRUCTION_V2', '건설', 0, 299000, 0, 0, true, 3);
```

### 1-3. 연결 서비스 사전등록 테이블

```sql
CREATE TABLE IF NOT EXISTS connect_pre_registration (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  reg_type TEXT NOT NULL,
  service_type TEXT NOT NULL,
  company_name TEXT,
  contact_name TEXT NOT NULL,
  contact_phone TEXT NOT NULL,
  contact_email TEXT,
  region TEXT,
  description TEXT,
  status TEXT DEFAULT 'PENDING',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 2. API 작업

### 2-1. 공개 가격 API (인증 불필요)

파일: `app/routers/public_pricing.py` 신규

```
GET /public/pricing/saas-plans
  → is_active=true만 반환
  → sector별 그룹핑: { building: [...], industry: [...], construction: [...] }

GET /public/pricing/diagnosis-reports
  → is_active=true만 반환

GET /public/pricing/overage-rates
  → 초과 과금 단가 (하드코딩 또는 별도 테이블)
```

응답 캐시: Cache-Control: public, max-age=300 (5분)
CORS: new.taieng.co.kr 허용

### 2-2. 연결 사전등록 API

파일: `app/routers/connect_registration.py` 신규

```
POST /public/connect/pre-register (인증 불필요)
  body: { reg_type, service_type, company_name, contact_name, contact_phone, ... }
  → INSERT + 관리자 SMS 알림

GET /connect/pre-registrations (관리자 인증)
  → 전체 목록, 필터: reg_type, service_type, status

PATCH /connect/pre-registrations/{id} (관리자 인증)
  → status 변경
```

### 2-3. 기존 price-setting API 수정

- GET /price-setting/saas-plans → sector 파라미터 추가
- 새 컬럼(sector, sms_included 등) 포함

### 2-4. main.py 라우터 등록

```python
from app.routers import public_pricing, connect_registration
app.include_router(public_pricing.router)
app.include_router(connect_registration.router)
```

---

## 3. 작업 순서

```
[1] DB 마이그레이션 (Supabase MCP)
[2] public_pricing.py 생성 + 배포 + 확인
[3] connect_registration.py 생성 + 배포 + 확인
[4] price_setting.py 수정
```

---

## 4. 주의사항

- 법령진단 = 리포트만 제공. 일정생성·TBM·신고서식은 SaaS 기능.
- 공개 API는 인증 불필요, rate limit 적용
- 기존 데이터 삭제 금지 (is_active=false)
- 관리자가 가격 수정 → 5분 내 사이트 반영 (캐시 TTL)
