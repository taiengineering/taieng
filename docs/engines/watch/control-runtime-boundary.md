# Control Runtime Boundary Declaration

## 선언

**Control Runtime**은 TAI Safe 플랫폼의 **Operational Truth Engine**이다.

플랫폼 전체 운영 의미의 원본(Source of Truth)은 Control Runtime이 독점 소유한다.
다른 Runtime은 Truth를 소비(consume)하거나 투영(project)할 수 있지만, 생성(create)하거나 수정(mutate)할 수 없다.

---

## Runtime 계층 구조

```
┌─────────────────────────────────────────────┐
│  UI Runtime = Projection Surface            │
├─────────────────────────────────────────────┤
│  Notification = Communication Projection     │
│  Delivery    = Execution Engine              │
├─────────────────────────────────────────────┤
│  Workflow    = Business Process Runtime      │
├─────────────────────────────────────────────┤
│  ██ CONTROL  = Operational Truth Engine ██   │
├─────────────────────────────────────────────┤
│  Platform Core = Runtime Contract Layer      │
└─────────────────────────────────────────────┘
```

## Runtime 역할 정의

| Runtime | 정의 | Truth 권한 |
|---------|------|:---:|
| **Control Runtime** | Operational Truth Engine | ✅ 생성+수정+소유 |
| Notification Runtime | Communication Projection Engine | ❌ 소비만 |
| Delivery Runtime | Execution Engine | ❌ 소비만 |
| Workflow Runtime | Business Process Runtime | ❌ 소비만 |
| UI Runtime | Projection & Interaction Surface | ❌ 소비만 |
| Semantic Adapter | Translation Layer | ❌ 변환만 |

---

## Runtime별 허용/금지

### Control Runtime (✅ Owner)

허용:
- severity 생성/변경
- incident 생성/해결/종료
- escalation 판단/상향
- recovery 추천/종료
- ACK 요구/완료 판정
- operational status 생성
- anomaly 판정
- degradation 판정
- workflow blockage 판정
- pattern 탐지/축적
- stability 계산
- tenant impact 계산

### Notification Runtime (투영만)

허용:
- communication projection
- audience mapping
- delivery preference
- digest aggregation
- quiet hour
- fatigue reduction
- cooldown execution

금지:
- severity 생성
- incident 생성
- escalation 판단
- operational truth 수정
- ACK truth 수정
- recovery 종료 판단
- suppression truth 생성

### Delivery Runtime (실행만)

허용:
- queue management
- retry execution
- timeout execution
- transport (Telegram, SMS, Email)
- provider adapter
- delivery audit

금지:
- severity 판단
- incident 생성
- audience 판단
- suppression 판단
- escalation 판단

### Workflow Runtime (비즈니스 프로세스만)

허용:
- process execution
- state transition
- workflow step execution
- business event emission

금지:
- operational severity 생성
- incident truth 생성
- escalation truth 생성
- operational ACK 생성
- recovery truth 생성

핵심: Workflow는 상태(state)를 가질 수 있지만, Operational Truth는 가질 수 없다.

### UI Runtime (표시만)

허용:
- Control Runtime truth 표시
- 사용자 액션 전달 (ACK, RESOLVE, IGNORE → Control에 요청)
- 필터/정렬/검색

금지:
- severity 저장
- incident source 저장
- escalation source 저장
- operational truth overwrite

---

## 가장 위험한 상태

```
⚠️ Notification Runtime이 운영 의미를 먹는 것
```

예:
- Notification이 severity를 계산하기 시작
- Notification이 escalation을 판단
- Notification이 suppression truth를 생성
- Notification이 ACK ownership을 생성

이는 **Operational Truth Fragmentation**을 발생시킨다.
운영 플랫폼에서 Truth Source는 반드시 단일해야 한다.
