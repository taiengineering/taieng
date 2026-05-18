# TAI Safe — 현재 이슈 목록

작성일: 2026-05-18 (최종 갱신: TASK 50)

---

## 해결된 이슈

| # | 이슈 | 해결 |
|---|------|------|
| 1 | Scheduler 미실행 | cron_job_master RLS 정책 추가 → 18 job 등록 |
| 2 | Mock/Real 데이터 혼재 | environment='mock' 마킹 + evaluator/governance 필터 |
| 3 | Bridge projection 0건 | chk_eie_type CHECK constraint에 39개 canonical type 추가 |
| 4 | orchestrator WARNING 차단 | severity=INFO로 변경, Bridge가 projection |
| 5 | event_store NOT NULL | step_key='', step_order=0, source_trace, acknowledged, ignored 기본값 |
| 6 | 수평메뉴 드롭다운 안보임 | custom.css max-height + overflow-y |

---

## P0 — 런치 차단

| # | 이슈 | 상태 |
|---|------|:---:|
| 1 | **KG이니시스 승인** | ❌ BLOCKED — 110건 PENDING, 0건 PAID |
| 2 | **진단→SaaS Setup 연결** | ❌ 미구현 |
| 3 | **Telegram 토큰 로테이션** | ⚠️ 토큰 공개됨 → BotFather /revoke 필요 |
| 4 | **INTERNAL_API_SECRET 로테이션** | ⚠️ 노출됨 |

## P1 — 운영 가능하지만 위험

| # | 이슈 | 상태 |
|---|------|:---:|
| 5 | **배포 후 Scheduler 자동시작 실패** | ⚠️ WORKAROUND — 매 배포 후 POST /cron/reload 필요 |
| 6 | Synthetic 계정 미설정 | ⚠️ SYNTHETIC_TEST_EMAIL/PASSWORD/FACTORY_ID NOT_SET |
| 7 | RLS 미적용 | ⚠️ Watch Engine 24개 테이블 RLS 보류 |
| 8 | knowledge API 404 | ⚠️ /watch-engine/knowledge/patterns → 404 |
| 9 | product_pricing 레거시 | ⚠️ 3건, BASIC 가격 불일치 |

## P2 — 운영 중 개선

| # | 이슈 | 상태 |
|---|------|:---:|
| 10 | health degraded | law_engine + fix_chat (Watch 무관) |
| 11 | Gotenberg PDF E2E 실측 | 코드 완료, 실제 다운로드 미검증 |
| 12 | Payment callback → subscription | PAID 시 ACTIVE 자동 전환 확인 필요 |
| 13 | diagrams 버킷 SVG 25개 | 구프로젝트 → 서울 이전 |
| 14 | db.database vs db.supabase_client | import 통일 |
| 15 | 서비스 레이어 분리 | 20KB+ 파일 5개 |
| 16 | KOSHA API | APICODE_ERROR (resultCode: 90) |

---

## SaaS Readiness

| 영역 | 상태 |
|------|:---:|
| Watch Engine | ✅ READY |
| Intelligence | ✅ READY |
| Synthetic Civilization | ✅ READY (실가동) |
| Control Bridge | ✅ READY (실가동) |
| Calibration | ✅ READY |
| Feedback Loop | ✅ READY |
| Notification | ⚠️ WARNING |
| Document | ⚠️ WARNING |
| Governance | ✅ READY |
| Payment | ❌ BLOCKED |
| Runtime Foundation | ❄️ FROZEN |

| 단계 | 판정 |
|------|:---:|
| Internal Beta | ✅ 가능 |
| Pilot 고객 | ⚠️ 조건부 |
| 유료 SaaS | ❌ 불가 (Payment) |

---

## 즉시 실행 필요

1. Telegram Bot 토큰 `/revoke` → Railway 환경변수
2. INTERNAL_API_SECRET 로테이션
3. KG이니시스 승인 follow-up
