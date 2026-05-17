# Template Registry Structure

작성일: 2026-05-17
범위: Notification Engine · Template (문서 정의만, DB 구현 금지)

---

## Template 필드 구조

| 필드 | 설명 | 예시 |
|---|---|---|
| template_key | 고유 식별자 | PAYMENT_OVERDUE_SMS |
| template_type | 채널 유형 | sms / email / push / inapp |
| category | 분류 | payment / security / system / schedule |
| title | 제목 (템플릿) | `[TAI Safe] {{company_name}} 결제 미완료` |
| content | 본문 (템플릿) | `{{user_name}}님, {{amount}}원 결제가 미완료...` |
| variables | 변수 목록 (JSON) | `["company_name", "user_name", "amount"]` |
| enabled | 활성 | true/false |
| version | 버전 | 1 |

---

## 현재 상태

- `notification_templates` 테이블 존재 (Legacy, Frozen)
- `message_template_registry` 테이블 존재 (SMS 템플릿, Active)
- Runtime에서는 템플릿 미사용 (하드코딩 또는 payload 직접 전달)

---

## Phase 2 계획

1. Template Registry 통합 (notification_templates + message_template_registry → 단일)
2. Wiring에서 template_key 연결
3. Adapter에서 변수 치환 후 전달
4. Template Manager UI (admin Control Surface)

---

## 주의

현재 단계: **문서 정의만**. DB 구현 금지.
