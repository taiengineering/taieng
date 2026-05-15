# TAI / 45cm Platform Architecture Index

## 현재 플랫폼 구조

| Layer | 설명 | 상태 |
|---|---|---|
| Event Layer | 플랫폼 공통 Event Contract 및 Event Flow | PARTIAL |
| Workflow Layer | Business Workflow 흐름 재구성 | PARTIAL |
| Integrity Layer | Workflow 정상성 평가 및 Drift 감지 | PARTIAL |
| Alert Layer | Integrity 기반 운영 승격 | DONE |
| Notification Layer | 중앙 운영 커뮤니케이션 Runtime | PARTIAL |
| Browser Synthetic | 실제 사용자 흐름 기반 Synthetic Monitoring | PLANNED |
| SLA Layer | Business SLA / Workflow SLA 추적 | PLANNED |

---

## 핵심 방향

현재 플랫폼 목표는:

```text
Infra Monitoring Platform
```

이 아니라:

```text
Business Workflow Observability Platform
```

이다.

핵심 흐름:

```text
Event
→ Workflow
→ Integrity
→ Alert
→ Notification
→ Reaction
```

---

## 핵심 엔진

- Watch Engine
- Notification Engine
- Runtime Engine
- Workflow Engine
- Browser Synthetic Engine
- SLA Layer

---

## 현재 우선순위

1. Event Contract 통일
2. Notification Runtime 중앙화
3. Browser Synthetic 구축
4. SLA Layer 구축
5. Workflow Reconstruction 안정화
