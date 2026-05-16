# Notification Naming Convention

작성일: 2026-05-16

---

## 식별자

| 이름 | 의미 | 예시 |
|---|---|---|
| `notification_id` | 전달 이력 ID | uuid |
| `source_type` | 알림 발생 출처 | `runtime` / `service` |
| `channel_key` | 채널 식별 | `TELEGRAM` / `SMS` / `EMAIL` / `IN_APP` |
| `audience_key` | 대상 그룹 | `operator` / `tenant_admin` / `tenant_user` |
| `policy_key` | 전달 정책 | `default_retry` / `critical_immediate` |
| `template_key` | 템플릿 | `alert_critical` / `billing_notice` |
| `delivery_status` | 전달 상태 | QUEUED / DELIVERED / FAILED / ... |
| `message_key` | 메시지 유형 | `WORKFLOW_STUCK` / `BILLING_DUE` |

## Severity (외부 제공)

| 값 | 의미 |
|---|---|
| `INFO` | 정보성 |
| `WARNING` | 주의 필요 |
| `CRITICAL` | 즉시 대응 필요 |
| `FATAL` | 시스템 위험 |

## delivery_status

| 값 | 의미 |
|---|---|
| `QUEUED` | Queue 진입 |
| `PROCESSING` | Worker 처리 중 |
| `DELIVERED` | 전달 완료 |
| `FAILED` | 전달 실패 |
| `RETRY_PENDING` | 재시도 대기 |
| `DEADLETTER` | DLQ 이동 |
| `ACKNOWLEDGED` | 수신자 ACK |
| `RESOLVED` | 해결 완료 |
| `READ` | 수신자 확인 |
| `SUPPRESSED` | 정책 억제 |
| `MUTED` | 사용자 뮤트 |

## source_engine

| 값 | 의미 |
|---|---|
| `watch_engine` | Watch Engine 런타임 알림 |
| `workflow_engine` | Workflow 상태 변화 |
| `alert_layer` | Alert 승격 |
| `notification_engine_test` | 테스트 |
| `service` | 서비스 알림 (SMS/In-App 등) |
