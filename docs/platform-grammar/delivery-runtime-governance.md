# Delivery Runtime Governance

작성일: 2026-05-17
범위: Delivery Layer 허용/금지 규칙

---

## 허용

| 항목 | 설명 |
|---|---|
| Retry | 실패 시 재시도 (max 3, exponential) |
| Adapter 추가 | 신규 채널 adapter (Adapter Interface 준수) |
| Delivery Audit | policy_audit + timeline 기록 |
| Timeout | adapter 호출 시간 제한 |
| Fallback Transport | primary 실패 시 secondary 전환 (Phase 2) |
| Delivery Metrics | 성공률/latency 집계 |
| Compat Layer | Legacy 전환 중간 계층 |

---

## 금지

| 항목 | 이유 |
|---|---|
| Severity 판단 | Notification 영역 |
| Audience 판단 | Notification 영역 |
| Suppression 판단 | Notification 영역 (mute/disabled) |
| Escalation 판단 | Notification 영역 |
| Digest 판단 | Notification 영역 |
| Event 의미 해석 | Notification 영역 |
| Queue 구조 변경 | Freeze 대상 |
| Lifecycle 변경 | Canonical Lifecycle 유지 |

---

## 핵심

**Delivery는 판단하지 않는다.** Notification이 결정한 것을 실행만 한다.
