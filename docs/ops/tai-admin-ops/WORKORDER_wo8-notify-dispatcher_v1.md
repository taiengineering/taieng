---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-8 NotifyDispatcher — Gmail 발송·수신 통합 + 3채널 단일화
version: 1
status: ACTIVE
owner: taiwang
---

# WO-8 — NotifyDispatcher (Gmail 발송·수신 통합 + 발송 단일화)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-8
- **오브젝트:** NotifyDispatcher (백엔드) + GmailChannel (신설). SMS는 기존 capability 재사용.
- **닫는 시나리오:** S25(발송 단일화)·S26(발송설정/미리보기)·자동화(WO-12) 수신 트리거 재료

---

## 1. 현황 (실측)

**SMS/알림톡** — 이미 capability 패턴으로 잘 구조화:
- `capabilities.sms.core.send_sms(receiver, message, title)` (async), `call_edge(payload)`.
- Supabase Edge Function(서울) 경유 MessageMi. 카카오 금지 준수.
- `routers/messaging.py`는 thin wrapper(v8.0.0).

**메일** — `routers/mail.py`(v2.2.0)에서 **Resend 직접 호출**(`resend_client.Emails.send`).
- 발송: send / send-system / reply. 수신: Resend 웹훅(`/mail/webhook/inbound`).
- mail_logs 테이블에 발송·수신 이력 적재. 첨부는 Supabase Storage(mail-attachments).
- 주석에 "MX를 Resend→Google Workspace로 변경하면 수신 웹훅 미호출" 명시.

**FCM** — `routers/fcm.py` 존재(푸시). 이번 범위 밖(인터페이스만 예약).

## 2. 결정 — 메일을 Gmail API로 전환 (발송+수신 통합)

TAI는 Google Workspace 사용 중, 발신 주소 `tai@taieng.co.kr`. **자동화(수신 트리거)를 위해 수신도 어드민(mail_logs)으로 들어와야** 함 → 발송·수신을 하나의 Gmail 연동으로 통일.

**방식: Gmail API + 서비스계정 도메인 위임(DWD)**
- 서비스계정(GCP) + JSON 키 → Workspace 관리콘솔 도메인 위임 승인(슈퍼관리자).
- Python: `Credentials.from_service_account_info(...).with_subject("tai@taieng.co.kr")`.
- 스코프(좁게): `gmail.send`(발송), `gmail.readonly`(수신 읽기). `mail.google.com` 전체는 회피(CASA Tier2 심사 회피).
- 발송: `messages.send`(RFC822 MIME base64url). 수신: `messages.list`→`messages.get`→mail_logs 적재.

## 3. 단계 분할 (독립 배포·검증)

- **WO-8A — GmailChannel 발송:** `services/gmail_channel.py` send(). mail.py의 Resend 발송을 Gmail로 교체(send-system 우선, 이후 send/reply). SDK 지연 import. env 미설정 시 501(배포 안전).
- **WO-8B — Gmail 수신 폴링:** `pull_inbox()` — messages.list(신규) → get → mail_logs(direction=inbound) 적재. 중복 방지(gmail message id UNIQUE). 스케줄러/수동 트리거. 자동화 훅 자리 예약.
- **WO-8C — NotifyDispatcher 통합:** `services/notify_svc.py` `send(channel, target, ...)` 단일 진입(SMS=capability, MAIL=gmail_channel, PUSH=fcm 예약) + DryRunPreview(대량발송 대상수·샘플).

## 4. env (Railway 단일 저장, §5-1)

| 키 | 용도 |
|---|---|
| `GMAIL_SA_JSON` | 서비스계정 JSON 키(전체 문자열) 또는 `GMAIL_SA_JSON_B64`(base64) |
| `GMAIL_SENDER` | 가장할 발신 계정 = tai@taieng.co.kr |
| `GMAIL_POLL_LABEL` | (선택) 수신 폴링 대상 라벨/쿼리 |

## 5. 완료 판정

- WO-8A: gmail_channel.send 구현, mail.py 발송 경로 Gmail 전환, SDK 미설정 배포 안전, 감사(MAIL_SEND).
- WO-8B: pull_inbox 구현, mail_logs 적재, 중복 방지. 
- WO-8C: notify_svc.send 단일 진입 + DryRun.
- 실발송/수신 검증(VERIFIED)은 서비스계정 + 도메인 위임 승인 후 사람 게이트.

## 6. 사람 게이트 (실연동)

1. GCP 프로젝트 → Gmail API 활성화 → 서비스계정 생성 → JSON 키 발급
2. Workspace 관리콘솔 → 보안 → API 제어 → 도메인 위임 → 서비스계정 client ID + 스코프(gmail.send, gmail.readonly) 승인
3. Railway env: GMAIL_SA_JSON(_B64), GMAIL_SENDER=tai@taieng.co.kr
4. `pip install google-api-python-client google-auth`
5. Resend 발송 경로 은퇴(수신 웹훅은 Gmail 폴링으로 대체)
