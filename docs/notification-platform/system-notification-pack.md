# System Notification Pack

작성일: 2026-05-17
범위: 시스템 운영 알림

---

## 원칙

**System Pack ≠ Runtime Alert.** 운영 공지 성격.

---

## 이벤트

| event_key | 설명 | audience | channel | severity | digest | quiet bypass |
|---|---|---|---|---|---|---|
| maintenance_notice | 점검 공지 | tenant_admin | IN_APP | INFO | ✅ | ❌ |
| incident_notice | 장애 공지 | tenant_admin | IN_APP | WARNING | ❌ | ❌ |
| deployment_completed | 배포 완료 | system_admin | IN_APP | INFO | ✅ | ❌ |
| backup_failed | 백업 실패 | system_admin | TELEGRAM | CRITICAL | ❌ | ✅ |
| scheduler_failed | 스케줄러 실패 | system_admin | IN_APP | WARNING | ❌ | ❌ |
| service_degraded | 서비스 저하 | system_admin | TELEGRAM | CRITICAL | ❌ | ✅ |

---

## System vs Runtime Alert 구분

| 항목 | System Pack | Runtime Alert |
|---|---|---|
| 발생 주체 | 운영자/시스템 공지 | Watch Engine 자동 감지 |
| 성격 | 공지/알림 | 장애/이상 |
| Wiring | notification_event_wiring_registry | Event Intake 직접 |
| 대상 | tenant_admin/system_admin | operator/safety_manager |
