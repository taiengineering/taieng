# TAI Safe — 현재 이슈 목록

작성일: 2026-05-16

---

## P0 — 런치 차단

| # | 이슈 | 상태 | 설명 |
|---|------|:---:|------|
| 1 | **Payment E2E** | ❌ BLOCKED | KG이니시스 승인 대기. 110건 PENDING, 0건 PAID. 도메인 전환 (`new.taieng.co.kr` → `taieng.co.kr`) 대기 중 |
| 2 | **진단→SaaS Setup 연결** | ❌ | 진단 결과에서 SaaS tenant bootstrap으로 연결하는 흐름 미구현 |
| 3 | **Scheduler 자동 시작 실패** | ⚠️ WORKAROUND | Railway 배포 시 APScheduler 자동 시작 실패. `POST /cron/reload`로 수동 시작 가능. 근본 원인 미해결 |

## P1 — 운영 가능하지만 위험

| # | 이슈 | 상태 | 설명 |
|---|------|:---:|------|
| 4 | **Telegram Bot 토큰 로테이션** | ⚠️ | 토큰이 대화에서 공개됨. BotFather `/revoke` 후 Railway 환경변수 업데이트 필요 |
| 5 | **INTERNAL_API_SECRET 로테이션** | ⚠️ | 이전 세션에서 노출됨 |
| 6 | **Synthetic 계정 미설정** | ⚠️ | SYNTHETIC_TEST_EMAIL/PASSWORD/FACTORY_ID 미설정 → Synthetic job skip |
| 7 | **PATTERN_SYNC mock 누적** | ⚠️ | Mock 데이터가 패턴에 포함 누적 (학습용으로 허용했으나 운영 오염 가능성) |
| 8 | **RLS 미적용** | ⚠️ | Watch Engine 24개 테이블에 Row Level Security 보류 |
| 9 | **product_pricing 레거시** | ⚠️ | 3건 레거시 데이터. BASIC 가격 불일치 (79K vs 49K). 정리 또는 비활성화 필요 |
| 10 | **knowledge API 404** | ⚠️ | `/watch-engine/knowledge/patterns` 및 `/playbooks` → 404 Not Found. 라우터 미등록 또는 경로 불일치 |

## P2 — 운영 중 개선

| # | 이슈 | 상태 | 설명 |
|---|------|:---:|------|
| 11 | **Playwright + Chromium** | ❌ | Browser Synthetic 전용. Railway에 설치되어 있으나 PLAYWRIGHT_BASE_URL 미설정 |
| 12 | **data-testid 프론트 추가** | ❌ | CSS selector fallback으로 운영 가능 |
| 13 | **Tenant bootstrap 자동화** | ❌ | 현재 수동 등록만 |
| 14 | **Playbook/Recovery CRUD UI** | ❌ | Cockpit에서 조회만 가능, 편집 UI 없음 |
| 15 | **form-templates HTML 업로드** | ❌ | 63종 중 일부만 HTML 존재. Gotenberg PDF는 _build_default_html fallback |
| 16 | **diagrams 버킷 SVG 이전** | ❌ | 25개 SVG가 구프로젝트(xntdkrjhgcscmqctdzyo)에만 존재. 서울 프로젝트로 이전 필요 |
| 17 | **db.database vs db.supabase_client** | ❌ | import 통일 필요. scheduler.py는 db.database, 라우터들은 db.supabase_client |
| 18 | **서비스 레이어 분리** | ❌ | 20KB+ 파일 5개 (legal_engine 77KB, construction 58KB, payment 52KB, law_rule_generator 46KB, matching 42KB) |
| 19 | **health degraded** | ❌ | law_engine (master_building_legal_rules 테이블 없음), fix_chat (권한 부족). Watch Engine 무관 |
| 20 | **Gotenberg PDF E2E 실측** | ❌ | 코드 완료되었으나 실제 고객 다운로드 미검증 |
| 21 | **Payment callback → subscription 자동 연결** | ❌ | PAID 시 subscription ACTIVE 자동 전환 확인 필요 |
| 22 | **Subscription → factory 자동 연결** | ❌ | onboarding 흐름에서 factory_id 자동 매핑 필요 |
| 23 | **Railway 고정 IP** | ❌ | law.go.kr 판례 API에 고정 outbound IP 필요 ($2/월) |
| 24 | **KOSHA API** | ❌ | `APICODE_ERROR (resultCode: 90)` — data.go.kr 계정 활성화 확인 필요 |

---

## SaaS Readiness 판정

| 영역 | 상태 |
|------|:---:|
| Watch Engine | ✅ READY |
| Notification | ⚠️ WARNING (Telegram 환경변수 OK, 실발송 미검증) |
| Workflow | ✅ READY |
| Document | ⚠️ WARNING (Gotenberg 연결 OK, E2E 미검증) |
| Governance | ✅ READY |
| Worker UX | ⚠️ WARNING |
| Payment | ❌ BLOCKED |
| Tenant Onboarding | ⚠️ WARNING |

| 단계 | 판정 |
|------|:---:|
| Internal Beta | ✅ 가능 |
| Pilot 고객 | ⚠️ 조건부 |
| 유료 SaaS | ❌ 불가 |

---

## 즉시 실행 필요

1. `curl -s -X POST https://api.taieng.co.kr/cron/reload` — Scheduler 수동 시작
2. Telegram Bot 토큰 로테이션 (BotFather `/revoke`)
3. INTERNAL_API_SECRET 로테이션 (Railway 환경변수)
4. KG이니시스 승인 follow-up
5. knowledge API 404 원인 확인 (라우터 경로 불일치)
