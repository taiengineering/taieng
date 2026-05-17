# Notification Mapping Governance

작성일: 2026-05-17
범위: Notification Engine · 이벤트 등록 절차

---

## 새 이벤트 추가 절차

1. **event_type 등록** — `notification_event_registry`에 새 이벤트 유형 등록
2. **Policy 확인/생성** — 기존 policy 사용 가능하면 재사용, 아니면 `notification_policy_registry`에 신규 등록
3. **Wiring 등록** — `notification_event_wiring_registry`에 event_type → policy → audience 연결
4. **Audience 확인** — `notification_recipient_rules`에 대상 규칙 존재 확인
5. **Test emit 검증** — `POST /notification-engine/wirings/test` 로 발송 확인

---

## 무분별 direct send 방지

| 금지 | 대안 |
|---|---|
| `pipeline.emit_notification()` 직접 호출 | `event_wiring.wire_and_emit()` 사용 |
| 하드코딩된 channel/severity | Policy registry에서 조회 |
| 하드코딩된 audience | Wiring registry에서 조회 |

---

## 예외

- **E2E 테스트**: `emit-test` API는 wiring 없이 직접 발송 허용
- **시스템 내부 알림**: deadletter/cron_failure는 wiring 등록 후 사용
