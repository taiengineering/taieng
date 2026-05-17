# Notification Catalog Governance

작성일: 2026-05-17
범위: 알림 추가 절차 표준

---

## 신규 Notification 추가 절차

1. **Event Taxonomy 등록** — event_key 명명 규칙 준수, category 분류
2. **Audience 정의** — Default Audience Matrix에 추가
3. **Channel 정의** — Default Channel Matrix에 추가
4. **Policy 정의** — notification_policy_registry에 등록 (또는 기존 재사용)
5. **Template 정의** — message_template_registry에 본문 등록 (Phase 2)
6. **Runtime Wiring** — notification_event_wiring_registry에 event→policy→audience 연결
7. **Pack 문서 업데이트** — 해당 Pack 문서에 이벤트 추가
8. **Test Emit** — `POST /notification-engine/wirings/test`로 발송 확인

---

## 금지

| 금지 항목 | 대안 |
|---|---|
| Direct send (`send_sms()` 직접) | `wire_and_emit()` 사용 |
| Template-only event (wiring 없이) | 반드시 wiring 등록 |
| Undocumented event | Pack 문서 필수 업데이트 |
| 하드코딩된 audience | audience_resolver 사용 |
| 하드코딩된 channel | policy_registry 사용 |
| 중복 event_key | 기존 event 재사용 검토 |

---

## 검증 체크리스트

- [ ] event_key가 Taxonomy 규칙 준수?
- [ ] Audience Matrix에 등록?
- [ ] Channel Matrix에 등록?
- [ ] Policy 존재?
- [ ] Wiring 등록?
- [ ] Pack 문서 업데이트?
- [ ] Test emit 성공?
