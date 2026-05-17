# Runtime Collision Prevention

작성일: 2026-05-17
범위: Runtime 간 충돌 방지 규칙

---

## 금지 목록

| 충돌 유형 | 설명 | 방지 방법 |
|---|---|---|
| Double Severity | 2곳에서 severity 결정 | Control Runtime만 결정 |
| Double Escalation | 2곳에서 에스컬레이션 | Control Runtime만 결정 |
| Double Suppression | Notification+Delivery 양쪽에서 억제 | Notification만 억제 |
| Double Retry | Notification+Delivery 양쪽에서 재시도 | Delivery만 재시도 |
| Double Incident | 2곳에서 인시던트 생성 | Control Runtime만 생성 |
| Double Audience | Notification+Delivery 양쪽에서 대상 결정 | Notification만 결정 |
| Double Queue | 2개 Queue에 동시 삽입 | 단일 runtime_notification_queue만 |
| Double Feed | 2곳에서 Feed INSERT | IN_APP Adapter만 INSERT |
| Double Timeline | 2곳에서 Timeline 기록 | Worker만 기록 |

---

## 핵심

**운영 Truth는 하나만 존재한다.** 모든 판단/실행은 단일 Owner가 수행.
