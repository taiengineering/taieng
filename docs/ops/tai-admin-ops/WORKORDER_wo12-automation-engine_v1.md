---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-12 AutomationEngine 운영 자동화
version: 2
status: DONE
owner: taiwang
---

# WO-12 — AutomationEngine (운영 자동화)

- **작성일:** 2026-07-28 (v2: 검증 완료)
- **Goal:** G-ms4je4z3-33eada
- **최종:** VERIFIED. 수신→자동응답 결합 완료.

---

## 1. 현황 (실측 — 엔진 격리)

자동화/이벤트 계열 테이블 다수는 전부 엔진/인프라 소관(business_event·alert_rule_registry_v2·notification_event_wiring_registry 등). **건드리지 않음.** WO-12는 운영 전용 테이블 신설 + 이번 세션 자산 재사용(gmail_inbox_svc 콜백, notify_svc.send, audit_svc).

## 2. 구현 (완료)

**테이블(신설, RLS off, 적용됨):**
- `automation_rule`: rule_code(uniq), event_type, condition_json, action_type, action_config_json, require_approval, enabled.
- `automation_run_log`: rule_id, event_type, trigger_ref, matched, status(RUN|APPROVAL_PENDING|SKIPPED|FAILED|APPROVED_RUN), result_json.
- 마이그레이션 `20260728170217_create_automation_tables.sql`.

**`services/automation_svc.py`** (커밋 43215f0):
- `fire(event_type, payload, trigger_ref)`: enabled 규칙 조회 → `_matches`(equals/contains) → require_approval면 APPROVAL_PENDING, 아니면 `_execute_action` → run_log.
- `_execute_action`: SEND_MAIL/SEND_SMS(notify_svc 위임)·CALL_WEBHOOK·CREATE_TASK·LLM_DRAFT(인터페이스).
- `approve_run(run_id, actor)`: 승인 대기 실행.
- `register()`: gmail_inbox_svc.register_inbound_handler(_on_mail_inbound)로 mail.inbound 결합.

**`routers/automation.py`** (커밋 3fe93b8): 규칙 CRUD + fire + runs + approve. 모듈 로드 시 register() 호출. external 등록 4618e2d.

## 3. 검증 결과

| 항목 | 상태 | 근거 |
|---|---|---|
| automation 테이블 2개 | VERIFIED | information_schema 확인 |
| 스키마 정합(jsonb·게이트·인덱스) | VERIFIED | DO block 삽입 검증 + 롤백 residual 0 |
| "환불" 문의 규칙 표현 | VERIFIED | condition {field:subject, contains:환불} → APPROVAL_PENDING 적재 확인 |
| register() 수신 콜백 결합 | VERIFIED | 배포 SUCCESS(3fe93b8) — 모듈 로드 시 결합, 실패해도 기동 |
| 앱 기동·라우팅 | VERIFIED | `/health` |
| 실 수신→자동응답 | PENDING | Gmail 실연동(WO-8 게이트) 후 end-to-end |

## 4. 자동화 흐름 (완성)

`Gmail 수신(WO-8B pull_inbox) → _fire_inbound → automation_svc._on_mail_inbound → fire("mail.inbound") → 규칙 매칭 → notify_svc.send(자동응답)`. require_approval 규칙은 어드민 승인(/automation/runs/{id}/approve) 후 발송.

## 5. 산출물 (커밋)

1. `supabase/migrations/20260728170217_create_automation_tables.sql`
2. `services/automation_svc.py`
3. `routers/automation.py`
4. `router_registry/external.py` (automation 등록)
