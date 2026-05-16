# Preference Timeline

작성일: 2026-05-16
상태: Concept Only

---

## 정의

**Preference도 운영 기록이다.**

## 추적 대상

| 이벤트 | 의미 |
|---|---|
| preference_created | 선호 최초 설정 |
| preference_updated | 선호 변경 |
| channel_disabled | 채널 비활성화 |
| channel_enabled | 채널 활성화 |
| mute_enabled | 뮤트 활성화 |
| mute_disabled | 뮤트 해제 |
| quiet_hour_set | 조용한 시간 설정 |
| preferences_reset | 전체 초기화 |

## 현재 단계

`notification_preference_registry.updated_at`으로 최종 변경 시점만 추적.
상세 이력은 Phase 2에서 preference_audit_log 테이블로 확장 예정.
