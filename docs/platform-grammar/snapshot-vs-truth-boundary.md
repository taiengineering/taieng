# Snapshot vs Truth Boundary

작성일: 2026-05-17
범위: Projection 경계 정의

---

## 정의

| 항목 | Snapshot | Truth |
|---|---|---|
| 소유자 | Notification Runtime | Control Runtime |
| 성격 | 읽기 전용 복사 | 유일한 원본 |
| 수정 | ❌ 금지 | ✅ Control만 가능 |
| 생성 시점 | 이벤트 발생 시 복사 | Control Runtime이 생성 |
| 생명주기 | 알림 전달 완료까지 | 운영 상태 변경까지 |
| 용도 | 전달 우선순위/채널 결정 | 운영 판단 근거 |

---

## 예시

| 항목 | Snapshot (알림) | Truth (관제) |
|---|---|---|
| severity | "CRITICAL" (전달 시점 복사) | CRITICAL → WARNING → RESOLVED (변경 가능) |
| incident | incident_ref="INC-001" | incident 상태 관리 (open/investigating/resolved) |
| escalation | level_snapshot=2 | level 1→2→3 변경 |

---

## 규칙

1. **Notification은 Snapshot만 가진다** — Truth를 직접 수정하지 않음
2. **Snapshot은 전달 시점에 고정** — 이후 Truth 변경에 영향받지 않음
3. **Truth 변경 시 새 알림 발생** — 기존 Snapshot 수정이 아닌 새 이벤트

---

## 핵심

**Notification은 Snapshot만 가진다.** Truth는 Control Runtime에만 존재.
