# Existing Push Flow Validation

작성일: 2026-05-17
범위: 기존 Push 흐름 검증

---

## 검증 결과

| 항목 | 결과 | 근거 |
|---|---|---|
| Login 시 token 저장 | **PARTIAL** | `POST /workers/fcm-token` API 존재, 앱 측 호출 여부 미확인 |
| Token refresh | **FAIL** | 갱신 로직 없음 (등록만 존재) |
| Push send API | **PASS** | `POST /workers/send-push` + `POST /workers/push-test` |
| 실제 발송 경로 | **PASS** | `fcm_utils.send_push()` → firebase-admin SDK |
| Queue | **FAIL** | Push 전용 큐 없음 (direct send) |
| Retry | **FAIL** | 재시도 로직 없음 |
| Push history | **PARTIAL** | `tbm_attendees.push_sent_at`, `overdue_history.fcm_sent` 단편적 |
| 실데이터 | **PARTIAL** | 2명 push_token 등록 |

---

## 요약

- **PASS**: 2/8
- **PARTIAL**: 3/8
- **FAIL**: 3/8

**Push 인프라 존재하나 운영 수준 불충분.**
주요 결함: Token refresh 없음, Queue 없음, Retry 없음.
