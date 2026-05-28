# free-diagnosis.html 본인인증 연동 수정 — Cursor 작업지시서

> 작성일: 2026-05-28
> 대상: `taieng/nexas/free-diagnosis.html`
> 목적: startAuth() 함수를 이니시스 SA API(`/auth/inicis/request`)로 교체

---

## 현재 코드 (삭제 대상)

### 1. `startAuth()` 함수 전체 교체

현재:
```javascript
async function startAuth() {
  const btn = document.getElementById('btnAuth');
  btn.disabled = true; btn.textContent = '준비 중...';
  try {
    const r = await fetch(`${API}/diagnosis/auth/prepare`, { method: 'POST' });
    if (r.status === 503) {
      alert('본인인증 서비스를 일시적으로 이용할 수 없습니다. 잠시 후 다시 시도해주세요.');
      btn.disabled = false; btn.textContent = '본인 확인 시작 →'; return;
    }
    const json = await r.json();
    openInicisPopup(json.data);
  } catch(e) {
    alert('오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    btn.disabled = false; btn.textContent = '본인 확인 시작 →';
  }
}
```

변경 후:
```javascript
async function startAuth() {
  const btn = document.getElementById('btnAuth');
  btn.disabled = true; btn.textContent = '준비 중...';
  try {
    const r = await fetch(`${API}/auth/inicis/request`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ svc_code: '01', fixed_user: false })
    });
    if (!r.ok) {
      const errJson = await r.json().catch(() => ({}));
      alert(errJson.detail || '본인인증 요청 실패');
      btn.disabled = false; btn.textContent = '본인 확인 시작 →'; return;
    }
    const json = await r.json();
    const data = json.data;
    window._pendingMtxId = data.mtx_id;

    // 폼 생성 + 팝업으로 제출
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = data.form_action;
    form.target = 'inicisAuthPopup';
    form.acceptCharset = 'utf-8';

    Object.keys(data.form_params || {}).forEach(function(key) {
      var input = document.createElement('input');
      input.type = 'hidden';
      input.name = key;
      input.value = data.form_params[key];
      form.appendChild(input);
    });

    window.open('', 'inicisAuthPopup',
      'width=' + (data.popup_width || 400) + ',height=' + (data.popup_height || 640));
    document.body.appendChild(form);
    form.submit();
    form.remove();

    btn.disabled = false; btn.textContent = '본인 확인 시작 →';
  } catch(e) {
    alert('오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    btn.disabled = false; btn.textContent = '본인 확인 시작 →';
  }
}
```

### 2. `openInicisPopup()` 함수 삭제

아래 함수 전체 삭제:
```javascript
function openInicisPopup(params) {
  if (typeof INIStdPay !== 'undefined') { INIStdPay.pay(params); }
  else { onAuthSuccess({ auth_token: 'DEV_TOKEN_' + Date.now() }); }
}
```

### 3. `onAuthCallback()` 함수 삭제

아래 함수 전체 삭제:
```javascript
window.onAuthCallback = async function(callbackData) {
  try {
    const r = await fetch(`${API}/diagnosis/auth/callback`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(callbackData)
    });
    const json = await r.json();
    if (json.data?.auth_token) await onAuthSuccess(json.data);
  } catch(e) {}
};
```

### 4. postMessage 리스너 추가

`init()` IIFE 내부 또는 `<script>` 상단에 추가:

```javascript
// 이니시스 팝업 결과 수신
window.addEventListener('message', async function(e) {
  if (!e.data || e.data.type !== 'INICIS_AUTH_RESULT') return;
  if (e.data.success && e.data.mtxId) {
    try {
      // 인증 결과 조회
      const r = await fetch(`${API}/auth/inicis/result/${encodeURIComponent(e.data.mtxId)}`);
      const json = await r.json();
      const d = json.data || {};
      if (d.status === 'SUCCESS') {
        // 기존 onAuthSuccess 흐름과 연결
        // auth_token으로 mtx_id 사용 (무료진단 횟수 관리용)
        await onAuthSuccess({ auth_token: d.mtx_id });
      } else {
        alert('인증에 실패했습니다: ' + (d.result_msg || ''));
      }
    } catch(err) {
      alert('인증 결과 조회 실패');
    }
  } else if (e.data.type === 'INICIS_AUTH_RESULT' && !e.data.success) {
    alert(e.data.message || '인증에 실패했습니다.');
    const btn = document.getElementById('btnAuth');
    if (btn) { btn.disabled = false; btn.textContent = '본인 확인 시작 →'; }
  }
});
```

### 5. `onAuthSuccess()` 함수는 그대로 유지

`onAuthSuccess(data)` 함수는 `auth_token`을 받아서 횟수 체크 + 다음 스텝 이동을 처리하므로 그대로 유지.

`auth_token` 값으로 `mtx_id`를 전달하면 기존 `/diagnosis/auth/check?auth_token=` API와 호환.

---

## 요약

| 변경 | 내용 |
|---|---|
| `startAuth()` | `/diagnosis/auth/prepare` → `/auth/inicis/request` + 폼 팝업 방식 |
| `openInicisPopup()` | 삭제 (팝업 로직이 startAuth 내로 통합) |
| `onAuthCallback()` | 삭제 (postMessage로 대체) |
| postMessage 리스너 | 신규 추가 — INICIS_AUTH_RESULT 수신 → onAuthSuccess 호출 |
| `onAuthSuccess()` | 변경 없음 (그대로 유지) |

## 주의사항

- taieng 레포 `main` 직접 커밋 (Cloudflare Pages 자동배포)
- `INIStdPay` 관련 코드가 있으면 전부 제거 (구버전 PG 결제 모듈)
- 테스트 MID(INIiasTest)로는 팝업 UI 흐름만 확인 가능
