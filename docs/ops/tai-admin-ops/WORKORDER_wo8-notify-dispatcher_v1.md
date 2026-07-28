---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-8 NotifyDispatcher — Gmail 발송·수신 통합 + 3채널 단일화
version: 4
status: DONE
owner: taiwang
---

# WO-8 — NotifyDispatcher (Gmail 발송·수신 통합 + 발송 단일화)

- **작성일:** 2026-07-28 (v4: WO-8 전체 완료)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-8
- **최종:** WO-8A(발송)·WO-8B(수신)·WO-8C(통합) 전부 VERIFIED. 실연동만 사람 게이트.

---

## 1. 결정 — 메일 Gmail API 전환 (발송+수신 통합, DWD)

TAI Workspace `tai@taieng.co.kr`. 자동화(수신 트리거)를 위해 발송·수신을 하나의 Gmail 연동으로 통일. 서비스계정 도메인 위임(DWD), 좁은 스코프(gmail.send/readonly, mail.google.com 전체 회피).

## 2. WO-8A — GmailChannel 발송 (VERIFIED)

- `services/gmail_channel.py`: send(도메인위임 impersonate + messages.send RFC822 base64url).
- `routers/mail.py` v3.0.0: `_dispatch_send` **Gmail 우선 → Resend fallback**. `_gmail_enabled()` 채널선택. send/send-system/reply 적용. 첨부는 Resend(Gmail 첨부 후속).
- 커밋 97b5034·8da3807. SDK 미설치 배포 SUCCESS(지연 import).

## 3. WO-8B — Gmail 수신 폴링 (VERIFIED)

- `services/gmail_channel.py`: `parse_message`(헤더·본문 재귀 추출). 커밋 7a5ef34.
- `services/gmail_inbox_svc.py`: `pull_inbox` — list→get→parse→mail_logs(inbound) 적재, 중복방지(선조회+DB UNIQUE). `register_inbound_handler`/`_fire_inbound` = 수신 콜백 레지스트리(WO-12 결합점). 커밋 312b4f2.
- `routers/gmail_inbox.py`: `POST /mail/pull`. 커밋 daa63b3, 등록 fff7b63.
- 마이그레이션 `20260728155131_mail_inbound_dedup_index.sql`(inbound resend_id 부분 UNIQUE). 적용·인덱스 확인 완료.

## 4. WO-8C — NotifyDispatcher 통합 (VERIFIED)

- **`services/notify_svc.py`**: `send(channel, target, ...)` 단일 진입 — SMS(capabilities.sms.core 위임, async→_run_async), MAIL(gmail_channel.send 위임), PUSH(501 예약). `dry_run_preview(channel, targets)` = 대량발송 안전장치(대상수·유효/무효·중복제거·샘플). 감사 NOTIFY_SEND. 커밋 8b5d2e8.
- **`routers/notify.py`**: `POST /notify/send`, `POST /notify/dry-run`. 커밋 73d0891. external 등록 f0d8dac.

| 항목 | 상태 | 근거 |
|---|---|---|
| notify_svc.send 단일 진입(SMS/MAIL/PUSH) | VERIFIED | 배포 SUCCESS(f0d8dac) + `/health` |
| SMS/MAIL 위임 시그니처 정합 | VERIFIED | send_sms(receiver,message,title)·gmail_channel.send 대조 일치 |
| dry_run_preview 안전장치 | VERIFIED | @/자릿수 검증·중복제거·샘플, 발송 없음 |
| 감사 NOTIFY_SEND | VERIFIED | audit_svc.record 위임 |
| notify 라우터 등록 | VERIFIED | external 그룹 등록 배포 SUCCESS |

## 5. 최종 산출물 (커밋)

1. `services/gmail_channel.py` (send + parse_message + list/get)
2. `services/gmail_inbox_svc.py` (수신 폴링 + 콜백 레지스트리)
3. `services/notify_svc.py` (통합 발송 + DryRun)
4. `routers/mail.py` v3.0.0 (발송 Gmail 우선)
5. `routers/gmail_inbox.py` (POST /mail/pull)
6. `routers/notify.py` (POST /notify/send, /notify/dry-run)
7. `router_registry/external.py` (gmail_inbox·notify 등록)
8. `supabase/migrations/20260728155131_mail_inbound_dedup_index.sql`

## 6. 사람 게이트 (실연동 — 이후 실행)

1. GCP → Gmail API 활성화 → 서비스계정 생성 → JSON 키 발급
2. Workspace 관리콘솔 → 보안 → API 제어 → 도메인 위임 → 서비스계정 client ID + 스코프(gmail.send, gmail.readonly) 승인(슈퍼관리자, 최대 60분)
3. Railway env: GMAIL_SA_JSON(_B64), GMAIL_SENDER=tai@taieng.co.kr
4. `pip install google-api-python-client google-auth` (requirements.txt)
5. 검증: `/mail/send-system` 발송 1건(provider=gmail), `POST /mail/pull` 수신 1건 적재, `POST /notify/send`(MAIL/SMS) 각 1건
6. Resend 발송·수신웹훅 은퇴

## 7. 자동화 연결 (WO-12 예정)

`gmail_inbox_svc.register_inbound_handler(handler)`로 수신 트리거 결합. notify_svc.send로 자동 발송(SEND_SMS/SEND_MAIL 액션). 이 둘이 WO-12 AutomationEngine의 입출력.
