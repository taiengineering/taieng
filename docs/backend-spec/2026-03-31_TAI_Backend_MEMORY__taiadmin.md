# TAI Backend Memory — 2026-03-31

## 오늘 완료된 작업

### 1. DB 마이그레이션 — 회원 역할 구조 개편

#### roles 테이블 신규 추가 (10개)
| code | role_name | 근거 |
|------|-----------|------|
| 010 | 대표 | 산안법 제2조 |
| 011 | 안전보건관리책임자 | 산안법 제15조 |
| 012 | 안전관리자 | 산안법 제17조 |
| 013 | 관리감독자 | 산안법 제16조 |
| 014 | 작업자 | 산안법 제5조 |
| 015 | 산업보건의 | 산안법 제22조 |
| 016 | 보건관리자 | 산안법 제18조 |
| 020 | 하도급대표 | — |
| 021 | 하도급안전관리자 | — |
| 022 | 하도급직원 | — |

#### roles 테이블 비활성화
- 003(안전관리자) → 012로 마이그레이션
- 004(작업자) → 014로 마이그레이션
- 005(협력업체관리자) → 020으로 마이그레이션
- 006(협력업체작업자) → 022로 마이그레이션
- 007(점검자), 008(승인자) → 비활성화

#### system_codes 그룹 헤더 추가
- `GRP_ADMIN` — 플랫폼 관리 (depth=1)
- `GRP_CONTRACTOR` — 원청 (depth=1)
- `GRP_SUBCON` — 하도급 (depth=1)

#### users role_code 마이그레이션 완료
- 003→012, 004→014, 005→020, 006→022

#### role_permissions 복사 완료
- 003→012, 004→014, 신규역할 모두 014 수준 기본권한 복사

### 2. DB 신규 테이블

#### internal_api_registry
- TAI 내부 API 엔드포인트 21개 등록
- 컬럼: group_name, api_name, method, endpoint, auth_required, expect_status
- 프론트에서 GET으로 목록 조회 → 모니터 페이지 자동 렌더링

#### report_api_registry
- 외부 자동신고 시스템 5개 등록 (고용24, 화관법민원24, 올바로, 전기안전공사, 세움터)
- apply_status: PENDING → APPLIED → APPROVED 상태 관리

#### master_building_legal_rules 컬럼 추가
- `online_system`, `system_url`, `automation_level` (HIGH/MEDIUM/LOW)
- `official_api_available`, `api_apply_required`, `api_apply_url`, `auto_report_notes`
- 9개 법령 자동신고 수준 데이터 반영 완료

### 3. price_saas_plan 데이터
- INDUSTRY_L1~L4, FACILITY_L1~L4, ADDON_EDU, ADDON_REPORT 삽입

### 4. 미구현 API (Code 창 작업 필요)
| 엔드포인트 | 상태 | 우선순위 |
|----------|------|--------|
| GET/PATCH /price-setting/repair-brokerage | 404 | 높음 |
| GET/PATCH /price-setting/safety-management | 404 | 높음 |
| GET/PATCH /price-setting/consulting | 404 | 높음 |
| GET /inspection/schedules | 404 | 중간 |
| GET /internal-api-registry | 미구현 | 높음 |
| GET /report-api-registry | 미구현 | 높음 |
| GET /equipment-assets | CORS 오류 | 중간 |

#### Code 창 작업지시서 위치
- `docs/TASK_API_MONITOR_BACKEND_20260330.md` (tai-api)

## API 상태 점검 결과 (2026-03-31 기준)
| 상태 | 엔드포인트 수 |
|------|-------------|
| 200 정상 | 12개 |
| 404 미구현 | 5개 |
| CORS/NET 오류 | 1개 |
| 405 메서드 오류 | 1개 |
| 응답지연(1.5s+) | 1개 |
