# Notification Runtime Forbidden Semantics

작성일: 2026-05-17
범위: Notification Runtime 의미 금지 목록

---

## 금지 의미

| 금지 의미 | 이유 | Owner |
|---|---|---|
| Operational Severity Truth | severity 최종 결정은 Control 영역 | Control Runtime |
| Incident Truth | 사고 생성/종료는 Control 영역 | Control Runtime |
| Recovery Truth | 복구 판단은 Control 영역 | Control Runtime |
| Escalation Truth | 에스컬레이션 단계 결정은 Control 영역 | Control Runtime |
| Operator State Truth | 운영 상태 판단은 Control 영역 | Control Runtime |
| Queue State Mutation | 큐 상태 변경은 Delivery 영역 | Delivery Runtime |
| Adapter 직접 호출 | 전달 실행은 Delivery 영역 | Delivery Runtime |

---

## 허용 의미

| 허용 의미 | 설명 |
|---|---|
| Communication Priority | severity snapshot 기반 전달 우선순위 |
| Delivery Priority | 채널 우선순위 |
| Quiet Hour | 야간 억제 |
| Digest | 묶음 전달 |
| Audience Mapping | 수신 대상 결정 |
| Cooldown | 전달 빈도 조절 |
| Mute (User Preference) | 사용자 억제 |
| Severity Snapshot | Control이 제공한 severity를 읽기 전용 |

---

## 핵심

**Notification은 의미를 생성하지 않는다.** Control이 제공한 의미를 **읽고** 전달 방법을 결정할 뿐.
