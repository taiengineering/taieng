# Runtime Semantic Collision Registry

작성일: 2026-05-17
범위: Runtime 간 의미 충돌 등록

---

## 충돌 등록

| 의미 | 충돌 위치 | 상태 | 설명 |
|---|---|---|---|
| severity | Policy default_severity vs Control 판단 | ⚠️ WARNING | Control 미구현으로 Policy가 임시 대체. 충돌 없음 (단일 소스). |
| escalation | Wiring escalation_enabled vs Control 판단 | ⚠️ WARNING | 플래그만 존재, 실제 로직 미구현. 충돌 없음. |
| escalation_delay | Policy에 값 존재 | ⚠️ WARNING | 실제 사용 없음. 충돌 없음. |
| ACK | Queue ACKNOWLEDGED | ✅ SAFE | Delivery 전용 — 충돌 없음 |
| suppression (mute) | Notification preferences | ✅ SAFE | Notification 전용 — 충돌 없음 |
| suppression (cooldown) | Policy + Wiring | ✅ SAFE | Notification 전용 — 충돌 없음 |
| audience | audience_resolver | ✅ SAFE | Notification 전용 — 충돌 없음 |
| retry | retry_policy | ✅ SAFE | Delivery 전용 — 충돌 없음 |
| incident | 미구현 | ✅ SAFE | 충돌 불가 |
| recovery | 미구현 | ✅ SAFE | 충돌 불가 |

---

## 요약

| 상태 | 건수 |
|---|---|
| SAFE | 7 |
| WARNING | 3 |
| CRITICAL | 0 |

**현재 CRITICAL 충돌 없음.** WARNING 3건은 Control Runtime 구현 시 자동 해소.
