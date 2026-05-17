# Notification Event Taxonomy

작성일: 2026-05-17
범위: 이벤트 명명 표준

---

## 분류 체계

| category | 설명 | prefix |
|---|---|---|
| auth | 인증/보안 | `auth_` 또는 동사형 |
| billing | 결제/재무 | `payment_`, `invoice_`, `refund_` |
| subscription | 구독 관리 | `subscription_` |
| organization | 조직/협업 | `member_`, `role_`, `organization_`, `approval_` |
| workflow | 워크플로우 | `schedule_`, `inspection_`, `workflow_` |
| safety | 안전 관리 | `weather_`, `accident_`, `violation_`, `education_`, `risk_` |
| system | 시스템 운영 | `maintenance_`, `incident_`, `deployment_`, `backup_`, `scheduler_`, `service_` |
| marketing | 마케팅 | `campaign_`, `newsletter_`, `feature_` |

---

## 명명 규칙

1. `{명사}_{과거분사}` 형태: `payment_success`, `member_invited`
2. 소문자 + 밑줄 (snake_case)
3. 동사 현재형 금지: `pay` ❌ → `payment_success` ✅
4. 약어 금지: `pmt_succ` ❌ → `payment_success` ✅
5. category prefix 권장: `subscription_expiring` (subscription 카테고리)

---

## 등록 절차

1. event_key 명명 (위 규칙 준수)
2. category 분류
3. `notification_event_registry` 등록
4. `notification_event_wiring_registry` 연결
5. 문서 업데이트 (해당 Pack 문서)
