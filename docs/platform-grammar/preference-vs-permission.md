# Preference vs Permission

작성일: 2026-05-16

---

## 구분

| 개념 | 의미 | 주체 | 예시 |
|---|---|---|---|
| **Preference** | 사용자 선택 | 사용자 | SMS 알림 끄기 |
| **Permission** | 플랫폼 정책 | 플랫폼 | CRITICAL alert는 무조건 수신 |

## 핵심

```
사용자가 받고 싶어도 권한이 없으면 볼 수 없다
사용자가 무트해도 CRITICAL은 전달된다
```

## 우선순위

```
Permission (\ud50c\ub7ab\ud3fc \uc815\ucc45)
  > Preference (\uc0ac\uc6a9\uc790 \uc120\ud0dd)
    > Default (\uae30\ubcf8\uac12)
```

## \ud604\uc7ac \ub2e8\uacc4

- Preference: `notification_preference_registry` \ud14c\uc774\ube14
- Permission: \ubbf8\uad6c\ud604 (Phase 2+, Identity Core \uc5f0\ub3d9)
- Escalation bypass: CRITICAL severity\ub294 mute \ubb34\uc2dc (\ubbf8\uad6c\ud604, \uac1c\ub150\ub9cc)
