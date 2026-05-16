# Notification Feed Contract

작성일: 2026-05-16

---

## Feed Item 최소 구조

```json
{
  "notification_id": "uuid",
  "source_type": "service_notice | runtime_alert | campaign | ...",
  "channel_key": "SITE | TELEGRAM | SMS | IN_APP",
  "title": "알림 제목",
  "body": "알림 본문",
  "severity": "INFO | HIGH | CRITICAL",
  "created_at": "2026-05-16T00:00:00Z",
  "read_at": "null | timestamp",
  "is_read": false,
  "trace_id": "null | TRACE-xxx",
  "source_reference_id": "null | 관련 엔티티 URL",
  "link_url": "null | 상세 링크",
  "actor_id": "null | user_id",
  "tenant_id": "null | company_id",
  "trigger_code": "OVERDUE_ESCALATION | RUNTIME_NOTIFICATION | ..."
}
```

## 매핑 (notifications 테이블 → Feed Item)

| Feed Item | notifications 컨럼 |
|---|---|
| notification_id | id |
| source_type | trigger_group |
| channel_key | channel |
| title | title |
| body | body |
| severity | priority |
| created_at | created_at |
| read_at | read_at |
| is_read | is_read |
| source_reference_id | link_url |
| actor_id | user_id |
| tenant_id | company_id |
| trigger_code | trigger_code |

## 원칙

Feed는 Notification 결과 객체다. 운영 판단을 포함하지 않는다.
