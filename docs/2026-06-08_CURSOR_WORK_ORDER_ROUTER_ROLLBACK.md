# Cursor 작업 지시서 — 라우터 격리 롤백 (2026-06-08)

> 배경: `docs/2026-06-08_ROUTER_ORPHAN_RECLASSIFICATION_AND_PIVOT.md`
> 대상 repo: `taiengineering/tai-api`
> 현재: main fb4a88a 기준, `_archive/routers_20260608/`에 43개 격리(실삭제 0)

## 0. 목적
재감사 결과 격리한 43개 대부분이 "완성됐는데 미등록"인 기능으로 확인됨. 진짜 잔재만 `_archive`에 남기고 나머지를 `routers/`로 복원한다. **복원은 파일 위치만 되돌리는 것이며 router_registry 등록과 무관(미등록 상태 유지)하므로 런타임 라우팅에 영향 없음.**

## 1. 최종 분류 (확정)
### A. `_archive` 유지 = 진짜 제거 대상 (22개)
- 스텁(2): factory_process, factory_process_v2
- 이관완료 45cminc(19): watch_engine_api, watch_engine_alert_api, watch_engine_browser_api, watch_engine_control_api, watch_engine_document_api, watch_engine_governance_api, watch_engine_identity_api, watch_engine_incident_api, watch_engine_intelligence_api, watch_engine_memory_api, watch_engine_recovery_api, watch_engine_sla_api, semantic_adapter_api, production_guard_api, control_runtime_gateway_api, synthetic_control_api, calibration_api, trans_engine_api, browser_synthetic
- ROLLBACK 빈 파일(1): diagnosis_input_draft ← **현재 routers/에 있음. 이번에 _archive로 격리.**

### B. `routers/` 복원 대상 (22개)
oauth, auth_oauth, workers, alert_messages, areas, buildings, connect_provider, contacts, debug, emergency_report, feature_flags, fix_matching_api, industry, kin_generate, posts, process_management, roles, slack_kin, teams, uploads, workflow_integrity, tbm_issue

### C. 등록 검토 (이미 routers/, 미등록 — 이번 작업 대상 아님, 별도 트랙)
ksic_engine, law_viewer, documents, document_forms, document_schema, document_runtime, kosha_collect, inspection_templates, inspection_set_auto, pw_reset, safety_reports

## 2. 작업 절차
브랜치: `git checkout -b cleanup/router-rollback-20260608` → 작업 → PR

**STEP 1 — diagnosis_input_draft 격리**
- `git mv routers/diagnosis_input_draft.py _archive/routers_20260608/diagnosis_input_draft.py`

**STEP 2 — 22개 복원** (B 목록 전부)
- 각 파일 `git mv _archive/routers_20260608/{name}.py routers/{name}.py`

**STEP 3 — 커밋·배포·검증**
- commit → push → PR → 배포
- `/health` 200 확인
- `GET /` → MODULE_STATUS 10개 그룹 정상, degraded/failed 없음 (복원·격리 모두 미등록 대상이라 변화 없어야 정상)
- `POST /cron/reload` 200
- 인증·진단 각 1회 스모크
- 503/degraded 시 즉시 직전 커밋 revert 후 STOP 보고

## 3. 주의
- **A 목록(22개)은 절대 복원하지 말 것.** 특히 watch_engine_* 19개는 45cminc 이관 완료분.
- C 목록(등록 검토 11개)은 이번 작업에서 **건드리지 말 것.** routers/에 그대로 둔다.
- 복원 후 B 목록은 여전히 **미등록 상태**다. 등록(router_registry 추가)은 이번 작업에 포함하지 않는다.

## 4. 금지
- A 목록 복원 금지 / C 목록 변경 금지
- router_registry 등록 변경 금지 (이번은 파일 위치 복원만)
- git rm(실삭제) 금지 / main 직접 push 금지 / railway CLI 금지

## 5. 후속 (별도 지시 예정)
- B 복원분 + C 미등록분에 대해 "기능별 등록 / 중복 폐기" 결정.
- 중복 택일: oauth·auth_oauth(↔auth.py), workers(↔worker_registry).
- 등록 우선: ksic_engine, safety_reports, inspection_templates, documents/document_forms/document_schema.
- debug: 프로덕션 등록 비권장(개발용).
- document_* 4종: document_engine(isolated) 정책 확인 후 등록.
