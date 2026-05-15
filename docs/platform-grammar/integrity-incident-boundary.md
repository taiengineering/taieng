# Integrity ↔ Incident Boundary

## Integrity (무결성)
- **정의**: Event/Flow의 정합성 판단
- **저장**: `engine_integrity_event`
- **책임**: "무엇이 잘못되었는가" 탐지
- **생성**: Integrity Evaluator (자동)
- **규칙**: `flow_integrity_rule_registry`
- **이벤트 유형**: field_mismatch, sequence_violation, stuck_detected, timeout_exceeded, sla_warning, sla_critical

**Integrity는 탐지한다. 대응하지 않는다.**

## Incident (인시던트)
- **정의**: 운영 대응이 필요한 이슈
- **책임**: "무엇을 먼저 봐야 하는가" 판단
- **우선순위**: P1~P4 (Priority Engine)
- **반복탐지**: repeated_failure, workflow_instability
- **위험도**: Workflow Risk Score

**Incident는 판단한다. 실행하지 않는다.**

## 경계 규칙
- Integrity ≠ Incident: Integrity는 탐지, Incident는 운영 판단
- Integrity event가 쌓이면 Incident가 될 수 있음
- 모든 Incident의 근거는 Integrity event
- Incident는 Integrity를 집계/분석한 운영 레이어
