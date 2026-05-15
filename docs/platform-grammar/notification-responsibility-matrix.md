# Notification Engine Responsibility Matrix

## Notification Engine = Delivery Infrastructure

**Notification은 판단하지 않는다. 전달한다.**

---

## 유지 (Notification Engine 책임)

| 기능 | 설명 |
|------|------|
| Channel Routing | Telegram/SMS/Push 채널 선택 |
| Delivery Execution | 실제 메시지 발송 |
| Delivery History | 발송 이력 기록 (`alert_history`) |
| Retry | 발송 실패 시 재시도 |
| Cooldown | 동일 알림 재발송 방지 |
| Mute/Snooze | 특정 규칙 임시 무음 |
| Quiet Hour | 야간 발송 제한 (향후) |
| Digest | 알림 묶음 발송 (향후) |
| Delivery Status | 성공/실패/대기 상태 관리 |
| Template | 메시지 포맷 (향후) |

## 이관/제거 (Notification Engine에서 금지)

| 기능 | 소유 엔진 | 이유 |
|------|----------|------|
| Severity 판단 | Integrity Layer | 무결성 판단은 Evaluator 책임 |
| Incident 생성 | Incident Layer | 운영 판단은 Incident Engine 책임 |
| Priority 계산 | Incident Layer | P1~P4는 Priority Engine 책임 |
| Workflow Instability 판단 | Incident Layer | 반복 탐지는 Repeated Failure Detector 책임 |
| SLA 계산 | SLA Layer | 업무 시간 기준은 SLA Evaluator 책임 |
| Governance Scoring | Governance Layer | Tenant 영향도는 Tenant Impact Engine 책임 |
| Tenant Impact 계산 | Governance Layer | 조직 안정성은 Governance 책임 |
| Visibility Policy | Identity Layer | 가시성은 Identity Core 책임 |
| Audience 계산 | Identity Layer | `resolve_notification_audience()`만 소비 |
| Escalation 판단 | Governance Layer | L1~L4는 Governance 책임 |

---

## Notification Engine Lifecycle (Delivery-only)

```
[Watch Engine]
  Alert Rule 매칭 → "이 이슈를 알려야 한다"
       │
[Identity Core]
  resolve_notification_audience() → "누구에게 알릴 것인가"
       │
[Notification Engine] ← 여기서부터 책임
  1. Audience 소비 (계산하지 않음)
  2. Delivery Policy 적용 (cooldown, mute, quiet hour)
  3. Channel Routing (Telegram, SMS 등)
  4. Delivery Execution (실제 발송)
  5. Delivery Result 기록 (성공/실패)
  6. Read/Ack 추적 (향후)
```

## Naming Convention (Notification 전용)

| Key | 설명 |
|-----|------|
| `notification_id` | 개별 알림 ID |
| `delivery_status` | PENDING / SENT / FAILED / READ |
| `channel_key` | telegram / sms / push / email |
| `audience_key` | 수신 대상 식별자 |
| `template_key` | 메시지 템플릿 (향후) |
| `delivery_policy_key` | 발송 정책 (cooldown 등) |

**금지**: `incident_id`, `alert_id`를 Notification 내부에서 생성하지 않는다.
소비만 가능.
