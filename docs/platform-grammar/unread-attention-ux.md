# Unread Attention UX

작성일: 2026-05-16

---

## 상태

| 상태 | 의미 | UX 표현 |
|---|---|---|
| unread | 아직 확인 안 함 | 파란 보더 + 하이라이트 배경 |
| read | 확인 완료 | 일반 배경 |
| critical unread | 즉시 attention 필요 | 빨간 Badge + 빨간 보더 |

## Badge 규칙

- Header Bell Badge: 총 unread 수 (99+ 상한)
- 60초 주기 자동 갱신 (Polling)
- 0건이면 Badge 숨김

## 핵심

**Unread는 운영 Attention Signal이지, Incident Severity가 아니다.**

- Unread ≠ 긴급
- CRITICAL Severity ≠ 읽지 않음
- 두 개는 독립적인 신호
