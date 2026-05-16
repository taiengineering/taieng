# Cursor 작업지시서: Legacy Direct Send Runtime 흡수

작성일: 2026-05-16
대상: Cursor / Claude Code
상태: 실행 대기

---

## 목적

`overdue_checker.py` 및 `messaging.py`의 Direct Send를
Notification Engine Runtime Pipeline 경유로 전환한다.

Legacy 삭제 금지. 병렬 유지 + Runtime 경유 유도.

---

## 필수 규칙

1. 파일 최대 400줄(15KB). 초과 시 Router/Service/Schema 분리
2. Router = HTTP만 (SQL 금지), Service = 비즈니스 로직 (from fastapi import 금지)
3. `from db.supabase_client import get_supabase`
4. `/health` 엔드포인트 절대 503 금지 (200 고정)
5. main.py 직접 import 금지 → router_registry/ 그룹 파일에 spec 추가
6. Notification Engine 내부에 Severity 계산 / Incident 생성 / Workflow 판단 / SLA 계산 금지

---

## TASK 1: overdue_checker.py Runtime 흡수

### 파일

`routers/overdue_checker.py` (19KB)

### 현재 Direct Send 3개

#### 1. `_send_sms(phone, message)` (라인 ~55)

```python
# 현재: Supabase Edge Function 직접 호출
def _send_sms(phone: str, message: str) -> bool:
    resp = _req.post(_SMS_EDGE, json={...}, timeout=20)
```

변경:

```python
def _send_sms(phone: str, message: str) -> bool:
    """Runtime Pipeline 경유 SMS. Fallback: Edge Function 직접."""
    try:
        from services.notification_engine.compatibility.compat_send import compat_send_sms
        result = compat_send_sms(
            message=message,
            phone=phone,
            source_type="service_notice",
            trace_id=f"OVERDUE-{phone[-4:] if phone else 'UNKNOWN'}",
        )
        if result.get("status") == "success":
            log.info("[OVERDUE] SMS %s → Runtime OK", phone[-4:] if phone else "?")
            return True
        # fallback 실행됨
        if result.get("status") == "fallback":
            log.info("[OVERDUE] SMS %s → fallback OK", phone[-4:] if phone else "?")
            return True
        log.warning("[OVERDUE] SMS Runtime 실패: %s", result.get("message"))
        return False
    except Exception as e:
        log.warning("[OVERDUE] SMS Runtime import 실패, Edge Function fallback: %s", e)
        # 기존 Edge Function fallback
        if not phone:
            return False
        try:
            resp = _req.post(
                _SMS_EDGE,
                json={"receiver": phone, "message": message, "type": "sms"},
                timeout=20,
            )
            result_json = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            ok = bool(result_json.get("success")) or resp.status_code < 300
            log.info("[OVERDUE] SMS %s → Edge %s", phone[-4:], "OK" if ok else "FAIL")
            return ok
        except Exception as e2:
            log.warning("[OVERDUE] SMS Edge 실패: %s", e2)
            return False
```

#### 2. `_write_notification(sb, user_id, company_id, title, body)` (라인 ~86)

```python
# 현재: notifications 테이블 직접 INSERT
def _write_notification(sb, user_id, company_id, title, body):
    sb.table("notifications").insert({...}).execute()
```

변경:

```python
def _write_notification(sb, user_id: str, company_id: Optional[str], title: str, body: str) -> None:
    """Runtime Pipeline 경유 In-App. Fallback: DB 직접 INSERT."""
    try:
        from services.notification_engine.compatibility.compat_send import compat_send_in_app
        result = compat_send_in_app(
            message=body,
            user_id=user_id,
            title=title,
            notification_type="OVERDUE_ESCALATION",
            source_type="service_notice",
            trace_id=f"OVERDUE-INAPP-{user_id[:8] if user_id else 'UNKNOWN'}",
        )
        if result.get("status") in ("success", "fallback"):
            return
    except Exception as e:
        log.warning("[OVERDUE] In-App Runtime 실패, 직접 INSERT fallback: %s", e)

    # 기존 직접 INSERT fallback
    try:
        sb.table("notifications").insert({
            "user_id":      user_id,
            "company_id":   company_id,
            "trigger_code": "OVERDUE_ESCALATION",
            "trigger_group": "OVERDUE",
            "title":        title,
            "body":         body,
            "priority":     "HIGH",
            "is_read":      False,
            "channel":      "push",
            "send_status":  "SENT",
            "sent_at":      datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        log.warning("[OVERDUE] notifications INSERT 실패: %s", e)
```

#### 3. `_send_fcm(push_token, title, body)` (라인 ~75)

현재 단계: **변경 금지**. Push Adapter 미구현. Phase 2에서 전환.

### 주의사항

- `_send_fcm()` 수정 금지 (현재 단계)
- `_process_one()` 함수 내부 로직 변경 금지
- 에스켈레이션 레벨 로직 변경 금지
- overdue_history 기록 로직 변경 금지
- API 엔드포인트 변경 금지

---

## TASK 2: messaging.py Runtime 흡수

### 파일

`routers/messaging.py`

### 변경 대상

SMS 발송 함수에서 `sms_service` 직접 호출 부분을 `compat_send_sms()` 경유로 전환.

### 패턴

```python
# 기존
from services.sms_service import send_sms
send_sms(phone, message)

# 전환
try:
    from services.notification_engine.compatibility.compat_send import compat_send_sms
    compat_send_sms(message=message, phone=phone, source_type="service_notice")
except Exception:
    # fallback: 기존 직접 호출
    from services.sms_service import send_sms
    send_sms(phone, message)
```

### 주의사항

- `from services.sms_service import send_sms` 삭제 금지 (fallback 유지)
- API 엔드포인트 변경 금지
- 응답 포맷 변경 금지

---

## 검증 방법

### overdue_checker

```bash
curl -X POST "https://api.taieng.co.kr/overdue/check?dry_run=true&limit=5"
```

dry_run=true로 시뮤레이션 후, dry_run=false로 실제 실행.
Runtime Queue에 SMS/IN_APP 항목 생성 확인:

```bash
curl "https://api.taieng.co.kr/notification-engine/queue-status"
```

### messaging.py

기존 SMS 발송 API 호출 후 Runtime Queue 확인.

---

## 완료 기준

1. overdue_checker `_send_sms()` → `compat_send_sms()` 경유 (fallback 유지)
2. overdue_checker `_write_notification()` → `compat_send_in_app()` 경유 (fallback 유지)
3. messaging.py SMS → `compat_send_sms()` 경유 (fallback 유지)
4. `_send_fcm()` 변경 없음
5. API 엔드포인트 변경 없음
6. 기존 테스트 깨지지 않음
7. Railway deploy 성공
