---
doc: RECORD_phase3-backend-complete_v1
class: records
type: RECORD
scope: tbm
project: hybrid
title: Phase 3 서버측 완료 — 리더 인증·스코프·TBM 생성
version: 1
status: ACTIVE
owner: taiwang
created: 2026-08-12
related: [WORKORDER_phase3-leader-mobile_v1, DESIGN_phase3-leader-auth_v2]
tags: [tbm, leader, auth, scope, api-contract]
---

# Phase 3 서버측 완료 기록

- 선행: `WORKORDER_phase3-leader-mobile_v1`(5ac2ce01), `DESIGN_phase3-leader-auth_v2`(12dd96a)
- 검증: 실제 curl 호출 + DB 실측. 카운트가 아니라 응답으로 확인했다.
- 남은 것: **앱 화면(C)·작업자 화면(D)**. 서버는 준비됐다.

---

## 1. 앱이 호출할 계약

### 1-1. 인증 — 기존 흐름 그대로, 토큰이 추가됐다

```
POST /auth/send-otp    {phone}
POST /auth/verify-otp  {phone, otp}
```

응답에 기존 필드가 그대로 있고 다음이 **추가**됐다. 구버전 앱은 깨지지 않는다.

```json
{
  "id": "...", "worker_id": "...", "name": "김태형", "sector": "INDUSTRIAL",
  "access_token": "eyJ...",   ← 신규
  "refresh_token": "...",     ← 신규
  "token_type": "Bearer",     ← 신규
  "role_code": "013",         ← 신규
  "team_id": "9866..."        ← 신규
}
```

**앱이 해야 할 일** — `access_token` 을 저장하고 이후 요청에 `Authorization: Bearer` 로 싣는다. `_utils.js` 의 `getToken()` 이 지금 빈 문자열을 반환하므로 그 부분을 바꾸면 된다.

`send-otp` 는 더 이상 `dev_otp` 를 응답에 싣지 않는다(`OTP_DEV_ECHO=1` 인 환경 제외).

### 1-2. 리더 전용 — 5경로

모두 `Authorization: Bearer` 필수. **team_id 를 보내지 않는다** — 서버가 토큰에서 도출한다.

| 경로 | 용도 | 지시서 대응 |
|---|---|---|
| `GET /leader/me` | 리더 컨텍스트·팀 정보·`is_leader` | 화면 분기 |
| `GET /leader/groups` | 내 팀 그룹 + `member_count` | C-1 |
| `GET /leader/members?group_id=` | 그룹원 + `app_installed` | C-1 |
| `GET /leader/templates` | 쓸 수 있는 템플릿(팀 전용 + 팀 미지정) | C-2 |
| `POST /leader/tbm` | TBM 생성 + 그룹원 자동 소집 | C-2 |

`POST /leader/tbm` 요청/응답:

```json
요청  {"template_id":"...", "group_id":"...", "work_date":"2026-08-12",
       "override_location":null, "override_description":null}

응답  {"status":"success","data":{
        "meeting_id":"d80dc65a-...", "template_name":"[제조] 프레스 작업",
        "work_date":"2026-08-12", "group_id":"...", "team_id":"...",
        "attendee_count":2}}
```

`conductor_name` 은 받지 않는다. 토큰의 리더 이름을 쓴다 — 클라이언트가 보낸 이름을 쓰면 진행자를 사칭할 수 있다.

### 1-3. 실행·서명·추적 — 기존 경로 재사용 (신규 개발 없음)

```
GET   /tbm/{id}/attendees                  참석자·서명현황  ← C-3, C-4
GET   /tbm/{id}/sign-info?attendee_id=     서명 페이지 정보(토큰 불필요)
POST  /tbm/{id}/sign                       base64 PNG 서명
POST  /tbm/{id}/request-sign  {attendee_ids[]}  FCM 서명요청 푸시
POST  /tbm/{id}/complete                   전원 서명 후 완료
PATCH /tbm/{id}/attendees/{attendee_id}/sign
```

`attendees` 응답의 `sign_status`(`PENDING`/`SIGNED`)로 미서명자를 가린다.

---

## 2. 서버측 변경 요약

### tai-api

| 커밋 | 내용 |
|---|---|
| `3b945b1` | `auth.py` v3.8.0 — verify-otp 세션 발급 + 계정 배선 |
| `a466d5a` | v3.8.1 — users INSERT 시 `sector` 명시 |
| `c547d2c` | v3.8.2 — `dev_otp` 환경변수 통제 + 배선 견고화 |
| `13acd89` | `leader_scope.py` v1.0.0 — 리더 조회 3경로 |
| `aff2d13` | `router_registry` 등록 |
| `824a30d` | `leader_scope.py` v1.1.0 — `/leader/templates`, `POST /leader/tbm` |
| `85ea97c` | `worker_registry.py` v1.2.0 — 초대 발송을 기존 SMS 모듈로 |
| `f1cd253` | `adapters/sms.py` v2.0.0 — 알림엔진 SMS 채널 복구 |
| `20260811225446` | 마이그레이션 — `users.sector` 기본값 오타 수정 |

### DB (데이터)

```
role_data_scope  ('013','TEAM') 추가
users            김태형 role_code=013, team_id=사출팀
worker_registry  user_id 배선, app_installed=true
```

---

## 3. 검증 결과

| 항목 | 결과 |
|---|---|
| OTP 로그인 → 토큰 | ✅ `access_token` 발급, payload email `{phone}@worker.taieng.co.kr` |
| `users` 자동 생성 | ✅ worker_registry 기준, 미등록 번호는 생성 안 함 |
| 리더 판정 | ✅ `role_code=013`, `team_id` 응답에 실림 |
| `/leader/me` | ✅ `is_leader:true`, `scope_type:TEAM`, 사출팀 |
| `/leader/groups` | ✅ 후공정반 1건, `member_count:2` |
| `/leader/members` | ✅ 김태형·김민재, `app_installed` 각각 true/false |
| `/leader/templates` | ✅ 팀 미지정 제조 템플릿, team_id 미전송 |
| `POST /leader/tbm` | ✅ `attendee_count:2`, 그룹원 자동 소집 |
| 스코프 격리 | ✅ 남의 group_id → 403, 존재 여부 미노출 |
| 토큰 없음 | ✅ 401 |
| `/tbm/{id}/attendees` | ✅ 2명 `PENDING`, `worker_id` 연결 |
| 초대 문자 | ✅ 실제 단말 수신 |

---

## 4. 설계 판단 기록

### 4-1. OTP 인증과 세션의 분리

`verify-otp` 의 번호·인증번호 대조 자체는 올바르다. 본인 기기 수신 문자를 확인해야 통과하므로 최초 인증 강도는 아이디·비밀번호 이상이다.

문제는 **통과 이후**였다. 토큰을 발급하지 않아 그 사실을 이후 요청에 이어붙일 수단이 없었고, 서버는 요청 바디의 `phone` 문자열만 근거로 삼았다. 앱을 거치지 않고 API 를 직접 호출하면 인증 단계를 건너뛴다.

작업자는 자기 데이터 범위라 허용됐으나, 리더는 "남의 팀을 못 본다"는 판정 대상이라 성립하지 않는다. **인증 방식을 바꾸지 않고 토큰 발급만 추가**했다. 앱은 저장·전송만 하므로 자동 로그인 UX 는 동일하다.

### 4-2. 기존 로직 재사용 — 감싸되 바꾸지 않는다

`POST /tbm-templates/{id}/use` 는 `group_id` 지정 시 그룹원을 자동 소집하는 로직을 이미 갖고 있다(Phase 2). **다시 만들지 않고 위임한다.**

다만 그 경로는 `group_id` 소유권을 검증하지 않는다 — `body.group_id` 를 그대로 쓰고 `groups` 에서 `team_id` 를 역으로 읽을 뿐이며 인증 의존성도 없다. 리더가 직접 부르면 남의 팀 그룹원 전체를 소집할 수 있다.

그래서 `POST /leader/tbm` 이 소유권을 먼저 확인한 뒤 위임한다. **`/use` 자체는 바꾸지 않았다** — 웹 관리자(안전관리자) 경로이며 거기서는 전체 권한을 갖는 것이 정상이다.

### 4-3. 스코프 표현

`role_data_scope` 에는 `scope_value` 컬럼이 없다. 이 테이블은 **"어느 등급까지 보는가"만 정의**하고 경계값은 `users.team_id`·`factory_id`·`company_id` 에서 온다. `004 TEAM` 이 이미 정의돼 있어 새 개념이 불필요했고, `013 관리감독자`(산안법 제16조)도 이미 존재해 `TBM_LEADER` 를 만들지 않았다.

정의가 없는 role 은 `TEAM` 으로 좁힌다 — 모르는 값을 넓게 열어주면 권한이 샌다.

### 4-4. 정보 노출 차단

경계 밖 `group_id` 에 대해 404 가 아니라 **403 + 존재 여부 미노출**로 응답한다. 남의 팀 그룹 id 를 넣어 존재를 확인하는 것도 정보 노출이기 때문이다.

---

## 5. 부수적으로 잡은 결함

작업 중 드러난 것들이며 Phase 3 범위 밖이지만 함께 고쳤다.

**`users.sector` 기본값 오타** — 컬럼 기본값이 `'INDUSTRY'` 인데 `users_sector_check` 는 `'INDUSTRIAL'` 만 허용해, `sector` 를 명시하지 않은 **모든 users INSERT 가 23514 로 실패**했다. `POST /auth/register` 도 같은 이유로 막혀 있었다.

**`dev_otp` 응답 노출** — `send-otp` 가 인증번호를 응답에 그대로 실었다. 번호만 알면 남의 인증번호를 받아볼 수 있어 전화번호 인증이 무력해진다.

**SMS 어댑터의 실재하지 않는 도메인** — `notification_engine/adapters/sms.py` 가 `api.messagemi.com` 을 직접 호출했으나 그 도메인은 존재하지 않는다(DNS 실패). 이 어댑터는 `channel_registry` 의 `sms` 채널이므로 **알림엔진을 통한 SMS 가 전부 실패**하고 있었다. 검증된 경로(`capabilities.sms.core` → Edge Function 서울)로 교체했다.

**초대 발송 stub** — `POST /worker-registry/{id}/invite` 가 메시지를 `print` 로 출력하고 `invite_sent_at` 만 갱신하면서 "초대 문자가 발송됐습니다"를 응답했다. 관리자 화면에서는 성공으로 보이지만 아무것도 나가지 않았다.

**초대 링크 `w.taieng.co.kr`** — 프로젝트 어디에도 근거가 없는 도메인이었다. `safe.taieng.co.kr/app/` 로 정정.

---

## 6. 미해결 / 확인 필요

- **`_link_worker_registry` 자동 배선** — v3.8.0 에서 동작하지 않아 수동 SQL 로 처리했다. 컬럼·제약을 실측했으나 원인을 특정하지 못했고, v3.8.2 에서 관측성을 보강했다. 다음 작업자 로그인 시 로그로 확인할 것.
- **초대 문자 일부 번호 미수신** — `010-8399-4168` 로는 접수(code 100)됐으나 단말 수신이 안 됐다. 다른 번호는 정상 수신되므로 해당 번호 사유로 보인다.
- **`POST /workers/fcm-token` 저장 위치** — `worker_registry.push_token` 과 `users.push_token` 중 어디인지 미확인(UNKNOWN). 푸시는 동작 중이다.
- **`/leader/members` 의 group_id 경계 검증** — 그룹이 1개뿐이라 남의 팀 그룹으로는 미검증. 코드상으로만 보장된다.
- **`TEST_BYPASS` 고정 OTP 2건** — Play 심사용으로 유지 중. 오픈 후 정리 대상.

---

## 변경 이력
- v1 (2026-08-12): Phase 3 A·B·C 서버측 완료 기록. 앱 화면 착수 근거.
