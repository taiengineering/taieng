# Trace / Flow Relationship Spec

**TASK 02-1 산출물 | 2026-05-15**

---

## 1. ID 체계

```
scenario_run_id        하나의 테스트/검증 실행 단위 (여러 flow 묶음)
  └── trace_id         하나의 독립 업무 흐름 (1 flow = 1 trace)
       └── step_key    흐름 내 개별 단계 (step_order로 순서 보장)
```

| ID | 범위 | 생성 시점 | 생존 범위 |
|----|------|-----------|-----------|
| scenario_run_id | N개 flow 묶음 | synthetic/regression 실행 시 1회 | 테스트 세션 전체 |
| trace_id | 1개 독립 flow | flow 시작 시 1회 | flow 완료까지 |
| parent_trace_id | 선행 flow 참조 | 후속 flow 시작 시 선행 trace_id 복사 | 후속 flow에만 존재 |
| session_id | 사용자 세션 | 로그인 시 1회 | 세션 만료까지 |

---

## 2. trace_id 생성 규칙

### 원칙: 1 독립 업무 흐름 = 1 trace_id

**독립 흐름의 정의:** 사용자 또는 시스템이 하나의 비즈니스 목적을 달성하기 위해 시작부터 완료까지 수행하는 단계들의 연속.

### 생성 형식

```
{flow_key}_{uuid7_short}

예:
login_01JXR3K9M7
process_registration_01JXR3KBN2
diagnosis_01JXR3KD5P
```

- UUID v7 기반 (시간순 정렬 가능)
- flow_key prefix로 로그 읽기 용이
- 12자 short form (충돌 방지 충분)

### 생성 주체별 규칙

| 주체 | 생성 방식 | 예시 |
|------|-----------|------|
| 실제 사용자 행동 | Thin Agent가 flow 시작 감지 시 자동 생성 | 사용자가 공정등록 화면 진입 → trace 시작 |
| synthetic test | 테스트 러너가 flow 시작 전 명시 생성 | Playwright가 로그인 flow 시작 전 생성 |
| scheduler/cron | cron 실행 시 자동 생성 | SYSTEM_HEALTH_CHECK 실행 → trace 시작 |
| webhook | 수신 시 자동 생성 | 외부 콜백 수신 → trace 시작 |

### trace_id 불변 원칙

- 한번 생성된 trace_id는 flow 내 모든 step에서 동일하게 사용
- flow 중간에 trace_id를 변경하지 않음
- retry도 같은 trace_id 유지 (step_key로 구분)

---

## 3. scenario_run_id 생성 규칙

### 원칙: 1 테스트 실행 = 1 scenario_run_id

### 생성 형식

```
{run_type}_{YYYYMMDD}_{sequence}

예:
synthetic_20260515_001      ← synthetic test 1회 실행
regression_20260515_001     ← regression test 1회 실행
smoke_20260515_001          ← smoke test 1회 실행
```

### 사용 범위

| 상황 | scenario_run_id | 설명 |
|------|-----------------|------|
| synthetic test | 필수 | 테스트 실행 묶음 |
| regression test | 필수 | golden scenario 검증 묶음 |
| 실제 사용자 행동 | NULL | 테스트가 아닌 실제 운영 |
| cron/scheduler | NULL | 운영 스케줄 실행 |
| smoke test | 필수 | 배포 후 빠른 검증 |

### scenario_run_id → trace_id 관계

```
scenario_run_id: regression_20260515_001
  │
  ├── trace_id: login_01JXR3K9M7
  │     flow_key: login
  │     step 0~3
  │
  ├── trace_id: process_registration_01JXR3KBN2
  │     flow_key: process_registration
  │     parent_trace_id: login_01JXR3K9M7
  │     step 0~6
  │
  └── trace_id: diagnosis_01JXR3KD5P
        flow_key: diagnosis
        parent_trace_id: null  (독립)
        step 0~3
```

---

## 4. parent_trace_id 사용 규칙

### 원칙: 선행 flow가 필수 전제조건인 경우에만 사용

### 사용 기준

| 조건 | parent_trace_id | 이유 |
|------|-----------------|------|
| 로그인 → 공정등록 | login의 trace_id | 인증 없이 등록 불가 |
| 로그인 → 대시보드 조회 | login의 trace_id | 인증 필요 |
| 법령진단 (비회원) | NULL | 로그인 불필요 |
| 법령진단 (회원) | login의 trace_id | 인증 필요 |
| cron 작업 | NULL | 독립 실행 |
| webhook 수신 | NULL 또는 원본 flow의 trace_id | 비동기 후속이면 연결 |

### 연결 깊이 제한

- **최대 3단계:** trace → parent → grandparent
- 이유: 깊은 체이닝은 디버깅 복잡도만 증가
- 3단계 초과 시 scenario_run_id로 묶어서 관리

### 원인 추적 방향

```
후속 flow 실패 시:

process_registration FAILED
  → parent_trace_id = login_01JXR3K9M7
    → login flow의 마지막 step 확인
      → result = success → 원인은 registration 자체
      → result = failure → 원인은 인증 실패
```

---

## 5. flow_key / step_key / step_order 규칙

### 5.1 flow_key 네이밍 규칙

```
형식: {domain}_{action}  (snake_case)
```

| 규칙 | 예시 | 반례 |
|------|------|------|
| snake_case 필수 | process_registration | processRegistration ❌ |
| 영문 소문자만 | login | Login ❌ |
| 동사 또는 명사_동사 | diagnosis_submit | 진단제출 ❌ |
| 서비스 종속 금지 | payment_process | tai_payment ❌ |
| 최대 3단어 | equipment_inspection_submit | equipment_safety_inspection_submit_form ❌ |

**현재 식별된 flow_key 목록:**

| flow_key | 설명 |
|----------|------|
| login | 로그인 |
| process_registration | 공정등록 |
| diagnosis_submit | 법령진단 실행 |
| diagnosis_purchase | 진단 결제 |
| equipment_register | 설비 등록 |
| inspection_execute | 점검 실행 |
| payment_process | 결제 처리 |
| report_generate | 보고서 생성 |
| schedule_generate | 일정 자동생성 |
| health_check | 시스템 헬스체크 |
| cron_execute | cron 작업 실행 |
| notification_dispatch | 알림 발송 |

### 5.2 step_key 네이밍 규칙

```
형식: {verb}_{object}  (snake_case)
```

| 규칙 | 예시 | 반례 |
|------|------|------|
| 동사_목적어 | submit_form | form ❌ (동사 없음) |
| flow_key 반복 금지 | validate_input | process_registration_validate ❌ |
| 범용 용어 사용 | save_db | insert_into_factory_process ❌ |

**표준 step_key 카탈로그:**

| step_key | connector_type | 설명 |
|----------|---------------|------|
| open_form | browser | 화면/폼 진입 |
| load_data | api/database | 초기 데이터 로드 |
| select_option | browser | 선택 입력 |
| input_field | browser | 필드 입력 |
| submit_form | browser/api | 폼 제출 |
| validate_input | api | 서버 검증 |
| save_db | database | DB 저장 |
| read_result | api/database | 저장 결과 조회 |
| render_result | browser | 결과 화면 렌더 |
| dispatch_notification | queue | 알림 발송 |
| generate_output | api | 산출물 생성 (보고서/PDF 등) |
| complete_flow | api | 흐름 완료 확인 |

### 5.3 step_order 규칙

| 규칙 | 설명 |
|------|------|
| 0-based | 첫 step = 0 |
| 연속 정수 | 0, 1, 2, 3... (건너뛰기 금지) |
| retry = 같은 step_order | retry 시 동일 step_order로 재기록, event_type으로 구분 |
| optional step = 포함하되 result로 구분 | optional step은 step_order 부여하되 result = 'skipped' 허용 |
| 분기(branch) = 같은 step_order + 다른 step_key | 분기점에서 선택된 경로만 success, 나머지 skipped |

### 5.4 특수 상황 처리

**Retry:**
```
step_order 2: submit_form → result: failure   (1차 시도)
step_order 2: submit_form → result: failure   (2차 시도)
step_order 2: submit_form → result: success   (3차 시도)

→ 같은 trace_id, 같은 step_order, 같은 step_key
→ created_at으로 시도 순서 구분
→ 3개 business_event 행 생성
```

**Optional Step:**
```
step_order 3: upload_attachment → result: skipped  (첨부 없음)
step_order 4: save_db → result: success

→ skipped step도 기록하여 흐름 완전성 유지
```

**Branch (분기):**
```
step_order 2: select_sector_building → result: success  (선택됨)
step_order 2: select_sector_industrial → result: skipped (선택 안 됨)
step_order 2: select_sector_construction → result: skipped

→ 같은 step_order, 다른 step_key
→ success인 것만 후속 step에 영향
```

---

## 6. business_event → engine_integrity_event 연결 방식

### 6.1 연결 메커니즘

```
[Watch Engine]
     │
     │  1. trace_id 기준으로 business_event 그룹 조회
     │  2. flow_key에 등록된 integrity rule 적용
     │  3. 판단 결과 → engine_integrity_event 기록
     │
     ├── 단일 이벤트 판단: source_event_id = 해당 event.id
     │
     └── 복수 이벤트 비교 판단: source_event_id = 마지막 관련 event.id
                               detail.compared_events = [event_id_1, event_id_2]
```

### 6.2 source_event_id 사용 기준

| 판단 유형 | source_event_id | detail 내용 |
|-----------|-----------------|-------------|
| 단일 이벤트 기반 (payload_missing, timeout) | 해당 event.id | 해당 이벤트 정보 |
| 복수 이벤트 비교 (field_mismatch, db_mismatch) | 마지막 event.id | compared_events: [id1, id2] |
| 흐름 전체 기반 (stuck, sequence_violation) | NULL | trace_id로 전체 흐름 참조 |
| 외부 비교 (regression_detected) | NULL | scenario_run_id + golden_scenario_id |

---

## 7. Integrity 판단별 필요한 이벤트 조합

### 7.1 판단 유형 → 필요 이벤트 매트릭스

| 판단 유형 | 필요 이벤트 | 비교 방식 | 판단 로직 |
|-----------|------------|-----------|-----------|
| **payload_missing** | submit_form (1건) | 단일 이벤트 | payload_summary에서 required_field_exists = false |
| **field_mismatch** | submit_form + read_result (2건) | 같은 trace 내 2개 step 비교 | submit의 payload_summary vs read의 payload_summary 값 비교 |
| **db_mismatch** | save_db + read_result (2건) | 같은 trace 내 2개 step 비교 | save의 payload_hash vs read의 payload_hash 불일치 |
| **stuck_detected** | 마지막 기록된 event (1건) | 시간 기반 | flow의 마지막 event 이후 기대 시간 초과 + 다음 step 미도착 |
| **timeout_exceeded** | 임의 step (1건) | 단일 이벤트 | event의 created_at 간격이 임계값 초과 |
| **regression_detected** | flow 전체 + golden_scenario (N건) | 현재 실행 vs golden 기대값 | 현재 result set과 expected_* 비교 |
| **sequence_violation** | flow 전체 (N건) | 같은 trace 내 step_order 검사 | step_order 순서 역전 또는 필수 step 누락 |
| **orphan_event** | 단일 event (1건) | trace 소속 확인 | trace_id에 해당하는 flow 정의 없음, 또는 step_key가 flow에 미등록 |
| **schema_drift** | save_db (1건) | payload 구조 비교 | payload_summary의 key 구조가 이전 실행과 다름 |
| **health_degraded** | heartbeat 이벤트 (N건) | 시계열 | 연속 N회 failure 또는 응답시간 증가 추세 |

### 7.2 판단 시점

| 시점 | 대상 판단 유형 | 트리거 |
|------|---------------|--------|
| **실시간 (step 단위)** | payload_missing, timeout_exceeded | 개별 event 도착 시 |
| **flow 완료 후** | field_mismatch, db_mismatch, sequence_violation, orphan_event | trace의 마지막 step 도착 시 |
| **주기적 (cron)** | stuck_detected, health_degraded | 1분~10분 주기 |
| **테스트 실행 후** | regression_detected | scenario_run 완료 시 |
| **스키마 변경 감지** | schema_drift | save_db 이벤트의 payload 구조 변경 시 |

---

## 8. 예시 3개

### 8.1 로그인 Flow

```
flow_key: login
actor_type: user
connector_type: browser → api → database

trace_id: login_01JXR3K9M7
parent_trace_id: null
scenario_run_id: null (실제 운영) 또는 regression_20260515_001 (테스트)

┌─────────────────────────────────────────────────────────────────────────┐
│ step │ step_key      │ event_type │ connector │ result  │ 비고        │
│ 0    │ open_form     │ submit     │ browser   │ success │ 로그인 화면 │
│ 1    │ submit_form   │ submit     │ browser   │ success │ ID/PW 제출  │
│ 2    │ validate_auth │ validate   │ api       │ success │ 인증 검증   │
│ 3    │ read_result   │ read       │ api       │ success │ 토큰 발급   │
└─────────────────────────────────────────────────────────────────────────┘

payload_summary 예시 (step 1):
{
    "has_username": true,
    "has_password": true,
    "login_method": "email"
}

가능한 integrity 판단:
- payload_missing: step 1에서 has_username = false
- timeout_exceeded: step 2 응답 5초 초과
- stuck_detected: step 2 이후 step 3 미도착 (30초 이상)
```

### 8.2 공정등록 Flow

```
flow_key: process_registration
actor_type: user
connector_type: browser → api → database → api → browser

trace_id: process_registration_01JXR3KBN2
parent_trace_id: login_01JXR3K9M7
scenario_run_id: null (운영) 또는 regression_20260515_001 (테스트)

┌──────────────────────────────────────────────────────────────────────────────┐
│ step │ step_key            │ event_type │ connector │ result  │ 비고         │
│ 0    │ open_form           │ submit     │ browser   │ success │ 등록 화면    │
│ 1    │ load_data           │ read       │ api       │ success │ 공정목록 로드│
│ 2    │ select_process_type │ submit     │ browser   │ success │ 공정유형 선택│
│ 3    │ input_field         │ submit     │ browser   │ success │ 상세정보 입력│
│ 4    │ submit_form         │ submit     │ api       │ success │ 서버 전송    │
│ 5    │ validate_input      │ validate   │ api       │ success │ 서버 검증    │
│ 6    │ save_db             │ save       │ database  │ success │ DB 저장      │
│ 7    │ read_result         │ read       │ api       │ success │ 저장값 조회  │
│ 8    │ render_result       │ render     │ browser   │ success │ 결과 표시    │
└──────────────────────────────────────────────────────────────────────────────┘

payload_summary 예시 (step 4, submit_form):
{
    "process_type": "PRESS",
    "field_count": 8,
    "has_equipment_link": true,
    "required_field_exists": true
}

payload_summary 예시 (step 7, read_result):
{
    "process_type": "PRESS",
    "row_count": 1,
    "required_field_exists": true
}

가능한 integrity 판단:
- payload_missing: step 4에서 required_field_exists = false
- field_mismatch: step 4 process_type = "PRESS" vs step 7 process_type = "press" (대소문자)
- db_mismatch: step 6 payload_hash ≠ step 7 payload_hash
- sequence_violation: step 6(save_db) 없이 step 7(read_result) 도착
- stuck_detected: step 6 이후 step 7 미도착 (60초 이상)
- regression_detected: golden scenario에서 기대 step 수 = 9인데 8개만 도착
```

### 8.3 법령진단 Flow

```
flow_key: diagnosis_submit
actor_type: user (회원) 또는 system (비회원 자동)
connector_type: browser → api → database → api → browser

trace_id: diagnosis_submit_01JXR3KD5P
parent_trace_id: login_01JXR3K9M7 (회원) 또는 null (비회원)
scenario_run_id: null (운영) 또는 regression_20260515_001 (테스트)

┌──────────────────────────────────────────────────────────────────────────────────┐
│ step │ step_key             │ event_type │ connector │ result  │ 비고            │
│ 0    │ open_form            │ submit     │ browser   │ success │ 진단 입력 화면  │
│ 1    │ select_sector        │ submit     │ browser   │ success │ 섹터 선택       │
│ 2    │ input_conditions     │ submit     │ browser   │ success │ 조건값 입력     │
│ 3    │ submit_form          │ submit     │ api       │ success │ 진단 요청       │
│ 4    │ validate_input       │ validate   │ api       │ success │ 조건값 검증     │
│ 5    │ evaluate_rules       │ validate   │ api       │ success │ 법령 룰 판정    │
│ 6    │ save_db              │ save       │ database  │ success │ 결과 저장       │
│ 7    │ generate_output      │ submit     │ api       │ success │ 보고서 생성     │
│ 8    │ read_result          │ read       │ api       │ success │ 결과 조회       │
│ 9    │ render_result        │ render     │ browser   │ success │ 결과 표시       │
└──────────────────────────────────────────────────────────────────────────────────┘

payload_summary 예시 (step 3, submit_form):
{
    "sector": "BUILDING",
    "tier": "STANDARD",
    "condition_count": 5,
    "required_field_exists": true,
    "has_area": true
}

payload_summary 예시 (step 5, evaluate_rules):
{
    "matched_rule_count": 23,
    "obligation_count": 15,
    "penalty_count": 8,
    "evaluation_ms": 340
}

가능한 integrity 판단:
- payload_missing: step 3에서 required_field_exists = false
- timeout_exceeded: step 5 evaluation_ms > 5000 (5초 초과)
- regression_detected: golden scenario 기대 obligation 23개인데 15개만 반환
- stuck_detected: step 5 이후 step 6 미도착 (120초 이상)
- sequence_violation: step 4(validate) 없이 step 5(evaluate) 도착
```

---

## 결론

### 1. Trace 구조 결론

- **1 독립 flow = 1 trace_id** (불변)
- trace_id 형식: `{flow_key}_{uuid7_short}`
- 선행 flow 필요 시 parent_trace_id로 연결 (최대 3단계)
- 테스트 묶음은 scenario_run_id (실 운영은 NULL)

### 2. Flow 구조 결론

- flow_key: `{domain}_{action}` snake_case, 최대 3단어
- step_key: `{verb}_{object}` snake_case, flow_key 반복 금지
- step_order: 0-based 연속 정수
- retry = 같은 step_order 재기록 (created_at으로 순서)
- optional = step_order 부여 + result: skipped
- branch = 같은 step_order + 다른 step_key

### 3. Event 연결 방식

- 단일 이벤트 판단: `source_event_id` = 해당 event.id
- 복수 이벤트 비교: `source_event_id` = 마지막 event.id + `detail.compared_events`
- 흐름 전체 판단: `source_event_id` = NULL, `trace_id`로 그룹 참조
- 외부 비교: `scenario_run_id` + golden_scenario 참조

### 4. Integrity 판단 방식

- **실시간 판단 (3종):** payload_missing, timeout_exceeded, orphan_event
- **flow 완료 후 판단 (4종):** field_mismatch, db_mismatch, sequence_violation, schema_drift
- **주기적 판단 (2종):** stuck_detected, health_degraded
- **테스트 후 판단 (1종):** regression_detected

### 5. 위험 요소

1. **trace_id 전파 누락:** 서비스 코드에서 trace_id를 전파하지 않으면 flow 연결 불가. emitEvent() Thin Agent가 이를 강제해야 함
2. **step_order 순서 보장:** 비동기 처리에서 step_order가 역전될 수 있음. created_at 기반 보조 정렬 필요
3. **payload_summary PII 유출:** 개발자가 실수로 PII를 payload_summary에 포함할 수 있음. emitEvent()에서 PII 필터링 필요
4. **retry 폭발:** retry 무한 루프 시 같은 step_order로 이벤트 폭발. retry 상한(max 5) 필요
5. **stuck 판단 오탐:** 네트워크 지연과 실제 stuck 구분 어려움. 임계값 설정이 flow별로 다를 수 있음
6. **golden scenario 유지보수:** 코드 변경 시 golden scenario도 갱신 필요. 방치 시 regression 오탐 폭발

### 6. 다음 구현 제안

| 순서 | 작업 | 도구 | 내용 |
|------|------|------|------|
| 1 | business_event 테이블 생성 | Supabase migration | TASK 02 SQL 실행 |
| 2 | engine_integrity_event ALTER | Supabase migration | TASK 02 SQL 실행 |
| 3 | Flow Registry 테이블 설계 | 설계 → migration | flow_key별 step 정의 저장 (Flow DSL 기반) |
| 4 | emitEvent() Python 함수 | Cursor (tai-api) | Thin Agent 코드 구현 |
| 5 | Process Registration Flow Mapping | 설계 (기획창) | TASK 03 실행 |
| 6 | Watch Engine 판단 로직 | Cursor (tai-api) | integrity rule 실행 코드 |