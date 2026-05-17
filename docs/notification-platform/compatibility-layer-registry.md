# Compatibility Layer Registry

작성일: 2026-05-17
범위: Notification Engine · Compat Layer

---

## 목적

Legacy direct send를 Runtime으로 전환하는 중간 계층.
**영구화 방지** — 모든 compat layer는 제거 대상.

---

## Compat 함수 목록

| 함수 | 파일 | 상태 | 대체 방법 |
|---|---|---|---|
| `compat_send_sms()` | `compatibility/compat_send.py` | temporary | `wire_and_emit(event_type)` |
| `compat_send_in_app()` | `compatibility/compat_send.py` | temporary | `wire_and_emit(event_type)` |
| `compat_send_telegram()` | `runtime_compat.py` | fallback | `wire_and_emit(event_type)` |

---

## 상태 정의

| 상태 | 의미 |
|---|---|
| temporary | 전환 예정, 제거 대상 |
| fallback | 전환 실패 시 fallback으로 유지 |
| migration-only | 마이그레이션 기간에만 사용 |

---

## 규칙

1. 새 compat 함수 생성 금지
2. 기존 compat 함수에 새 호출자 추가 금지
3. compat 호출 시 로그에 `[COMPAT]` prefix 기록
4. 월별 compat 호출 수 모니터링
