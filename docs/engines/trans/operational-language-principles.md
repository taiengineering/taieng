# Operational Language Principles

## 목적

Trans Engine이 운영 언어를 생성할 때 지켜야 하는 표현 원칙.

## 핵심 철학

> 이 엔진의 성공 기준은 "기술적으로 정확한 event 표현"이 아니라,
> 운영자가 "지금 무슨 일이 벌어지고 있는지" 이해할 수 있는가이다.

## 표현 원칙

### 1. 상황 중심 표현

| 금지 | 권장 |
|------|------|
| workflow.failed 이벤트 발생 | 작업이 완료되지 못했습니다 |
| ERROR level event | 문제가 발생했습니다 |
| trace_id: abc-123 실패 | 결제 처리 중 문제가 발생했습니다 |

### 2. 영향 중심 표현

| 금지 | 권장 |
|------|------|
| 3건 실패 | 일부 사용자가 영향을 받을 수 있습니다 |
| severity: CRITICAL | 즉시 확인이 필요합니다 |
| degradation 0.7 | 서비스 안정성이 낮아지고 있습니다 |

### 3. 행동 중심 표현

| 금지 | 권장 |
|------|------|
| recovery 필요 | 결제 로그를 확인하세요 |
| escalation 발생 | 담당자에게 전달하세요 |
| incident 생성됨 | 문제가 기록되었습니다 |

### 4. 우선순위 표현

| Severity | 운영 표현 | 의미 |
|----------|----------|------|
| CRITICAL | 즉시 확인 필요 | 지금 바로 확인해야 합니다 |
| WARNING | 주의 필요 | 상황을 지켜볼 필요가 있습니다 |
| INFO | 참고 | 참고만 하면 됩니다 |

### 5. 영향 범위 표현

| 상황 | 운영 표현 |
|------|----------|
| 단일 사용자 | 특정 사용자에게 영향 |
| 일부 사용자 | 일부 사용자 영향 가능 |
| 전체 사용자 | 전체 서비스 영향 |
| 내부만 | 내부 처리 관련 (사용자 영향 없음) |

### 6. 운영 설명 원칙

- 1~2문장으로 완결
- 전문 용어 없이 설명
- "무슨 일이 벌어지고 있는지"에 집중
- "왜 발생했는지"는 developer 프로필에서만

### 7. 권장 확인사항 원칙

- 구체적 행동 제시 ("결제 로그를 확인하세요")
- 추상적 표현 금지 ("상태를 확인하세요")
- 최소 1개, 최대 5개
- 우선순위 순서로 나열

## Audience별 표현 차이 예시

### Event: workflow.failed / payment_attempt / WARNING

**developer:**
- title: workflow.failed/payment_attempt
- summary: payment_attempt 워크플로우 WARNING 레벨 실패, 최근 15분 3건
- technical: { event_type, flow_key, severity, trace_id, count }

**admin:**
- title: 결제 흐름 실패 증가
- summary: 최근 15분 동안 결제 처리 실패가 증가하고 있습니다.

**operator:**
- title: 결제 처리에 문제가 발생했습니다
- summary: 일부 사용자가 결제를 완료하지 못할 수 있습니다.

## 금지 표현 목록

- trace_id, span_id 직접 노출
- event_type 원본 노출 (operator/admin)
- projection, runtime_state
- JSON 구조 직접 노출
- 내부 함수명/클래스명
- severity 코드 직접 노출 (operator)
- 기술 약어 (RPC, gRPC, API 등) — operator 한정
