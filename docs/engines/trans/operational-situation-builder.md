# Operational Situation Builder

## 정의

Situation Builder는 여러 Runtime Event를 조합하여
"현재 운영 상황"을 사람이 이해할 수 있는 형태로 요약한다.

## 단일 Event vs Situation

| 구분 | 예시 |
|------|------|
| Event 번역 | "작업이 완료되지 못했습니다" |
| Situation | "결제 흐름의 안정성이 낮아지고 있습니다. 최근 실패와 응답 지연이 함께 증가하고 있습니다." |

운영자가 알고 싶은 것:
- 지금 서비스가 안정적인가?
- 위험이 증가하는가?
- 반복 문제가 있는가?
- 고객 영향이 있는가?
- 상황이 좋아지는가/나빠지는가?
- 무엇을 먼저 봐야 하는가?

## 출력 구조

```json
{
  "situation_title": "결제 흐름 안정성 저하",
  "situation_summary": "최근 실패와 응답 지연이 함께 증가하고 있습니다.",
  "urgency": "즉시 확인 필요",
  "impact": "일부 사용자가 결제를 완료하지 못할 수 있습니다.",
  "trend": "degrading",
  "trend_description": "서비스 안정성이 점차 낮아지고 있습니다.",
  "recommended_focus": [
    "결제 API 상태 확인",
    "최근 배포 여부 확인"
  ],
  "storyline": [
    "최근 응답 지연이 증가했습니다.",
    "이후 실패 흐름이 반복 발생하기 시작했습니다.",
    "현재 일부 사용자가 작업을 완료하지 못하고 있습니다."
  ],
  "confidence": 0.85
}
```

## 절대 원칙

- Truth 생성 금지
- Severity 생성 금지
- Escalation 생성 금지
- Incident 생성 금지
- Runtime Ownership 침범 금지

오직 Situation 설명, 흐름 요약, 위험 흐름 표현, 영향 표현, 우선순위 표현, 추천 확인사항 생성만 수행.

## 구성 모듈

| 모듈 | 역할 |
|------|------|
| situation_builder | 전체 상황 조합 |
| storyline_builder | 원인→악화→영향→확인사항 흐름 서술 |
| risk_explainer | severity → 운영 위험 언어 |
| impact_explainer | 영향 범위 언어 |
| priority_ranker | 우선순위 결정 |
| trend_narrator | 추세 서술 |

## 금지 표현

- ChatGPT 스타일 답변
- 대화체
- AI 비서 톤
- 추상적/장황한 설명

## 필수 표현

- 운영 상황 중심
- 짧고 명확
- 행동 중심
- 영향 중심
- 우선순위 중심
