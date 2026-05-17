# Notification Admin Readiness v2

작성일: 2026-05-17
범위: Notification Engine · Control Surface 평가

---

## 평가 항목

| 항목 | 점수 | 상태 |
|---|---|---|
| Runtime Visibility | 9/10 | Health Grid (Queue/Retry/Delayed/DLQ/Unread/Status) |
| Wiring Visibility | 9/10 | Wiring 테이블 (14건, 전체 필드) |
| Policy Visibility | 9/10 | Policy 테이블 (8건, cooldown/severity/digest) |
| Delivery Visibility | 8/10 | Delivered/Failed/Retry/DLQ/Delayed/Resumed 그리드 |
| Legacy Visibility | 9/10 | 10건 전수 + 상태 badge + 대체 방법 |
| Operator Usability | 8/10 | Vuexy 레이아웃, 메뉴 연결, 알림센터 링크 |

---

## Notification Admin Readiness Score

**52/60 = 87% — A 등급**

(v1 57% C+ → v2 87% A)

---

## 개선 요인

| 항목 | v1 → v2 |
|---|---|
| Control Surface | API 조회만 → 전용 admin 페이지 |
| Wiring Visibility | 없음 → 전체 테이블 |
| Legacy Visibility | 없음 → 10건 상태 매트릭스 |
| Navigation | API 직접 → 메뉴 > 알림 관리 |

---

## 남은 걸치

1. **Wiring 편집 UI** — enable/disable 토글 (Phase 2)
2. **Policy 편집 UI** — cooldown 조정 (Phase 2)
3. **Delivery Logs** — 개별 전달 기록 조회 (Phase 2)
4. **Template Manager** — SMS/Email 템플릿 관리 (Phase 2)
