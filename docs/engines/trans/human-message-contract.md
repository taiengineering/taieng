# Human Message Contract

## 목적

Trans Engine이 출력하는 사람 메시지의 표준 구조를 정의한다.
모든 번역 결과는 이 Contract을 따른다.

## 표준 구조

```json
{
  "title": "상황 제목",
  "summary": "상황 설명 1~2문장",
  "urgency": "즉시 확인 필요 | 주의 필요 | 참고",
  "impact": "영향 범위 설명",
  "recommended_checks": [
    "확인해야 할 사항 1",
    "확인해야 할 사항 2"
  ],
  "recommended_actions": [
    "권장 조치 1",
    "권장 조치 2"
  ],
  "confidence": 0.85,
  "technical": {
    "event_type": "workflow.failed",
    "flow_key": "payment_attempt",
    "severity": "WARNING",
    "trace_id": "abc-123"
  }
}
```

## 필드 정의

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| title | string | Y | 상황 중심 제목 (기술 용어 금지) |
| summary | string | Y | 1~2문장 운영 설명 |
| urgency | string | Y | "즉시 확인 필요" / "주의 필요" / "참고" |
| impact | string | Y | 영향 범위 |
| recommended_checks | list[str] | Y | 확인 사항 (최소 1개) |
| recommended_actions | list[str] | N | 권장 조치 |
| confidence | float | Y | 번역 신뢰도 0.0~1.0 |
| technical | dict | 조건부 | developer만 포함 |

## Audience별 출력 차이

### operator (일반 운영자)

- title, summary, urgency, impact, recommended_checks 포함
- technical **생략**
- recommended_actions 선택적
- 모든 표현에서 기술 용어 완전 제거

### admin (관리자)

- 전체 필드 포함
- technical 선택적 (요청 시 포함)
- 도메인 용어 사용 가능 ("결제 흐름", "문서 생성")

### developer (개발자)

- 전체 필드 포함
- technical **필수 포함**
- event_type, flow_key, severity, trace_id 포함

## urgency 매핑

| Severity (Input) | Urgency (Output) |
|-------------------|-------------------|
| CRITICAL | 즉시 확인 필요 |
| WARNING | 주의 필요 |
| INFO | 참고 |

## confidence 기준

| 값 | 의미 |
|-----|------|
| 0.9+ | Dictionary 정확 매칭 |
| 0.7~0.9 | Core Dictionary 매칭 |
| 0.5~0.7 | 유추 기반 번역 |
| 0.5 미만 | 기본 템플릿 사용 |
