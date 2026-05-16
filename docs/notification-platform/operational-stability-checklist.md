# Operational Stability Checklist

작성일: 2026-05-16
상태: Phase 1 완료

---

## Runtime Stability

| 항목 | 상태 | 비고 |
|---|---|---|
| Queue Runtime | ✅ 안정 | QUEUED→PROCESSING→DELIVERED |
| Retry Runtime | ✅ 안정 | Exponential backoff 30s~300s |
| DLQ | ✅ 안정 | max_retry 초과 → deadletter |
| Quiet Hour Delay | ✅ 안정 | DELAYED→Resume→DELIVERED |
| Feed Surface | ✅ 안정 | notifications 테이블 기반 |
| Preference Enforcement | ✅ 안정 | Mute/Disabled/QH/CRITICAL |
| Policy Audit | ✅ 안정 | 모든 정책 결정 기록 |
| Timeline | ✅ 안정 | trace_id 기반 E2E 추적 |
| Metrics | ✅ 안정 | Health Score + QH 지표 |
| Adapter: TELEGRAM | ✅ 운영 | Bot API 연동 |
| Adapter: SMS | ✅ 구현 | MessageMi 연동 |
| Adapter: IN_APP | ✅ 구현 | notifications INSERT |
| Channel Registry | ✅ 안정 | 7채널 (3 활성) |
| E2E Test Runner | ✅ 구현 | 7 시나리오 |

## 자동화

| 항목 | 상태 | 비고 |
|---|---|---|
| Worker Cron (1분) | ⚠️ 미설정 | scheduler.py 등록 필요 |
| Metrics Cron (10분) | ⚠️ 미설정 | scheduler.py 등록 필요 |

## Legacy 전환

| 항목 | 상태 | 비고 |
|---|---|---|
| overdue_checker | ✅ compat 경유 | Cursor 완료 |
| messaging.py | ✅ compat 경유 | Cursor 완료 |
| notifications.py | ✅ Freeze | 신규 사용 금지 |
| watch_engine alert | ✅ Pipeline | v2.0 전환 완료 |
| Auth SMS (pw_reset 등) | ⏸ 보류 | Auth 특수 |
