# Legacy Notification Freeze

작성일: 2026-05-16
상태: Freeze Active

---

## Freeze 대상

### 1. `routers/notifications.py`

- **신규 사용 금지**
- 기존 엔드포인트 유지 (backward compat)
- 신규 알림 로직은 `notification_engine_api.py` 사용

### 2. Direct Send 신규 생성 금지

아래 함수 신규 호출 금지:

- `sms_service.send_sms()` 직접 호출 → `compat_send_sms()` 사용
- `inbox_notify_svc.create_notification()` 직접 호출 → `compat_send_in_app()` 사용
- `slack_dispatcher` 직접 호출 → Phase 2+ Slack Adapter

### 3. Direct Toast 신규 생성 금지

- Frontend에서 신규 toast/popup 직접 구현 금지
- Runtime Feed 경유 원칙

### 4. Runtime 경유 원칙

모든 신규 알림은:

```
Notification Engine Pipeline
    → Event Intake
    → Recipient Resolution
    → Queue
    → Adapter
    → Delivery
```

을 경유해야 한다.

---

## 예외

- **Auth SMS** (pw_reset, auth, auth_oauth): 인증 분리 원칙으로 별도 검토
- **기존 작동 코드**: 삭제 금지, 점진적 전환

---

## Migration Path

1. 신규 알림 → `notification_engine_api` 또는 `compat_send_*()` 사용
2. 기존 코드 → 점진적으로 `compat_send_*()` 전환
3. 전체 전환 완료 후 Legacy 코드 제거 (현재 단계 아님)
