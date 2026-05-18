# Domain Dictionary

## 목적

시스템 이벤트를 도메인별 운영 언어로 변환하기 위한 사전.
Core Dictionary + Domain Dictionary 2계층 구조.

## 구조

```
Core Dictionary (공통)
  └─ Domain Dictionary (도메인별 확장)
       ├─ Payment
       ├─ Document
       ├─ Construction
       ├─ Marketing
       └─ TAI (자사 전용)
```

## Core Dictionary

모든 도메인에 공통 적용되는 기본 번역.

| Event Pattern | operator 표현 | admin 표현 |
|---------------|---------------|------------|
| workflow.failed | 작업이 완료되지 못했습니다 | 워크플로우 실패 발생 |
| step.failed | 처리 중 문제가 발생했습니다 | 처리 단계 실패 |
| degradation | 서비스 안정성이 낮아지고 있습니다 | 성능 저하 감지 |
| repeated_failure | 같은 문제가 반복되고 있습니다 | 반복 실패 패턴 감지 |
| escalation | 운영 위험이 증가하고 있습니다 | 에스컬레이션 발생 |
| recovery.started | 문제 해결이 진행 중입니다 | 복구 절차 시작 |
| recovery.completed | 문제가 해결되었습니다 | 복구 완료 |
| runtime.degraded | 시스템 성능이 저하되고 있습니다 | 런타임 성능 저하 |
| health.warning | 시스템 상태에 주의가 필요합니다 | 헬스체크 경고 |

## Domain Dictionary: Payment

| Event Pattern | operator 표현 | admin 표현 |
|---------------|---------------|------------|
| payment.failed | 결제 처리가 실패했습니다 | 결제 흐름 실패 |
| payment.timeout | 결제 응답 대기 시간이 초과되었습니다 | 결제 타임아웃 |
| payment.retry_exhausted | 결제 재시도가 모두 실패했습니다 | 결제 재시도 한도 초과 |

## Domain Dictionary: Document

| Event Pattern | operator 표현 | admin 표현 |
|---------------|---------------|------------|
| document.failed | 문서 생성이 실패했습니다 | 문서 생성 실패 |
| document.timeout | 문서 처리 시간이 초과되었습니다 | 문서 생성 타임아웃 |
| document.template_missing | 문서 양식을 찾을 수 없습니다 | 템플릿 누락 |

## Domain Dictionary: Construction

| Event Pattern | operator 표현 | admin 표현 |
|---------------|---------------|------------|
| inspection.overdue | 점검 기한이 지났습니다 | 점검 기한 초과 |
| schedule.conflict | 일정이 겹칩니다 | 일정 충돌 감지 |
| compliance.gap | 법령 준수 사항을 확인하세요 | 컴플라이언스 갭 감지 |

## Domain Dictionary: Marketing

| Event Pattern | operator 표현 | admin 표현 |
|---------------|---------------|------------|
| campaign.failed | 캠페인 발행이 실패했습니다 | 캠페인 발행 실패 |
| campaign.low_engagement | 캠페인 반응이 낮습니다 | 캠페인 참여율 저조 |

## Domain Dictionary: TAI

| Event Pattern | operator 표현 | admin 표현 |
|---------------|---------------|------------|
| diagnosis.failed | 법령진단 처리가 실패했습니다 | 진단 처리 실패 |
| diagnosis.timeout | 법령진단 응답이 지연되고 있습니다 | 진단 타임아웃 |
| subscription.failed | 구독 처리가 실패했습니다 | 구독 결제 실패 |

## 매칭 우선순위

1. Domain Dictionary 정확 매칭 → confidence 0.95
2. Domain Dictionary 패턴 매칭 → confidence 0.85
3. Core Dictionary 정확 매칭 → confidence 0.80
4. Core Dictionary 패턴 매칭 → confidence 0.70
5. 기본 템플릿 → confidence 0.50

## 확장 규칙

- 새로운 도메인 추가 시 Core Dictionary는 변경 금지
- Domain Dictionary는 Core를 **override** 가능
- TAI 전용 표현은 반드시 TAI Dictionary에만 배치
- Core Dictionary는 범용적이어야 함 (TAI 전용 금지)
