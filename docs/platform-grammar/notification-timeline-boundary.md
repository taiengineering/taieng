# Notification Timeline Boundary

작성일: 2026-05-16

---

## Timeline 종류

| Timeline | 책임 | 엔드포인트 |
|---|---|---|
| **Workflow Timeline** | 상태 흐름 추적 | `/workflow/timeline/{workflow_id}` |
| **Integrity Timeline** | 이상 평가 추적 | Watch Engine Cockpit |
| **Incident Timeline** | 운영 상태 추적 | Watch Engine Incident API |
| **Alert Timeline** | 운영 Alert 이력 | `/workflow/alerts/timeline/{wf_id}` |
| **Notification Timeline** | **전달 흐름 추적** | `/notification-engine/timeline/{trace_id}` |
| **Feed Timeline** | Feed 기반 전달 추적 | `/notification-inbox/timeline/{trace_id}` |

## 핵심

**Notification Timeline은 전달 추적이다.**

Workflow나 Incident의 상태를 추적하지 않는다.
전달의 어느 단계에서 어떤 일이 일어났는지만 추적한다.

## 전달 흐름 추적 대상

```
EVENT (runtime_notification_event)
  ↓
QUEUE (runtime_notification_queue)
  ↓
PROCESSING → DELIVERED / FAILED
  ↓
AUDIT (runtime_notification_audit)
  ↓
FEED (notifications 테이블 - IN_APP 채널)
```
