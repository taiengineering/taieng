# Engine Monitoring Admin Architecture
## 2026-05-13

## 아키텍처

```
[Worker App /app]
    │ 엔진감시 접근 불가
    │
[Runtime 운영 /html/runtime]
    │ 엔진감시 링크 없음
    │
[Admin Audit /html/admin]
    └─ engine-monitoring.html
        └─ /engine-monitoring/* API (admin-only)
```

## 3계층 분리

| 계층 | 대상 | 노출 |
|------|------|------|
| Worker App | 작업자 | 점검/체크/완료만 |
| Runtime 운영 | 안전관리자 | dashboard/review/notification |
| Admin Audit | 엔진관리자 | drift/contamination/integrity |

## API 보호

- v1.1.0: `_check_admin(request)` 적용
- ALLOWED_ROLES: ENGINE_ADMIN, SYSTEM_AUDITOR, SUPER_ADMIN
- public exposure 차단
