# Runtime Dependency Graph

---

## Layer Model

```
Layer 6  Surface      │  UI (Cockpit, SaaS)
Layer 5  Execution    │  Delivery, Scheduler
Layer 4  Projection   │  Notification
Layer 3  Intelligence │  Semantic, Knowledge*
Layer 2  Truth        │  Control, Governance*
Layer 1  Core         │  Platform Core

* = Control 하위 계층
```

## 의존 방향 원칙

```
상위 Layer → 하위 Layer 의존 가능
하위 Layer → 상위 Layer 의존 금지
동일 Layer 간 의존 제한적 허용
```

## 허용된 의존

```
UI          ──→ Control      (truth 읽\uae30)
UI          ──→ Notification (projection 읽\uae30)
Notification ──→ Control     (truth \uc18c\ube44)
Notification ──→ Delivery    (\ubc1c\uc1a1 \uc694\uccad)
Delivery     ──→ Platform Core (contract \uc900\uc218)
Control      ──→ Platform Core (contract \uc900\uc218)
Control      ──→ Workflow    (event \uc218\uc2e0)
Semantic     ──→ Platform Core (\ubcc0\ud658 \uaddc\uce59)
Knowledge    ──→ Control     (\uc774\ubca4\ud2b8 \uc9d1\uacc4)
Governance   ──→ Control     (\uc774\ubca4\ud2b8 \uc9d1\uacc4)
Scheduler    ──→ Control     (job \uc2e4\ud589)
Workflow     ──→ Platform Core (event emission)
```

## 금지된 의존 (Forbidden)

| From | To | \uc774\uc720 |
|------|-----|------|
| Control | → Notification | Truth가 Projection에 의존하면 순환 |
| Control | → UI | Truth가 Surface에 의존 금지 |
| Control | → Delivery | Truth가 Execution에 의존 금지 |
| Notification | → Control mutation | Projection이 Truth 수정 금지 |
| Delivery | → Notification | Execution이 Projection에 역의존 금지 |
| Delivery | → Control mutation | Execution이 Truth 수정 금지 |
| Workflow | → Control mutation | Process가 Truth 생성 금지 |
| UI | → Control mutation | Surface가 Truth 직접 수정 금지 |
| UI | → Delivery | Surface가 Execution 직접 호출 금지 |
| Semantic | → Control mutation | Adapter가 Truth 생성 금지 |

**\ud575\uc2ec: \ud558\uc704 Layer\ub294 \uc0c1\uc704 Layer\ub97c mutation\ud560 \uc218 \uc5c6\ub2e4. \uc77d\uae30(\uc18c\ube44)\ub9cc \uac00\ub2a5.**

## Dependency \uac80\uc99d \ubc29\ubc95

Runtime Sovereignty Layer (`truth_enforcer.py`)\uc5d0\uc11c:
- `enforce(runtime, action)` \ud638\ucd9c \uc2dc \uad8c\ud55c \uac80\uc99d
- \uc704\ubc18 \uc2dc `RuntimeCapabilityViolation` + CRITICAL \uc774\ubca4\ud2b8 \uae30\ub85d
