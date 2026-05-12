# API Payload 예시

Base URL 예: `https://api.taieng.co.kr`

---

## 1. POST `/api/v1/partner-submissions` — 초안 또는 즉시 제출

### 수선업체 (초안)

```json
{
  "partner_type": "REPAIR_CONTRACTOR",
  "submit": false,
  "common": {
    "legal_name": "(주)한빛시공",
    "ceo_name": "김대표",
    "manager_name": "이담당",
    "phone": "010-1234-5678",
    "email": "biz@hanbit.co.kr",
    "business_number": "123-45-67890",
    "address": "서울특별시 강남구 테헤란로 123",
    "address_detail": "4층",
    "service_regions": ["SEOUL", "GYEONGGI"],
    "website_url": "https://example.com",
    "introduction": "소방·전기 긴급 출동 전문입니다.",
    "tax_invoice_available": true
  },
  "detail": {
    "trades": ["FIRE", "ELECTRIC"],
    "work_scope_description": "소방시설 점검·보수, 전기 판넬 교체",
    "construction_regions": ["SEOUL"],
    "emergency_dispatch": true,
    "quote_method": "BOTH",
    "as_available": true,
    "work_hours_description": "평일 09~18, 긴급 시 협의",
    "insurance_enrolled": true,
    "technical_staff_count": 8
  }
}
```

### 선임기술자 (제출)

```json
{
  "partner_type": "APPOINTED_EXPERT",
  "submit": true,
  "common": {
    "legal_name": "홍길동 기술사 사무소",
    "manager_name": "홍길동",
    "phone": "010-0000-0000",
    "email": "hong@example.com",
    "business_number": null,
    "service_regions": ["GYEONGGI", "INCHEON"],
    "introduction": "제조업 안전·보건 선임 12년 경력입니다.",
    "tax_invoice_available": true,
    "terms_agreed_at": "2026-04-01T09:00:00.000Z",
    "privacy_agreed_at": "2026-04-01T09:00:00.000Z"
  },
  "detail": {
    "registration_kind": "INDIVIDUAL",
    "appointment_fields": ["SAFETY", "HEALTH"],
    "industry_segments": ["MANUFACTURING"],
    "activity_regions": ["GYEONGGI"],
    "monthly_contract_ok": true,
    "short_consult_ok": true,
    "site_visit_ok": true,
    "certificate_type": "산업안전기사",
    "certificate_number": "1234567890",
    "certificate_obtained_at": "2018-05-01",
    "career_years": 12,
    "task_scope_description": "안전보건관리책임자 선임, 현장 점검",
    "monthly_facility_capacity": 5
  }
}
```

### 안전관리대행업체

```json
{
  "partner_type": "SAFETY_AGENCY",
  "submit": true,
  "common": {
    "legal_name": "(주)세이프파트너스",
    "ceo_name": "박대표",
    "manager_name": "최팀장",
    "phone": "02-0000-0000",
    "email": "contact@safe-partners.kr",
    "business_number": "987-65-43210",
    "address": "경기도 성남시 분당구",
    "service_regions": ["NATIONWIDE"],
    "introduction": "중대재해 대응 및 안전관리체계 구축 컨설팅.",
    "tax_invoice_available": true,
    "terms_agreed_at": "2026-04-01T10:00:00.000Z",
    "privacy_agreed_at": "2026-04-01T10:00:00.000Z"
  },
  "detail": {
    "agency_kind": "CONSULTING",
    "services_offered": ["중대재해 예방 컨설팅", "안전관리체계 수립"],
    "target_industries": ["제조", "건설"],
    "service_regions": ["SEOUL", "GYEONGGI"],
    "contract_forms": ["MONTHLY", "PROJECT"],
    "online_management_ok": true,
    "report_provided": true,
    "saas_integration_ok": true,
    "periodic_visit_per_month": 2
  }
}
```

---

## 2. PATCH `/api/v1/partner-submissions/:id`

```json
{
  "common": {
    "introduction": "소개 문구 보완"
  },
  "detail": {
    "emergency_dispatch": false
  },
  "submit": false
}
```

---

## 3. POST `/api/v1/partner-submissions/:id/submit`

```json
{}
```

서버: `status`를 `DRAFT` → `SUBMITTED`, `submitted_at` 기록.

---

## 4. POST `/api/v1/admin/partner-submissions/:id/transition`

```json
{
  "to": "NEEDS_SUPPLEMENT",
  "note": "사업자등록증 스캔본과 보험가입 증빙을 업로드해 주세요.",
  "fields": ["common.logo_url", "detail.insurance_enrolled", "detail.license_file_urls"]
}
```

```json
{
  "to": "APPROVED",
  "note": "심사 완료. 공개 프로필 생성됨."
}
```

```json
{
  "to": "REJECTED",
  "note": "제출 서류 상 위조 의심으로 반려."
}
```

---

## 5. 응답 예시 GET `/api/v1/partner-submissions/:id`

```json
{
  "id": "psub_01jqxyz",
  "partner_type": "REPAIR_CONTRACTOR",
  "status": "NEEDS_SUPPLEMENT",
  "schema_version": 1,
  "common": { },
  "detail": { },
  "supplement_note": "보험 증빙 필요",
  "supplement_requested_fields": ["detail.insurance_proof"],
  "created_at": "2026-04-01T08:00:00.000Z",
  "updated_at": "2026-04-01T12:00:00.000Z"
}
```

*(관리자 전용 필드는 일반 사용자 토큰에서는 제외)*
