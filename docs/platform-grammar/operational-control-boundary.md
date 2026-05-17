# Operational Control Boundary

작성일: 2026-05-17
상태: **공식 고정**

---

## 3계층 정의

| 계층 | 책임 | 핵심 문장 |
|---|---|---|
| **관제 (Control Runtime)** | 상태 판단 | "무엇이 이상한가" |
| **알림 (Notification Intelligence)** | 전달 판단 | "누구에게 어떻게 알릴까" |
| **전달 (Delivery Runtime)** | 전달 실행 | "안전하게 전달한다" |

---

## 관제 (Control Runtime) 책임

| 책임 | 설명 |
|---|---|
| Anomaly 판단 | 이상 감지 + 분류 |
| Incident 생성 | 사고 기록 생성 |
| Severity Truth | CRITICAL/WARNING/INFO 최종 결정 |
| Shutdown 판단 | 작업 중단 여부 결정 |
| Operational Truth | 운영 상태 진실 |
| Escalation Truth | 에스컬레이션 단계 결정 |

---

## Notification Intelligence 책임

| 책임 | 설명 |
|---|---|
| Audience | 수신 대상 결정 |
| Channel | 전달 채널 결정 |
| Quiet Hour | 야간 억제 |
| Digest | 묶음 전달 |
| Fatigue Reduction | 알림 피로 감소 |
| Communication Priority | 전달 우선순위 |

---

## Delivery Runtime 책임

| 책임 | 설명 |
|---|---|
| Queue | 대기열 관리 |
| Retry | 재시도 (max 3, exponential) |
| Timeout | 전달 시간 제한 |
| Adapter | 채널별 전달 실행 |
| Transport | 외부 채널 연결 |
| Audit | 전달 감사 기록 |

---

## 핵심

**관제만 상태를 판단한다.** 알림은 전달 방법을 결정하고, 전달은 실행만 한다.
