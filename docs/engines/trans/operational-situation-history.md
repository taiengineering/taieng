# Operational Situation History

## 목적

Situation의 시간 흐름을 추적하여 "상황이 어떻게 변했는가"를 파악할 수 있는 기반 구조 정의.

## Situation Snapshot 구조

```json
{
  "situation_id": "sit_20260519_001",
  "title": "결제 흐름 안정성 저하",
  "summary": "최근 실패와 응답 지연이 함께 증가하고 있습니다.",
  "priority": "P1",
  "trend": "degrading",
  "impact": "일부 사용자 영향 가능",
  "storyline": [
    "최근 응답 지연이 증가했습니다.",
    "이후 실패 흐름이 반복 발생하기 시작했습니다.",
    "현재 일부 사용자가 작업을 완료하지 못하고 있습니다.",
    "결제 API 상태를 우선 확인하세요."
  ],
  "recommended_focus": [
    "결제 로그 확인",
    "PG사 상태 확인"
  ],
  "status": "active",
  "confidence": 0.82,
  "event_count": 20,
  "generated_at": "2026-05-19T14:30:00Z"
}
```

## 필드 정의

| 필드 | 타입 | 설명 |
|------|------|------|
| situation_id | string | 고유 식별자 |
| title | string | 상황 제목 |
| summary | string | 상황 요약 |
| priority | string | P1~P4 |
| trend | string | improving/stable/degrading/accelerating |
| impact | string | 영향 범위 |
| storyline | list[str] | 흐름 설명 |
| recommended_focus | list[str] | 우선 확인사항 |
| status | string | 상황 상태 (Lifecycle) |
| confidence | float | 신뢰도 |
| event_count | int | 입력 이벤트 수 |
| generated_at | datetime | 생성 시점 |

## 이력 활용 목적

- 상황 변화 추이 파악
- 운영 보고서 기반 데이터
- Situation Timeline UI 데이터 소스
- 운영 품질 측정 기반

## 현재 단계 제한

- DB 저장 구현 없음 (문서 정의만)
- Scheduler 저장 없음
- Situation Runtime 생성 없음

History Foundation 정의 단계.
