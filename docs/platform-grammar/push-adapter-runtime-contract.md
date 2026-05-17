# Push Adapter Runtime Contract

작성일: 2026-05-17
범위: Push Adapter 책임 정의

---

## Adapter Interface

```python
def send(message: str, context: dict) -> Tuple[bool, Optional[str]]:
    """
    context 필수 필드:
    - fcm_token: str (디바이스 토큰)
    - title: str
    - body: str
    - data: dict (optional)
    """
```

---

## Push Adapter 책임

| 책임 | 설명 |
|---|---|
| Queue consume | Worker에서 PUSH channel 알림 수신 |
| Actor → Token resolve | context에서 fcm_token 추출 (audience_resolver가 미리 삽입) |
| FCM 발송 | `fcm_utils.send_push()` 호출 |
| Delivery result normalize | (success, error) 반환 |
| Audit emit | Worker가 자동 처리 (Adapter 반환값 기반) |

---

## Push Adapter 금지

| 금지 | 이유 |
|---|---|
| 직접 token 저장 | token 등록은 fcm.py 전용 |
| Runtime bypass | Queue → Worker 경유 필수 |
| Audience 판단 | audience_resolver 영역 |
| Severity 변경 | Policy 영역 |
| Retry 직접 구현 | Worker retry 로직 사용 |

---

## Phase 2 구현 시

```python
# push.py send() 내부
from utils.fcm_utils import send_push as fcm_send

def send(message, context):
    token = context.get('fcm_token')
    if not token:
        return False, 'No FCM token'
    try:
        fcm_send(fcm_token=token, title=context.get('title','알림'),
                 body=context.get('body', message), data=context.get('data'))
        return True, None
    except Exception as e:
        return False, str(e)
```
