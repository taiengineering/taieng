# Push Runtime Compatibility

작성일: 2026-05-17
범위: 기존 Push → Notification Runtime 연결 가능성

---

## 연결 가능성 분석

| 항목 | 연결 가능 | 방법 |
|---|---|---|
| Adapter 연결 | ✅ 가능 | `push.py` mock을 `fcm_utils.send_push()` 실호출로 교체 |
| Audience 연결 | ✅ 가능 | audience_resolver에서 phone 조회 → push_token 확인 |
| Actor Mapping | ⚠️ 부분적 | 전화번호 기반 → user_id 기반 전환 필요 |
| Audit 연결 | ✅ 가능 | Worker에서 policy_audit + timeline 자동 기록 |
| Timeline 연결 | ✅ 가능 | Push Adapter 반환값으로 timeline step 기록 |
| Queue 연결 | ✅ 가능 | Runtime Queue → Worker → Push Adapter 흐름 |
| Retry 연결 | ✅ 가능 | Runtime Retry 로직 그대로 사용 |
| Quiet Hour | ✅ 가능 | channel_registry.supports_quiet_hour=true |

---

## 필요 작업

1. `push.py` mock → `fcm_utils.send_push()` 실호출 교체
2. `notification_channel_registry` PUSH enabled=true
3. Audience resolver에 push_token 조회 추가
4. `push.py send()` context에서 fcm_token 추출 로직

---

## 핵심

기존 Push 인프라(`fcm_utils.send_push`)를 **그대로 사용**하면서
Notification Runtime의 Queue/Retry/Audit/Timeline을 **추가**하는 방향.
