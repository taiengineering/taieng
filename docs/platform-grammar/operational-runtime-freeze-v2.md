# Operational Runtime Freeze v2

작성일: 2026-05-17
상태: **공식 선언**

---

## 선언

관제 / 알림 / 전달 3계층의 **책임 경계를 공식 고정**한다.

---

## Freeze 대상

| 대상 | 고정 내용 |
|---|---|
| Notification Boundary | audience/channel/quiet hour/digest/suppression/cooldown |
| Delivery Boundary | queue/retry/adapter/timeout/audit/timeline |
| Control Boundary | severity/incident/anomaly/shutdown/escalation |
| Runtime Ownership | 기능별 단일 Owner (Ownership Matrix) |
| Truth Source | Truth별 단일 Source (Truth Source Registry) |
| Adapter Interface | `send(message, context) → (success, error)` |
| Queue Grammar | PENDING→PROCESSING→DELIVERED/FAILED/RETRY/DLQ |
| Lifecycle | Canonical Lifecycle (12상태) |

---

## 경계 침범 금지

| 침범 | 결과 |
|---|---|
| Notification이 severity 생성 | 금지 — Control 영역 |
| Delivery가 audience 판단 | 금지 — Notification 영역 |
| Notification이 adapter 직접 호출 | 금지 — Delivery 영역 |
| Delivery가 mute 판단 | 금지 — Notification 영역 |
| 어디서든 이중 판단 | 금지 — 단일 Owner 원칙 |

---

## 허용

| 항목 | 조건 |
|---|---|
| 버그 수정 | 즉시 |
| 파라미터 튜닝 | 관찰 근거 기반 |
| 신규 Adapter | Adapter Interface 준수 |
| 신규 Wiring | 기존 Policy 범위 내 |
| Compat → wire_and_emit 전환 | 점진적, try/except |
| 실사용 검증 | 항상 |

---

## 해제 조건

1. 실사용 검증 80%+ 달성
2. Runtime Integrity 전항목 PASS
3. 운영 1주 무장애
4. Phase 2 Boundary 문서 기반 승인
