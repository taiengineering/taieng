# Notification Center Boundary

작성일: 2026-05-16

---

## 정의

Notification Center는 **운영 커뮤니케이션 Surface**이다.

**아닌 것:**
- Incident Console 아님
- Queue Admin 아님
- Runtime Debugger 아님

## 허용 영역

| 허용 | 금지 |
|---|---|
| Feed 조회 | Queue 수정 |
| Read/Unread 전환 | Incident 판단 |
| Timeline 조회 | Workflow 수정 |
| Preference 설정 | Governance 판단 |
| Health 조회 | 발송 취소 |
| UI Grouping | Backend Grouping |

## Frontend = Runtime Consumer

Frontend는 Runtime의 **소비자**이다. Runtime 판단 금지.
