# Quiet Hour UX Rules

작성일: 2026-05-16

---

## UX 상태 표시

| 상태 | UX 의미 | 사용자 표시 |
|---|---|---|
| QUIET_HOUR_DELAYED | 지연 중 | "조용한 시간 설정으로 지연되었습니다" |
| RESUMED | 재개됨 | "조용한 시간 종료 후 전달되었습니다" |
| SUPPRESSED | 전달 안 됨 | 사용자에게 표시 안 함 |

## 핵심

**사용자는 왜 늦게 받았는지 알 수 있어야 한다.**

## Feed 표시 규칙

- Quiet Hour로 지연된 항목: 일반 Feed와 동일하게 표시 (전달 시간 기준)
- Timeline Modal에서 QUIET_HOUR_DELAYED → RESUMED 전이 확인 가능
- Suppressed 항목은 Feed에 나타나지 않음 (Queue 자체가 생성되지 않음)

## 설정 UI

- 조용한 시간 활성/비활성 토글
- 시작/종료 시간 설정
- CRITICAL은 항상 전달됨을 안내
