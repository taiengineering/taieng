# [회원 인증] 간편로그인 + 본인인증 통합 — Day 1 (Step 1 완료)

> **본 보고서**: 카카오/네이버/구글 간편로그인 + NICE 본인인증 통합 시작. 작업 범위 정의 + 결정 사항 + Step 1 (DB 마이그레이션) 완료.
> **범위**: 회원 인증 도메인 (TAI 법령엔진과 별개 도메인, 동일 Supabase 프로젝트 활용).
> **마스터 §3.2 정합**: TAI Supabase (`vwlahtguyggrhvslabax`) 활용, DDL = `apply_migration`.

---

## 작업 범위

- **간편가입 + 간편로그인**: 카카오 / 네이버 / 구글 (3개 채널 우선 개발, 페이스북·삼성·Apple 후순위)
- **본인인증**: NICE 평가정보 PASS
- **두 흐름 통합 지원**:
  - **SOCIAL_FIRST** (default): 소셜 로그인 → 가입 → 본인인증 → 활성화
  - **AUTH_FIRST**: 본인인증 → 소셜 로그인 → 가입 (CI 매칭 시 기존 계정 로그인)
- **프론트**: Web (Next.js) 우선, App은 로그인 방식 자체가 달라 후속 (Native SDK)

## 결정 사항 (사용자 OK)

| 항목 | 결정 |
|---|---|
| 본인인증 사업자 | **NICE** |
| 인증 백엔드 | **Supabase Auth** (TAI 인프라 일치) |
| DB | TAI Supabase (`vwlahtguyggrhvslabax`) |
| 프론트 | Web (Next.js) 우선 |
| 흐름 default | **SOCIAL_FIRST** |

---

## Step 1 완료 — DB 마이그레이션 (`auth_user_profile_and_verification_token`)

### 산출 테이블

| 테이블 | 컬럼 | 인덱스 | RLS | 정책 |
|---|---|---|---|---|
| `public.user_profile` | 18 | 5 | ON | select_own + update_own |
| `public.verification_token` | 14 | 3 | ON | (service_role only) |

### 핵심 컬럼

**`user_profile`** (auth.users 1:1 확장):
- 소셜: `social_provider` ('kakao'/'naver'/'google'), `social_provider_id`, `nickname`, `email`
- 본인인증: `ci_hash` (SHA-256 CI), `di_hash`, `real_name`, `birthdate`, `gender`, `phone`, `carrier`, `verification_provider` (default 'NICE')
- 흐름·상태: `signup_flow` ('SOCIAL_FIRST'/'AUTH_FIRST'), `status` ('PENDING_VERIFICATION'/'ACTIVE'/'SUSPENDED'/'DELETED')

**`verification_token`** (AUTH_FIRST 흐름 brigde, 15분 expire):
- `token` (UUID), `ci_hash`, `di_hash`, `real_name`, `birthdate`, `gender`, `phone`, `carrier`
- `used`, `used_at`, `used_by_user_id`, `expires_at`

### 핵심 룰

- **CI 평문 저장 X** — SHA-256 hash. 한국 개보법 정합.
- **ACTIVE 계정 CI UNIQUE** — 한 사람당 ACTIVE 계정 1개 (Partial Unique Index `WHERE status = 'ACTIVE'`)
- **소셜 식별자 UNIQUE** — `(social_provider, social_provider_id)` 조합 (`WHERE status != 'DELETED'`)
- **RLS** — `user_profile` 사용자 본인만 select/update / `verification_token` service_role만 (Edge Function 내부 사용)
- **`updated_at` 자동 갱신** — 트리거 `set_updated_at()`

### 마스터 §2 정합

| 원칙 | 적용 |
|---|---|
| ① LLM 0% | ✅ 결정적 OAuth flow + NICE PASS |
| ② 법령 보전 | ✅ 회원 인증은 별도 도메인, 법령 데이터 영향 0 |
| ③ 누락 0 | Step 1 인프라 단계, 운영 단계 진입 시 monitoring |
| ④ 100% 매핑 | ✅ auth.users 1:1 + verification_token brigde |
| ⑤ 오염=폐기 | ✅ verification_token 15분 expire + used 플래그 / SUSPENDED·DELETED 상태 분리 |
| ⑥ 사용자 검증 부담 0 | ✅ NICE PASS = ground truth (사람 검증 X) |
| ⑦ ground truth 우선 | ✅ NICE 본인확인 + 카카오/네이버/구글 OAuth 표준 |

---

## 작업 단계

| Step | 내용 | 주체 | 상태 |
|---|---|---|---|
| **1** | DB 마이그레이션 | 본 창 (apply_migration) | ✅ **완료** |
| 2 | OAuth Provider 등록 (카카오·네이버 디벨로퍼스 + Google Cloud Console + Supabase 콘솔) | 사용자 | ⏳ 대기 |
| 3 | Supabase Auth 설정 + Edge Function (카카오/네이버 OAuth callback) | 본 창 + Cursor | ⏳ 대기 |
| 4 | NICE 본인인증 통합 (가맹 등록 + Edge Function 표준 흐름) | 사용자 가맹 + Cursor | ⏳ 대기 |
| 5 | 프론트 Next.js 통합 (두 흐름 모두 지원) | Cursor | ⏳ 대기 |

---

## Step 2 — OAuth Provider 등록 가이드 (사용자 작업)

### 도메인 가정 (정정 가능)

- 개발: `http://localhost:3000`
- 운영: 미정 (운영 도메인 결정 시 redirect_uri 추가 등록)

### 1) 카카오 디벨로퍼스 — https://developers.kakao.com/

```
[애플리케이션 추가] → 앱 생성
[앱 설정 → 플랫폼] → Web 도메인 등록 (localhost:3000 + 운영)
[제품 설정 → 카카오 로그인] → 활성화 ON
   Redirect URI:
     - http://localhost:3000/api/auth/callback/kakao
     - https://yourdomain/api/auth/callback/kakao
[제품 설정 → 동의항목]
   - 닉네임 (필수)
   - 이메일 (선택 동의 권장 — 필수 시 가입 거절률 ↑)
[보안 → Client Secret 활성화]
발급: REST API 키 (Client ID) + Client Secret
```

### 2) 네이버 디벨로퍼스 — https://developers.naver.com/

```
[Application → 애플리케이션 등록]
   사용 API: 네이버 아이디로 로그인
   제공 정보: 회원이름 (필수) + 이메일 (필수) + (선택) 별명/프로필
   서비스 환경: PC웹
   서비스 URL: localhost:3000 + 운영
   Callback URL:
     - http://localhost:3000/api/auth/callback/naver
     - https://yourdomain/api/auth/callback/naver
발급: Client ID + Client Secret
```

### 3) Google Cloud Console — https://console.cloud.google.com/

```
[프로젝트] → [APIs & Services → OAuth consent screen]
   User Type: External
   범위: openid + email + profile
[Credentials → Create OAuth 2.0 Client ID → Web]
   Authorized JavaScript origins:
     - http://localhost:3000
     - https://yourdomain
   Authorized redirect URIs (Supabase native):
     - https://vwlahtguyggrhvslabax.supabase.co/auth/v1/callback
발급: Client ID + Client Secret
```

### 4) Supabase 콘솔 — https://supabase.com/dashboard/project/vwlahtguyggrhvslabax/auth/providers

```
Google: Enable + Client ID + Secret 입력 (native provider)
Kakao: 비활성화 유지 (Edge Function 처리, native 미지원)
Naver: 비활성화 유지 (동일)
```

### 5) Edge Function 환경 변수 — Supabase 콘솔

```
[Project Settings → Edge Functions → Secrets]
   KAKAO_CLIENT_ID = (REST API 키)
   KAKAO_CLIENT_SECRET = (Client Secret)
   NAVER_CLIENT_ID = (Client ID)
   NAVER_CLIENT_SECRET = (Client Secret)
```

### 보안 주의

- **`client_secret` 본 창에 전달 X** — Supabase 콘솔에만 직접 입력
- 본 창은 코드 작성만, 비밀값은 Supabase Edge Function secrets에만 보관

---

## Step 3 예고 — Edge Function 시안 (Step 2 완료 후 진입)

```
supabase/functions/
  kakao-oauth-callback/    # 카카오 토큰 교환 + Supabase JWT 발급
    index.ts
  naver-oauth-callback/    # 네이버 동일
    index.ts
  nice-verify-callback/    # NICE PASS 결과 처리 → verification_token 발급
    index.ts
```

핵심 흐름:
1. 프론트 → 카카오/네이버 OAuth 인가 → callback에 `code`
2. Edge Function: `code` → access_token 교환 → 사용자 정보 조회
3. Supabase admin API로 `auth.users` 생성/매칭 → JWT 발급
4. 프론트 redirect with JWT → 세션 시작

---

## Step 4 예고 — NICE 본인인증 통합

NICE 평가정보 가맹 후:
- `nice-verify-callback` Edge Function — NICE PASS 결과 (CI/DI/이름/생년월일/성별/통신사) 처리
- SOCIAL_FIRST: 기존 user_profile에 본인인증 정보 추가 + status 'ACTIVE'
- AUTH_FIRST: `verification_token` 신규 발급 (15분 expire)

---

## Step 5 예고 — 프론트 Next.js 통합

```
app/
  auth/
    signup/                  # 회원가입 (SOCIAL_FIRST default)
    verify/                  # 본인인증 (AUTH_FIRST 또는 SOCIAL 후 단계)
    callback/
      kakao/                 # 카카오 OAuth callback
      naver/                 # 네이버 OAuth callback
      google/                # 구글 OAuth callback (Supabase native, 자동)
  middleware.ts              # 세션 검증
lib/
  supabase/
    client.ts                # 브라우저용 supabase-js
    server.ts                # 서버용 (Server Component)
```

---

## Pending 사항

1. **Step 2 OAuth Provider 등록 완료** — 사용자 작업 진행 대기
2. **운영 도메인 결정** — redirect_uri 정정
3. **NICE 가맹 계약** — Step 4 진입 조건
4. **Apple/Facebook/삼성** — 후순위 (요구 시 추가)
5. **Mobile App** — 별도 트랙 (Native SDK + universal link)

---

**END OF DAY 1 — Step 2 사용자 작업 대기.**
