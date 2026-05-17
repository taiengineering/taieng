# Delivery Runtime Direction

작성일: 2026-05-17
범위: Delivery 엔진 최종 방향

---

## 방향

```
Notification Intelligence (판단)
  │  event → policy → audience → severity → digest
  ↓
Delivery Runtime (실행)
  │  queue → worker → adapter → retry → audit
  ↓
External Channels (transport)
  │  SMS · Telegram · Push · IN_APP · Email(Phase2)
```

---

## 역할 분리 원칙

| 계층 | 역할 | 변경 빈도 |
|---|---|---|
| Notification | 운영 의미 판단 | 이벤트 추가 시 |
| Delivery | 전달 orchestration | 채널 추가 시 |
| Channel | Transport 실행 | 외부 API 변경 시 |

---

## 현재 상태

| 계층 | 상태 |
|---|---|
| Notification | ✅ 완성 (Freeze) — Wiring/Policy/Audience/Digest |
| Delivery | ✅ 운영 가능 — Queue/Worker/Retry/Audit |
| Channel | ✅ 4채널 Active (SMS/Telegram/IN_APP/Push-mock) |

---

## Intelligence 확장 금지

| 금지 항목 | 이유 |
|---|---|
| AI suppression | 실사용 데이터 없이 과잉 |
| AI routing | Policy로 충분 |
| Dynamic escalation | 실패 패턴 미관찰 |
| Smart grouping | Digest로 충분 |
| Predictive notification | 범위 초과 |
| Auto policy mutation | 운영자 제어 원칙 위반 |

---

## 핵심

**지금은 더 똑똑하게 만들 때가 아니라, 안정적으로 전달할 때.**

Runtime은 충분히 완성. 실사용 검증이 우선.
