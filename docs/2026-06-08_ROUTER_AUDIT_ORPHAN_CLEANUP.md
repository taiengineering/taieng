# 라우터 전수검사 및 잔재 정리 — 2026-06-08

## 1. 검사 범위
- repo: `taiengineering/tai-api` (main)
- `router_registry/` 10개 그룹 파일 전수
- `routers/` 약 205개 `.py` 파일과 대조

## 2. 등록 구조 (권위 출처)
- `main.py` v6.0.0 → `router_registry/__init__.py`의 `load_module_group()`이 각 그룹의 `ROUTERS` 리스트를 `importlib`로 로드.
- **실제 로딩되는 라우터 = 각 그룹 파일 `ROUTERS`에 등록된 `module` 경로뿐.**
- 활성 등록 라우터 약 150개.

## 3. 핵심 발견
- `routers/` 파일 ~205개 중 **약 55개가 어느 그룹에도 등록되지 않음(orphan).**
- ⚠️ **미등록 ≠ 死코드.** 라우터 등록은 안 됐어도 다른 모듈이 `import`해서 쓰는 헬퍼/서비스가 섞여 있음 (`_messaging_compat`, `matching_deps`, `_rule_gen_prompts`, `health`, `ksic_engine` 등). 등록 여부만 보고 삭제 금지 → 반드시 import 참조 검사 선행.

## 4. 그룹별 활성 등록 목록
- **saas_core (8):** auth, users, companies, factories, system_codes, notifications, fcm, onboarding
- **diagnosis (13):** diagnosis, diagnosis_engine, diagnosis_integrated, diagnosis_autofill, diagnosis_fields, diagnosis_report, diagnosis_proposal, diagnosis_roi, diagnosis_transform, diagnosis_plan_recommend, diagnosis_result_web, diagnosis_runtime_projection, saas_setup
- **legal_engine (19, isolated):** legal_engine, legal_engine_patch, engine_qa, law_rule_generator, engine_legal, byulpyo, compiler_core, residual_intelligence, legal_intake, legal_diff, deterministic_qa, engine_publish, integrity_monitor, engine_monitoring, runtime_activation, runtime_chaos, persistence_api, runtime_evaluator_api, simulation_api / (law_collector 주석 — import 오류로 비활성)
- **document_engine (7, isolated):** document_engine, document_engine_api, engine_document, report_forms, document_monitoring, requirement_engine, diagram_proxy
- **runtime_bridge (21):** legacy_freeze, runtime_bridge, inspection_bridge, obligation_bridge, my_inspection_bridge, notification_bridge, notification_engine_api, notification_inbox_api, notification_preference_api, notification_wiring_api, notification_digest_api, workflow_alert_api, workflow_engine_api, review_bridge, evidence_bridge, submission_bridge, runtime_task_api, runtime_schedule_api, legal_adapter_api, runtime_cockpit_api, runtime_candidate_api
- **inspection (12):** inspection_sets, inspection_schedule, inspection_checklist, inspection_setup, work_schedules, schedule_engine, schedule_pipeline, overdue_checker, safety_template, corrective_actions, factory_process_v3, legal_status_api
- **payment (13):** payment, payment_test, payment_ops, payment_billing, contracts, contracts_engine, quotes, price_setting, price_master_admin, product_pricing, price_policy, connection_commission, settlements
- **public (11):** public, site_public(+admin_router), public_admin, public_pricing, anonymous_diagnosis, connect_registration, admin_connect, admin_pricing, internal_inbox, admin_inquiries, inicis_auth
- **construction (17):** construction, subcontractors, tbm, tbm_templates, safety_meetings, risk_assessments, worker_registry, worker_check, worker_home, equipment_assets, equipment_checkins, engine_equipment, engine_model, education, education_assign, personnel, safety_info
- **external (37 활성):** weather, juso, building_register, biz_verify, kosha_apis, messaging, fcm, mail, ai_copywrite, event_trigger, repair, fix_chat, fix_providers_api, matching, matching_commission, experts, identity, identity_test, agent_service, admin_review, admin_stats, cron_manager, internal_api_registry, report_api_registry, fire_hazmat, precedent_api, contract_kmong, pricing_validation_api, payment_activation_api, feedback_api, situation_dashboard_api, attention_dashboard_api, situation_detail_api, situation_history_api, response_guidance_api, operational_learning_api, operational_closure_api

## 5. 미등록(orphan) 분류

### A. 버전 중복 잔재 — "진짜가 뭔지 모름"의 직접 원인 (최우선)
- `factory_process.py`(202B 스텁) + `factory_process_v2.py`(205B 스텁) → 현역은 `factory_process_v3`
- `oauth.py` + `auth_oauth.py` → 둘 다 미등록, 현역 인증은 `auth.py`
- `workers.py` → 현역은 `worker_registry.py`

### B. Watch Engine 계열 19개 — 이관 완료(45cminc), external.py에 전부 주석 → 가장 안전한 삭제 후보
watch_engine_api, watch_engine_alert_api, watch_engine_browser_api, watch_engine_sla_api, watch_engine_incident_api, watch_engine_recovery_api, watch_engine_governance_api, watch_engine_identity_api, watch_engine_control_api, watch_engine_document_api, watch_engine_intelligence_api, watch_engine_memory_api, semantic_adapter_api, production_guard_api, control_runtime_gateway_api, synthetic_control_api, calibration_api, trans_engine_api, browser_synthetic

### C. 기타 미등록 orphan (~30) — import 참조 검사 필요
alert_messages, areas, buildings, connect_provider, contacts, debug, diagnosis_input_draft, document_forms, document_runtime, document_schema, documents, emergency_report, feature_flags, fix_matching_api, industry, inspection_set_auto, inspection_templates, kin_generate, kosha_collect, ksic_engine, law_viewer, posts, process_management, pw_reset, roles, safety_reports, slack_kin, tbm_issue, teams, uploads, workflow_integrity

### D. GPT 도메인 — 보류 (GPT 확인 후 결정)
legal_engine_v510, law_collector, law_collector_admrul, law_catalog_collector

### E. 헬퍼/특수 — 삭제 금지 (라우터 아님)
_messaging_compat, _rule_gen_prompts, matching_deps, health(추정: main 직접 등록)

### F. 기타 이상
- `fcm`이 saas_core·external **양쪽 그룹에 중복 등록** → 한쪽 제거 필요

## 6. 정리 순서 원칙
1. 진단 → 격리(등록 해제) → 배포 → /health 200 & 동작 확인 → 삭제
2. `legal_engine`·`document_engine` (isolated) 등록 모듈은 제외
3. 모든 변경 전 main 브랜치 SHA 확인
4. 권장 순서: B(이관완료) → A(버전 스텁) → import 검사 통과한 C → F(fcm 중복)

## 7. import 참조 검사 결과
(아래 섹션에 추가 예정)
