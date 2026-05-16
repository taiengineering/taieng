# READ vs ACK Boundary

작성일: 2026-05-16

---

## 구분

| 개념 | 의미 | 주체 | 위치 |
|---|---|---|---|
| **READ** | 사용자가 확인함 | 수신자 (작업자/관리자) | Notification Feed |
| **ACK** | 운영자가 대응 수락 | 운영자 (operator) | Alert/Incident Layer |

## 핵심

```
READ ≠ ACK
```

- READ는 **전달 상태**다 ("\ubcf4\uc558\ub2e4")
- ACK는 **\uc6b4\uc601 \uc0c1\ud0dc**\ub2e4 ("\ub300\uc751\ud558\uaca0\ub2e4")

## \ud14c\uc774\ube14 \ub9e4\ud551

| \uc0c1\ud0dc | \ud14c\uc774\ube14 | \ud544\ub4dc |
|---|---|---|
| READ | notifications | is_read, read_at |
| ACK | workflow_alert_event | acknowledged, acknowledged_at |
| ACK | runtime_notification_queue | delivery_status=ACKNOWLEDGED |

## \uaddc\uce59

- READ\ub294 Inbox API\uc5d0\uc11c \ucc98\ub9ac (`/notification-inbox/{id}/read`)
- ACK\ub294 Alert API\uc5d0\uc11c \ucc98\ub9ac (`/workflow/alerts/{id}/ack`)
- \ub450 \uac1c\ub97c \ud63c\ud569\ud558\uc9c0 \uc54a\ub294\ub2e4
