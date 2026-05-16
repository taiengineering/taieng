# Runtime vs UX Boundary

작성일: 2026-05-17
범위: Notification Engine · Architecture Boundary

---

## 영역 구분

| 영역 | 책임 |
|---|---|
| Runtime | 전달 현실 (event → queue → delivery → feed) |
| UX | 전달 표현 (feed → card → badge → timeline) |

---

## 핵심 원칙

**UX는 Runtime Reality를 왕곡하면 안 된다.**

---

## 예시

| 상황 | Runtime Reality | UX 표현 | 올바른가? |
|---|---|---|---|
| 알림 전달 성공 | DELIVERED | Feed 카드 표시 | ✅ |
| Quiet Hour 지연 | QUIET_HOUR_DELAYED | Feed 미표시 + badge 숨김 | ✅ |
| 전달 실패 | FAILED | Feed 미표시 | ✅ |
| Mute | MUTED | Feed 미표시 | ✅ |
| 전달 성공인데 Feed 숨김 | DELIVERED | Feed 미표시 | ❌ |
| 전달 실패인데 Feed 표시 | FAILED | Feed 카드 표시 | ❌ |

---

## UX 변경 금지 영역

- Feed 데이터 필터링으로 Runtime 결과 숨기기
- Severity 임의 변경
- Read 상태로 delivery 상태 변경
- Badge count를 Runtime count와 다르게 표시
