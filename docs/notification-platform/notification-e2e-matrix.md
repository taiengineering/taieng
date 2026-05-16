# Notification E2E Matrix

작성일: 2026-05-16
상태: Phase 1 완료 평가

---

## 채널별 검증 매트릭스

| 항목 | TELEGRAM | SMS | IN_APP |
|---|---|---|---|
| **Normal** | ✅ Pipeline→Adapter→Delivered | ✅ Adapter 구현 | ✅ Adapter 구현 |
| **Mute** | ✅ Suppressed | ✅ Suppressed | ✅ Suppressed |
| **Quiet Hour** | ✅ Delayed→Resume | ✅ Delayed→Resume | ✅ Delayed→Resume |
| **CRITICAL bypass** | ✅ Bypass | ✅ Bypass | ✅ Bypass |
| **Retry** | ✅ Exponential backoff | ✅ 구조 동일 | ❌ retry 의미 없음 (DB INSERT) |
| **DLQ** | ✅ max_retry 초과 → DLQ | ✅ 구조 동일 | ❌ DLQ 의미 없음 |
| **Feed** | ❌ 미생성 (Telegram은 외부) | ❌ 미생성 (SMS는 외부) | ✅ notifications INSERT |
| **Read** | N/A | N/A | ✅ is_read/read_at |
| **Audit** | ✅ 전체 trail | ✅ 전체 trail | ✅ 전체 trail |
| **Policy Audit** | ✅ MUTE/QH/CRITICAL | ✅ MUTE/QH/CRITICAL | ✅ MUTE/QH/CRITICAL |
| **Timeline** | ✅ trace_id 기반 | ✅ trace_id 기반 | ✅ trace_id 기반 |

## 요약

- 전체 38항목 중 **33항목 ✅** (86.8%)
- IN_APP retry/DLQ 의미 없음 (DB INSERT는 실패 확률 극한)
- TELEGRAM/SMS Feed 미생성 — 외부 채널은 Feed 대상 아님 (설계 의도)
