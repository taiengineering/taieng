# Telegram Operational Workflow

## 목적

모바일 운영 흐름 정의. Telegram 알림을 통한 운영자 실시간 대응 흐름.

## 흐름

```
Attention (critical/high)
  → Telegram 알림 발송
    → 상황 제목 + 운영 요약
    → guidance 요약 (1~3번 대응)
    → 상황 상세 링크
  → Operator 확인
    → 대응 시작
    → 대응 결과 기록 (POST /learning/feedback)
  → Closure
    → 종료 승인 (POST /closure/resolve)
```

## 알림 형식

```
🔴 즉시 확인 필요

결제 흐름 안정성 저하
상황이 악화되고 있습니다.

권장 대응:
1. 영향 범위 확인
2. 최근 변경사항 점검

상세: https://admin.taieng.co.kr/situation-detail.html?id=xxx
```

## 발송 조건

| 조건 | 발송 |
|------|------|
| attention_level = critical | 즉시 |
| attention_level = high + worsening | 즉시 |
| recurring + escalating | 즉시 |
| attention_level = medium | 요약 (1시간 배치) |

## 구현 계획

- 현재: 정의 단계 (문서)
- 다음: Scheduler에 Telegram 발송 hook 추가
- MessageMi 연동 (기존 인프라 활용)

## 원칙

- 운영 언어만 사용 (기술 용어 금지)
- 상세 링크 필수
- 대응 가이드 포함
- PROD/SYN 구분 표시
