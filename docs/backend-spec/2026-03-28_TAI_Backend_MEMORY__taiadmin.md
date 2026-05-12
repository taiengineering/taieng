# TAI Backend 메모리 — 2026-03-28

---

## 서버 정보
- API: api.taieng.co.kr (Railway)
- DB: Supabase (xntdkrjhgcscmqctdzyo)
- 스택: FastAPI + Python 3.13.4
- GitHub: taiengineering/tai-api
- 최고관리자: hetto@kakao.com / 심태왕 / role_code: 001

---

## 오늘 완료된 작업

### 1. repair 테이블 2개 생성 ✅

**repair_companies:**
```sql
CREATE TABLE repair_companies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name text NOT NULL,
  representative_name text,
  contact_phone text,
  contact_email text,
  address text,
  service_regions text[] DEFAULT '{}',
  max_project_amount int,
  verified_status text DEFAULT 'UNVERIFIED',
  is_active bool DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz
);
```

**repair_requests (컴럼 4개 추가):**
```sql
CREATE TABLE repair_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  factory_id uuid REFERENCES factories(id),
  company_id uuid REFERENCES companies(id),
  request_title text,           -- 크럼 영→ 정상
  request_content text,         -- 크럼 영→ 정상
  project_amount int DEFAULT 0, -- 크럼 영→ 정상
  fee_amount int DEFAULT 0,
  matched_repair_company_id uuid REFERENCES repair_companies(id), -- 크럼 영→ 정상
  status_code text DEFAULT 'PENDING',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz
);
```

**문제점:** 기존 repair_requests 테이블이 다른 구조로 존재했을 가능성 → 커럼 추가 조진

### 2. notification_settings 42개 재입력 ✅
- 기존 42개 삭제 후 신규 42개 INSERT
- 컴럼: trigger_code, trigger_name, trigger_group, channel_email/kakao/push/site, email_subject, email_body, site_title, site_body, is_active
- API 확인: https://api.taieng.co.kr/notification-settings

---

## 현재 라우터 목록 (main.py v3.2.0)

| 파일 | prefix | 주요 기능 |
|------|--------|----------|
| auth.py | /auth | 로그인/회원가입/토큰 |
| users.py | /users | 회원 CRUD |
| companies.py | /companies | 사업장 CRUD |
| factories.py | /factories | 시설 CRUD |
| system_codes.py | /system-codes | 전역변수 (195카테/1,471코드) |
| legal_engine.py | /legal-engine | 법령 판정 v4.1.2 (396룰) |
| ksic_engine.py | /ksic-engine | KSIC 설비 판정 |
| factory_process_v3.py | /factory-process | 공정 관리 |
| process_management.py | /process-management | 공정 마스터 |
| building_register.py | /building-register | 건축물대장 |
| quotes.py | /quotes | 견적/설문 |
| report_forms.py | /report-forms | 신고서식 |
| contracts.py | - | 계약 (⚠️ 503 오류 확인 필요) |
| contacts.py | - | 문의 |
| education.py | - | 법정교육 |
| notifications.py | - | 알림 |
| equipment_assets.py | /equipment-assets | 설비 자산 |
| schedule_engine.py | /schedule-engine | 점검 일정 |
| roles.py, teams.py | - | 권한/팀 |
| areas.py, buildings.py | - | 구역/건물 |
| inspection_sets.py | - | 점검 세트 |
| work_schedules.py | - | 작업 일정 |
| personnel.py | /personnel | 선임연결 |
| repair.py | /repair | 수선중개 (v1.0.0) |
| admin_stats.py | /admin/stats | 대시보드 통계 |
| engine_equipment.py | /engine-equipment | 설비엔진 (MV 기반) |
| inspection_checklist.py | /inspection | 점검 체크리스트 |

---

## 미완료 이슈

| 이슈 | 상태 | 세부 |
|------|------|------|
| contracts 503 오류 | ⚠️ 열린 | 파일/문법/등록 정상 → Railway 런타임 로그 확인 필요 |
| 로그인 2.5초 지연 | ⚠️ 열린 | bcrypt + Supabase auth 이중 검증 의심 → auth.py 수정 필요 |
| system_codes POST/PATCH/DELETE | ⚠️ 미구현 | 프론트 연동 필요 |
| health 엔드포인트 | ⚠️ server_ip 임시 추가됨 | 원복 필요 |
| 건축물도면 API | ⏸️ 승인 대기 | blcm.go.kr 신청 완료 |

---

## 이메일 스택 (확정)
```
Resend API (HTTP 방식)
포트: 무관 (라우마우 SMTP 새드없음)
발신: noreply@taieng.co.kr
수신: tai@taieng.co.kr
RESEND_API_KEY: Railway 환경변수
```

---

## JUSO API
- URL: business.juso.go.kr
- Key: U01TX0FVVEgyMDI2MDMxODEyMjUxNjExNzc1MTc=
- firstSort 도로명/지번 자동 판별
- bdMgtSn 직접 반환 → 건축물대장 100% 연동

---

## Materialized View
| MV명 | 행수 | 용도 |
|------|------|------|
| engine_equipment_summary | 508행 | 설비엔진 목록/통계 |
| dashboard_stats | 1행 | 대시보드 통계 |

---

## 환경변수 (Railway)
```
SUPABASE_URL     = https://xntdkrjhgcscmqctdzyo.supabase.co
SUPABASE_KEY     = sb_secret_fBeYn... (service_role)
LAW_API_OC       = taieng
JUSO_API_KEY     = U01TX0FVVEgyMDI2MDMxODEyMjUxNjExNzc1MTc=
BUILDING_API_KEY = da4e826323c2c9fef9f325bd4e39a3765d06ac1b582695bcbc475bc0a076255b
RESEND_API_KEY   = (Railway에만 저장)
```
