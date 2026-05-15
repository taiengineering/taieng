# TAI Watch Engine — Task Archive

작성일: 2026-05-15
프로젝트: 45cm / TAI Platform
목적: Watch Engine 개발 과정의 TASK 지시서 및 설계 흐름 보존

---

# TASK 01 — Existing Monitoring Structure Analysis

목표:
- 기존 monitoring/cron/integrity 자산 분석
- 재사용 가능한 구조 식별
- dead/stale 구조 제거 후보 식별

핵심 발견:
- cron_job_master / cron_job_log 재사용 가능
- engine_integrity_event가 Watch Engine 핵심 저장소로 확장 가능
- 기존 monitoring 구조는 일부 stale 상태

---

# TASK 02 — Standard Event Schema

목표:
- business_event 구조 정의
- Integrity Event 구조 정의
- Event ≠ Integrity 원칙 확립

핵심 철학:
- 행위와 판단 분리
- Event는 원자적 사건
- Integrity는 흐름 해석 결과

결과:
- business_event
- engine_integrity_event 확장
- trace_id 구조 도입

---

# TASK 02-1 — Trace / Flow Relationship

목표:
- trace_id / parent_trace_id 구조 정의
- workflow reconstruction 가능 구조 설계

핵심 개념:
- 1 workflow = 1 trace
- step_order 기반 흐름 복원
- scenario_run_id 기반 synthetic 연결

---

# TASK 02-2 — Flow Registry

목표:
- workflow registry 설계
- step registry 설계
- integrity rule registry 설계

핵심 철학:
- 감시는 명시적 registry 기반
- auto discovery 과도 확장 금지

결과:
- flow_registry
- flow_step_registry
- flow_integrity_rule_registry
- flow_scenario_binding

---

# TASK 03 — Migration Structure

목표:
- 실제 Supabase migration 구조 생성
- 기존 시스템 영향 없이 확장

핵심 원칙:
- idempotent migration
- nullable/default 기반 안전 확장
- 기존 cron/integrity 영향 최소화

---

# TASK 04 — emit_event SDK

목표:
- 서비스 공통 Event SDK 구현

결과:
- emitter.py
- trace.py
- pii.py
- validation.py
- types.py

핵심 철학:
- emit_event() 실패가 서비스 장애가 되면 안 됨
- fail-safe 최우선

---

# TASK 05 — Real Flow Integration

목표:
- login
- process_registration
- law_diagnosis

3개 실제 flow에 emit_event 삽입.

핵심 발견:
- SelectBar mismatch 재현 가능
- UI와 저장값 mismatch 탐지 가능

---

# TASK 06 — Integrity Evaluator

목표:
- field_mismatch
- sequence_violation
- stuck_detected
- timeout_exceeded

자동 판단 엔진 구현.

핵심 철학:
- Business Integrity 중심
- 단순 서버 health 아님

---

# TASK 06-1 — False Positive Suppression

목표:
- 정상 실패 flow와 실제 장애 구분

핵심 철학:
- Alert fatigue 최소화
- failed flow는 stuck로 보지 않음

결과:
- flow_status 개념 도입
- completed / failed / abandoned 분리

---

# TASK 06-2 — Scheduler Integration

목표:
- Integrity Evaluator scheduler 연결

핵심 구조:
- direct:// 방식 도입
- HTTP self-call 제거

핵심 철학:
- 운영 안정성 우선
- 내부 direct execution 유지

---

# TASK 07 — Synthetic Runner

목표:
- login synthetic
- process_registration synthetic

구현.

핵심 철학:
- 사람이 쓰기 전에 workflow 자동 검증

---

# TASK 07-1 — Synthetic Cleanup

목표:
- synthetic data retention
- synthetic 격리

핵심 구조:
- actor_type = synthetic_user
- synthetic marker 기반 cleanup

---

# TASK 08 — Founder Cockpit

목표:
- 운영자 Cockpit 구축

핵심 섹션:
- Health
- Active Issues
- Scheduler
- Synthetic
- Top Failures

핵심 철학:
- 운영 가시성
- Founder Operating System 방향

---

# TASK 08-1 — Issue Workflow

목표:
- ACK
- RESOLVE
- IGNORE
- NOTE

Issue lifecycle 구현.

핵심 철학:
- 운영 workflow 자체도 workflow

---

# TASK 08-2 — Alert Engine

목표:
- Alert Rule Engine 구축

구현:
- cooldown
- dedupe
- mute/unmute
- alert history

핵심 발견:
- Alert는 Notification Layer로 확장 가능

---

# TASK 09 — Browser Synthetic

목표:
- 실제 브라우저 기반 사용자 흐름 감시

핵심 발견:
- API 정상이어도 UI 장애 가능
- Business Workflow Observability 필요

결과:
- Playwright synthetic
- browser event_type
- browser integrity detection

---

# TASK 09-1 — Browser Coverage & Stabilization

목표:
- data-testid 규약
- Browser Coverage Registry
- Browser Synthetic Cockpit

핵심 철학:
- 무엇을 감시하는지 자체가 플랫폼 자산

---

# TASK 09-2 — Workflow SLA Layer

목표:
- Business Workflow SLA
- User Impact Layer

핵심 철학:
- 서버 metric이 아니라
- 업무 완료 품질 중심

예:
- login 3초 이상
- process_registration 60초 이상
- workflow stuck

---

# 플랫폼 핵심 철학 요약

## Event
플랫폼 공통 사건 언어

## Workflow
의미 있는 Event sequence

## Integrity
Workflow 정상성 판단

## Alert
운영 중요도로 승격된 Integrity/Event

## Notification
권한/역할 기반 운영 커뮤니케이션 레이어

## Synthetic
실제 사용자 흐름 자동 sensing

## SLA
업무 완료 품질 기준

---

# 중요한 방향성

현재 방향:

```text
Infra Observability Platform
```

이 아니라,

```text
Business Workflow Observability Platform
```

이다.

즉:
- CPU/RAM monitoring 중심이 아니라
- 업무 흐름 정상성 중심
- 실제 사용 가능성 중심
- Business Integrity 중심

구조를 유지한다.
