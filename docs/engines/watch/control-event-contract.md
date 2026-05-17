# Control Event Contract

## 정의

Control Runtime이 생성하는 Operational Event의 표준 형식.
Notification/Delivery/UI는 이 Contract를 소비만 가능.

---

## Event 구조

```json
{
  "event_type": "watch.<domain>_<action>",
  "version": "1.0",
  "truth_source": "control_runtime",
  "severity": "CRITICAL | WARNING | INFO",
  "incident_ref": "uuid | null",
  "requires_ack": true,
  "recoverable": true,
  "tenant_id": "string",
  "trace_id": "string",
  "flow_key": "string",
  "timestamp": "ISO-8601",
  "payload": {}
}
```

## 필수 필드

| 필드 | 필수 | 설명 |
|------|:---:|------|
| event_type | ✅ | `watch.<domain>_<action>` |
| truth_source | ✅ | 항상 `control_runtime` |
| severity | ✅ | CRITICAL / WARNING / INFO |
| tenant_id | ✅ | 테넌트 식별 |
| trace_id | ✅ | 추적 ID |
| timestamp | ✅ | UTC ISO-8601 |
| requires_ack | ✅ | ACK 필요 여부 |
| recoverable | ✅ | 복구 가능 여부 |

## Event Type 등록부

| Event Type | Severity | ACK | 설명 |
|-----------|:---:|:---:|------|
| `watch.integrity_detected` | WARNING/CRITICAL | ✅ | 무결성 이슈 |
| `watch.incident_created` | CRITICAL | ✅ | 인시던트 생성 |
| `watch.alert_fired` | WARNING/CRITICAL | ❌ | 알림 발송 |
| `watch.escalation_triggered` | CRITICAL | ✅ | 위험 상향 |
| `watch.recovery_recommended` | INFO | ❌ | 복구 추천 |
| `watch.tenant_risk_changed` | WARNING | ❌ | 테넌트 위험도 변경 |
| `watch.stability_changed` | WARNING | ❌ | 안정성 변경 |
| `watch.sla_violated` | WARNING/CRITICAL | ✅ | SLA 위반 |
| `watch.pattern_detected` | INFO | ❌ | 패턴 탐지 |
| `watch.ack_completed` | INFO | ❌ | ACK 완료 |
| `watch.incident_resolved` | INFO | ❌ | 인시던트 해결 |

## 소비 규칙

| Consumer | 허용 | 금지 |
|----------|------|------|
| Notification | 읽기 + routing | severity 변경, incident 생성 |
| Delivery | 읽기 + 발송 | 모든 truth 수정 |
| UI | 읽기 + 표시 | truth overwrite |
| Governance | 읽기 + 집계 | truth 생성 |
