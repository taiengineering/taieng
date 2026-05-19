# Runtime Activation Contract v1.0

Standard contract for activating candidates into runtime objects.

## RuntimeActivationRequest

```
activation_mode: manual | automatic | conditional | delegated
assignment_strategy: user | team | facility | auto_routing
schedule_strategy: periodic | one_time | deadline | none
escalation_policy: standard | strict | none
runtime_policy: default | custom
governance_policy: passive | standard | strict | critical
capability_scope: [list of required capabilities]
```

## activation_mode

| mode | 설명 | 사용 예시 |
|------|------|----------|
| manual | 안전관리자가 직접 확정 | Safe 점검항목관리 |
| automatic | 조건 충족 시 자동 활성화 | 알림/복구 작업 |
| conditional | 조건부 자동 | 규정 충족 시 |
| delegated | 외부 시스템에 위임 | API 기반 활성화 |

## assignment_strategy

| strategy | 설명 |
|----------|------|
| user | 특정 사용자 지정 |
| team | 팀 단위 배정 |
| facility | 사업장 담당자 자동 |
| auto_routing | 우선순위/부하 기반 자동 |

## Contract Rules

1. activation MUST produce exactly 1 runtime_task
2. schedule is optional (based on schedule_strategy)
3. document/evidence requirements are migrated from candidate
4. activation MUST emit runtime.candidate_activated event
5. activation MUST update candidate status to "activated"
6. activation MUST NOT modify engine truth
