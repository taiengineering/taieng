# WP-FRONT-01 — API CONTRACT AUDIT

- frontend baseline: `tai-admin@0a61fe5e`
- backend baseline: `tai-api@27970b61facc73cadd84d8e445f78b1939925c91`
- 판정: 프론트 호출을 추정하지 않고 tai-api 라우터 직독으로 대조

## 판정 범례
- CONFIRMED: 백엔드 라우터/필드 실재, 프론트 계약과 일치
- PARTIAL: 라우터는 있으나 일부 필드/응답 형태 미검증
- INFERRED→CONFIRMED: 프론트 주석이 "추정"이라 표기했으나 백엔드 직독 결과 실재
- MISSING: 프론트가 부르나 백엔드에 없음
- UNUSED: 백엔드에 있으나 프론트가 안 부름

## 1. 핵심 반전 — "추정" 계약은 실재했다

work-schedule-list는 코드 주석에서 아래 3개를 "추정(백엔드 확정 전)"이라 명시했으나, `routers/work_schedules.py v1.2.7` 직독 결과 **전부 실재**:

| 프론트 계약 | 백엔드 실측 | 판정 |
|---|---|---|
| `GET /work-schedules?factory_id=&status_code=&obligation_type=&keyword=&page=&size=` | GET `""` — factory_id/status_code/source_type/obligation_type/is_assigned/planned_date_from/planned_date_to/keyword/page/size(le=500) 전부 선언 | **CONFIRMED** |
| `PATCH /work-schedules/{id} {assigned_user_id}` | SchedulePatchBody: assigned_user_id + 별칭 assignee_id, status_code + 별칭 status, is_excluded, excluded_reason, custom_cycle, resolved_at, planned_date | **CONFIRMED** |
| `POST /work-schedules/bulk-assign {ids, assigned_user_id}` | BulkAssignBody: ids[], assigned_user_id/assignee_id | **CONFIRMED** |

추가 사실:
- 백엔드가 화면 별칭(`assignee_id → assigned_user_id`, `status → status_code`) 흡수 → 프론트 필드명 불확정성 방어됨.
- 백엔드 주석이 프론트 화면 LEDGER 번호(㈡㈨㈝)를 추적 → 백엔드가 프론트 요구에 맞춰 이미 구현됨.
- `_apply_one_update`가 assignment INSERT 시 parent work_schedules.factory_id를 PRE-READ, 실패 시 409 fail-closed (WP-04C writer LIVE).
- company_scope guard(v1.2.7): scoped_filter(company_id+factory_id), FACTORY role은 자기 factory만 → **프론트에서 factory 격리 재구현 불필요**.

## 2. flow별 계약 판정

### 점검(my-inspection) — 원본 이식, CONFIRMED
- `GET /inspection/status/{factoryId}` — CONFIRMED (inspection_schedule.py LIVE)
- `GET /inspection-sets?factory_id=&source=LEGAL_ENGINE` (폴백 `/inspection-sets/factory/{id}`) — CONFIRMED (inspection_sets.py LIVE)
- `GET /inspection/schedules/{factoryId}?month=&status_code=` — CONFIRMED
- `POST /inspection/start/{wid} {inspector_name}` — CONFIRMED
- `POST /inspection/complete/{wid} {completed_at, summary}` — CONFIRMED

### 기준일(inspection-anchor) — CONFIRMED
- `PATCH /inspection-sets/anchor/bulk {items:[...]}` — CONFIRMED (inspection_sets.py)

### 캘린더(inspection-calendar)
- `GET /work-schedules?planned_date_from=&planned_date_to=&factory_id=&obligation_type=&size=100` — CONFIRMED
- `GET /inspection-sets/factory-preview?factory_id=&months=2` (또는 `/preview-schedule`) — PARTIAL (preview 응답 형태 미검증)
- `PATCH /work-schedules/{id} {status_code:'COMPLETED'}` — CONFIRMED 경로, **값 drift(P0-A)**

### 설비(my-equipment, equipment-qr-manager)
- `GET /equipment-assets?factory_id=&page=&size=` — CONFIRMED (equipment_assets.py LIVE)
- `POST/GET /equipment-checkins` — **UNUSED** (백엔드 LIVE, 프론트 미호출) → flow H GAP

### 담당자(work-schedule Panel, safety-dashboard)
- `GET /users?factory_id=&size=200` — CONFIRMED (users.py LIVE)

### 작업자(worker-list)
- `GET /worker-registry?...` — CONFIRMED (worker_registry.py LIVE)
- `GET /construction/sites/{id}/workers` — CONFIRMED (construction_sites/workflow_router.py)
- `/departments`, `/teams`, `/groups` — PARTIAL (org.py 추정, 직독 미완)

### 문서(document-forms)
- `GET /document-forms?per_page=200`, `GET /document-forms/{id}` — CONFIRMED (document_forms.py)
- `POST /document-engine/documents` — CONFIRMED (document_engine_api.py)
- `PATCH /document-engine/documents/{docId}` — CONFIRMED
- `POST /document-engine/documents/{docId}/generate` — CONFIRMED

### 서식 카탈로그(engine-document)
- `GET /engine/forms/summary`, `GET /engine/forms?form_type=LEGAL|STANDARD|FREE` — PARTIAL (engine_document.py 추정)
- `GET /engine/forms/{code}/download` — PARTIAL

### 대시보드(safety-dashboard)
- `GET /work-schedules?factory_id=&size=500&active_yn=true` — CONFIRMED
- `GET /overdue/summary`, `/overdue/history`, `POST /overdue/urge/{id}` — PARTIAL (overdue_checker.py LIVE, 필드 미검증)
- `GET /weather/now`, `/weather/work-stop-criteria` — PARTIAL (weather.py LIVE)

## 3. UNUSED 백엔드 능력 (프론트 미소비)

`document_engine_api.py`의 runtime document lifecycle 대부분이 프론트에서 소비되지 않음:
- `GET /document-engine/documents` (횡단 목록) — UNUSED
- `POST /document-engine/documents/{id}/status` (SUBMITTED_FOR_REVIEW / APPROVED_BY_HUMAN) — UNUSED
- `GET /document-engine/transitions` — UNUSED
- `POST/GET /document-engine/documents/{id}/evidence` — UNUSED
- `GET /document-engine/documents/{id}/audit-log` — UNUSED
- `GET /document-engine/metrics`, `/metrics/factory/{id}` — UNUSED

→ NEW 후보(Runtime Document 관리/검토)의 근거. §NEW_DEVELOPMENT_GAPS 참조.

`equipment_checkins.py`의 `GET /equipment-checkins` (관리자 이력) — UNUSED → equipment-qr-manager 확장(MODIFY-L) 근거.

## 4. MISSING

**MISSING = 0건** (확인된 범위 내). 단, 범위를 정확히 한정한다:

- **implementation 확정 대상(P0/NEW/MODIFY-L)이 의존하는 required API는 전부 LIVE로 직독 확인됨** — work_schedules(GET/PATCH/bulk-assign), users, inspection/*, inspection-sets/*, document-engine/*, equipment-checkins, equipment-assets, worker-registry.
- **PARTIAL로 표기된 계약은 라우터 존재만 확인했고 필드/응답 형태 검증이 잔존한다** — inspection-sets/factory-preview(preview 응답), engine/forms/*(카탈로그), overdue/*, weather/*, departments|teams|groups. 이들은 구현 착수 전 개별 검증 필요.
- 따라서 "모든 API가 LIVE"라는 포괄 단정은 하지 않는다. **정확히는: 확정 대상 required API는 LIVE, PARTIAL 계약은 별도 검증 잔존.**

## 5. status vocabulary drift (P0)

백엔드 canonical(work_schedules.status_code): `planned / scheduled / in_progress / completed` (소문자). `DONE`/`SCHEDULED` 등 대문자·구값은 READ 호환용.

프론트 write/계산 drift:
- **P0-A** inspection-calendar: `PATCH {status_code:'COMPLETED'}` write. 백엔드 PATCH는 normalize 없이 payload 전달 → DB에 'COMPLETED' 기록.
- **P0-B** work-schedule-list: filteredItems `case 'overdue'`에 `status_code !== 'DONE'` → canonical 'completed' 오분류(1곳).
- **P0-C** safety-dashboard: raw `status_code !== 'DONE'` **8 expressions** = statistics 4(statD0/statD3/statMonth/statUnassigned) + filteredSchedules branches 4(d0/d3/month/unassigned) → 완료 일정이 미완료로 오계산.

표시(statusBadge/STATUS_OPTIONS/statusLabels.ts)는 이미 canonical 정본. 계산/write만 drift. 해결은 statusLabels.ts에 canonical-aware 완료판정 헬퍼 공통화(신규 엔진 아님).
