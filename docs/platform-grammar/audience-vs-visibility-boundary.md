# Audience vs Visibility Boundary

작성일: 2026-05-16

---

## 구분

| 개념 | 의미 | 예시 |
|---|---|---|
| **Audience** | 전달 대상 (받을 수 있는 사람) | operator는 Telegram alert 수신 가능 |
| **Visibility** | 볼 수 있는 범위 (접근 권한) | 작업자는 자기 사업장 알림만 조회 |

## 핵심

```
받을 수 있다고 모두 볼 수 있는 것은 아니다
```

- Audience: 전달 레이어 책임 (Notification Engine)
- Visibility: 접근 레이어 책임 (Identity Core / RLS)

## 현재 단계

- Audience: recipient_rule 기반 단순 resolution
- Visibility: Supabase RLS 정책으로 처리
- 두 개를 Notification Engine 내부에서 혼합하지 않음
