# TAI Safe — Production Readiness Checklist

작성일: 2026-05-15

---

## 1. Infrastructure

| 항목 | 상태 | 비고 |
|------|:---:|------|
| Railway 배포 | ⚠️ | tai-api main push = auto-deploy. 현재 Watch Engine v1.7 배포 필요 |
| Supabase Seoul | ✅ | ap-northeast-2 (`vwlahtguyggrhvslabax`) |
| Cloudflare Pages (admin) | ✅ | tai-admin main push |
| Cloudflare Pages (marketing) | ✅ | taieng main push |
| Gotenberg PDF | ✅ | Railway Singapore |
| `/health` 응답 | ✅ | 항상 200 반환 |

## 2. Scheduler (9개 direct job)

| Job | 상태 | 비고 |
|-----|:---:|------|
| INTEGRITY_EVALUATE (5분) | ✅ | 마지막 성공 05:01 |
| SYNTHETIC_LOGIN (5분) | ✅ | 마지막 성공 05:19 |
| SYNTHETIC_PROCESS_REG (15분) | ✅ | 마지막 성공 05:19 |
| ALERT_EVALUATE (5분) | ❌ | 미배포 — scheduler v1.7 배포 필요 |
| INCIDENT_REPEATED (5분) | ❌ | 미배포 |
| PATTERN_SYNC (6시간) | ❌ | 미배포 |
| SYNTHETIC_BROWSER_LOGIN (15분) | ❌ | 미배포 + Playwright 설치 필요 |
| SYNTHETIC_BROWSER_PROCESS (15분) | ❌ | 미배포 + Playwright 설치 필요 |
| SYNTHETIC_CLEANUP (매일 3시) | ❌ | 미배포 |

**핵심**: scheduler.py v1.7 + 신규 라우터 11개 Railway 배포 후 전체 정상화.

## 3. Environment Variables (Railway)

| 변수 | 상태 | 용도 |
|------|:---:|------|
| TELEGRAM_BOT_TOKEN | ❌ 미설정 | Alert Telegram 발송 |
| TELEGRAM_CHAT_ID | ❌ 미설정 | Alert 수신 채팅 |
| SYNTHETIC_TEST_EMAIL | ❌ 미설정 | Synthetic 로그인 테스트 |
| SYNTHETIC_TEST_PASSWORD | ❌ 미설정 | Synthetic 비밀번호 |
| SYNTHETIC_FACTORY_ID | ❌ 미설정 | Synthetic 사업장 |
| PLAYWRIGHT_HEADLESS | ❌ 미설정 | Browser Synthetic |
| PLAYWRIGHT_BASE_URL | ❌ 미설정 | Browser 대상 URL |

**미설정 시**: 해당 기능 skip, 서비스 영향 없음 (fail-safe).

## 4. Browser Synthetic

| 항목 | 상태 | 비고 |
|------|:---:|------|
| Playwright 설치 | ❌ | Railway에 `playwright install chromium` 필요 |
| 메모리 (1GB+) | ❓ | Chromium headless ~200MB |
| data-testid 속성 | ❌ | 프론트엔드 추가 필요 (`browser-synthetic-coverage.md`) |
| Selector fallback | ✅ | CSS selector fallback 구현됨 |

## 5. Alert / Notification

| 항목 | 상태 | 비고 |
|------|:---:|------|
| Alert Rule (6개) | ✅ | DB 등록 완료 |
| Cooldown/Dedupe | ✅ | 코드 구현 완료 |
| Mute/Snooze | ✅ | API + UI 구현 완료 |
| Telegram 발송 | ❌ | 환경변수 미설정 |
| Alert 폭탄 방지 | ✅ | threshold + cooldown + dedupe + mute |

## 6. Payment E2E

| 항목 | 상태 | 비고 |
|------|:---:|------|
| KG이니시스 연동 | ⚠️ | 코드 완료, 승인 대기 중 |
| 도메인 전환 | ⚠️ | `new.taieng.co.kr` → `taieng.co.kr` 대기 |
| 결제 → 권한 활성화 | ❓ | E2E 검증 필요 |
| 중복 결제 방지 | ❓ | 검증 필요 |
| 결제 취소 | ❓ | 검증 필요 |

## 7. Diagnosis → SaaS 연결

| 항목 | 상태 | 비고 |
|------|:---:|------|
| 진단 결과 저장 | ✅ | diagnosis_report 테이블 |
| SaaS tenant 생성 | ❓ | 진단 → SaaS 연결 플로우 검증 필요 |
| Workflow bootstrap | ❓ | 초기 설정 자동화 검증 필요 |
| 본인인증 | ⚠️ | KG이니시스 통합인증 CI 기반 |

## 8. Tenant Isolation

| 항목 | 상태 | 비고 |
|------|:---:|------|
| RLS (Row Level Security) | ⚠️ | Watch Engine 테이블 RLS 보류 |
| FK constraints | ⚠️ | Watch Engine 테이블 FK 보류 |
| Visibility filtering | ✅ | Identity Core 구현 |
| Synthetic isolation | ✅ | actor_type + 3중 격리 |

## 9. Cockpit 운영성

| 항목 | 상태 |
|------|:---:|
| 18개 섹션 UI | ✅ |
| 60초 polling | ✅ |
| 이슈 ACK/해결/무시 | ✅ |
| 알림 규칙 설정 | ✅ |
| 복구 조치 기록 | ✅ |
| 플레이북 조회 | ✅ |
| 패턴 동기화 | ✅ |
| API 실패 시 crash 없음 | ✅ |

## 10. Fail-safe

| 항목 | 상태 |
|------|:---:|
| emit_event 실패 시 서비스 영향 없음 | ✅ |
| Evaluator 실패 시 서비스 영향 없음 | ✅ |
| Telegram 실패 시 warning log만 | ✅ |
| Playwright 미설치 시 skip | ✅ |
| Scheduler job 실패 시 다음 실행 정상 | ✅ |
| Cockpit API 실패 시 empty 표시 | ✅ |
