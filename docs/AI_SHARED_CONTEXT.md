# TAI Shared AI Context

## 프로젝트 방향

현재 TAI / 45cm Platform은 단순 SaaS가 아니라:

```text
Business Workflow Observability Platform
```

방향으로 진행 중.

---

## 현재 핵심 우선순위

1. Event Contract 통일
2. Workflow Reconstruction
3. Integrity Layer 안정화
4. Notification Runtime 중앙화
5. Browser Synthetic 구축
6. SLA Layer 구축

---

## 핵심 철학

### Event ≠ Alert

모든 Event가 운영 Alert는 아니다.

### Alert ≠ Notification

Alert는 운영 중요도 승격.
Notification은 전달.

### Engine은 Signal만 발생

각 엔진은 직접 발송하지 않는다.

### Notification Engine이 전달

모든 Delivery는 중앙 Notification Runtime 담당.

### 사람은 마지막 Escalation

자동 반응 우선.

---

## 현재 플랫폼 방향

현재 목표:

```text
Infra Observability
```

아님.

실제 목표:

```text
Business Workflow Observability
```

---

## 금지 방향

- 엔진별 직접 메시지 발송
- Notification 내부 비즈니스 로직
- AI recipient inference
- Infra 중심 관제 구조
- Slack-style 협업 플랫폼화
- 채널별 분산 구현

---

## 현재 단계

현재는 플랫폼 공통 규약 구축 단계.

중요:

- Event 규약
- Trace 규약
- Alert 규약
- Notification 규약
- Workflow 규약

안정화가 우선.

기능 확장보다:

```text
개념 경계 유지
```

가 더 중요.
