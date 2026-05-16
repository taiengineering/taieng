# Notification Control Surface

작성일: 2026-05-16

---

## 정의

Control Surface = Operational Communication Surface.
Dashboard가 아님.

---

## 구성

### 1. Runtime Monitor

- Queue 상태 (QUEUED/PROCESSING/RETRY_PENDING/DELIVERED/FAILED)
- DLQ 상태 (deadletter count, delta)
- Retry 상태 (avg retry, backoff 현황)
- Health Score (HEALTHY/WARNING/DEGRADED/CRITICAL)
- API: `/notification-engine/health`, `/notification-engine/runtime-summary`

### 2. Announcement Manager

- 공지 사항
- 배너 메시지
- 캔페인 메시지
- 점검 안내
- 현재 상태: 하드코딩/DB 직접 (통합 필요)

### 3. Audience Manager

- `platform_admin` — 플랫폼 운영자
- `tenant_admin` — 업체 관리자
- `tenant_user` — 업체 작업자
- `operator` — 시스템 운영자 (현재 Telegram 수신)

### 4. Delivery Policy Console

- Retry 정책 (exponential backoff: 30s/60s/120s/240s/300s max)
- Cooldown (dedupe_key 기반, 기본 15분)
- Mute (미구현)
- Quiet Hour (미구현)

### 5. Notification Timeline

- 생성 → Queue → Delivery → Read → ACK
- API: `/notification-engine/timeline/{trace_id}`
- Workflow Timeline 분리: `/workflow/timeline/{workflow_id}`
