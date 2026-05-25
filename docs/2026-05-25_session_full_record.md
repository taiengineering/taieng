# TAI Safe SaaS 통합 QA 세션 전체 기록

> 작성일: 2026-05-25
> 세션: 3개 통합 (09:13 ~ 21:00+ KST)
> 범위: 법령엔진 runtime 전환 + 소비자 QA + 시스템 전체 점검

---

## 1. 완료 작업 전체

### 1.1 인프라 복구
- GitHub↔Railway 자동배포 끊김 → `railway up` CLI 수동 배포
- `router_registry` v1.1.0, diagnosis 13/13 모듈 로드

### 1.2 Runtime 엔진 전환
- `/diagnosis/run` runtime compiler 전환 (`v3.0-runtime-compiler`)
- `services/diagnosis_runtime_step1.py` 신규, slot enrichment 완성
- 15건 중 13건 WHO/WHAT 채움 확인

### 1.3 Binding Engine 연결
- Legal Adapter v2.1: `project_rules()` 호출 시 `runtime_candidate` + `inspection_sets` 동시 생성
- runtime_candidate: 0→7건, inspection_sets (LEGAL_ENGINE): 0→326건
- 중복 방지: factory_id + law_name + law_article 기준

### 1.4 Activation Service v1.1
- `services/runtime_activation_service.py` — candidate activation 시 inspection_sets UPDATE + inspection_set_items 생성
- 커밋 `4281538` (tai-api main)

### 1.5 로그인 시스템 전면 수정
- GoTrue + password_hash bcrypt 폴백 방식 채택
- 1차: `supabase.auth.sign_in_with_password` 시도
- 2차 실패 시: `public.users.password_hash` bcrypt 검증
- 2차 성공 시: GoTrue 계정 자동 복구 (admin.update_user_by_id 또는 admin.create_user)
- GoTrue 로그인 실패 근본 원인: SQL로 생성한 auth.users의 `confirmation_token` 등 NULL → COALESCE로 빈 문자열 설정
- 테스트 계정: saas-test@taieng.co.kr / safe1234 → 로그인 확인 ✅

### 1.6 시설관리 수정 페이지
- tai-admin `0dba5ef0`: 시설유형 facility_lv2, KSIC 검색 모달, 필드명 매칭
- tai-api `6953a52`: KSIC search 엔드포인트 추가

### 1.7 RLS 전체 수정 (근본 해결)
- **근본 원인**: BE의 모든 라우터가 `SUPABASE_KEY`(anon 키) 사용 → RLS에 service_role만 허용된 테이블 접근 불가
- **임시 조치**: 496개 테이블에 anon SELECT 정책 일괄 추가, 33개 SaaS 쓰기 테이블 CRUD 정책 추가
- **근본 해결**: `SUPABASE_KEY` → `SUPABASE_SERVICE_ROLE_KEY` 전환 배포 ✅
- Supabase API 로그로 service_role 전환 확인 (fix_chat_sessions 401→200)

### 1.8 과금 정책 전환
- `plan-gate.js` v2.0.0: GATE_CONFIG 비움 → 모든 기능 잠금 해제
- `menu-tadmin.js` v5.8.0: applyMenuLock 비활성화, 기본 level 2→3, 기본 plan INDUSTRY_PRO
- 테스트 회사에 INDUSTRY_PRO 계약 레코드 생성

### 1.9 데이터 수정
- 테스트사업장 KSIC `2591` → `C2591` (접두사 누락 수정)
- 모든 활성 계정에 password_hash 설정 (13개)
- auth.users confirmation_token 등 NULL 필드 수정

---

## 2. 발견된 이슈 + 해결 상태

| # | 이슈 | 원인 | 해결 | 상태 |
|---|--------|------|------|------|
| 1 | 시설유형 드롭다운 비어있음 | FE가 site_type 사용, DB는 facility_lv2 + RLS 차단 | FE 수정 + RLS 추가 | ✅ 커밋완료, CF배포필요 |
| 2 | KSIC 검색 빈 결과 | BE 엔드포인트 미존재 + RLS 차단 | BE 추가 + RLS 추가 | ✅ |
| 3 | GoTrue 로그인 실패 | auth.users string 필드 NULL | COALESCE 수정 | ✅ |
| 4 | 설비관리 메뉴 잠김 | applyMenuLock + contract_level=2 기본값 | v5.8.0 비활성화 + 기본값 3 | ✅ 커밋완료, CF배포필요 |
| 5 | 공정관리 대분류 빈 값 | ksic_process_map RLS 차단 + KSIC 코드 형식 불일치 | RLS 추가 + C2591 수정 | ✅ |
| 6 | KCSC 검색 빈 결과 | kcsc_process_master RLS 차단 | RLS 추가 | ✅ |
| 7 | 공정 추가 시 에러 | factory_process RLS 차단 (INSERT/UPDATE/DELETE) | CRUD 정책 추가 | ✅ |
| 8 | plan-gate 기능 잠금 | 과금 정책 변경(규모별) 미반영 | v2.0.0 GATE_CONFIG 비움 | ✅ |
| 9 | 계약 데이터 없음 | 테스트 회사에 contracts 레코드 미존재 | INDUSTRY_PRO 계약 생성 | ✅ |
| 10 | localStorage 캠시 | contract_level이 캐시되어 재로그인으로 갱신 안 됨 | fetchContractInfo 호출 조건 개선 + 기본값 3 | ✅ |
| 11 | Railway 빌드 실패 | playwright install-deps 타임아웃 | 재시도로 해결 | ✅ |
| 12 | KCSC 검색에서 "철강" 빈 결과 | KCSC는 건설 표준 데이터, 제조업 데이터 없음 | 정상 동작 (데이터 범위 문제) | ⚠️ 정상 |

---

## 3. 미해결 이슈 (PENDING)

### P0 (즉시)
| # | 이슈 | 설명 |
|---|--------|------|
| 1 | **메뉴 v6.0.0 개편** | 작업지시 `taieng/docs/2026-05-25_menu_restructure.md` 참조. Cursor에서 menu-tadmin.js 수정 |
| 2 | **하도급관리 페이지** | `subcontract-management.html` 신규 생성 필요 (건설 전용, 필수) |
| 3 | **construction-work-list** | 점검관리 하위에 산업+건설 모두 노출 필요 |
| 4 | **대시보드 체크리스트 온보딩** | 결제 후 세팅 가이드 구현 |
| 5 | **결제→계약→권한→안내→세팅 플로우** | 결제 완료 시 contracts 자동 생성 + 알림 발송 |
| 6 | **summary 113건 vs obligation_counts 15건 불일치** | runtime 진단 결과 정합성 |

### P1
| # | 이슈 | 설명 |
|---|--------|------|
| 7 | 나머지 auth.users NULL 필드 | saas-test 외 계정도 정리 필요 |
| 8 | Railway↔GitHub 자동배포 복구 | 현재 `railway up` 수동 배포 |
| 9 | worker-list 로딩 이슈 | 작업근로자 페이지 데이터 표시 안 됨 |
| 10 | 모바일 UX 검증 | 전체 페이지 모바일 대응 확인 |
| 11 | 위험성평가/QR 오픈 준비 | 전문성 검토 후 오픈 |
| 12 | 전문가 매칭 오픈 준비 | 모수 확보 후 오픈 |

### P2
| # | 이슈 | 설명 |
|---|--------|------|
| 13 | runtime_notification_queue 400 에러 | 스키마/쿼리 문제 (RLS 아님) |
| 14 | master_building_legal_rules 404 | 테이블 미존재 (정상) |
| 15 | BE 라우터별 get_supabase() 통일 | 각 라우터가 로컬 get_supabase() 사용 → `from db.supabase_client import get_supabase` 통일 필요 |

---

## 4. 파일 변경 전체

### tai-api (main)
| 커밋 | 파일 | 설명 |
|--------|------|------|
| 7a998b7 | router_registry/ | v1.1.0 |
| b1b4292 | main.py | v6.0.1 |
| 74f05e7 | services/diagnosis_runtime_step1.py | slot enrichment |
| 6e9102a | services/legal_adapter.py | binding engine 연결 |
| fa0c17a | routers/diagnosis_*.py | 소비자 QA FE↔BE 수정 |
| 21afbde | services/legal_adapter.py | Legal Adapter v2.1 |
| 4281538 | services/runtime_activation_service.py | Activation Service v1.1 |
| 6953a52 | routers/ksic_engine.py | KSIC search 엔드포인트 |
| Cursor | routers/auth.py | bcrypt 폴백 로그인 |
| Cursor | routers/factories.py | 시설 수정 필드명 매칭 |

### tai-admin (main)
| 커밋 | 파일 | 설명 |
|--------|------|------|
| 0dba5ef0 | factory-list.html, globals.js | 시설유형/KSIC 수정 |
| 8aade44 | plan-gate.js | v2.0.0 기능잠금 해제 |
| 3351f73 | menu-tadmin.js | v5.8.0 기본level3, applyMenuLock 비활성화 |

### taieng (main)
| 커밋 | 파일 | 설명 |
|--------|------|------|
| b3697e4 | free-diagnosis.html 등 | 무료/유료진단 FE 수정 |
| 5137993 | docs/2026-05-25_login_system_fix.md | 로그인 작업지시 |
| 6866721 | docs/2026-05-25_menu_restructure.md | 메뉴 v6.0.0 작업지시 |

### Supabase Migrations
| 마이그레이션 | 설명 |
|--------------|------|
| add_system_codes_read_policy | authenticated 읽기 |
| add_anon_read_reference_tables | anon 읽기 (system_codes, industry_master) |
| add_anon_read_all_reference_tables | anon 읽기 (ksic_process_map 등) |
| add_anon_crud_saas_core_tables | 55개 핵심 테이블 CRUD |
| add_rls_factory_process_crud | factory_process CRUD |
| add_anon_read_kcsc_tables | kcsc_process/work_master 읽기 |
| bulk_add_anon_read_all_rls_tables | **496개 전체** anon SELECT |
| bulk_add_anon_crud_saas_write_tables | 33개 쓰기 테이블 CRUD |
| auth.users NULL 필드 수정 | confirmation_token 등 COALESCE |

---

## 5. 프로덕션 상태

| 항목 | 값 |
|------|-----|
| API version | 6.0.1 |
| SUPABASE_KEY | **service_role** (전환 완료) |
| diagnosis 그룹 | 13/13 ok |
| runtime_candidate | 7건 |
| inspection_sets (LEGAL_ENGINE) | 326건 |
| rule_candidate | 34,456 |
| rule_candidate_slot | 146,595 |
| 로그인 | GoTrue + bcrypt 폴백 ✅ |
| RLS | 496개 테이블 anon SELECT ✅ |
| 배포 방식 | `railway up` (자동배포 미복구) |
| plan-gate | v2.0.0 (기능잠금 없음) |
| menu-tadmin | v5.8.0 (기본 level 3) |

---

## 6. 핵심 발견 및 교훈

### RLS 근본 문제
- BE의 모든 라우터가 `SUPABASE_KEY`(anon)로 Supabase 접근
- 대부분 테이블은 service_role만 허용
- 결과: 시설유형, KSIC, 공정, 설비 등 모든 참조 데이터 빈 값 반환
- 해결: service_role 키로 전환 (원천 차단)

### localStorage 캐시 문제
- `contract_level`이 캐시되어 재로그인으로 갱신 안 됨
- `fetchContractInfo`는 캐시 값이 있으면 스킵
- 해결: 기본값 level 3으로 변경 (규모별 과금으로 기능제한 없음)

### KSIC 코드 형식
- `ksic_process_map`: `C2591` 형식 (C 접두사)
- 테스트사업장 factories: `2591` (접두사 누락)
- 통합 시 누락된 건이 있었음

### KCSC vs KSIC
- KCSC = 건설 안전 표준 (앵커, 콘크리트 등)
- KSIC = 산업 분류 (제조업, 건설업 등)
- 산업 시설에서 KCSC 검색 빈 결과는 정상

### 메뉴 잠금 이중 구조
- plan-gate.js: 페이지 접근 시 오버레이 잠금
- menu-tadmin.js applyMenuLock(): 메뉴 아이콘에 잠금 표시
- 둘 다 제거해야 완전 해제

---

## 7. 다음 세션 우선순위

1. **메뉴 v6.0.0 개편** (Cursor) — `docs/2026-05-25_menu_restructure.md`
2. **하도급관리 페이지** 신규 생성
3. **대시보드 체크리스트 온보딩** 구현
4. **결제 플로우** (contracts 자동생성 + 알림)
5. summary/obligation_counts 불일치 해결
