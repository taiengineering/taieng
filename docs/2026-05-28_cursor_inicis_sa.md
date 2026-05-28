# KG이니시스 통합인증서비스(SA) 연동 — Cursor 작업지시서

> 작성일: 2026-05-28
> 대상 레포: tai-api (백엔드) + tai-admin (프론트)
> 목적: 본인인증 연동 — 테스트 키로 개발, 완료 후 실 키 교체

---

## API 스펙 (매뉴얼 기반)

### 연동 흐름 (4단계)

```
[FE] 본인인증 버튼 클릭
    ↓
[BE] POST /auth/inicis/request → 이니시스 요청 파라미터 생성 (authHash 등)
    ↓ JSON 응답: { formAction, formParams }
[FE] 폼 자동 제출 → 팝업 열림 (400x640)
    ↓ 사용자 인증 수행
[INICIS] → successUrl / failUrl 호출
    ↓
[BE] GET /auth/inicis/callback/success → txId 수신
    ↓
[BE] SERVER-to-SERVER: POST authRequestUrl { mid, txId } → 결과 조회
    ↓ SEED 복호화 → userName, userPhone, userBirthday, userCi, userDi 저장
    ↓
[FE] 팝업에서 opener.postMessage → 부모창에 결과 전달
```

### STEP1: 통합인증 요청

- 간편인증: `POST https://sa.inicis.com/auth`
- 본인확인: `POST https://sa.inicis.com/id/auth`
- Content-Type: `application/x-www-form-urlencoded;charset=utf-8`

| 파라미터 | 설명 | 필수 |
|---|---|---|
| mid | 상점아이디 | * |
| reqSvcCd | "01":간편인증, "02":전자서명, "03":본인확인 | * |
| mTxId | 가맹점 트랜잭션 ID (유일값, 20byte) | * |
| successUrl | 인증성공 콜백 URL | * |
| failUrl | 인증실패 콜백 URL | * |
| authHash | SHA256(mid + mTxId + apikey) | * |
| flgFixedUser | "Y" or "N" | * |
| userName | flgFixedUser=Y일 때 필수 | |
| userPhone | flgFixedUser=Y일 때 필수 | |
| userBirth | YYYYMMDD, flgFixedUser=Y일 때 필수 | |
| userHash | SHA256(userName+mid+userPhone+mTxId+userBirth+reqSvcCd), flgFixedUser=Y일 때 필수 | |
| reservedMsg | "isUseToken=Y" 고정 | * |
| logoUrl | 로고 URL (164x28) | |

### STEP2: 통합인증 응답 (successUrl/failUrl로 수신)

| 파라미터 | 설명 |
|---|---|
| resultCode | "0000":성공, 이외 실패 |
| resultMsg | UTF-8 urlEncoded |
| authRequestUrl | 결과조회 URL (**이니시스 URL 검증 필수**) |
| txId | 트랜잭션 ID |
| token | Base64 (인증 토큰) |

### STEP3: 결과조회 요청 (Server-to-Server)

- URL: STEP2에서 받은 authRequestUrl
- Method: POST
- Content-Type: `application/json;charset=utf-8`
- **반드시 HTTPS S2S 통신**
- Timeout 권고: 5초

```json
{ "mid": "INIiasTest", "txId": "..." }
```

### STEP4: 결과조회 응답

| 파라미터 | 설명 | 암호화 |
|---|---|---|
| resultCode | "0000":성공 | - |
| resultMsg | 결과메시지 | - |
| txId | 트랜잭션 ID | - |
| mTxId | 가맹점 트랜잭션 ID | - |
| svcCd | "01"/"02"/"03" | - |
| userName | 사용자 이름 | SEED |
| userPhone | 휴대폰번호 | SEED |
| userBirthday | 생년월일 | SEED |
| userCi | CI 데이터 | SEED |
| userDi | DI 데이터 (본인확인만) | SEED |
| userGender | M/F (본인확인만) | SEED |
| isForeign | 0/1 (본인확인만) | SEED |

### 암호화

- 알고리즘: **SEED-128-CBC** (PKCS5Padding)
- KEY: API KEY (Base64 디코딩 후 사용)
- IV: SEED IV (16바이트 문자열)
- 복호화 결과: Base64 디코딩 → SEED 복호화 → 평문

### 방화벽

| 항목 | 값 |
|---|---|
| URL | fcsa.inicis.com, kssa.inicis.com |
| IP | 118.129.210.217, 183.109.71.217 |
| PORT | 443 |
| 방향 | OUTBOUND |
| 프로토콜 | TLS 1.2+ |

---

## 테스트 키 (환경변수)

```env
# .env (tai-api)
INICIS_SA_MID=INIiasTest
INICIS_SA_API_KEY=TGdxb2l3enJDWFRTbTgvREU3MGYwUT09
INICIS_SA_SEED_IV=SASKGINICIS00000
INICIS_SA_MODE=test
```

실 키 교체 시 `INICIS_SA_MID=taieng4ias` + iniweb.inicis.com에서 확인한 API KEY/SEED IV로 변경.

---

## 구현 파일 목록

### tai-api (백엔드)

#### 1. `routers/inicis_auth.py` (신규)

```python
"""
inicis_auth.py — KG이니시스 통합인증서비스 연동

API:
  POST /auth/inicis/request          인증요청 파라미터 생성
  GET  /auth/inicis/callback/success  성공 콜백 수신 + S2S 결과조회 + DB 저장
  GET  /auth/inicis/callback/fail     실패 콜백 수신
  GET  /auth/inicis/result/{mtx_id}   인증결과 조회
"""
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import hashlib
import uuid
import os
import httpx
import base64
from datetime import datetime, timezone
from db.supabase_client import get_supabase

router = APIRouter(prefix="/auth/inicis", tags=["inicis_auth"])

# === 환경변수 ===
SA_MID     = os.getenv("INICIS_SA_MID", "INIiasTest")
SA_API_KEY = os.getenv("INICIS_SA_API_KEY", "TGdxb2l3enJDWFRTbTgvREU3MGYwUT09")
SA_SEED_IV = os.getenv("INICIS_SA_SEED_IV", "SASKGINICIS00000")
SA_MODE    = os.getenv("INICIS_SA_MODE", "test")  # test / production

# === URL ===
# 간편인증/전자서명: https://sa.inicis.com/auth
# 본인확인: https://sa.inicis.com/id/auth
SA_AUTH_URL    = "https://sa.inicis.com/auth"
SA_ID_AUTH_URL = "https://sa.inicis.com/id/auth"

# === 콜백 URL (도메인 등록 필수) ===
BASE_URL = os.getenv("API_BASE_URL", "https://api.taieng.co.kr")
SUCCESS_URL = f"{BASE_URL}/auth/inicis/callback/success"
FAIL_URL    = f"{BASE_URL}/auth/inicis/callback/fail"


def _generate_mtx_id() -> str:
    """가맹점 트랜잭션 ID 생성 (20바이트 이내)"""
    return "TAI" + datetime.now().strftime("%y%m%d%H%M%S") + uuid.uuid4().hex[:5].upper()
    # 예: TAI2605281430ABCDE (20자)


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _seed_decrypt(encrypted_b64: str) -> str:
    """
    SEED-128-CBC 복호화.
    KEY = Base64디코딩(API_KEY), IV = SEED_IV (16byte 문자열)

    Python에서 SEED 암호화를 지원하는 라이브러리:
    - pip install pyseedcipher
    - 또는 kisa-seed 패키지
    - 또는 직접 구현 (KISA 참고)

    아래는 구현 패턴:
    """
    from utils.seed_cipher import seed_cbc_decrypt
    key = base64.b64decode(SA_API_KEY)  # 16바이트 키
    iv  = SA_SEED_IV.encode("utf-8")   # 16바이트 IV
    encrypted = base64.b64decode(encrypted_b64)
    decrypted = seed_cbc_decrypt(key, iv, encrypted)
    return decrypted.decode("utf-8")


# === Pydantic 모델 ===
class AuthRequestBody(BaseModel):
    svc_code: str = "01"   # "01":간편인증, "02":전자서명, "03":본인확인
    fixed_user: bool = False
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    user_birth: Optional[str] = None  # YYYYMMDD
    identifier: Optional[str] = None  # 전자서명 시 서명내용


# === STEP1: 인증요청 파라미터 생성 ===
@router.post("/request")
def create_auth_request(body: AuthRequestBody):
    """
    프론트에서 호출.
    이니시스에 직접 POST하지 않고, 폼 파라미터를 생성해서 프론트에 반환.
    프론트가 폼을 만들어서 팝업으로 제출.
    """
    mtx_id = _generate_mtx_id()

    # authHash = SHA256(mid + mTxId + apikey)
    auth_hash = _sha256(SA_MID + mtx_id + SA_API_KEY)

    # 요청 URL 결정
    form_action = SA_ID_AUTH_URL if body.svc_code == "03" else SA_AUTH_URL

    # 폼 파라미터
    params = {
        "mid": SA_MID,
        "reqSvcCd": body.svc_code,
        "mTxId": mtx_id,
        "successUrl": SUCCESS_URL,
        "failUrl": FAIL_URL,
        "authHash": auth_hash,
        "flgFixedUser": "Y" if body.fixed_user else "N",
        "reservedMsg": "isUseToken=Y",
    }

    # 특정 사용자 지정 시
    if body.fixed_user:
        if not all([body.user_name, body.user_phone, body.user_birth]):
            raise HTTPException(400, "fixed_user=true 시 user_name, user_phone, user_birth 필수")
        params["userName"] = body.user_name
        params["userPhone"] = body.user_phone
        params["userBirth"] = body.user_birth
        # userHash = SHA256(userName+mid+userPhone+mTxId+userBirth+reqSvcCd)
        user_hash = _sha256(
            body.user_name + SA_MID + body.user_phone + mtx_id + body.user_birth + body.svc_code
        )
        params["userHash"] = user_hash

    # 전자서명 시 identifier
    if body.svc_code == "02" and body.identifier:
        params["identifier"] = body.identifier

    # DB에 요청 기록 저장
    supabase = get_supabase()
    supabase.table("inicis_auth_requests").insert({
        "mtx_id": mtx_id,
        "svc_code": body.svc_code,
        "status": "REQUESTED",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    return {
        "status": "success",
        "data": {
            "form_action": form_action,
            "form_params": params,
            "mtx_id": mtx_id,
            "popup_width": 400,
            "popup_height": 640,
        }
    }


# === STEP2: 콜백 수신 (successUrl) ===
@router.get("/callback/success")
async def callback_success(request: Request):
    """
    이니시스가 인증 성공 후 리다이렉트하는 URL.
    쿼리 파라미터로 resultCode, resultMsg, authRequestUrl, txId, token 수신.
    """
    params = dict(request.query_params)
    result_code = params.get("resultCode", "")
    result_msg  = params.get("resultMsg", "")
    auth_request_url = params.get("authRequestUrl", "")
    tx_id = params.get("txId", "")
    token = params.get("token", "")

    if result_code != "0000":
        # 실패 응답 → 오류 페이지 표시
        return HTMLResponse(_popup_result_html(False, result_msg))

    # authRequestUrl 검증 (이니시스 도메인 확인)
    if not auth_request_url or "inicis.com" not in auth_request_url:
        return HTMLResponse(_popup_result_html(False, "유효하지 않은 응답 URL"))

    # === STEP3: Server-to-Server 결과조회 ===
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                auth_request_url,
                json={"mid": SA_MID, "txId": tx_id},
                headers={"Content-Type": "application/json;charset=utf-8"}
            )
            data = resp.json()
    except Exception as e:
        return HTMLResponse(_popup_result_html(False, f"결과조회 실패: {str(e)}"))

    if data.get("resultCode") != "0000":
        return HTMLResponse(_popup_result_html(False, data.get("resultMsg", "인증 실패")))

    # === STEP4: 응답 복호화 + DB 저장 ===
    mtx_id = data.get("mTxId", "")
    svc_cd = data.get("svcCd", "")

    try:
        user_name     = _seed_decrypt(data["userName"]) if data.get("userName") else None
        user_phone    = _seed_decrypt(data["userPhone"]) if data.get("userPhone") else None
        user_birthday = _seed_decrypt(data["userBirthday"]) if data.get("userBirthday") else None
        user_ci       = _seed_decrypt(data["userCi"]) if data.get("userCi") else None
        user_di       = _seed_decrypt(data["userDi"]) if data.get("userDi") else None
        user_gender   = _seed_decrypt(data["userGender"]) if data.get("userGender") else None
    except Exception as e:
        return HTMLResponse(_popup_result_html(False, f"복호화 실패: {str(e)}"))

    # DB 저장
    supabase = get_supabase()
    supabase.table("inicis_auth_requests").update({
        "status": "SUCCESS",
        "tx_id": tx_id,
        "svc_cd": svc_cd,
        "provider_dev_cd": data.get("providerDevCd"),
        "user_name": user_name,
        "user_phone": user_phone,
        "user_birthday": user_birthday,
        "user_ci": user_ci,
        "user_di": user_di,
        "user_gender": user_gender,
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }).eq("mtx_id", mtx_id).execute()

    # 팝업에서 부모창으로 결과 전달
    return HTMLResponse(_popup_result_html(True, "본인인증이 완료되었습니다.", mtx_id))


@router.get("/callback/fail")
async def callback_fail(request: Request):
    params = dict(request.query_params)
    result_msg = params.get("resultMsg", "인증 실패")
    mtx_id = params.get("mTxId", "")

    if mtx_id:
        supabase = get_supabase()
        supabase.table("inicis_auth_requests").update({
            "status": "FAILED",
            "result_msg": result_msg,
        }).eq("mtx_id", mtx_id).execute()

    return HTMLResponse(_popup_result_html(False, result_msg))


@router.get("/result/{mtx_id}")
def get_auth_result(mtx_id: str):
    """프론트에서 인증 결과 조회"""
    supabase = get_supabase()
    result = supabase.table("inicis_auth_requests").select(
        "mtx_id, status, user_name, user_phone, user_birthday, user_ci, svc_cd, verified_at"
    ).eq("mtx_id", mtx_id).limit(1).execute()

    if not result.data:
        raise HTTPException(404, "인증 요청을 찾을 수 없습니다.")

    return {"status": "success", "data": result.data[0]}


def _popup_result_html(success: bool, message: str, mtx_id: str = "") -> str:
    """팝업 결과 페이지 HTML — opener에 postMessage 전송 후 닫기"""
    return f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><title>본인인증 결과</title></head>
    <body>
    <script>
      try {{
        window.opener.postMessage({{
          type: 'INICIS_AUTH_RESULT',
          success: {'true' if success else 'false'},
          message: '{message}',
          mtxId: '{mtx_id}'
        }}, '*');
      }} catch(e) {{}}
      setTimeout(function(){{ window.close(); }}, 1500);
    </script>
    <div style="text-align:center;padding:40px;font-family:sans-serif;">
      <h2>{'\u2705 인증 완료' if success else '\u274c 인증 실패'}</h2>
      <p>{message}</p>
      <p style="color:#999;font-size:13px;">이 창은 자동으로 닫힙니다.</p>
    </div>
    </body></html>
    """
```

#### 2. `utils/seed_cipher.py` (신규)

KISA SEED-128-CBC 복호화 유틸리티.

**구현 옵션 3가지 (우선순위순):**

1. **pyseedcipher 패키지 사용** (pip install pyseedcipher)
2. **kisa-seed 패키지 사용** (pip install kisa-seed)
3. **직접 구현** — KISA 공개 참고 코드 (https://seed.kisa.or.kr)

```python
"""
utils/seed_cipher.py — SEED-128-CBC 복호화

우선 pyseedcipher 시도, 없으면 kisa-seed, 없으면 직접 구현.
"""
import base64


def seed_cbc_decrypt(key: bytes, iv: bytes, encrypted: bytes) -> bytes:
    """
    SEED-128-CBC 복호화 + PKCS5 언패딩.
    key: 16바이트, iv: 16바이트, encrypted: 암호문
    """
    try:
        # Option 1: pyseedcipher
        from seedcipher import SeedCipher
        cipher = SeedCipher(key)
        return _pkcs5_unpad(cipher.decrypt_cbc(iv, encrypted))
    except ImportError:
        pass

    try:
        # Option 2: kisa_seed
        from kisa_seed import SEED
        # kisa_seed 라이브러리 사용법에 맞게 구현
        return _pkcs5_unpad(SEED.decrypt_cbc(key, iv, encrypted))
    except ImportError:
        pass

    # Option 3: 직접 구현 (fallback)
    raise ImportError(
        "SEED 복호화 라이브러리가 없습니다. "
        "pip install pyseedcipher 또는 pip install kisa-seed 실행해주세요."
    )


def _pkcs5_unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        return data
    return data[:-pad_len]
```

**주의:** SEED 패키지가 없으면 에러 발생. Railway 배포 전에 `requirements.txt`에 추가 필수:
```
pyseedcipher>=1.0.0
```

또는 패키지가 안되면 AES-128-CBC로 대체 시도 (이니시스가 실제로는 AES 사용하는 경우가 있음):
```python
from Crypto.Cipher import AES
def aes_cbc_decrypt(key, iv, encrypted):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return _pkcs5_unpad(cipher.decrypt(encrypted))
```

#### 3. 라우터 등록

`router_registry/public.py`에 추가:
```python
{"module": "routers.inicis_auth", "prefix": "", "tags": ["inicis_auth"]}
```

#### 4. DB 마이그레이션

Supabase MCP로 실행:
```sql
CREATE TABLE IF NOT EXISTS inicis_auth_requests (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    mtx_id text NOT NULL UNIQUE,
    svc_code text,           -- 01/02/03
    status text DEFAULT 'REQUESTED',  -- REQUESTED/SUCCESS/FAILED
    tx_id text,
    svc_cd text,
    provider_dev_cd text,
    user_name text,
    user_phone text,
    user_birthday text,
    user_ci text,
    user_di text,
    user_gender text,
    result_msg text,
    verified_at timestamptz,
    created_at timestamptz DEFAULT now(),
    -- 연결: 인증 결과를 user와 연결할 때 사용
    user_id uuid REFERENCES auth.users(id),
    company_id uuid
);

CREATE INDEX idx_inicis_auth_mtxid ON inicis_auth_requests(mtx_id);
CREATE INDEX idx_inicis_auth_ci ON inicis_auth_requests(user_ci);
```

#### 5. 환경변수 추가 (Railway)

Railway 에서 환경변수 설정:
```
INICIS_SA_MID=INIiasTest
INICIS_SA_API_KEY=TGdxb2l3enJDWFRTbTgvREU3MGYwUT09
INICIS_SA_SEED_IV=SASKGINICIS00000
INICIS_SA_MODE=test
```

---

### tai-admin (프론트)

#### `tadmin/.../identity-verify.html` (신규)

본인인증 페이지. SaaS 내 마이페이지 또는 독립 페이지로 사용.

**핵심 로직 (JS):**

```javascript
// 인증 요청
async function requestVerify(svcCode) {
    var res = await apiCall('POST', '/auth/inicis/request', {
        svc_code: svcCode,
        fixed_user: false
    });
    var data = res.data;

    // 폼 생성 + 팝업 열기
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = data.form_action;
    form.target = 'inicisAuthPopup';
    form.acceptCharset = 'utf-8';

    Object.keys(data.form_params).forEach(function(key) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = data.form_params[key];
        form.appendChild(input);
    });

    // 팝업 열기
    var popup = window.open('', 'inicisAuthPopup',
        'width=' + data.popup_width + ',height=' + data.popup_height);

    document.body.appendChild(form);
    form.submit();
    form.remove();

    // 결과 수신 대기
    window._pendingMtxId = data.mtx_id;
}

// 팝업에서 postMessage 수신
window.addEventListener('message', async function(e) {
    if (e.data && e.data.type === 'INICIS_AUTH_RESULT') {
        if (e.data.success) {
            // 인증 성공 → 결과 조회
            var result = await apiCall('GET', '/auth/inicis/result/' + e.data.mtxId);
            showToast('success', '본인인증이 완료되었습니다.');
            // UI 업데이트: 이름, 전화번호, 생년월일 표시
            document.getElementById('verifiedName').textContent = result.data.user_name;
            document.getElementById('verifiedPhone').textContent = result.data.user_phone;
            document.getElementById('verifyStatus').textContent = '인증완료';
        } else {
            showToast('error', e.data.message || '인증에 실패했습니다.');
        }
    }
});
```

---

## 배포 순서

1. Supabase: `inicis_auth_requests` 테이블 생성
2. tai-api: `utils/seed_cipher.py` 생성
3. tai-api: `routers/inicis_auth.py` 생성
4. tai-api: `router_registry/public.py`에 라우터 등록
5. tai-api: `requirements.txt`에 `pyseedcipher` 추가
6. Railway: 환경변수 4개 추가
7. Railway: 배포
8. tai-admin: `identity-verify.html` 생성 (테스트용)
9. 이니시스 도메인 등록 확인: `taieng.co.kr` 등록되어 있는지 iniweb.inicis.com에서 확인

## 검증

- [ ] `/auth/inicis/request` 호출 시 폼 파라미터 정상 반환
- [ ] 팝업에서 이니시스 인증창 로드
- [ ] 인증 완료 후 successUrl 콜백 수신
- [ ] S2S 결과조회 성공
- [ ] SEED 복호화 정상 (userName, userPhone, userCi 확인)
- [ ] DB 저장 확인
- [ ] 팝업 → 부모창 postMessage 전달
- [ ] 실패 시나리오 (사용자 취소, 타임아웃)

## 주의사항

- **테스트 MID로 인증 시 실 인증은 되지 않음** (UI 흐름만 테스트)
- **실 MID(taieng4ias)로 테스트 시 인증 성공 건당 요금 발생** — 주의
- SEED 패키지가 설치 안되면 AES-128-CBC로 대체 시도 (seed_cipher.py 내 fallback)
- `tai-admin`에는 dev 브랜치 없음 → main 직접 커밋
- `tai-api`는 dev 브랜치에서 작업 후 PR
