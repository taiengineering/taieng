# 작업지시서 — verify-otp 로그인 이메일 자가치유 (auth.py)

> 2026-08-17 · Goal G-mswtdmi1-420f8c 별건 3
> 대상 `tai-api` · `routers/auth.py` · 함수 `_issue_session_for_phone`
> 처리 주체: **Cursor / Claude Code** (auth.py 46KB > 20KB → MCP 전면 재작성 금지, 로컬 편집 → git push)

---

## 배경 (오늘 실측으로 드러난 문제)

작업자 로그인(`POST /auth/verify-otp`)은 OTP 통과 후 `_issue_session_for_phone` 에서
GoTrue `sign_in_with_password` 로 세션(access_token)을 발급한다.

그런데 **이메일이 미확인(email_confirmed_at IS NULL)인 GoTrue 계정**은
`sign_in_with_password` 가 `400 "Email not confirmed"` 로 실패한다 → **토큰이 안 나온다**.

- 운영 로그 실측(2026-08-17): 테스트 계정 `01083994168`(auth_id `dab70db2…`)이
  `POST /token` 에서 `400: Email not confirmed` 로 반복 실패(12:16·12:42·12:56).
- 이메일을 수동 확인 처리한 뒤 `POST /token 200` + `GET /user 200` 으로 정상화.

토큰이 없거나 거부되면 인증이 필요한 화면(작업 전 점검 항목 조회 등)이 401 로
로그인에 튕기고, 제출도 막힌다. 오늘은 이 문제가 ⑤ 검증을 막았다.

현재 미확인 계정은 15개 중 1개뿐이었고(대부분 정상), 그 1개는 조치됨.
다만 **웹가입(`/auth/register` → `sign_up`)은 email_confirm 없이 계정을 만들어**
미확인 상태가 남을 수 있다. 그 계정이 OTP 로그인하면 같은 문제가 재발한다.

## 변경 (한 줄)

`_issue_session_for_phone` 의 **기존 GoTrue 계정(auth_id 있음) 분기**에서
비밀번호 재설정 시 `email_confirm=True` 를 함께 넣어 **로그인 때 이메일을 자동 확인**한다.

```python
# 변경 전
if auth_id:
    # 기존 GoTrue 계정 — 비밀번호를 재설정해 세션을 얻는다.
    admin.auth.admin.update_user_by_id(auth_id, {"password": password})

# 변경 후
if auth_id:
    # 기존 GoTrue 계정 — 비밀번호 재설정 + 이메일 확인(미확인 계정 자가치유).
    # email_confirm 없이는 웹가입 등으로 만든 미확인 계정이 sign_in_with_password 에서
    # "Email not confirmed" 로 실패해 토큰이 발급되지 않는다.
    admin.auth.admin.update_user_by_id(auth_id, {"password": password, "email_confirm": True})
```

- 계정 **생성 분기**(`create_user`)는 이미 `"email_confirm": True` 라 손댈 필요 없음.
- `list_users` 폴백 후 `update_user_by_id` 하는 지점도 있으면 동일하게 `email_confirm=True` 를 더해두면 안전(선택).

## 이유 / 안전성

- OTP 통과자에게만 실행되므로 임의 확인이 아니다(전화번호 인증을 이미 통과).
- 로그인 UX·응답 구조 불변. 토큰 발급 성공률만 올라간다.
- 소유자 검증(ⓐ, worker_assets v1.2.0)이 토큰을 요구하므로, 이 자가치유가
  ⓐ의 잔여 위험(미확인 계정 튕김)을 없앤다.

## 검증

1. 미확인 이메일 계정 하나로 OTP 로그인 → 응답에 `access_token` 이 있고
   이후 `GET /auth/me` 등 인증 호출이 200 인지 확인.
2. 운영 로그(tai-api-prod)에서 `POST /token` 의 `Email not confirmed` 400 이 재발하지 않는지.
   - 로그 접근: project `7c3ab53b-feb6-40a4-a4f0-7ade3f6e524b` · service `tai-api-prod 4cf52678…` · env `production 9dacb6f0…`

## 배포
`main` push → Railway(tai-api-prod) 자동 배포.
