# Slack Delivery Contract

작성일: 2026-05-17
범위: Slack = 운영 협업 채널

---

## 목적

| 용도 | 설명 |
|---|---|
| Operator Collaboration | 운영팀 실시간 협업 |
| Incident Visibility | 장애 상황 공유 |
| Operational Broadcast | 운영 공지 방송 |

---

## 포함

| 항목 | 설명 |
|---|---|
| Webhook | Slack Incoming Webhook URL |
| Channel Mapping | event_type → Slack channel |
| Thread Reply | incident_ref 기반 스레드 응답 |
| Message Projection | severity + title + body → Slack Block Kit |
| Delivery Audit | 발송 결과 기록 |

---

## 금지

| 금지 | 이유 |
|---|---|
| Incident Ownership | Control Runtime 영역 |
| ACK Truth | Delivery Runtime 영역 |
| Escalation Truth | Control Runtime 영역 |
| Slack Bot 명령 처리 | Notification은 Projection만 |

---

## Adapter Interface

```python
def send(message: str, context: dict) -> Tuple[bool, Optional[str]]:
    # context: {webhook_url, channel, blocks, thread_ts}
```
