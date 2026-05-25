# 로그인 시스템 전면 수정 작업지시

> 작성일: 2026-05-25
> 목표: 이메일 + 핸드폰 둘 다 로그인 가능하게
> 심각도: P0 (SaaS 전체 차단 중)

---

## 현재 문제

GoTrue `sign_in_with_password`만 사용 중인데, SQL로 생성한 계정은 GoTrue가 인식 못함.
결과적으로 **이메일+비밀번호로 로그인 가능한 계정이 0개**.

### 현재 로그인 플로우 (auth.py POST /auth/login)
```
1. login_id에 "@" 있으면 → public.users에서 email로 조회
   login_id에 "@" 없으면 → public.users에서 phone으로 조회
2. 조회된 user의 email을 가져옴
3. supabase.auth.sign_in_with_password({email, password}) 호출
4. 실패 시 401 반환
```

### 문제점
| 문제 | 설명 |
|------|------|
| GoTrue 의존 | SQL로 만든 auth.users는 GoTrue가 인식 못함 |
| identity 누락 | auth.identities에 email provider 없으면 로그인 불가 |
| password_hash 미사용 | public.users.password_hash을 아예 안 보고 있음 |
| 계정 20개 중 0개 로그인 가능 | 실질적으로 SaaS 사용 불가 |

## 수정 방향

### 로그인 플로우 변경 (routers/auth.py)

```
1. login_id에 "@" 있으면 → public.users에서 email로 조회
   login_id에 "@" 없으면 → public.users에서 phone으로 조회
2. 조회된 user의 email을 가져옴
3. [1차] supabase.auth.sign_in_with_password({email, password}) 시도
4. [1차 성공] → 기존과 동일하게 JWT 발급
5. [1차 실패] → [2차] public.users.password_hash로 bcrypt 검증
6. [2차 성공] → GoTrue 계정 자동 복구 (admin API) + JWT 발급
7. [2차 실패] → 401 반환
```

### 구체 구현

#### Step 1: bcrypt 폴백 추가

`routers/auth.py`의 `login()` 함수에서:

```python
import bcrypt

# ... 기존 코드: user 조회 완료 ...

# 1차: GoTrue 시도
try:
    auth_res = supabase.auth.sign_in_with_password({"email": login_email, "password": req.password})
except Exception:
    auth_res = None

if auth_res and auth_res.user and auth_res.session:
    # GoTrue 성공 → 기존 플로우
    pass
else:
    # 2차: password_hash 폴백
    pw_hash = user.get("password_hash")
    if not pw_hash:
        raise HTTPException(status_code=401, detail="비밀번호가 올바르지 않습니다")
    
    if not bcrypt.checkpw(req.password.encode('utf-8'), pw_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="비밀번호가 올바르지 않습니다")
    
    # password_hash 일치 → GoTrue 계정 복구
    try:
        supabase_admin = get_supabase_admin()
        # auth.users에 이미 있으면 비밀번호 업데이트
        if user.get("auth_id"):
            supabase_admin.auth.admin.update_user_by_id(
                user["auth_id"],
                {"password": req.password}
            )
        else:
            # auth.users 없으면 생성
            new_auth = supabase_admin.auth.admin.create_user({
                "email": login_email,
                "password": req.password,
                "email_confirm": True
            })
            # auth_id 연결
            supabase.table("users").update({
                "auth_id": str(new_auth.user.id),
                "updated_at": _now_iso()
            }).eq("id", user["id"]).execute()
        
        # 복구 후 다시 sign_in
        auth_res = supabase.auth.sign_in_with_password({
            "email": login_email,
            "password": req.password
        })
    except Exception as e:
        logger.warning(f"GoTrue 복구 실패: {e}")
        raise HTTPException(status_code=401, detail="로그인 실패")
```

#### Step 2: 사용자 조회 시 password_hash 포함

현재 조회:
```python
rows = supabase.table("users").select(
    "id, email, name, phone, role_code, company_id, factory_id, status_code, profile_image_url"
).eq("email", identifier).limit(1).execute()
```

변경: **password_hash, auth_id** 추가
```python
rows = supabase.table("users").select(
    "id, email, name, phone, role_code, company_id, factory_id, status_code, profile_image_url, password_hash, auth_id"
).eq("email", identifier).limit(1).execute()
```

phone 조회도 동일하게 변경.

#### Step 3: 테스트 계정 password_hash 설정

모든 테스트 계정에 password_hash 설정:
```sql
UPDATE public.users
SET password_hash = crypt('tai1234!', gen_salt('bf', 12))
WHERE password_hash IS NULL AND is_active = true;
```

## 테스트 계정

| 이메일 | 전화번호 | 비밀번호 | 역할 | factory_id |
|--------|----------|----------|------|------------|
| saas-test@taieng.co.kr | 01099990001 | safe1234 | 안전관리자 | c1938931... (점검항목 3건) |
| safety-mgr@korean-safe.co.kr | 010-1111-2222 | tai1234! | 안전관리자 | cc000003... |
| admin@tai.com | 01011112222 | tai1234! | 관리자 | b3ef791c... |

## 검증

```bash
# 이메일로 로그인
curl -s -X POST https://api.taieng.co.kr/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"login_id": "saas-test@taieng.co.kr", "password": "safe1234"}' | python3 -m json.tool | head -10

# 전화번호로 로그인
curl -s -X POST https://api.taieng.co.kr/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"login_id": "01099990001", "password": "safe1234"}' | python3 -m json.tool | head -10
```

둘 다 `status: success` + `access_token` 반환되어야 함.

## 배포

```bash
cd ~/tai-api
git add -A
git commit -m "fix: 로그인 시스템 — GoTrue + password_hash 폴백, 이메일/핸드폰 둘 다 지원"
git push origin main
railway up
curl -X POST https://api.taieng.co.kr/cron/reload
```

## 주의

- `bcrypt` 패키지 필요 — requirements.txt에 이미 있는지 확인, 없으면 `pip install bcrypt`
- GoTrue 복구는 로그인 시 한 번만 실행됨 (다음부터는 GoTrue 직접 로그인)
- password_hash 응답에 노출 금지 (조회 후 응답 전 제거)
- 엔진 파일 절대 수정 금지
