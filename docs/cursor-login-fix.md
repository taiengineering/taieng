# Cursor 작업지시서: taieng.co.kr 로그인 페이지 수정

> **레포**: `taiengineering/taieng`
> **파일**: `nexas/log-in.html` (21KB)
> **문제**: 로그인 버튼(`doLogin()`) 클릭 시 아무 반응 없음
> **원인**: Supabase JS 라이브러리 미로드 (`createClient` 미정의)

---

## 변경 1: Supabase JS CDN 추가

`</head>` 직전에 추가:

```html
<!-- Supabase Auth -->
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>
<script>
  var SUPABASE_URL = 'https://vwlahtguyggrhvslabax.supabase.co';
  var SUPABASE_ANON_KEY = '여기에_anon_key_입력';
  var _sb = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
</script>
```

> **anon key 확인**: Supabase Dashboard → Settings → API → Project API keys → `anon` `public`

## 변경 2: doLogin() 함수 — Supabase signInWithPassword 연결

현재 `doLogin()` 함수가 Supabase 클라이언트를 참조하는 방식을 확인 후, `_sb`로 연결:

```javascript
async function doLogin() {
  var email = document.getElementById('login-id').value.trim();
  var password = document.getElementById('login-pw').value;
  
  if (!email || !password) {
    alert('이메일과 비밀번호를 입력해주세요.');
    return;
  }

  try {
    var { data, error } = await _sb.auth.signInWithPassword({
      email: email,
      password: password
    });

    if (error) {
      alert('로그인 실패: ' + error.message);
      return;
    }

    // 로그인 성공 — localStorage에 사용자 정보 저장
    localStorage.setItem('tai_user_id', data.user.id);
    localStorage.setItem('tai_user_email', data.user.email);
    localStorage.setItem('tai_access_token', data.session.access_token);

    // redirect 파라미터가 있으면 해당 페이지로 이동
    var params = new URLSearchParams(window.location.search);
    var redirect = params.get('redirect');
    window.location.href = redirect || '/';
  } catch (e) {
    alert('로그인 오류: ' + e.message);
  }
}
```

## 변경 3: 회원가입 함수도 확인

`#reg-name`, `#reg-email`, `#reg-phone`, `#reg-pw` 입력 필드가 있으므로, 회원가입 함수도 Supabase `_sb.auth.signUp()` 연결 필요.

```javascript
async function doRegister() {
  var name = document.getElementById('reg-name').value.trim();
  var email = document.getElementById('reg-email').value.trim();
  var phone = document.getElementById('reg-phone').value.trim();
  var pw = document.getElementById('reg-pw').value;
  var pw2 = document.getElementById('reg-pw2').value;

  if (pw !== pw2) { alert('비밀번호가 일치하지 않습니다.'); return; }
  if (pw.length < 8) { alert('비밀번호는 8자 이상이어야 합니다.'); return; }

  try {
    var { data, error } = await _sb.auth.signUp({
      email: email,
      password: pw,
      options: {
        data: { name: name, phone: phone }
      }
    });

    if (error) { alert('회원가입 실패: ' + error.message); return; }

    alert('회원가입 완료! 이메일 인증 후 로그인해주세요.');
  } catch (e) {
    alert('회원가입 오류: ' + e.message);
  }
}
```

## 검증

1. `taieng.co.kr/log-in` 접속
2. 이메일/비밀번호 입력 → 로그인 클릭
3. Supabase 인증 성공 → redirect URL로 이동
4. 브라우저 콘솔에 에러 없음 확인

## 참고

- Supabase 서울 프로젝트: `vwlahtguyggrhvslabax`
- safe.taieng.co.kr 로그인은 같은 Supabase 프로젝트 사용
- anon key는 공개 키이므로 프론트엔드에 노출 가능
