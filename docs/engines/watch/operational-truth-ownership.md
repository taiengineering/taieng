# Operational Truth Ownership Registry

## 선언

아래 Operational Truth는 전부 **Control Runtime**이 소유한다.
다른 Runtime은 이 Truth를 생성하거나 수정할 수 없다.

---

## Ownership 등록부

| Operational Truth | Owner | Consumer | 생성 위치 |
|-------------------|:---:|----------|----------|
| **severity** | Control | Notification, UI | evaluator.py |
| **incident** | Control | Notification, UI, Governance | evaluator.py, repeated.py |
| **escalation** | Control | Notification, UI | governance/__init__.py |
| **recovery** | Control | UI, Notification | recovery_registry |
| **anomaly** | Control | Governance, UI | evaluator.py |
| **ACK** | Control | UI | incident_action_log |
| **operational status** | Control | UI, Governance | tenant_operational_registry |
| **operator state** | Control | UI | incident_action_log |
| **degradation** | Control | Governance, UI | stability.py |
| **workflow blockage** | Control | UI, Notification | evaluator.py |
| **pattern** | Control | Knowledge, UI | pattern_registry |
| **stability score** | Control | Governance, UI | stability.py |
| **tenant impact** | Control | Governance, UI | governance/__init__.py |
| **SLA violation** | Control | Alert, UI | sla_violation.py |
| **suppression** | Control | Alert | flow_status.py |

---

## Truth Flow

```
Business Event (Workflow Runtime)
  │
  ▼
Control Runtime (Truth Engine)
  ├── severity     ──→ Notification (projection)
  ├── incident     ──→ UI (display)
  ├── escalation   ──→ Notification (routing)
  ├── recovery     ──→ UI (recommendation)
  ├── ACK          ──→ UI (interaction)
  └── stability    ──→ Governance (aggregation)
```

## 규칙

1. **Truth는 Control Runtime에서만 생성된다**
2. **Consumer는 Truth를 읽기만 한다**
3. **UI는 사용자 액션을 Control에 요청한다** (ACK, RESOLVE → Control API 호출)
4. **Notification은 Truth를 투영만 한다** (severity를 보여주되 계산하지 않음)
5. **Truth 충돌 시 Control이 승리한다**
