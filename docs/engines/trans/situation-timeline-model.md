# Situation Timeline Model

## 목적

Situation의 시간 흐름을 표현하는 모델.
Event Timeline이 아닌 **Situation Timeline**.

## Event Timeline vs Situation Timeline

| 구분 | Event Timeline | Situation Timeline |
|------|----------------|-------------------|
| 단위 | 개별 이벤트 | 운영 상황 |
| 표현 | workflow.failed | "결제 흐름 안정성 저하" |
| 대상 | 개발자 | 운영자 |
| 목적 | 디버깅 | 운영 상황 인지 |

## Timeline Entry 구조

```json
{
  "situation_id": "sit_20260519_001",
  "timestamp": "2026-05-19T14:30:00Z",
  "status": "active",
  "priority": "P1",
  "trend": "degrading",
  "title": "결제 흐름 안정성 저하",
  "delta": {
    "priority_changed": true,
    "trend_changed": false,
    "status_changed": true
  }
}
```

## Timeline 흐름 예시

```
14:00  emerging   P3  stable     "응답 지연 감지"
14:15  active     P2  degrading  "실패 흐름 증가"
14:25  escalating P1  degrading  "결제 흐름 안정성 저하"
14:45  active     P2  stable     "실패 감소 중"
15:10  stabilizing P3 improving  "상황 안정화 중"
15:30  resolved   P4  improving  "문제 해결됨"
```

## delta 필드

이전 Snapshot 대비 변경된 항목을 표시.
UI에서 변경 포인트를 강조할 때 사용.

## 현재 제한

이 모델은 문서 정의만. 실제 DB 테이블/Scheduler는 미구현.
