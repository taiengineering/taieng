# Push Channel Readiness Report

작성일: 2026-05-17
범위: Push 채널 운영 준비도

---

## 평가

| 항목 | 점수 | 상태 |
|---|---|---|
| Infra | 8/10 | firebase-admin SDK + fcm_utils.send_push() 존재 |
| Token Mapping | 6/10 | users + worker_registry, 전화번호 기반 (refresh 없음) |
| Delivery | 7/10 | send_push() 동작, 7개 호출처 존재 |
| Retry | 3/10 | 재시도 로직 없음 (Runtime 연결 시 해결) |
| Audit | 3/10 | push_sent_at/fcm_sent 단편적 (Runtime 연결 시 해결) |
| Runtime Integration | 5/10 | push.py mock 존재, 실연동 미완 |
| Operational Readiness | 4/10 | 2명만 토큰 등록, 실사용 미검증 |

---

## Push Channel Readiness

**36/70 = 51% — C 등급**

---

## 개선 우선순위

1. push.py mock → fcm_utils.send_push() 실연동
2. channel_registry PUSH enabled=true
3. Token refresh 로직 추가
4. 앱 완료 후 push_token 등록 유도
