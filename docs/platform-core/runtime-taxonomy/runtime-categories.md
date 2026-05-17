# Runtime Taxonomy — 공식 분류

---

## Runtime Category

### A. Core Runtime
| Runtime | 상태 | 설명 |
|---------|:---:|------|
| **Platform Core** | ✅ | Event Envelope + Contract + Tenant Isolation |

### B. Truth Runtime
| Runtime | 상태 | 설명 |
|---------|:---:|------|
| **Control** | ✅ | Operational Truth Engine. severity/incident/escalation/ACK/recovery |
| **Governance** | ✅ | Tenant Impact. Control 하위 계층 (독립 Runtime 아님) |

### C. Process Runtime
| Runtime | 상태 | 설명 |
|---------|:---:|------|
| **Workflow** | ✅ | Business Process. state transition + event emission |

### D. Intelligence Runtime
| Runtime | 상태 | 설명 |
|---------|:---:|------|
| **Semantic** | ✅ | Legacy→Canonical 변환. Translation Layer |
| **Knowledge** | ✅ | Pattern/Stability/Recovery. Control 하위 |

### E. Projection Runtime
| Runtime | 상태 | 설명 |
|---------|:---:|------|
| **Notification** | ✅ | Communication Projection. audience/routing/cooldown |

### F. Execution Runtime
| Runtime | 상태 | 설명 |
|---------|:---:|------|
| **Delivery** | ✅ | Transport. Telegram/SMS/Email |
| **Scheduler** | ✅ | Cron. APScheduler + DIRECT handler |

### G. Surface Runtime
| Runtime | 상태 | 설명 |
|---------|:---:|------|
| **UI (Cockpit)** | ✅ | Admin Projection Surface |
| **UI (SaaS)** | ✅ | Worker Projection Surface |

---

## 현재 독립 Runtime: 8개

| # | Runtime | Category | 독립 |
|---|---------|----------|:---:|
| 1 | Platform Core | Core | ✅ |
| 2 | Control | Truth | ✅ |
| 3 | Workflow | Process | ✅ |
| 4 | Semantic | Intelligence | ✅ |
| 5 | Notification | Projection | ✅ |
| 6 | Delivery | Execution | ✅ |
| 7 | Scheduler | Execution | ✅ |
| 8 | UI | Surface | ✅ |

## Control 하위 계층 (\ub3c5\ub9bd Runtime \uc544\ub2d8): 2\uac1c

| # | 계층 | 소속 |
|---|--------|------|
| 1 | Governance | Control 하위 |
| 2 | Knowledge | Control 하위 |

## 미존재 / 향후 검토 Runtime

| Runtime | 판정 | 이유 |
|---------|:---:|------|
| Feed | ❌ 불필요 | Notification Projection에 포함 |
| Timeline | ❌ 불필요 | UI Projection에 포함 |
| Queue | ❌ 불필요 | Delivery 내부 |
| Policy | ❌ 불필요 | Knowledge에 포함 |
| Orchestration | ❌ 불필요 | Workflow와 동일 |
| Dashboard | ❌ 불필요 | UI와 동일 |
| Contract | ❌ 불필요 | Platform Core에 포함 |

---

## Engine vs Runtime 구분

| 개념 | 정의 | 예시 |
|------|------|------|
| **Engine** | 제품/도메인 단위 | Watch Engine, Marketing Engine, TAI Engine |
| **Runtime** | 실행 책임 계층 | Control, Notification, Delivery, Workflow |

Watch Engine 내부에 Control + Notification + Delivery + Knowledge + Governance Runtime이 존재.
Engine은 여러 Runtime을 조합한 도메인 단위.

## Runtime Explosion 방지 규칙

1. **신규 Runtime 생성 전 반드시 기존 Runtime 포함 가능성 검토**
2. **독립 Runtime 최대 10개** (현재 8개)
3. **하위 계층은 상위 Runtime에 소속** (Governance → Control)
4. **기능단위 Runtime 금지** (Feed Runtime, Queue Runtime 등)
5. **Runtime 생성 시 ownership + contract + dependency 필수 정의**
