# Runtime Responsibility Freeze v3

작성일: 2026-05-17
상태: **공식 고정**

---

## 3계층 책임 고정

| Runtime | 책임 | 의미 범위 |
|---|---|---|
| **Control Runtime** | 상태 판단 + Truth 생성 | severity, incident, escalation, recovery, operator state |
| **Notification Intelligence** | 전달 판단 + Projection | audience, channel, quiet hour, digest, mute, cooldown, severity snapshot |
| **Delivery Runtime** | 전달 실행 + Audit | queue, retry, adapter, timeout, timeline, audit, metrics |

---

## Freeze 대상 (v3 추가)

| 대상 | 고정 내용 |
|---|---|
| Notification = Projection Layer | Truth 생성 금지, Snapshot만 허용 |
| Semantic Ownership | Truth별 단일 Owner 고정 |
| Collision Prevention | 이중 판단 금지 (severity/escalation/incident) |
| Control 임시 대체 | severity default — Control 구현 시 이관 |

---

## v1 → v2 → v3 변화

| 버전 | 초점 |
|---|---|
| v1 | Notification/Delivery 경계 정의 |
| v2 | 3계층 경계 공식 고정 + Truth Source + Collision Prevention |
| v3 | **Notification = Projection Layer** + Semantic Ownership + Forbidden Semantics |

---

## 해제 조건

1. Control Runtime 구현 완료
2. severity/escalation 이관 완료
3. 실사용 검증 80%+
4. Runtime Integrity 전항목 PASS
