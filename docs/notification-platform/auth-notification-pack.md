# Auth Notification Pack

작성일: 2026-05-17
범위: 인증/보안 알림

---

## 원칙

**보안성 우선.** 인증 이벤트는 지연/묶음 없이 즉시 전달.

---

## 이벤트

| event_key | 설명 | audience | channel | severity | digest | quiet bypass |
|---|---|---|---|---|---|---|
| signup_completed | 회원가입 완료 | tenant_admin | IN_APP | INFO | ✅ | ❌ |
| login_detected | 로그인 감지 | tenant_admin | IN_APP | INFO | ✅ | ❌ |
| new_device_login | 새 디바이스 로그인 | tenant_admin | SMS | WARNING | ❌ | ✅ |
| password_reset | 비밀번호 재설정 | actor | SMS | INFO | ❌ | ✅ |
| otp_requested | OTP 요청 | actor | SMS | INFO | ❌ | ✅ |
| account_locked | 계정 잠금 | tenant_admin | SMS+IN_APP | CRITICAL | ❌ | ✅ |

---

## 규칙

- password_reset, otp_requested: `pw_reset.py` frozen 유지 (auth 플로우)
- new_device_login, account_locked: quiet hour bypass 필수
- signup_completed, login_detected: digest 가능 (일간 요약)
