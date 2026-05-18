# Operational Situation History

## 목적

Situation의 시간 흐름을 추적하여 "상황이 어떻게 변했는가"를 파악한다.

## 구현 상태 (T-05 완료)

- ✅ DB 테이블: `operational_situation_snapshot`
- ✅ Snapshot Builder: `situation_snapshot_builder.py`
- ✅ Snapshot Store: `situation_snapshot_store.py`
- ✅ Scheduler: `SITUATION_SNAPSHOT_GENERATE` (5분 주기)
- ✅ API: `situation_history_api.py` (4개 엔드포인트)
- ✅ Cockpit S25 연동

## Situation Snapshot 구조

```json
{
  "id": "uuid",
  "situation_id": "{tenant}:{domain}:{flow}:{type}",
  "tenant_id": "mock_flaky_01",
  "title": "결제 흐름 안정성 저하",
  "summary": "최근 실패와 응답 지연이 함께 증가하고 있습니다.",
  "priority": "P1",
  "urgency": "즉시 확인 필요",
  "trend": "degrading",
  "impact": "일부 사용자 영향 가능",
  "storyline": [...],
  "recommended_focus": [...],
  "status": "active",
  "confidence": 0.82,
  "event_count": 20,
  "source_event_ids": [...],
  "generated_at": "2026-05-19T14:30:00Z",
  "environment": "production"
}
```

## DB 테이블

`public.operational_situation_snapshot`

| 컨럼 | 타입 | 설명 |
|------|------|------|
| id | uuid | PK |
| situation_id | text | {tenant}:{domain}:{flow}:{type} |
| tenant_id | text | 테넌트 |
| title | text | 상황 제목 |
| summary | text | 상황 요약 |
| priority | text | P1~P4 |
| urgency | text | 운영 긴급도 |
| trend | text | improving/stable/degrading/accelerating |
| impact | text | 영향 범위 |
| storyline | jsonb | 흐름 설명 |
| recommended_focus | jsonb | 우선 확인사항 |
| status | text | Lifecycle 상태 |
| confidence | numeric | 신뢰도 |
| event_count | integer | 입력 이벤트 수 |
| source_event_ids | jsonb | 원본 이벤트 ID |
| generated_at | timestamptz | 생성 시점 |
| environment | text | production / mock |
| created_at | timestamptz | 개례 생성일 |

RLS enabled + service_role full access.

## API

| Endpoint | 설명 |
|----------|------|
| GET /situation/recent | 최근 상황 |
| GET /situation/timeline/{sid} | 상황 timeline |
| GET /situation/detail/{id} | 특정 상황 |
| GET /situation/history/{sid} | lifecycle history |

## Scheduler

| Job | 주기 | Handler |
|-----|------|--------|
| SITUATION_SNAPSHOT_GENERATE | 5분 | direct://situation_snapshot_generate |
