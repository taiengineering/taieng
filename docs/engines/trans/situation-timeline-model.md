# Situation Timeline Model

## 목적

Situation의 시간 흐름을 표현하는 모델.

## Event Timeline vs Situation Timeline

| 구분 | Event Timeline | Situation Timeline |
|------|----------------|-------------------|
| 단위 | 개별 이벤트 | 운영 상황 |
| 표현 | workflow.failed | "결제 흐름 안정성 저하" |
| 대상 | 개발자 | 운영자 |
| 목적 | 디버깅 | 운영 상황 인지 |

## 구현 상태 (T-05 완료)

- ✅ DB 저장: `operational_situation_snapshot` 테이블
- ✅ Timeline API: `GET /situation/timeline/{situation_id}`
- ✅ History API: `GET /situation/history/{situation_id}` (시간순)
- ✅ Cockpit S25 연동

## Timeline Entry

DB에서 조회 시 반환되는 구조:

```json
{
  "id": "uuid",
  "situation_id": "mock_flaky_01:payment:payment_attempt:degradation",
  "title": "결제 흐름 안정성 저하",
  "priority": "P1",
  "trend": "degrading",
  "status": "escalating",
  "confidence": 0.82,
  "event_count": 20,
  "environment": "production",
  "generated_at": "2026-05-19T14:30:00Z"
}
```

## Timeline 흐름 예시

```
14:00  emerging   P3  stable     "응답 지연 감지"
14:05  active     P2  degrading  "실패 흐름 증가"
14:10  escalating P1  degrading  "결제 흐름 안정성 저하"
14:15  active     P2  stable     "실패 감소 중"
14:20  stabilizing P3 improving  "상황 안정화 중"
14:25  resolved   P4  improving  "문제 해결됨"
```

5분 간격으로 스냅샷이 생성되어 자연스럽게 timeline을 형성.
