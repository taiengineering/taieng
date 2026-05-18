# Situation Lifecycle

## 목적

Operational Situation의 생명주기를 정의.

## 중요

이것은:
- ❌ Truth Lifecycle가 아님
- ❌ Incident Lifecycle가 아님

이것은:
- ✅ **Human Operational Situation Lifecycle**

운영자가 인지하는 상황의 변화 흐름.

## 상태 정의

| 상태 | 설명 | 예시 |
|------|------|------|
| emerging | 이상 징후 감지 | timeout 증가 |
| active | 운영 영향 확인 | repeated failure 증가 |
| escalating | 심각도 상승 | critical escalation |
| stabilizing | 상황 안정화 중 | failure 감소 |
| resolved | 문제 해결 | recovery 완료 |

## 상태 전이

```
emerging → active → escalating
                 ↓
              stabilizing → resolved
```

- emerging → active: 실패/영향 확인되면
- active → escalating: severity 상승 / 영향 확대
- active/escalating → stabilizing: 실패 감소 / recovery 시작
- stabilizing → resolved: 복구 완료 / 정상 복귀
- stabilizing → active: 재악화

## 운영 표현

| 상태 | 운영 표현 |
|------|----------|
| emerging | 이상 감지 |
| active | 운영 영향 중 |
| escalating | 위험 증가 중 |
| stabilizing | 상황 안정화 중 |
| resolved | 문제 해결됨 |

## 판단 기준

- Situation Builder의 trend + priority + event 패턴으로 판단
- Trans Engine은 상태를 **설명**하지만 **결정**하지 않음
- 상태 결정은 향후 Situation Runtime 역할 (현재 미구현)

## 현재 단계

Lifecycle 정의만. DB/Scheduler/Runtime 구현 없음.
