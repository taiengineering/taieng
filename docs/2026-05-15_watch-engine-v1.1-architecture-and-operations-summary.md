# TAI Watch Engine v1.1
## 서비스 관제 엔진 — 철학 / 설계 / 작업내역 / 이슈 정리

작성일: 2026-05-15
프로젝트: 45cm / TAI Platform
상태: 운영형 MVP 완료

---

# 1. 프로젝트 배경

TAI 프로젝트는 단순 SaaS 제작이 아니라,
AI 시대의 업무 운영 플랫폼(Operational Platform)을 목표로 한다.

프로젝트 진행 중 실제 운영 이슈가 발생했다.

대표 사례:

```text
SelectBar 값 mismatch
submit: KCSC
read: kcsc
```

겉보기에는 API 성공 및 DB 저장 성공처럼 보였으나,
실제 업무 데이터는 변형되어 있었다.

이 경험을 통해 아래 문제를 확인했다.

- 일반 로그 시스템은 “업무 실패”를 잡지 못함
- API 200 OK는 실제 정상 운영을 의미하지 않음
- LLM 검수만으로 silent corruption 탐지 불가능
- 사용자가 먼저 발견하는 구조는 SaaS 운영에서 치명적

따라서 TAI는:

```text
인프라 감시
→ 업무 흐름 무결성 감시
```

방향으로 전환.

---

# 2. 핵심 철학

## 2.1 서비스 정상 ≠ 업무 정상

기존 모니터링:

- CPU
- Memory
- Error rate
- API latency

중심.

TAI Watch Engine은:

```text
“업무가 정상적으로 끝났는가”
```

를 감시.

---

## 2.2 로그 수집이 아닌 업무 의미 판단

목표:

```text
로그 저장 ❌
업무 흐름 무결성 판단 ✅
```

핵심:

- submit ↔ read 비교
- flow completion
- stuck detection
- field mismatch
- sequence validation

---

## 2.3 핵심 business flow 중심 감시

전체 코드 감시가 아니라:

- login
- process_registration
- diagnosis
- approval
- payment

같은 핵심 흐름 중심.

철학:

```text
적게 감시하지만 정확하게
```

---

## 2.4 Founder 운영 중심

Watch Engine은 DevOps 툴이 아니라:

```text
Founder Operations System
```

을 목표로 함.

따라서:

- DB 직접 수정 운영 지양
- UI 기반 제어
- Noise 최소화
- 중요한 것만 표시
- Alert 폭탄 방지

를 핵심 원칙으로 설정.

---

# 3. 아키텍처 개요

## 전체 흐름

```text
Synthetic Runner
    ↓
emit_event()
    ↓
business_event
    ↓
Integrity Evaluator
    ↓
engine_integrity_event
    ↓
Alert Engine
    ↓
Founder Cockpit
```

---

# 4. 핵심 구성요소

# 4.1 business_event

실제 업무 이벤트 저장.

예:

- submit
- validate
- save
- read
- render
- timeout
- error

핵심 필드:

- tenant_id
- service_key
- flow_key
- step_key
- trace_id
- scenario_run_id
- actor_type
- connector_type
- result
- payload_summary
- payload_hash

특징:

- PII 저장 금지
- payload_summary만 허용
- trace 기반 흐름 연결
- SaaS 종속 제거

---

# 4.2 engine_integrity_event

무결성 판단 결과 저장.

역할:

```text
“무슨 일이 일어났는가”
→ business_event

“그것이 정상인가”
→ engine_integrity_event
```

---

# 4.3 Flow Registry

업무 흐름 메타 관리.

구성:

## flow_registry

- flow_key
- parent_flow_key
- stuck_threshold_ms
- expected_step_count

## flow_step_registry

- step_key
- step_order
- timeout_ms
- is_required
- payload_schema

## flow_integrity_rule_registry

- rule_type
- evaluation_timing
- operator
- severity
- integrity_status

---

# 4.4 Integrity Evaluator

Watch Engine 핵심 판단 엔진.

v1 Rule:

1. field_mismatch
2. sequence_violation
3. stuck_detected
4. timeout_exceeded

---

# 4.5 Synthetic Scenario

업무 heartbeat.

구성:

## login synthetic

- submit_credentials
- validate_auth
- session_issued

## process_registration synthetic

- submit_payload
- validate
- save_db
- read_result

---

# 4.6 Founder Cockpit

경로:

```text
admin.taieng.co.kr/html/horizontal-menu-template/watch-engine.html
```

구성:

1. System Health Summary
2. Active Integrity Issues
3. Synthetic Heartbeat
4. Scheduler Status
5. Top Failing Flows
6. Alert Settings
7. Alert History
8. Telegram Test

---

# 4.7 Alert Engine

목표:

```text
“진짜 위험한 것만 알림”
```

초기 Rule:

1. CRITICAL stuck_detected
2. repeated field_mismatch
3. synthetic_failure
4. evaluator_failure

구현:

- alert_rule_registry
- alert_history
- cooldown
- dedupe
- mute/unmute
- Telegram notify

---

# 5. 현재 Coverage 상태

| Flow | Coverage | Synthetic | Integrity | Alert |
|---|---|---|---|---|
| login | 100% | ✅ | ✅ | ✅ |
| process_registration | 100% | ✅ | ✅ | ✅ |
| diagnosis | 부분 | 부분 | 부분 | 부분 |
| payment | 0% | ❌ | ❌ | ❌ |
| approval | 0% | ❌ | ❌ | ❌ |

---

# 6. 주요 성과

## 6.1 Silent Corruption 탐지 성공

실제 사례:

```text
KCSC ↔ kcsc
```

field_mismatch 자동 탐지 성공.

---

## 6.2 False Positive Suppression

정상 실패 종료와 실제 stuck flow를 구분.

결과:

- false positive 감소
- alert noise 감소
- 운영 신뢰성 증가

---

## 6.3 Founder 운영 최적화

운영 목표:

- DB 직접 수정 제거
- UI 중심 운영
- Noise 최소화
- 빠른 의사결정

---

# 7. 현재 남은 이슈

## Railway 실운영 검증

- APScheduler
- Telegram delivery
- direct scheduler execution

## Coverage 확대

추가 필요:

- approval
- payment
- export
- file upload

## Alert 품질 조정

- threshold
- cooldown
- false positive
- noise

---

# 8. 플랫폼 관점 의미

Watch Engine은:

```text
Business Flow Integrity Platform
```

으로 정의.

단순 서버 모니터링이 아니라:

- business flow
- operational memory
- proactive heartbeat
- founder operation

을 핵심으로 함.

---

# 9. 45cm 프로젝트 내 위치

현재 Watch Engine은:

```text
플랫폼 공통 운영 커널
```

역할 수행.

향후:

- Workflow Engine
- Permission Engine
- Rule Engine
- Audit Engine
- Notification Engine

과 공통 규약 공유 예정.

---

# 10. 최종 정리

현재 Watch Engine은:

```text
에러 감시 시스템
```

이 아니라:

```text
Business Flow Integrity Platform
```

초기 운영형 수준.

그리고 45cm 프로젝트의 핵심 방향은:

```text
기능 개발
→ 반복 가능한 운영 구조 자산화
```

이다.
