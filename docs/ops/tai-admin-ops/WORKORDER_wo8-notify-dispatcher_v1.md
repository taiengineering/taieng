---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-8 NotifyDispatcher — Gmail 발송·수신 통합 + 3채널 단일화
version: 3
status: ACTIVE
owner: taiwang
---

# WO-8 — NotifyDispatcher (Gmail 발송·수신 통합 + 발송 단일화)

- **작성일:** 2026-07-28 (v3: WO-8B 완료 반영)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-8
- **진행:** WO-8A(발송)·WO-8B(수신) VERIFIED. WO-8C(통합) 예정.

---

## 1. 현황 (실측)

- **SMS/알림톡:** `capabilities.sms.core` — Edge Function MessageMi. 카카오 금지.
- **메일:** mail.py Resend→Gmail 전환 중(WO-8A). 수신 Resend웹훅→Gmail폴링(WO-8B).
- **FCM:** fcm.py 존재, 범위 밖(인터페이스만 예약).

## 2. 결정 — 메일 Gmail API 전환 (발송+수신 통합, DWD)

TAI Workspace `tai@taieng.co.kr`. 서비스계정 도메인 위임, 좁은 스코프(gmail.send/readonly).

## 3. WO-8A — GmailChannel 발송 (VERIFIED)

- `services/gmail_channel.py`: send(도메인위임 impersonate + messages.send).
- `routers/mail.py` v3.0.0: `_dispatch_send` Gmail 우선→Resend fallback. `_gmail_enabled()` 채널선택.
- 커밋 97b5034·8da3807. SDK 미설치 배포 SUCCESS(지연 import). 실발송 PENDING(사람 게이트).

## 4. WO-8B — Gmail 수신 폴링 (VERIFIED)

- **`services/gmail_channel.py`**: `parse_message`(헤더·본문 재귀 추출) 추가. 커밋 7a5ef34.
- **`services/gmail_inbox_svc.py`**: `pull_inbox(query, max_results)` — list→get→parse→mail_logs(inbound) 적재. 중복방지(선조회 + DB UNIQUE). `register_inbound_handler`/`_fire_inbound` = **수신 콜백 레지스트리**(WO-12 자동화 결합점). 커밋 312b4f2.
- **`routers/gmail_inbox.py`**: `POST /mail/pull`(수동/스케줄러 트리거). 커밋 daa63b3. external 등록 fff7b63.
- **마이그레이션**: `20260728155131_mail_inbound_dedup_index.sql` — inbound resend_id(=Gmail message id) 부분 UNIQUE. 기존 inbound 201건 중복 0 확인 후 적용.

| 항목 | 상태 | 근거 |
|---|---|---|
| dedup 부분 UNIQUE 인덱스 | VERIFIED | pg_indexes 확인(inbound+resend_id NOT NULL) |
| parse_message/pull_inbox/라우터 | VERIFIED | 배포 SUCCESS(fff7b63) + `/health` |
| 중복 방지(선조회+DB UNIQUE) | VERIFIED | 인덱스 + _existing_ids 이중 방어 |
| 수신 콜백 레지스트리(자동화 결합점) | VERIFIED | register_inbound_handler/_fire_inbound |
| 실수신(Gmail 폴링) | PENDING | 서비스계정+도메인위임+env+pip 후 사람 게이트 |

## 5. WO-8C — NotifyDispatcher 통합 (예정)

`services/notify_svc.py` `send(channel, target, ...)` 단일 진입(SMS=capability, MAIL=gmail_channel, PUSH=fcm 예약) + DryRunPreview(대량발송 대상수·샘플).

## 6. env (Railway 단일 저장, §5-1)

| 키 | 용도 |
|---|---|
| `GMAIL_SA_JSON` / `GMAIL_SA_JSON_B64` | 서비스계정 JSON 키 |
| `GMAIL_SENDER` | 발신 계정 = tai@taieng.co.kr |
| `GMAIL_POLL_LABEL`/쿼리 | (선택) 수신 폴링 대상 |

## 7. 사람 게이트 (실연동)

1. GCP → Gmail API 활성화 → 서비스계정 → JSON 키
2. Workspace 관리콘솔 도메인 위임 → client ID + 스코프(gmail.send, gmail.readonly) 승인
3. Railway env: GMAIL_SA_JSON(_B64), GMAIL_SENDER
4. `pip install google-api-python-client google-auth`
5. 검증: send-system 발송 1건(provider=gmail 확인), `POST /mail/pull` 수신 1건 적재 확인
6. Resend 발송·수신웹훅 은퇴

## 8. 산출물 (커밋)

1. `services/gmail_channel.py` (send + parse_message + list/get)
2. `services/gmail_inbox_svc.py` (수신 폴링 + 콜백 레지스트리)
3. `routers/mail.py` v3.0.0 (발송 Gmail 우선)
4. `routers/gmail_inbox.py` (POST /mail/pull)
5. `router_registry/external.py` (gmail_inbox 등록)
6. `supabase/migrations/20260728155131_mail_inbound_dedup_index.sql`
