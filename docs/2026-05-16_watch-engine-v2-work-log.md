# TAI Safe — Watch Engine v2.0 전체 작업 내역

작성일: 2026-05-16

---

## 세션 개요

TASK 01∶30 전체 구현 + Production 배포 + Platform Core 추출.
4개 세션에 걸쳐 진행.

| 세션 | Transcript | TASK |
|--------|-----------|------|
| 1차 | `2026-05-15-06-32-57` | 01∶08 |
| 2차 | `2026-05-15-13-50-55` | 01∶13 |
| 3차 | `2026-05-15-22-57-47` | 01∶23 |
| 4차 | `2026-05-16-10-21-15` | 01∶31 |

---

## TASK 별 완료 내역

### Phase 1: Core Engine (TASK 01∶04)
- DB 스키마 (flow_registry, flow_step_registry, flow_integrity_rule_registry, business_event, engine_integrity_event)
- emitEvent SDK (factory_process_v3.py, anonymous_diagnosis.py)
- Integrity Evaluator v1.0 (field_mismatch, sequence_violation, stuck_detected, timeout_exceeded)
- Flow Status + False Positive Suppression
- Scheduler v1.0 (INTEGRITY_EVALUATE, SYNTHETIC_LOGIN, SYNTHETIC_PROCESS_REG)

### Phase 2: Synthetic & Cockpit (TASK 05∶08)
- Synthetic Runner + Cleanup
- Flow Scenario Binding (6개 시나리오)
- Cockpit 18섹션 UI (watch-engine.html)
- engine-monitoring.html

### Phase 3: Alert & Browser (TASK 09∶10)
- Alert Engine (6개 rule, cooldown, dedupe, mute, Telegram)
- Browser Synthetic (5개 등록, Playwright 연결)

### Phase 4: SLA & Intelligence (TASK 11∶13)
- SLA Layer (5개 flow, warning/critical threshold)
- Incident Intelligence (Priority Engine P1∶P4, Risk Score)
- Recovery Layer (9개 매핑, 5개 Playbook)
- Operational Knowledge (Stability Tracker, Pattern Updater, Recovery Effectiveness)
- Operational Memory (tenant_operational_registry 12행)

### Phase 5: Platform Grammar & Identity (TASK 14∶19)
- Platform Grammar 7문서 (core-language, entity-map, AI_SHARED_CONTEXT, ownership-matrix, permission-system, semantic-adapter, alert-vs-notification)
- Notification Responsibility Refactoring (문서)
- Launch Readiness (checklist, blocking-risk)
- Real SaaS E2E Validation
- Operational Control Surface (message_template_registry 6, notification_routing_registry 6, workflow_visual_registry 5)
- Identity Core v2 (identity_role_registry 7, identity_role_mapping 14, resolve_actor_context v2)
- Permission System Interface

### Phase 6: Document MVP (TASK 20∶23)
- workflow_document_registry (10종 MVP)
- Document Activation Service v1.2 (activate_documents_for_workflow)
- Gotenberg PDF Rendering (render_pdf_gotenberg, _build_default_html)
- Document API v3 (activate, generate-pdf, download redirect)
- Workflow Auto Hook (factory_process_v3.py + anonymous_diagnosis.py)
- document-output.html (admin)
- form-outputs 버킷 public 전환

### Phase 7: Validation & Payment (TASK 24∶26)
- E2E Operational Validation
- Pricing Validation Layer (pricing_audit_log, validate, guard, payment-mapping)
- Payment Activation API (e2e-validate, activation-guard, orphans, activate-subscription)
- DB constraints (UNIQUE plan_code, CHECK price ≥ 0)

### Phase 8: Mock & Semantic (TASK 27∶28)
- Mock Operational Saturation (10 tenant, 772 business_event, 144 integrity_event, 6개 시나리오)
- Semantic Adapter (legacy_state_mapping 22행, translate_state, translate_record, LLM context)
- semantic-adapter.md

### Phase 9: Production (TASK 29∶30)
- Production Guard API (env-check, runtime-stats, safety-guard, scheduler-status, summary)
- Mock/Real Separation (environment='mock' 마킹, CHECK constraint 확장)
- Production Isolation (evaluator v1.3, governance v1.1, repeated v1.1, stability v1.1, incident API v1.1)
- Runtime Isolation Policy 문서
- Cron Manager v2 (reload+start, DIRECT run, scheduler-status)
- cron-list.html 크론 관리 UI

### Phase 10: Platform Core (TASK 31)
- Platform Core 추출 (event-envelope, runtime-contract, engine-namespace)
- Watch Engine Domain 재정의 (watch-domain.md)
- Engine Exchange 기준 정의

---

## 최종 시스템 규모

### DB (24개 Watch+Ops 테이블)
business_event, engine_integrity_event, flow_registry, flow_step_registry, flow_integrity_rule_registry, flow_scenario_binding, alert_rule_registry, alert_history, browser_synthetic_registry, workflow_sla_registry, workflow_risk_registry, workflow_recovery_registry, incident_action_log, incident_pattern_registry, operational_playbook_registry, tenant_operational_registry, identity_role_registry, identity_role_mapping, message_template_registry, notification_routing_registry, workflow_visual_registry, workflow_document_registry, legacy_state_mapping, pricing_audit_log

### 라우터 (external.py 45개, Watch 17개)
Watch 13: watch_engine_api, alert, browser, sla, incident, recovery, knowledge, memory, governance, identity, control, document_api
Ops 4: pricing_validation, payment_activation, semantic_adapter, production_guard
Cron 1: cron_manager (v2)

### Scheduler (9개 DIRECT)
INTEGRITY_EVALUATE(5분), ALERT_EVALUATE(5분), SYNTHETIC_LOGIN(5분), SYNTHETIC_PROCESS_REG(15분), SYNTHETIC_BROWSER_LOGIN(15분), SYNTHETIC_BROWSER_PROCESS(15분), SYNTHETIC_CLEANUP(매일3시), INCIDENT_REPEATED(5분), PATTERN_SYNC(6시간)

### Admin (7개)
watch-engine.html(18섹션), engine-monitoring.html, message-templates.html, notification-routing.html, workflow-registry.html, document-output.html, cron-list.html

### 문서 (16개)
platform-core/ 3개, platform-grammar/ 7개, engines/watch/ 1개, launch/ 5개

### 코드 버전
evaluator v1.3, governance v1.1, repeated v1.1, stability v1.1, incident API v1.1, scheduler v1.7, document activation v1.2, document API v3, identity core v2, cron_manager v2

---

## 환경변수 (Railway)

| 변수 | 상태 |
|------|:---:|
| SUPABASE_URL/KEY | ✅ |
| TELEGRAM_BOT_TOKEN | ✅ |
| TELEGRAM_CHAT_ID | ✅ |
| GOTENBERG_URL | ✅ |
| INTERNAL_API_SECRET | ✅ |
| SYNTHETIC_* (3개) | ❌ NOT_SET |
| PLAYWRIGHT_* (2개) | ❌ NOT_SET |

---

## Railway 배포 상태

- 배포: ✅ SUCCESS (2026-05-16 18:57 KST)
- Health: `degraded` (law_engine, fix_chat — Watch 무관)
- API: ✅ 전체 정상
- **Scheduler: ⚠️ 수동 reload 필요** (`POST /cron/reload`)
  - 원인: lifespan에서 start_scheduler() 실패 추정
  - 해결: cron_manager v2에서 reload 시 scheduler.start() 포함
