# Notification vs Delivery Boundary

작성일: 2026-05-17
범위: Notification Engine · 역할 분리 공식 정의

---

## 정의

| 영역 | 역할 | 핵심 |
|---|---|---|
| **Notification** | 판단 | "누구에게 무엇을 왜 보내는가" |
| **Delivery** | 실행 | "어떻게 안전하게 전달하는가" |

---

## Notification 책임

| 책임 | 설명 |
|---|---|
| 의미 (Semantics) | event_type, source_type 해석 |
| 정책 (Policy) | cooldown, quiet hour bypass, mute |
| Severity | CRITICAL / WARNING / INFO 결정 |
| Audience | 수신 대상 결정 |
| Digest | 묶음 여부 결정 |
| Suppression | 억제 여부 결정 |
| Operational Intent | 운영 목적 정의 |

---

## Delivery 책임

| 책임 | 설명 |
|---|---|
| Queue | 전달 대기열 관리 |
| Retry | 실패 시 재시도 (max 3, exponential) |
| Worker | 큐 소비 + adapter 호출 |
| Adapter | 채널별 전달 실행 |
| Timeout | 전달 시간 제한 |
| Delivery Result | 성공/실패 결과 정규화 |
| Transport | 외부 채널 연결 (FCM/MessageMi/Telegram) |
| Audit | 전달 감사 기록 (timeline + policy_audit) |

---

## 핵심

**Notification은 판단, Delivery는 실행.**

Notification이 "보내라"고 결정하면, Delivery가 "어떻게"를 실행한다.
Delivery는 "왜 보내는지" 판단하지 않는다.
