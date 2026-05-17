# Notification Projection Contract

작성일: 2026-05-17
범위: Notification Runtime = Projection Layer

---

## 선언

**Notification Runtime은 Projection Layer이다.**

Control Runtime이 생성한 Truth를 **읽어서** 전달 방법을 결정하는 계층.

---

## Projection 허용

| 항목 | 설명 |
|---|---|
| incident_ref | Control이 제공한 incident ID 참조 |
| severity_snapshot | Control이 결정한 severity 읽기 전용 복사 |
| operational_message | Control이 제공한 메시지 본문 projection |
| escalation_state_ref | Control의 에스컬레이션 상태 참조 |
| recovery_state_ref | Control의 복구 상태 참조 |

---

## Projection 금지

| 항목 | 이유 |
|---|---|
| severity 수정 | Truth 변경 금지 |
| incident 생성/종료 | Control 영역 |
| escalation 단계 변경 | Control 영역 |
| recovery 판단 | Control 영역 |
| operator state 변경 | Control 영역 |

---

## 핵심

**Projection = 읽기 전용 복사.** 원본 Truth를 수정하지 않는다.
