# Engine Audit Permission Enforcement
## 2026-05-13

## 권한 정책

### 허용 Role
- ROLE_ENGINE_ADMIN
- ROLE_SYSTEM_AUDITOR
- ROLE_SUPER_ADMIN
- admin
- super_admin

### 차단 대상
- worker
- reviewer
- 일반 운영 사용자
- tenant 일반 관리자

## API 보호

모든 `/engine-monitoring/*` endpoint에 `_check_admin(request)` 적용.

| Endpoint | 보호 |
|----------|------|
| /engine-monitoring/summary | ✅ admin-only |
| /engine-monitoring/drift-events | ✅ admin-only |
| /engine-monitoring/ai-contamination | ✅ admin-only |
| /engine-monitoring/mandatory-drift | ✅ admin-only |
| /engine-monitoring/checklist-explosion | ✅ admin-only |
| /engine-monitoring/unsupported-domain | ✅ admin-only |
| /engine-monitoring/explainability-audit | ✅ admin-only |

## 개발 단계 정책

role 미설정 시 허용 (운영 전환 시 차단으로 전환)
