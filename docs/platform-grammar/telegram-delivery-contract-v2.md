# Telegram Delivery Contract v2

작성일: 2026-05-17
범위: Telegram = 실시간 운영 알림

---

## 역할

| 용도 | 설명 |
|---|---|
| Realtime Operator Alert | 운영자 실시간 알림 |
| Mobile Operational Signal | 모바일 운영 신호 |

---

## 포함

| 항목 | 설명 |
|---|---|
| Bot Token | TELEGRAM_BOT_TOKEN 환경변수 |
| Chat ID | TELEGRAM_CHAT_ID 환경변수 |
| Retry | Runtime retry (max 3, exponential) |
| Delivery Audit | timeline + policy_audit 자동 |
| Message Format | `[{severity}] {title}\n{body}` |

---

## 금지

| 금지 | 이유 |
|---|---|
| Operator State Ownership | Control Runtime 영역 |
| Escalation Ownership | Control Runtime 영역 |
| Bot 명령 처리 | Notification은 Projection만 |
| 그룹 관리 | Telegram 채널 관리 금지 |

---

## v1 → v2 변화

| 변화 | 설명 |
|---|---|
| Projection 명확화 | severity_snapshot 읽기 전용 |
| Ownership 명확화 | operator state/escalation 금지 |
| Adapter Interface 통일 | `send(message, context)` 표준 |
