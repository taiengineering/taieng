# Feed UX Contract

작성일: 2026-05-16

---

## 정의

Feed는 **Communication History**다.

## Feed Item 상태

| 상태 | UX 의미 |
|---|---|
| unread | 읽지 않은 상태 — 강조 표시 |
| read | 읽음 — 일반 표시 |
| delayed | 조용한 시간으로 지연되었던 항목 — 전달 후 일반 표시 |
| resumed | 조용한 시간 종료 후 전달 — Timeline에서 확인 |
| suppressed | Feed에 나타나지 않음 |
| acknowledged | ACK 된 항목 |

## Grouping (UI Only)

| 기준 | 설명 |
|---|---|
| source_type | 유형별 (runtime_alert, service_notice 등) |
| severity | 중요도별 (INFO, WARNING, CRITICAL) |
| channel_key | 채널별 (TELEGRAM, SMS, IN_APP) |

Backend grouping 금지. UI에서만 정렬/그룹.

## Badge Grammar

| Severity | 색상 |
|---|---|
| INFO | 파란 (#1d4ed8) |
| WARNING | 노란 (#d97706) |
| CRITICAL | 빨간 (#dc2626) |
