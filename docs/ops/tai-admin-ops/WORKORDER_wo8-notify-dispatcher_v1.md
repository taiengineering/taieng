---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-8 NotifyDispatcher — Gmail 발송·수신 통합 + 3채널 단일화
version: 2
status: ACTIVE
owner: taiwang
---

# WO-8 — NotifyDispatcher (Gmail 발송·수신 통합 + 발송 단일화)

- **작성일:** 2026-07-28 (v2: WO-8A 완료 반영)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-8
- **오브젝트:** NotifyDispatcher + GmailChannel(신설). SMS는 기존 capability 재사용.
- **진행:** WO-8A(발송) VERIFIED. WO-8B(수신)·WO-8C(통합) 예정.

---

## 1. 현황 (실측)

- **SMS/알림톡:** `capabilities.sms.core.send_sms/call_edge` — Edge Function(서울) MessageMi. 카카오 금지 준수. messaging.py는 thin wrapper.
- **메일(변경 전):** mail.py에서 Resend 직접 호출. 수신은 Resend 웹훅. mail_logs 적재.
- **FCM:** fcm.py 존재. 이번 범위 밖(인터페이스만 예약).

## 2. 결정 — 메일 Gmail API 전환 (발송+수신 통합)

TAI Google Workspace 사용, `tai@taieng.co.kr`. 자동화(수신 트리거)를 위해 수신도 어드민(mail_logs)으로. **Gmail API + 서비스계정 도메인 위임(DWD)**, 좁은 스코프(gmail.send/readonly, mail.google.com 전체 회피).

## 3. WO-8A — GmailChannel 발송 (VERIFIED)

- **`services/gmail_channel.py`**(신설): `send(to, subject, html/text, cc, reply_to)` = 도메인위임 impersonate + messages.send(RFC822 base64url). `list_new_messages`/`get_message`(WO-8B용 스텁). SDK/키 지연 로딩.
- **`routers/mail.py` v3.0.0**: `_dispatch_send()` — **Gmail 우선 → Resend fallback**. `_gmail_enabled()`(GMAIL_SA_JSON+GMAIL_SENDER 설정 여부)로 채널 선택. send/send-system/reply 모두 적용. 첨부 있는 발송은 안전하게 Resend(첨부지원, Gmail 첨부는 후속). mail_logs에 provider 기록.

| 항목 | 상태 | 근거 |
|---|---|---|
| gmail_channel.py 구현 | VERIFIED | 커밋 97b5034 |
| mail.py v3 발송 전환 | VERIFIED | 커밋 8da3807 |
| SDK 미설치 배포 안전 | VERIFIED | Gmail SDK 미설치인데 gmail_channel 배포 SUCCESS + `/health` (지연 import) |
| env 미설정 fallback | VERIFIED | _gmail_enabled()=False → Resend 자동. 설정 시 Gmail 자동 전환 |
| 실발송(Gmail 호출) | PENDING | 서비스계정 + 도메인위임 승인 + env + pip 후 사람 게이트 |

## 4. WO-8B — Gmail 수신 폴링 (예정)

`pull_inbox()` — list_new_messages(신규 필터) → get_message → mail_logs(direction=inbound) 적재. gmail message id 중복 방지(resend_id 컬럼 재사용 + UNIQUE 인덱스 신규). 스케줄러/수동 트리거. 자동화 훅 자리 예약(WO-12).

## 5. WO-8C — NotifyDispatcher 통합 (예정)

`services/notify_svc.py` `send(channel, target, ...)` 단일 진입(SMS=capability, MAIL=gmail_channel, PUSH=fcm 예약) + DryRunPreview(대량발송 대상수·샘플).

## 6. env (Railway 단일 저장, §5-1)

| 키 | 용도 |
|---|---|
| `GMAIL_SA_JSON` 또는 `GMAIL_SA_JSON_B64` | 서비스계정 JSON 키 |
| `GMAIL_SENDER` | 발신 계정 = tai@taieng.co.kr |
| `GMAIL_POLL_LABEL`/쿼리 | (WO-8B, 선택) 수신 폴링 대상 |

## 7. 사람 게이트 (실연동)

1. GCP → Gmail API 활성화 → 서비스계정 생성 → JSON 키
2. Workspace 관리콘솔 → 보안 → API 제어 → 도메인 위임 → 서비스계정 client ID + 스코프(gmail.send, gmail.readonly) 승인(슈퍼관리자, 최대 60분 전파)
3. Railway env: GMAIL_SA_JSON(_B64), GMAIL_SENDER=tai@taieng.co.kr
4. `pip install google-api-python-client google-auth` (requirements.txt)
5. 검증: send-system으로 테스트 발송 1건 → provider=gmail 확인
6. 이후 Resend 발송 은퇴(수신은 WO-8B Gmail 폴링으로 대체)

## 8. 산출물 (커밋)

1. `services/gmail_channel.py` (신설)
2. `routers/mail.py` v3.0.0 (발송 Gmail 우선 전환)
