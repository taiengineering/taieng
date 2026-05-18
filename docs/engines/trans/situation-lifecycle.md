# Situation Lifecycle

## 목적

Operational Situation의 생명주기 정의.

## 중요

- ❌ Truth Lifecycle가 아님
- ❌ Incident Lifecycle가 아님
- ✅ **Human Operational Situation Lifecycle**

## 구현 상태 (T-05 완료)

- ✅ `_compute_lifecycle_status()` in `situation_snapshot_builder.py`
- ✅ DB `status` 컨럼에 저장
- ✅ Scheduler가 5분마다 상태 계산/저장

## 상태 정의

| 상태 | 운영 표현 | 판단 기준 |
|------|----------|----------|
| emerging | 이상 감지 | degradation/runtime.degraded 감지 |
| active | 운영 영향 중 | repeated_failure / .failed 이벤트 존재 |
| escalating | 위험 증가 중 | escalation 이벤트 또는 P1 우선순위 |
| stabilizing | 상황 안정화 중 | trend=improving |
| resolved | 문제 해결됨 | recovery.completed + trend=improving |

## 상태 전이

```
emerging → active → escalating
                 ↓
              stabilizing → resolved
```

## 계산 로직 (`_compute_lifecycle_status`)

```python
if recovery.completed + improving → resolved
if improving → stabilizing
if escalation or P1 → escalating
if repeated_failure or .failed → active
if degradation → emerging
default → emerging
```
