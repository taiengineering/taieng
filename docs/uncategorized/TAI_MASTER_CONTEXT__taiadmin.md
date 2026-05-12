# TAI MASTER CONTEXT
> **모든 창(비즈니스/백엔드/프론트/Claude Code/Cursor)이 작업 시작 전 반드시 읽는 공통 기준서**  
> 최종 업데이트: 2026-03-27  
> 업데이트 규칙: 주요 결정/완료/변경 시 비즈니스 창이 즉시 갱신

---

## 1. 프로젝트 기본 정보

| 항목 | 내용 |
|------|------|
| 서비스명 | TAI Engineering (산업안전 SaaS 플랫폼) |
| 프론트 레포 | `taiengineering/tai-admin` |
| 백엔드 레포 | `taiengineering/tai-api` |
| API URL | `https://api.taieng.co.kr` |
| 어드민 URL | `https://admin.taieng.co.kr` |
| 고객창 URL | `https://tadmin.taieng.co.kr` |
| DB | Supabase (xntdkrjhgcscmqctdzyo) |
| 백엔드 배포 | Railway (FastAPI, 자동배포) |
| 프론트 배포 | Cloudflare Pages (자동배포) |
| API 버전 | v3.2.0 |

---

## 2. 서비스 구조 (기획서 기준)

```
TAI 4대 서비스
① SaaS 법적진단 + 점검리스트 — 🟢 파이프라인 완성
② 선임연결        — 🟡 DB ✅ API ✅ (다음 단계)
③ 수선중개        — 🟡 DB ✅ (다음 단계)
④ 안전컨설팅      — 🔴 추후
```

### 수익 구조 (확정)
- 선임연결 상주: 연봉 × 15%
- 선임연결 비상주: 월방문비 × 12개월 × 10%
- 수선중개: 500만원 미만 고정5만 / ~5천만원 ×3% / 5천만원↑ ×5%

---

## 3. 기술 스택 및 규칙

### 백엔드 (tai-api)
- Python + FastAPI
- DB: `from db.supabase_client import get_supabase`
- 에러: `HTTPException(status_code=N, detail="...")`
- 라우터 등록 후 반드시 `main.py`에 추가
- 테스트: 터미널 Python (브라우저/Chrome 사용 금지)

### 프론트 (tai-admin)
- 순수 HTML + Bootstrap + Vuexy 템플릿
- API 호출: `apiCall()` 함수 (api.js)
- 인증: `localStorage.getItem('access_token')` 없으면 로그인 리다이렉트
- 로그인 URL(절대): `https://admin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html`
- 로그아웃: `doLogout()` 함수
- 알림: `showToast('success'|'warning'|'error', message)`
- 페이지네이션: `renderPagination(total, currentPage, pageSize, callback)`
- 슬라이드 패널: `.tai-side-panel` + `.open` 클래스 토글
- 상대경로 절대 금지 — 절대 URL 사용
- 특수문자 포함 파라미터: `encodeURIComponent()` 필수

### 멀티창 운영 구조 (변경)
| 역할 | 도구 | 대상 레포 | 주요 작업 |
|------|------|-----------|-----------|
| **백엔드** | Claude Code | `taiengineering/tai-api` | FastAPI 라우터, DB 스키마, API 엔드포인트 |
| **프론트엔드** | Cursor | `taiengineering/tai-admin` | tadmin HTML/JS 페이지, UI 컴포넌트 |

### Claude Code / Cursor 사용 규칙
- 백엔드 변경 → Claude Code에서 수정 후 `git push origin main`
- 프론트엔드 변경 → Cursor에서 수정 후 `git push origin main`
- API 스펙 변경 시 양쪽 동기화 필수
- 작업 시작 전 이 파일(`docs/TAI_MASTER_CONTEXT.md`) 읽기
- 완료 후 반드시 GitHub push
- 커밋 메시지 형식: `feat|fix|perf|refactor(범위): 설명`

---

## 4. 완료된 기능 현황

### 백엔드 API (tai-api/routers/)

| 파일 | prefix | 상태 |
|------|--------|------|
| auth.py | /auth | ✅ 이메일 인증 포함 |
| users.py | /users | ✅ |
| companies.py | /companies | ✅ |
| factories.py | /factories | ✅ |
| system_codes.py | /system-codes | ✅ |
| legal_engine.py | /legal-engine | ✅ v4.1.2 |
| ksic_engine.py | /ksic-engine | ✅ |
| factory_process_v3.py | /factory-process | ✅ v3 |
| building_register.py | /building-register | ✅ |
| quotes.py | /quotes | ✅ v2.0.0 |
| report_forms.py | /report-forms | ✅ |
| contracts.py | /contracts | ✅ |
| contacts.py | /contacts | ✅ |
| education.py | /education | ✅ |
| notifications.py | /notifications | ✅ |
| equipment_assets.py | /equipment-assets | ✅ |
| engine_equipment.py | /engine-equipment | ✅ v1.1.0 |
| engine_model.py | /engine-model | ✅ |
| personnel.py | /personnel | ✅ |
| schedule_engine.py | /schedule-engine | ✅ |
| inspection_checklist.py | /inspection | ✅ v1.0.0 (7개 엔드포인트) |
| roles.py | /roles | ✅ |
| teams.py | /teams | ✅ |

### 프론트 페이지 (admin/)

| 파일 | 기능 | 상태 |
|------|------|------|
| index.html | 대시보드 (실통계 4종) | ✅ |
| factory-list.html | 시설관리 (탭5 법령진단) | ✅ |
| facility-process.html | 공정관리 | ✅ |
| equipment-list.html | 설비관리 | ✅ |
| inspection-list.html | 점검리스트 (탭3+슬라이드패널) | ✅ |
| quote-list.html | 견적관리 v2 | ✅ |
| contract-list.html | 계약관리 | ✅ |
| company-list.html | 회사관리 | ✅ |
| member-list.html | 회원관리 | ✅ |
| permission.html | 권한관리 | ✅ |
| education-list.html | 교육관리 | ✅ |
| inquiry-list.html | 문의관리 | ✅ |
| notification-setting.html | 알림설정 | ✅ |
| system-codes.html | 전역변수 | ✅ |
| engine-equipment.html | 엔진설정>설비 | ✅ |
| engine-model.html | 엔진설정>모델 | ✅ |
| report-v1.html | 보고서 v1.3.0 | ✅ |
| report-v1-viewer.html | 보고서 뷰어 | ✅ |
| maps-leaflet.html | 시설지도 | ✅ |
| personnel-list.html | 선임연결 관리 | 🔴 미생성 |
| repair-list.html | 수선중개 관리 | 🔴 미생성 |

### 프론트 페이지 (tadmin/)

| 파일 | 기능 | 상태 |
|------|------|------|
| index.html | 대시보드 | ✅ |
| factory-list.html | 시설관리 | ✅ |
| process-select.html | 공정선택 | ✅ |
| education-list.html | 교육관리 | ✅ |
| my-diagnosis.html | 법령진단 결과 조회 | ✅ |

---

## 5. 전체 파이프라인 — 완성

```
시설 등록 → 공정 등록 → 설비 등록 → 모델 등록
        ↓
POST /legal-engine/apply/{factory_id}   (261건 적용)
        ↓
POST /legal-engine/create-inspection-sets/{factory_id}  (67개 생성)
        ↓
POST /inspection/generate-items/{factory_id}    ✅ 점검 항목 자동 생성
        ↓
POST /inspection/generate-schedules/{factory_id}  ✅ 스케줄 일괄 생성
        ↓
GET  /inspection/schedules/{factory_id}           ✅ 일정 목록 조회
        ↓
POST /inspection/start/{work_schedule_id}         ✅ 점검 시작
        ↓
POST /inspection/result/{inspection_id}/items     ✅ 항목별 결과 기록 (PASS/FAIL/NA)
        ↓
POST /inspection/complete/{work_schedule_id}      ✅ 완료 처리
        - equipment_assets.last_inspection_date 갱신
        - 다음 점검 스케줄 자동 생성
```

### inspection_checklist.py v1.0.0 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /inspection/generate-items/{factory_id} | 법령별 표준 점검 항목 자동 생성 |
| POST | /inspection/generate-schedules/{factory_id} | 점검 스케줄 일괄 생성 |
| GET | /inspection/status/{factory_id} | 점검 현황 요약 |
| GET | /inspection/schedules/{factory_id} | 점검 일정 목록 (month/status 필터) |
| POST | /inspection/start/{work_schedule_id} | 점검 시작 → safety_inspections 생성 |
| POST | /inspection/result/{inspection_id}/items | 결과 기록 (PASS/FAIL/NA) |
| POST | /inspection/complete/{work_schedule_id} | 완료 처리 + 다음 스케줄 자동 생성 |

---

## 6. PENDING 작업 목록

### 🔴 성능 최적화 (PERF)

| ID | 작업 | 상태 | 설명 |
|----|------|------|------|
| PERF01 | engine_equipment MV 교체 | PENDING | `v_equipment_unified` 뷰 → `mv_equipment_summary` Materialized View로 교체. list 엔드포인트 응답 3초→0.3초 목표 |
| PERF02 | admin_stats 신규 API | PENDING | 대시보드용 통계 API 신규 개발. 시설수/회원수/교육현황/법령판정현황 집계 |

### 🟡 프론트엔드 미개발 페이지 (UI)

| ID | 페이지 | 상태 | 경로 |
|----|--------|------|------|
| UI01 | 점검체크리스트 관리 | PENDING | /html/horizontal-menu-template/inspection-checklist |
| UI02 | 설비자산 관리 | PENDING | /html/horizontal-menu-template/equipment-assets |
| UI03 | 교육관리 대시보드 | PENDING | /html/horizontal-menu-template/education-dashboard |
| UI04 | 계약/견적 관리 | PENDING | /html/horizontal-menu-template/contract-list |

### ⏸️ 보류

| # | 항목 | 이유 |
|---|------|------|
| S05 | plan_code 요금제 등록 | B01 금액 확정 후 |
| B01 | SaaS 요금제 금액 | 추후 결정 |
| B03 | 직업소개업 신고 | 오프라인 구청 방문 |

### 🔵 다음 단계 — 선임/수선 서비스

| # | 작업 | 담당 |
|---|------|------|
| P11 | 수선중개 API (repair_companies) | 백엔드 |
| P12 | 선임연결 관리 페이지 (personnel-list.html) | 프론트 |
| P13 | 수선중개 관리 페이지 (repair-list.html) | 프론트 |

---

## 7. 법령엔진 핵심 정보 (v4.1.2 — 변경 금지)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /legal-engine/apply/{factory_id} | 시설 법령판정 (mode: all) |
| GET | /legal-engine/result/{factory_id} | 판정 결과 조회 |
| POST | /legal-engine/create-inspection-sets/{factory_id} | 점검세트 자동 생성 |
| POST | /legal-engine/apply-quote/{quote_id} | 설문 법령판정 |
| GET | /legal-engine/quote-result/{quote_id} | 설문 결과 조회 |

- 조건: `condition_code` + `condition_operator_code` + `condition_value`
- inspection_sets.source: `MANUAL` 또는 `LEGAL_ENGINE`
- inspection_cycle_unit 005 = 반기 (6개월)

---

## 8. 엔진 데이터 현황

| 테이블 | 건수 | 비고 |
|--------|------|------|
| process_equipment_map | 118만 건 | 고유 설비 508개 |
| equipment_model_master | 2,874건 | 설비표준명 479종 |
| master_building_legal_rules | 396건 | is_active=true |
| inspection_sets | 67건 | LEGAL_ENGINE 자동생성 |

---

## 9. DB 최적화 현황

### Materialized View (2개)

| MV 이름 | 원본 테이블 | 용도 | 갱신 주기 |
|---------|------------|------|-----------|
| `mv_equipment_summary` | process_equipment_map + ksic_process_map | 공정별 설비 집계 (list API) | 수동 REFRESH / 트리거 |
| `mv_legal_summary` | legal_rules + factories | 시설별 법령 판정 요약 | 수동 REFRESH |

### 인덱스 현황 (21개)

| 테이블 | 인덱스 | 컬럼 |
|--------|--------|------|
| factories | idx_factories_company_id | company_id |
| factories | idx_factories_site_type | site_type |
| factories | idx_factories_address_sido | address_sido |
| factories | idx_factories_is_active | is_active |
| users | idx_users_auth_id | auth_id |
| users | idx_users_company_id | company_id |
| users | idx_users_factory_id | factory_id |
| users | idx_users_phone | phone |
| system_codes | idx_system_codes_category | category |
| system_codes | idx_system_codes_category_code | category, code |
| quotes | idx_quotes_quote_no | quote_no |
| quotes | idx_quotes_status_code | status_code |
| quotes | idx_quotes_created_at | created_at |
| contracts | idx_contracts_company_id | company_id |
| contracts | idx_contracts_status_code | status_code |
| ksic_process_map | idx_ksic_process_map_process_id | process_id |
| ksic_process_map | idx_ksic_process_map_industry_code | industry_code_full |
| process_equipment_map | idx_pem_process_id | process_id |
| process_equipment_map | idx_pem_match_band | match_band |
| factory_process | idx_factory_process_factory_id | factory_id |
| factory_process | idx_factory_process_process_id | process_id |

---

## 10. 멀티 창 운영 규칙

```
비즈니스 창: PENDING 관리, MASTER_CONTEXT 업데이트, DB 마이그레이션
백엔드 창:   Claude Code — API 구현, Python 터미널 테스트, Railway 배포 (브라우저 금지)
프론트 창:   Cursor — HTML 페이지 구현, 절대 URL, Cloudflare 배포
```

---

## 11. 작업지시 템플릿

### 백엔드 창
```
## 작업지시
[MASTER_CONTEXT: https://github.com/taiengineering/tai-admin/blob/main/docs/TAI_MASTER_CONTEXT.md]
- from db.supabase_client import get_supabase 사용
- 테스트: 터미널 Python
- push: taiengineering/tai-api main
- 커밋: feat(파일명): 설명
```

### 프론트 창
```
## 작업지시
[MASTER_CONTEXT: https://github.com/taiengineering/tai-admin/blob/main/docs/TAI_MASTER_CONTEXT.md]
- 탑메뉴: [참조파일].html 기준 복사 / active: [메뉴명]
- apiCall() / showToast() / renderPagination() / doLogout()
- push: taiengineering/tai-admin main
- 커밋: feat(파일명): 설명
```

---

*이 문서는 TAI Engineering 전 창 공통 기준서입니다. 변경 시 비즈니스 창이 즉시 업데이트합니다.*
