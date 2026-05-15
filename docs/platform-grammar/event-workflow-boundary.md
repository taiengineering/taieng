# Event ↔ Workflow Boundary

## Event (이벤트)
- **정의**: 업무 흐름의 단일 행위 기록
- **저장**: `business_event` 테이블
- **책임**: 사실 기록 (판단 없음)
- **생성**: `emit_event()` SDK
- **소비**: Integrity Evaluator, SLA Evaluator

**Event는 판단하지 않는다. 기록만 한다.**

## Workflow (워크플로우)
- **정의**: Step 순서로 구성된 업무 흐름
- **저장**: `flow_registry` + `flow_step_registry`
- **책임**: 흐름 정의 (실행 아님)
- **소비**: Evaluator가 flow 정의를 참조하여 event를 평가

**Workflow는 실행하지 않는다. 기준을 제공한다.**

## Trace (트레이스)
- **정의**: 하나의 Flow 실행 인스턴스
- **식별**: `trace_id`
- **생명주기**: create_trace() → emit_event()들 → flow_status 계산

## 경계 규칙
- Event ≠ Workflow: Event는 기록, Workflow는 구조
- Trace ≠ Flow: Trace는 실행, Flow는 정의
- Step ≠ Event: Step은 정의, Event는 발생
