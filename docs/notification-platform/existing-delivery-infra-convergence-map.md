# Existing Delivery Infra Convergence Map

작성일: 2026-05-17
범위: Delivery 인프라 수렴 현황

---

## 현황

| Infra | 유형 | 상태 | Runtime 연결 |
|---|---|---|---|
| MessageMi (SMS) | 외부 API | ✅ Active | ✅ SMS Adapter |
| Telegram Bot API | 외부 API | ✅ Active | ✅ Telegram Adapter |
| Firebase FCM | 외부 API | ✅ Active | ⬜ Push Adapter mock |
| Supabase notifications | DB INSERT | ✅ Active | ✅ IN_APP Adapter |
| sms_service.py | Legacy 직접 | ⚠️ Compat | ⬜ wire_and_emit 전환 대기 |
| messaging.py | Legacy API | ⚠️ Compat | ⬜ wire_and_emit 전환 대기 |
| runtime_compat.py | Bridge | ⚠️ Compat | — (제거 예정) |
| compat_send.py | Bridge | ⚠️ Compat | — (제거 예정) |
| fcm.py send-push | Legacy API | ⚠️ Compat | ⬜ wire_and_emit 전환 대기 |
| 6개 push 직접호출 | Legacy 직접 | ❌ Remaining | ⬜ wire_and_emit 전환 필요 |

---

## 수렴률

| 분류 | 건수 | 비율 |
|---|---|---|
| Runtime Adapter (완전 수렴) | 4 | 40% |
| Compat Layer (부분 수렴) | 4 | 40% |
| Remaining (미수렴) | 2 | 20% |

**전체 수렴률: 80%** (Adapter + Compat)
