---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-12 AutomationEngine 운영 자동화
version: 1
status: ACTIVE
owner: taiwang
---

# WO-12 — AutomationEngine (운영 자동화)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P2 WO-12
- **오브젝트:** automation_rule/run_log(신설) + automation_svc + 수신 콜백 결합
- **닫는 시나리오:** S30(문의 수신→자동 응답)·S31(결제 실패→알림)

---

## 1. 현황 (실측 — 엔진 자산과 분리 필요)

자동화/이벤트 계열 테이블 다수 존재하나 **전부 엔진/인프라 소관(격리)**:
- `business_event`(flow_key/trace_id/connector_type), `alert_rule_registry_v2`(integrity_type/workflow_type), `notification_event_wiring_registry`(source_engine) — 엔진 QA·무결성·알림 배선. **건드리지 않음.**

→ WO-12는 **운영 전용 automation 테이블 신설**(엔진과 물리 분리). 이번 세션 자산 재사용:
- `gmail_inbox_svc.register_inbound_handler(handler)` — 수신 트리거 결합점(WO-8B).
- `notify_svc.send(channel, ...)` — 통합 발송(WO-8C).
- `audit_svc.record` — 감사.

## 2. 설계

**테이블(신설, RLS off):**
- `automation_rule`: id, rule_code(uniq), event_type(mail.inbound|payment.failed|payment.success|subscription.expiring|manual), condition_json, action_type(SEND_MAIL|SEND_SMS|CREATE_TASK|CALL_WEBHOOK|LLM_DRAFT), action_config_json, require_approval(bool), enabled(bool), memo, created_by, created_at.
- `automation_run_log`: id, rule_id, event_type, trigger_ref, matched(bool), status(RUN|APPROVAL_PENDING|SKIPPED|FAILED), action_type, result_json, error, created_at.

**`services/automation_svc.py`(신설):**
- `fire(event_type, payload)`: enabled 규칙 조회 → 조건 매칭 → require_approval면 APPROVAL_PENDING 적재, 아니면 액션 실행 → run_log. 액션은 notify_svc/audit_svc 위임.
- `approve_run(run_id, actor)`: 승인 대기 건 실행.
- `register()`: gmail_inbox_svc.register_inbound_handler로 mail.inbound 결합(부팅 시 1회).
- LLM_DRAFT는 인터페이스만(엔진 LLM 미결합, 후속).

## 3. 엔드포인트

- `GET/POST /automation/rules` — 규칙 CRUD(얇게).
- `POST /automation/fire` — 수동 이벤트 발화(테스트/manual 트리거).
- `GET /automation/runs` — 실행 이력.
- `POST /automation/runs/{id}/approve` — 승인 실행.

## 4. 완료 판정 (IMPLEMENTED)

- 테이블 2개, automation_svc, 라우터, 등록.
- mail.inbound 콜백 결합(수신 시 규칙 발화). require_approval 게이트.
- `/health` 200, 배포 SUCCESS. 규칙 1건 목업으로 fire→run_log 동작 확인.

## 5. 산출물

1. 마이그레이션: automation_rule, automation_run_log
2. `services/automation_svc.py`
3. `routers/automation.py`
4. router_registry 등록(external)
