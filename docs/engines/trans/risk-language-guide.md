# Risk Language Guide

## 목적

내부 severity/risk 코드를 운영자가 이해할 수 있는 위험 언어로 변환하는 가이드.

## Severity → 운영 언어

| 내부 코드 | 운영 표현 | 설명 |
|-----------|----------|------|
| INFO | 정상 흐름 | 특이사항 없음 |
| WARNING | 주의 필요 | 상황을 지켜볼 필요 |
| CRITICAL | 즉시 확인 필요 | 지금 바로 확인해야 함 |
| FATAL | 운영 중단 가능성 | 서비스 중단 위험 |

## Risk Level → 운영 언어

| 내부 | 운영 표현 |
|------|----------|
| HEALTHY | 정상 운영 중 |
| RISK | 위험 요소 감지 |
| DEGRADED | 안정성 저하 중 |
| CRITICAL | 심각한 위험 상태 |

## Trend → 운영 언어

| 추세 | 운영 표현 |
|------|----------|
| improving | 상황이 점차 안정되고 있습니다 |
| stable | 현재 상태가 유지되고 있습니다 |
| degrading | 서비스 안정성이 점차 낮아지고 있습니다 |
| accelerating | 문제가 빠르게 증가하는 추세입니다 |

## 금지 표현

- severity 코드 직접 노출 (INFO, WARNING, CRITICAL)
- risk level 코드 직접 노출 (HEALTHY, RISK)
- 내부 metric 수치 직접 노출 (degradation=0.7)
- 기술 약어 (SLA, MTTR, P99)

## 허용 조건

- developer 프로필에서만 기술 코드 허용 (technical 필드)
- admin 프로필에서 도메인 용어 허용 ("워크플로우", "에스컬레이션")
- operator 프로필에서는 완전한 운영 언어만 사용
