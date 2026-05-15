# Watch Engine Resource Map

**TASK 01 산출물 | 2026-05-15**

---

## 1. 현재 상태 요약

| 테이블 | 행수 | 마지막 활동 | 판정 |
|--------|------|-------------|------|
| cron_job_master | 16 | 2026-04-20 | ✅ ALIVE — 16개 작업 정의 |
| cron_job_log | 4,964 | 2026-04-27 | ✅ ALIVE — 주력 운영 로그 |
| cron_schedule_config | 7 | 2026-03-30 | ⚠️ STALE — updated_at 갱신 안 됨 |
| health_checks | 0 | — | ❌ DEAD — 스키마만 존재 |
| health_alerts | 0 | — | ❌ DEAD — 스키마만 존재 |
| engine_integrity_event | 0 | — | ❌ DEAD — 스키마만 존재 |
| golden_scenario_registry | 50 | 2026-05-13 | ✅ ALIVE — 6개 도메인, 50개 시나리오 |
| regression_execution_log | 0 | — | ❌ DEAD — 실행 기록 없음 |
| internal_api_registry | 21 | 2026-03-30 | ⚠️ STATIC — 1회 적재 후 미갱신 |
| monitoring_config | 9 | 2026-04-20 | ⚠️ STATIC — 설정값 보관용 |

---

## 2. 구조별 상세 분석

### 2.1 CRON 클러스터 (ALIVE)

**cron_job_master** → **cron_schedule_config** → **cron_job_log**

FK 연결: `cron_job_log.job_id → cron_job_master.id`, `cron_schedule_config.job_id → cron_job_master.id`

**운영 현황:**

| job_code | 카테고리 | is_active(master) | 총 실행 | 성공률 | 마지막 실행 | 위험 |
|----------|----------|-------------------|---------|--------|-------------|------|
| SYSTEM_HEALTH_CHECK | SYSTEM | ✅ | 4,607 | 76.6% | 04-27 | ⚠️ 1,058 FAILED + 19 RUNNING stuck |
| REPORT_DAILY | REPORT | ✅ | 32 | 78.1% | 04-26 | ⚠️ 7 FAILED |
| DUE_ALERT_DAILY | SYSTEM | ✅ | 25 | 100% | 04-26 | — |
| EDU_EXPIRE_DAILY | education | ✅ | 32 | 100% | 04-26 | — |
| LAW_UPDATE_CHECK | LAW | ❌ master | 31 | 100% | 04-26 | 정상 비활성화 |
| DB_STATS_COLLECT | SYSTEM | ✅ | 32 | 78.1% | 04-26 | ⚠️ 7 FAILED |
| PRECEDENT_COLLECT_WEEKLY | — | ✅ | 3 | 100% | 04-20 | — |
| OVERDUE_DISPATCH | SAFETY | ❌ | 182 | 34.6% | 04-21 | 🔴 118 FAILED + 1 RUNNING stuck |
| OVERDUE_PREPARE | SAFETY | ❌ | 5 | 0% | 04-20 | 🔴 100% 실패 |
| LAW_COLLECT_MISSING | LAW | ❌ | 4 | 0% | 04-26 | 🔴 100% 실패 |
| RULE_REPARSE | LAW | ❌ | 8 | 0% | 04-22 | 🔴 100% 실패 |
| KCSC_SYNC | DATA | ✅ | 1 | 0% | 03-31 | 🔴 유일 실행 FAILED |
| LAW_RECOLLECT_15D | LAW | ❌ | 2 | 100% | 04-15 | — |
| AUTO_PARSE_NEW | LAW | ❌ | 0 | — | — | 미실행 |

**발견된 위험:**
- `cron_schedule_config` 7행 모두 `is_enabled=true`지만 `cron_job_master`에서 6개는 `is_active=false` → **master/config 불일치**
- `cron_schedule_config.next_run_at` 전부 NULL → 스케줄러가 이 테이블을 갱신하지 않음
- `cron_schedule_config.updated_at` 전부 2026-03-30 (최초 생성일) → **사실상 사용되지 않는 중복 구조**
- `cron_job_log`에 `status='RUNNING'` 19건 stuck (SYSTEM_HEALTH_CHECK 19, OVERDUE_DISPATCH 1)

**구조 판정:**
- `cron_job_master` + `cron_job_log` = **재사용 가능.** Watch Engine의 "작업 실행 이벤트" 로그로 변환 가능
- `cron_schedule_config` = **DEAD 중복.** `cron_job_master`에 이미 `cron_expression`, `is_active` 존재. 이 테이블의 `is_enabled`, `last_run_at`, `last_status`는 `cron_job_master`로 병합하거나 `cron_job_log`에서 조회 가능

### 2.2 HEALTH 클러스터 (DEAD)

**health_checks** / **health_alerts** — 0행. 스키마 설계는 "서버 alive 여부 + SMS 알림" 패턴.

`health_checks` 필드: status, total_ms, fail_count, warn_count, probe_count, probes(jsonb)
`health_alerts` 필드: status, failed_probes, message_ko, alert_type

**판정:** 코드에서 `SYSTEM_HEALTH_CHECK` cron이 `/health` 엔드포인트를 호출하고 있으나, 결과를 `cron_job_log`에만 기록하고 `health_checks` 테이블에는 적재하지 않는 것으로 보임. 기능 중복.

**재사용 가능성:** health_checks 스키마 자체는 "probe 기반 상태 점검" 패턴으로, Watch Engine의 heartbeat/probe 이벤트 저장소로 변환 가능. 단, 현재 스키마에는 `tenant_id`, `flow_key`, `trace_id` 등 표준 이벤트 필드가 없음.

### 2.3 ENGINE INTEGRITY 클러스터 (DEAD but DESIGNED)

**engine_integrity_event** — 0행. 스키마는 완전함:
- `event_type`, `severity`, `domain`, `description`, `detail(jsonb)`, `input_hash`, `source_trace`
- `resolved`, `resolved_at`, `resolved_by` — 해결 추적까지 포함

**판정:** 스키마가 Watch Engine의 "Integrity Event" 표준과 가장 근접. `tenant_id`, `flow_key`, `step_key`, `trace_id` 필드만 추가하면 표준 이벤트 스키마로 확장 가능.

**재사용 우선순위:** ★★★★★ (최우선 재사용 대상)

### 2.4 GOLDEN SCENARIO + REGRESSION 클러스터 (PARTIALLY ALIVE)

**golden_scenario_registry** — 50행, 6개 도메인 (FIRE, ELECTRICAL, INDUSTRIAL, GAS, HAZARDOUS 등)
- 법령진단 regression 용도로 설계
- `input_payload`, `expected_obligations/documents/checklists/evidence` — 입출력 쌍 보유
- `supported_status` 필드로 미지원 영역 표시

**regression_execution_log** — 0행. `golden_scenario_registry`의 실행 결과를 기록하도록 설계되었으나 한 번도 실행되지 않음.
- `total_scenarios`, `passed_count`, `failed_count`, `critical_failures`, `result_summary(jsonb)`

**판정:** 법령엔진 전용 구조이나, "Golden Scenario → 실행 → 결과 비교" 패턴 자체는 범용 Synthetic Scenario에 직결. Flow DSL 기반 시나리오로 확장 가능.

**재사용 우선순위:** ★★★★☆ (TASK 05 Synthetic Scenario에 직결)

### 2.5 STATIC REGISTRIES (REUSABLE AS-IS)

**internal_api_registry** — 21개 엔드포인트 등록. 7개 그룹(가격/기반/사용자/시설/업체/엔진/점검).
- Admin 모니터 페이지에서 동적 로드용
- Watch Engine에서 "어떤 API를 감시할 것인가"의 카탈로그로 그대로 재사용 가능

**monitoring_config** — 9개 설정값 (alert_email, api_url, infra 정보 등). 알림 발송 설정으로 재사용.

---

## 3. 인접 감시/감사 구조 (Watch Engine 통합 대상 여부)

| 테이블 | 행수 | 용도 | 통합 여부 |
|--------|------|------|-----------|
| verification_log | 1,638 | 법령엔진 v3.0 단계별 검증 | ❌ 법령엔진 전용, 분리 유지 |
| track_issue_log | 8,224 | Track A~E 검증 실패 이슈 | ❌ 법령엔진 전용, 분리 유지 |
| compliance_audit_log | 20 | 컴플라이언스 감사 | ⚠️ 향후 Watch Engine 이벤트로 표준화 가능 |
| audit_logs | 0 | 범용 데이터 변경 감사 | ❌ DEAD, 현재 미사용 |
| auto_qa_checks/log/pending | 0/0/0 | 자동 QA | ❌ DEAD, 전체 미사용 |
| runtime_*_audit | 대부분 0 | Runtime 단계별 감사 | ❌ Runtime 도메인 전용, 분리 유지 |

---

## 4. 위험 요소

1. **cron_schedule_config ↔ cron_job_master 불일치:** `is_enabled=true`인데 `is_active=false`인 작업 6개. 어느 쪽이 진실인지 불명확
2. **RUNNING stuck 로그 20건:** 완료 콜백이 실패한 좀비 프로세스 가능성
3. **health_checks 완전 미사용:** SYSTEM_HEALTH_CHECK cron이 4,607회 실행되었으나 health_checks 테이블은 0행 → 코드에서 이 테이블을 쓰지 않는 것이 확인됨
4. **regression 미실행:** golden_scenario_registry에 50개 시나리오가 등록되어 있으나 한 번도 regression이 실행되지 않음
5. **OVERDUE 완전 실패:** OVERDUE_PREPARE 100% 실패, OVERDUE_DISPATCH 65% 실패 → 알림 파이프라인 장애

---

## 5. 재사용 가능 자산 (우선순위 순)

| 순위 | 자산 | Watch Engine 역할 | 필요 작업 |
|------|------|-------------------|-----------|
| 1 | engine_integrity_event | **Standard Event 저장소** 원형 | tenant_id/flow_key/step_key/trace_id 추가 |
| 2 | cron_job_master + cron_job_log | **작업 실행 이벤트 소스** | flow_key 태깅, Standard Event emit 연결 |
| 3 | golden_scenario_registry | **Synthetic Scenario 카탈로그** | Flow DSL 기반으로 구조 확장 |
| 4 | internal_api_registry | **감시 대상 API 카탈로그** | flow_key 매핑 추가 |
| 5 | monitoring_config | **알림 설정** | 그대로 재사용 |

---

## 6. 수정 필요 사항

1. `cron_schedule_config` — **폐기 또는 병합.** `cron_job_master`와 중복. 의사결정 필요
2. `health_checks` / `health_alerts` — **빈 테이블 유지 or 스키마 변환.** Standard Event로 대체할 경우 삭제 가능
3. `cron_job_log`의 stuck RUNNING 레코드 — 정리 필요 (finished_at NULL + 24시간 경과 → TIMEOUT 처리)
4. `regression_execution_log` — golden_scenario_registry와 연결하여 실행 파이프라인 구축 필요

---

## 7. 제안 구조

```
[기존 자산 재사용 구조]

cron_job_master (작업 정의)
       │
       ├── cron_job_log (실행 기록) ──→ emitEvent() ──→ engine_integrity_event (확장)
       │                                                      │
       │                                                      ▼
       │                                              [Standard Event Store]
       │                                              (tenant_id, flow_key,
       │                                               step_key, trace_id,
       │                                               event_type, result,
       │                                               severity, payload_summary)
       │
       ├── golden_scenario_registry ──→ regression_execution_log
       │   (Synthetic Scenario 정의)     (실행 결과)
       │
internal_api_registry ──→ [감시 대상 카탈로그]
       │
monitoring_config ──→ [알림 설정]

폐기 대상:
  - cron_schedule_config (중복)
  - health_checks (미사용)
  - health_alerts (미사용)
```

**핵심 원칙 확인:** 새 테이블 생성 전에 `engine_integrity_event`를 Standard Event 기반으로 확장하는 것이 최우선. 이 테이블이 Watch Engine의 중앙 이벤트 저장소 역할을 수행.