# Delivery Runtime Channel Governance

작성일: 2026-05-17
범위: 채널 관리 규칙

---

## 허용

| 항목 | 설명 |
|---|---|
| Adapter 추가 | `send(message, context)` interface 준수 |
| Compat 연결 | 기존 infra 위임 |
| Retry | Runtime retry 적용 (adapter 개별 구현 금지) |
| Timeout | adapter별 연결 timeout 설정 |
| Audit | delivery result → timeline + policy_audit |
| Channel Registry | channel_key + enabled + config |
| Fallback | primary 실패 시 secondary 전환 (Phase 2) |

---

## 금지

| 금지 | 이유 |
|---|---|
| Channel-specific Truth | 채널별 severity/incident 판단 금지 |
| Adapter-specific Lifecycle | 전체 단일 lifecycle 사용 |
| Channel-specific Severity | severity는 Notification/Control 결정 |
| Adapter-specific Retry | Runtime retry 전체 적용 |
| Adapter-specific Queue | 단일 Queue 사용 |
| Channel 내부 정책 | adapter는 전달만 (판단 금지) |

---

## 핵심

**채널은 Transport일 뿐.** 판단은 Notification, 실행은 Delivery, 채널은 전달만.
