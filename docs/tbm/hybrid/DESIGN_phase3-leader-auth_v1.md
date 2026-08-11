---
doc: DESIGN_phase3-leader-auth_v1
class: plans
type: DESIGN
scope: tbm
project: hybrid
title: Phase 3 조사 결과 및 리더 인증·스코프 설계
version: 1
status: ACTIVE
owner: taiwang
created: 2026-08-11
supersedes_decisions_in: WORKORDER_phase3-leader-mobile_v1 §5
tags: [tbm, leader, auth, scope, otp, rbac]
---

# Phase 3 — 조사 결과 및 리더 인증·스코프 설계

- 선행 지시서: `docs/tbm/hybrid/WORKORDER_phase3-leader-mobile_v1.md` (5ac2ce01)
- 조사 방법: tai-api 소스 직독 + DB 실측 (`vwlahtguyggrhvslabax`)
- 이 문서는 지시서 3절이 요구한 조사의 결과이며, 5절 미결정 5건에 대한 결론을 담는다.

---

## 1. 조사 결과 — 지시서 전제와 다른 사실

### 1-1. `role_data_scope` 에 `scope_value` 가 없다

지시서 A-3은 "scope_type/scope_value 형태 추정, 확인 필요"라 했다. 실제 컬럼은 다음과 같다.

```
id · role_code · scope_type · scope_desc · created_at
```

**특정 team_id 를 저장할 자리가 없다.** 기존 데이터를 보면 이 테이블의 용법이 드러난다.

| role_code | scope_type | scope_desc |
|---|---|---|
| 001 | ALL | 전체 데이터 접근 |
| 002 | COMPANY | 자기 회사 전체 |
| 003 | FACTORY | 자기 공장 전체 |
| **004** | **TEAM** | **자기 팀 데이터** |
| 005~007 | ASSIGNED | 배정된 시설/작업/점검만 |

즉 이 테이블은 **"어느 등급까지 보는가"만 정의**하고, 실제 경계값은 `users.team_id`·`company_id`·`factory_id` 에서 가져오는 구조다. `TEAM` 스코프는 이미 정의되어 있으므로 새 개념을 만들 필요가 없다.

### 1-2. 리더 role 이 이미 있다

`roles` 에 **`013 관리감독자`**(산안법 제16조, users 2명 배정)가 존재한다. 지시서가 제안한 `TBM_LEADER` 를 새로 만들 필요가 없다.

다만 `role_data_scope` 에는 001~008만 있고 **013 정의가 없다.** `('013','TEAM')` 한 행 추가가 필요하다.

### 1-3. 조직 데이터 (2026-08-11 목업 투입 후)

```
departments 3 · teams 1(사출팀) · groups 1(후공정반) · worker_group 2
사출팀 lead_worker_id = 김태형(010-3001-1002)
worker_group.is_lead  = 0건 (팀 리더가 있으므로 진행에 지장 없음)
users.team_id         = 0건  ← 스코프 기준값 미설정
worker_registry.user_id = 0건 ← A단계 배선 대상
```

### 1-4. 인증 — Supabase auth (확정)

`routers/auth.py` v3.7.0 전체가 Supabase GoTrue 위에 있다.

- `POST /auth/login` — `sign_in_with_password` → `access_token` 반환. 실패 시 `password_hash`(bcrypt) 폴백 후 GoTrue 계정 복구.
- 검증 — `supabase.auth.get_user(token)` → `users.auth_id` 조회.
- `get_current_user()` Depends 함수가 이미 있다.

**자체 JWT 를 만들 이유가 없다. 기존 방식에 편승한다.**

---

## 2. 핵심 판단 — OTP 인증과 세션의 분리

### 2-1. 현재 동작 (구자산·신자산 동일)

`POST /auth/verify-otp` 는 `otp_store` 에서 `phone` 으로 행을 찾아 `otp` 값과 만료를 대조한다. **인증 로직 자체는 올바르다.** 본인 기기로 수신한 문자를 확인해야 통과하므로, 최초 인증 강도는 아이디·비밀번호와 동등하거나 그 이상이다.

문제는 **통과 이후**다.

- 대조 성공 시 사용자 정보(dict)만 반환하고 **토큰을 발급하지 않는다.**
- 검증에 쓰인 `otp_store` 행은 곧바로 삭제된다(소모).
- 앱은 응답을 `localStorage.tai_user` 에 저장하고, 이후 요청에는 `phone` 문자열만 싣는다.
- `_utils.js` 의 `getToken()` 은 항상 빈 문자열이라 `Authorization` 헤더가 붙지 않는다.

즉 **인증은 한 번 제대로 하지만, 그 사실을 이후 요청에 이어붙일 수단이 없다.** 서버 입장에서 아래 두 요청이 구분되지 않는다.

```
{"phone":"01030011002", ...}   ← OTP 를 통과한 본인
{"phone":"01030011002", ...}   ← 번호만 아는 제3자
```

앱을 거치지 않고 API 를 직접 호출하면 인증 단계 자체를 건너뛴다.

### 2-2. 작업자에게는 허용됐던 이유

작업자는 자기 점검을 제출하고 자기 이력을 보는 범위라 위험이 제한적이었다. 그래서 신설 작업자 라우터(`worker_reports`·`worker_assets`·`worker_permits`)도 `_optional_auth` 로 만들어 토큰이 없어도 동작하게 했다.

### 2-3. 리더에게는 성립하지 않는다

리더는 **"이 팀의 TBM 을 만들 수 있다 / 남의 팀은 볼 수 없다"** 는 판정 대상이다. 그 판정 근거가 클라이언트가 보낸 값이면, 요청 바디의 `phone` 이나 `team_id` 를 바꾸는 것만으로 남의 팀에 접근된다.

지시서 4절의 **"서버측 role_data_scope 강제 — 클라이언트 신뢰 금지"** 가 바로 이 지점이다.

### 2-4. 채택안 — `verify-otp` 가 토큰을 함께 발급

**인증 방식은 바꾸지 않는다.** 전화번호 인증을 그대로 두고, 대조 통과 시 `access_token` 을 함께 반환한다.

토큰은 새로운 인증 수단이 아니라 **"이 사람은 방금 번호·인증번호 대조를 통과했다"는 서버 발급 증서**다. 강한 인증을 한 번 하고 그 결과를 이후 요청에 이어붙이는 것이다.

- 사용자 경험은 동일하다. 앱이 토큰을 저장하고 헤더에 붙이는 것뿐이라 **자동 로그인도 그대로**다.
- 오히려 토큰 만료가 생겨 기기 분실 시 안전해진다.
- 작업자·리더가 **같은 인증 모델**을 쓰게 되어 앱이 하나로 유지된다.

---

## 3. 미결정 5건 — 결론

| # | 항목 | 결론 | 근거 |
|---|---|---|---|
| 1 | 앱 인증 방식 | **Supabase auth 편승** | `auth.py` 전체가 GoTrue 기반. 자체 JWT 불필요 |
| 2 | 초대 채널 | **카카오 우선, 실패 시 SMS** | 사용자 결정 |
| 3 | 리더 role·스코프 | **`013 관리감독자` + `role_data_scope('013','TEAM')`** | 013 이 이미 존재. TEAM 스코프도 정의돼 있음 |
| 4 | 즉석 TBM | **허용 (수동 입력 가능)** | 사용자 결정 |
| 5 | 단일앱 vs 별도진입 | **단일앱 · 서버 role 판정** | 토큰 도입으로 인증 모델이 하나가 됨 |

### 5번 보충 — 앱은 트리거

앱은 화면과 로직을 갖는 주체가 아니라, **서버가 판정한 결과를 띄우고 결과를 되돌려주는 층**으로 둔다. role 분기·스코프 필터·소집 대상은 전부 서버가 결정한다.

이 관점은 앞선 작업자앱 경험에서 나온 것이다. 홈 지표를 localStorage 로 세다가 서버 상태와 어긋났고, 점검항목을 하드코딩해 현장별 조정도 다국어도 막혔다. 판단을 서버로 올리면 그런 어긋남이 구조적으로 사라진다.

---

## 4. A단계 설계 — 계정 배선

### A-1. `verify-otp` 토큰 발급

기존 응답 형태를 유지하면서 `access_token`·`refresh_token` 을 추가한다. 기존 앱이 깨지지 않는다.

절차는 다음과 같다.

1. OTP 대조 (현행 유지)
2. `users` 에서 `phone` 조회
3. 계정이 없으면 생성 — GoTrue 는 email 필수이므로 **가상 이메일** 을 쓴다: `{phone}@worker.taieng.co.kr`. `admin.create_user` 로 만들고 `users.auth_id` 연결.
4. 계정이 있으나 `auth_id` 가 없으면 동일하게 생성·연결 (`login` 의 GoTrue 복구 패턴 재사용)
5. 세션 발급 → `access_token` 반환
6. `worker_registry` 에서 같은 `phone` 행을 찾아 `user_id`·`app_installed` 세팅

**중복 계정 방지** — `phone` 정규화(`normalize_phone`) 후 조회하며, `users.phone` 과 `worker_registry.phone` 의 하이픈 유무가 섞여 있으므로 양쪽 형식으로 조회한다(`worker_check.py` 관례).

### A-2. 리더 식별

리더 = `teams.lead_worker_id` 인 worker 의 `user_id`. 해당 `users` 행에 다음을 세팅한다.

- `role_code = '013'`
- `team_id = teams.id`

`users.team_id` 가 스코프 필터의 기준값이 된다.

### A-3. 스코프 강제

`role_data_scope` 에 `('013','TEAM')` 추가. 리더용 조회·생성 API 는 토큰에서 도출한 `users.team_id` 로 필터한다. **요청 바디의 team_id 를 신뢰하지 않는다.**

---

## 5. 남은 확인 사항

- 작업자 10명 중 `users` 계정 보유자 수 — A-1 의 계정 생성 분량을 좌우한다.
- 가상 이메일 도메인 확정 (`@worker.taieng.co.kr` 제안)
- 카카오 알림톡 발송 경로 — 기존 연동이 있는지 확인 필요 (NOT FOUND 시 SMS 우선 구현 후 추가)
- `POST /workers/fcm-token` 이 `worker_registry.push_token` 과 `users.push_token` 중 어디에 저장하는지 — 푸시 대상 해석에 영향

---

## 변경 이력
- v1 (2026-08-11): 조사 결과 및 미결정 5건 결론. A단계 설계 확정.
