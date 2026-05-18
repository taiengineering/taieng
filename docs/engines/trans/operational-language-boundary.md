# Operational Language Boundary

## 목적

Trans Engine이 변환하는 언어의 경계를 정의한다.
무엇이 내부 Runtime 언어이고, 무엇이 운영 언어인지 명확히 구분한다.

## 내부 Runtime 언어 (Input)

Trans Engine이 입력으로 받는 시스템 언어:

| 카테고리 | 예시 |
|----------|------|
| Event Type | workflow.failed, step.failed, integrity_event |
| Severity | CRITICAL, WARNING, INFO |
| Flow Key | payment_attempt, document_generation |
| Trace | trace_id, span_id |
| Projection | projection, runtime_state |
| Metric | degradation, repeated_failure, recovery_time |

이 언어들은 운영자에게 직접 노출되면 안 된다.

## 운영 언어 (Output)

운영자가 이해하는 언어:

| 구분 | 표현 방식 |
|------|----------|
| 상황 | "결제 흐름에서 문제가 발생했습니다" |
| 긴급도 | "즉시 확인 필요", "주의 필요", "참고" |
| 영향 | "일부 사용자 영향 가능", "전체 서비스 영향" |
| 확인사항 | "결제 로그를 확인하세요" |
| 조치 | "담당자에게 전달하세요" |

## 변환 원칙

| Event 개념 | 운영 개념 |
|------------|----------|
| Event → | Situation (상황) |
| Severity → | Urgency (긴급도) |
| Incident → | What happened (무슨 일) |
| Recovery → | What should be checked (확인사항) |
| Metric → | Impact (영향 범위) |

## 경계 규칙

1. Trans Engine은 Runtime 언어를 **읽기만** 한다
2. Trans Engine은 Runtime 언어를 **수정하지 않는다**
3. Trans Engine은 새로운 Severity를 **생성하지 않는다**
4. Trans Engine의 출력은 UI/Notification에서 **그대로 사용 가능**해야 한다
5. operator 프로필에서 기술 용어는 **완전히 제거**한다

## 기술 용어 제거 기준

운영 언어에서 다음은 **절대 노출 금지**:

- trace_id, span_id
- event_type 원본 (workflow.failed 등)
- projection, runtime_state
- severity 원본 코드 (CRITICAL 등)
- 내부 함수명, 클래스명
- JSON 구조체

단, developer 프로필에서는 `technical` 필드에 포함 가능.
