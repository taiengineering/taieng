# Notification Registry Structure (제안)

작성일: 2026-05-16

---

## Registry 테이블 구조

### 1. notification_channel_registry

채널 정의. Adapter 매핑.

| 필드 | 의미 |
|---|---|
| channel_key | TELEGRAM, SMS, EMAIL, PUSH, IN_APP, WEBHOOK |
| adapter_module | Python module path |
| enabled | 활성화 여부 |
| config | 채널별 설정 (JSON) |

### 2. notification_template_registry

메시지 템플릿.

| 필드 | 의미 |
|---|---|
| template_key | 템플릿 식별자 |
| channel_key | 대상 채널 |
| title_template | 제목 템플릿 |
| body_template | 본문 템플릿 |
| variables | 변수 정의 (JSON) |

### 3. notification_delivery_policy_registry

전달 정책.

| 필드 | 의미 |
|---|---|
| policy_key | 정책 식별자 |
| retry_max | 최대 재시도 |
| cooldown_sec | 쿨다운 (초) |
| dedupe_enabled | 중복 제거 |
| quiet_hour_start | 조용한 시간 시작 |
| quiet_hour_end | 조용한 시간 종료 |

### 4. notification_preference_registry

사용자 선호.

| 필드 | 의미 |
|---|---|
| user_id | 사용자 |
| channel_key | 선호 채널 |
| muted_types | 뮤트된 이벤트 타입 |
| quiet_hour | 개인 조용한 시간 |

### 5. notification_delivery_log

전달 이력. (현재: `runtime_notification_audit` 대응)

### 6. notification_audience_registry

대상 그룹 정의.

| 필드 | 의미 |
|---|---|
| audience_key | 그룹 식별자 |
| audience_type | role/tenant/custom |
| resolution_rule | 수신자 결정 규칙 |

## 핵심 원칙

Registry는 전달 정책을 정의한다. 운영 판단을 정의하지 않는다.
