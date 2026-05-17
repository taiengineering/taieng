# Control Runtime Required Fields

작성일: 2026-05-17
범위: 관제가 Notification에 제공해야 하는 필드

---

## 필수 필드

| 필드 | 유형 | 설명 | 현재 상태 |
|---|---|---|---|
| event_type | string | 이벤트 유형 | ✅ Wiring에서 제공 |
| severity | string | CRITICAL/WARNING/INFO | ⚠️ Policy default 임시 사용 |
| incident_ref | string? | 연관 사고 ID | ❌ 미구현 |
| truth_source | string | severity 결정 주체 | ❌ 미구현 |
| escalation_state | string? | 에스컬레이션 단계 | ❌ 미구현 |
| recovery_state | string? | 복구 상태 | ❌ 미구현 |
| requires_ack | boolean | ACK 필수 여부 | ❌ 미구현 |
| operational_context | dict? | 운영 컨텍스트 | ✅ payload로 전달 |

---

## 현재 상태

| 구현 | 미구현 |
|---|---|
| event_type, operational_context | severity (Control 버전), incident_ref, truth_source, escalation_state, recovery_state, requires_ack |

---

## 임시 대체

Control Runtime 미구현 기간:
- **severity** → Policy default_severity 사용 (WARNING: 임시)
- **incident_ref** → 미사용
- **requires_ack** → 미사용

Control Runtime 구현 시 이관.

---

## 핵심

**Notification Runtime이 이 필드들을 생성하면 안 된다.** Control Runtime이 제공해야 한다.
