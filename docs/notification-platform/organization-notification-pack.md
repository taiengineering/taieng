# Organization Notification Pack

작성일: 2026-05-17
범위: 조직/협업 알림

---

## 원칙

**협업 이벤트.** 승인 요청은 즉시, 나머지는 일반.

---

## 이벤트

| event_key | 설명 | audience | channel | severity | digest | quiet bypass |
|---|---|---|---|---|---|---|
| member_invited | 멤버 초대 | actor | IN_APP | INFO | ✅ | ❌ |
| member_joined | 멤버 참여 | tenant_admin | IN_APP | INFO | ✅ | ❌ |
| role_changed | 역할 변경 | actor | IN_APP | WARNING | ❌ | ❌ |
| organization_updated | 조직 정보 변경 | tenant_admin | IN_APP | INFO | ✅ | ❌ |
| approval_requested | 승인 요청 | approver | IN_APP+TELEGRAM | WARNING | ❌ | ❌ |
| approval_completed | 승인 완료 | requester | IN_APP | INFO | ✅ | ❌ |

---

## 규칙

- approval_requested: TELEGRAM 병행 (빠른 응답 유도)
- member_invited/joined: 일간 digest 가능
- role_changed: digest 불가 (즉시 인지 필요)
