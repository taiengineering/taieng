# Audience vs Visibility Boundary

## Audience (수신 대상)
- **정의**: 특정 이벤트에 대해 알림을 받아야 할 역할/그룹
- **산출**: `resolve_notification_audience(event)`
- **소유**: Identity Core
- **이벤트 기반**: 이벤트의 severity + tenant_id에 따라 동적 결정
- **소비자**: Notification Engine (계산하지 않고 결과만 사용)

## Visibility (가시성)
- **정의**: 행위자가 볼 수 있는 데이터 범위
- **산출**: `resolve_governance_visibility(actor_ctx)`
- **소유**: Identity Core
- **정적**: 행위자의 role/scope에 따라 고정
- **소비자**: Cockpit UI, API (데이터 필터링)

## 차이

| | Audience | Visibility |
|---|---------|------------|
| 방향 | 이벤트 → 사람 | 사람 → 데이터 |
| 트리거 | 이벤트 발생 시 | 화면 접근 시 |
| 기준 | event severity + tenant | actor role + scope |
| 산출 | `resolve_notification_audience()` | `resolve_governance_visibility()` |
| 소비자 | Notification Engine | Cockpit/API |

## Notification Engine 금지

- ❌ Visibility policy 구현
- ❌ tenant visibility 계산
- ❌ governance scope 계산
- ❌ role-based 데이터 필터링

Notification Engine은 `resolve_notification_audience()` 결과를 **소비만** 한다.
