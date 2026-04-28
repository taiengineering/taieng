# Cursor 작업지시서: taieng.co.kr 로그인 — 기존 auth API 연결

> **프론트 레포**: `taiengineering/taieng` → `nexas/log-in.html` (21KB)
> **백엔드 레포**: `taiengineering/tai-api` → `routers/auth.py` (28KB, 기존)
> **원칙**: 프론트에 Supabase anon key 노출하지 않음. 백엔드 API 경유.

---

## 현재 상태

- `log-in.html`에 `doLogin()` 함수 존재 (1055자)
- 로그인 버튼: `onclick="doLogin()"`
- 입력 필드: `#login-id` (이메일/휴대폰), `#login-pw` (비밀번호)
- **문제**: Supabase JS 미로드 → 인증 호출 실패

## 해결 방향

`doLogin()`을 **기존 백엔드 auth API** (`taieng.co.kr/_api/auth/...`)를 호출하도록 수정.
Supabase CDN 불필요 — 백엔드에서 처리.

## STEP 1: 백엔드 auth.py 엔드포인트 확인

```bash
grep -n 'def \|@router\.' routers/auth.py | head -30
```

로그인 엔드포인트 확인 (예: `POST /auth/login`, `POST /auth/signin` 등).
요청 형식과 응답 형식 파악.

## STEP 2: doLogin() 함수 수정

```javascript
async function doLogin() {
  var loginId = document.getElementById('login-id').value.trim();
  var password = document.getElementById('login-pw').value;

  if (!loginId || !password) {
    alert('이메일과 비밀번호를 입력해주세요.');
    return;
  }

  try {
    // 백엔드 auth API 호출 (Cloudflare 프록시 경유)
    var res = await fetch('https://taieng.co.kr/_api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: loginId, password: password })
    });

    var data = await res.json();

    if (data.status !== 'success' || !data.data) {
      alert('로그인 실패: ' + (data.detail || data.message || '이메일/비밀번호를 확인해주세요.'));
      return;
    }

    // 로그인 성공 — localStorage에 사용자 정보 저장
    var user = data.data;
    localStorage.setItem('tai_user_id', user.id || user.user_id);
    localStorage.setItem('tai_user_email', user.email || loginId);
    if (user.access_token) localStorage.setItem('tai_access_token', user.access_token);

    // redirect 파라미터가 있으면 해당 페이지로 이동
    var params = new URLSearchParams(window.location.search);
    var redirect = params.get('redirect');
    window.location.href = redirect || '/';
  } catch (e) {
    alert('로그인 오류: ' + e.message);
  }
}
```

> **주의**: `fetch` URL과 요청 body 형식은 STEP 1에서 확인한 실제 auth.py 엔드포인트에 맞춰 조정.

## STEP 3: 회원가입 함수도 동일 패턴

```javascript
async function doRegister() {
  // ... 입력값 검증 ...
  var res = await fetch('https://taieng.co.kr/_api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name, phone })
  });
  // ... 응답 처리 ...
}
```

## STEP 4 (필요시): auth.py에 로그인 엔드포인트 추가

기존 auth.py에 `POST /auth/login` 엔드포인트가 없다면 추가:

```python
@router.post("/login")
async def login(body: dict):
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_in_with_password({
            "email": body["email"],
            "password": body["password"]
        })
        return {
            "status": "success",
            "data": {
                "id": res.user.id,
                "email": res.user.email,
                "access_token": res.session.access_token
            }
        }
    except Exception as e:
        raise HTTPException(400, str(e))
```

## 검증

1. `taieng.co.kr/log-in` 접속
2. 이메일/비밀번호 입력 → 로그인 클릭
3. `taieng.co.kr/_api/auth/login` API 호출 확인 (Network 탭)
4. 로그인 성공 → redirect URL로 이동
