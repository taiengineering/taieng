# Watch Engine v1.1 — 전체 작업내역 + 이슈사항

작성일: 2026-05-15

---

## 완료 TASK 목록

### TASK 01: Watch Engine Resource Mapping
- 기존 Supabase 모니터링 테이블 8개 분석
- ALIVE: cron_job_master(16행), cron_job_log(4,964행), golden_scenario_registry(50행)
- DEAD: health_checks, health_alerts, engine_integrity_event(0행), regression_execution_log(0행)
- 핵심 발견: engine_integrity_event = Standard Event와 가장 근접, 최우선 재사용 대상

### TASK 02: Standard Event Schema + Trace/Flow + Flow Registry
- business_event 테이블 설계 (18컬럼)
- engine_integrity_event 10컬럼 확장
- trace_id / scenario_run_id / parent_trace_id 관계 정의
- flow_registry, flow_step_registry, flow_integrity_rule_registry, flow_scenario_binding 4개 테이블

### TASK 03: Migration SQL + Supabase 적용
- 멱등성(idempotent) SQL 작성
- FK 7건 / RLS 6건 보류 (운영 안정성 우선)
- Supabase migration 실제 적용 완료

### TASK 04: emitEvent SDK
- watch_engine/ 5개 파일: emitter.py, trace.py, validation.py, pii.py, types.py
- Fail-safe: 전체 try/except, 예외 swallow → return False
- PII 30개 blacklist

### TASK 05: 핵심 3개 Flow에 emit_event 삽입
- routers/auth.py (login), factory_process_v3.py (process_registration), anonymous_diagnosis.py (law_diagnosis)
- Cursor 작업 → 커밋 5aa4382
- 테스트 데이터 22행 + synthetic 7행 적재

### TASK 06: Integrity Rule Engine v1
- 4개 rule: field_mismatch, sequence_violation, stuck_detected, timeout_exceeded
- watch_engine/integrity/ 디렉토리 구조
- engine_integrity_event CHECK constraint 확장 (legacy 10종 + Watch Engine 10종)
- Dedupe: (trace_id, event_type, step_key) 기준
- 8건 integrity event 생성 검증

### TASK 06-1: Flow Completion + False Positive Suppression
- flow_step_registry에 is_terminal_success, is_terminal_failure 컬럼 추가
- flow_status 5종: completed, failed, running, stuck, abandoned
- Suppression: failed flow → sequence_violation + stuck_detected suppress
- 결과: 8건 → 6건 active + 2건 suppressed

### TASK 06-2: Scheduler 연결
- watch_engine_api.py → /watch-engine/evaluate 엔드포인트
- cron_job_master에 INTEGRITY_EVALUATE 등록 (*/5, direct://)

### TASK 06-3: Scheduler Direct Integration
- scheduler.py v1.1 → HTTP self-call 제거, direct:// convention
- evaluate_recent_events() direct import call
- cron_job_log status: SUCCESS/WARNING/FAILED 3단계

### TASK 07: Synthetic Scenario v1
- watch_engine/synthetic/ 구조: runner.py + scenarios/login.py + process_registration.py
- actor_type = synthetic_user, scenario_run_id 자동 생성
- Scheduler: SYNTHETIC_LOGIN(5분), SYNTHETIC_PROCESS_REG(15분)

### TASK 07-1: Synthetic Isolation + Cleanup
- 3중 격리: actor_type, payload_summary.synthetic, process_name
- Retention: business_event 7일, service_data 24시간
- Scheduler: SYNTHETIC_CLEANUP (매일 3시, direct://)

### TASK 08: Founder Cockpit
- watch_engine_api.py — 5개 Cockpit API 엔드포인트 (health, issues, synthetic, scheduler, top-failures)
- admin/full-version/html/horizontal-menu-template/watch-engine.html 생성

### TASK 08-1: Issue Workflow
- engine_integrity_event에 6개 컬럼 추가 (acknowledged, ignored, operator_note 등)
- API 4개: ACK, RESOLVE, IGNORE, NOTE
- issues 필터: active/acknowledged/resolved/ignored
- Cockpit UI에 확인/해결/무시 버튼 + 필터 탭

### TASK 09: Alert Engine
- alert_rule_registry + alert_history 테이블
- Alert Engine: rule matching + cooldown/dedupe + Telegram 발송
- watch_engine_alert_api.py — CRUD, mute/unmute, history, test
- Scheduler: ALERT_EVALUATE (5분, direct://)

### TASK 09-2: Alert Settings UI
- Cockpit에 알림 규칙 설정 + 알림 이력 + Telegram 테스트 통합
- UI에서 enabled 토글, threshold/cooldown 수정, 무음/해제 가능

---

## 현재 DB 현황

| 테이블 | 행수 | 역할 |
|--------|:---:|------|
| business_event | 29 | 업무 이벤트 (22 운영 + 7 synthetic) |
| engine_integrity_event | 8 | 무결성 판단 (4 active, 1 ack, 3 resolved, 1 ignored) |
| flow_registry | 3 | flow 정의 (login, process_registration, law_diagnosis) |
| flow_step_registry | 11 | step 정의 |
| flow_integrity_rule_registry | 5 | 무결성 규칙 |
| alert_rule_registry | 4 | 알림 규칙 |
| alert_history | 1 | 알림 발송 이력 |

## Scheduler 현황 (5개 direct job)

| job_code | 주기 | 방식 |
|----------|------|------|
| INTEGRITY_EVALUATE | */5 * * * * | direct://integrity_evaluate |
| ALERT_EVALUATE | */5 * * * * | direct://alert_evaluate |
| SYNTHETIC_LOGIN | */5 * * * * | direct://synthetic_login |
| SYNTHETIC_PROCESS_REG | */15 * * * * | direct://synthetic_process_reg |
| SYNTHETIC_CLEANUP | 0 3 * * * | direct://synthetic_cleanup |

---

## 이슈사항

### P0 (배포 전 필수)

1. **Railway 환경변수 미설정**
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — Telegram 알림 불가
   - `SYNTHETIC_TEST_EMAIL`, `SYNTHETIC_TEST_PASSWORD`, `SYNTHETIC_FACTORY_ID` — Synthetic heartbeat 불가
   - 미설정 시 기능 skip, 서비스 영향 없음

2. **본인인증 미완료로 실제 로그인 테스트 불가**
   - Synthetic login이 실제 API를 호출하지만, 본인인증 세팅 전까지 실패할 수 있음
   - 테스트 데이터로 검증 완료, 실제 API 검증은 본인인증 완료 후

3. **잘못 올린 파일 삭제 필요 (tai-admin)**
   - `tadmin/full-version/html/admin/watch-engine.html` — 사용하지 않음, 삭제 필요
   - `admin/full-version/html/watch-engine.html` — horizontal-menu-template 밖, 삭제 필요

### P1 (배포 후 확인)

4. **Railway 배포 후 APScheduler 동작 확인 필요**
   - `load_jobs_from_db()` 시 5개 direct:// job이 정상 등록되는지
   - scheduler.py v1.4 첫 배포

5. **db.database vs db.supabase_client import 경로**
   - scheduler.py는 `db.database.get_supabase` 사용
   - watch_engine은 `db.supabase_client.get_supabase` 사용
   - 동일 함수인지 확인 필요 (다르면 import 통일)

6. **factory_process 테이블명 확인**
   - Synthetic cleanup에서 `factory_process` 테이블 참조
   - 실제 테이블명이 다를 수 있음 (실패해도 warning만 기록)

7. **CORS 확인**
   - admin.taieng.co.kr → api.taieng.co.kr 요청 시 CORS 설정 확인
   - 기존 engine-monitoring과 동일하면 이미 설정됨

### P2 (운영 안정화)

8. **Synthetic 전용 사업장 생성 권장**
   - `SYNTHETIC_FACTORY_ID`를 운영 사업장이 아닌 전용 사업장으로 설정
   - 운영 데이터 오염 방지

9. **alert_rule_registry 초기 threshold 조정**
   - 운영 데이터 축적 후 threshold/cooldown 값 최적화 필요
   - Cockpit UI에서 조정 가능

10. **INTERNAL_API_SECRET 로테이션**
    - 세션 중 노출 이력 있음, 로테이션 권장

---

## 전체 아키텍처 (최종)

```
[Service] → emit_event() → business_event
                               │
              ┌─── scheduler (5분) ───┐
              │                       │
     INTEGRITY_EVALUATE         SYNTHETIC_LOGIN/REG
              │                       │
     Integrity Evaluator        Synthetic Runner
     flow_status + 4 rules      실제 API 호출
     false positive suppression  heartbeat 확인
              │                       │
     engine_integrity_event     business_event
              │
     ALERT_EVALUATE (5분)
              │
     Alert Engine
     rule matching + cooldown
     dedupe + mute 확인
              │
     Telegram 발송
     alert_history 기록
              │
     Founder Cockpit (60초 polling)
     ├── 건강 요약 (활성이슈/CRITICAL/Synthetic/Evaluator)
     ├── 스케줄러 | Synthetic Heartbeat
     ├── 실패 Top 플로우
     ├── 운영 이슈 (ACK/해결/무시 + 필터)
     └── 알림 설정 (토글/threshold/무음) | 알림 이력
```

## 커밋 이력 (tai-api)

| 커밋 | 내용 |
|------|------|
| 5aa4382 | feat: emit business events for login, process, diagnosis |
| 54fd195 | feat: Integrity Rule Engine v1 |
| 2a0c190 | feat: Flow Completion + False Positive Suppression |
| 57028419 | feat: Watch Engine API endpoint |
| c59b862 | feat: scheduler v1.1 — direct call |
| fc94cdd | feat: Synthetic Runner v1 |
| 25b1808 | feat: Synthetic Cleanup |
| 3d26fe2 | feat: scheduler v1.3 |
| ac52028 | feat: Cockpit API v1.1 — 5 sections |
| b61ddb8 | feat: Issue Workflow API |
| aab0079 | feat: Alert Engine v1 |
| ecd904c | feat: Alert Settings API |
| d17f76a | feat: scheduler v1.4 — ALERT_EVALUATE |
