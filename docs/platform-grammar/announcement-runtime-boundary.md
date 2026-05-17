# Announcement Runtime Boundary

작성일: 2026-05-17
범위: Notification Engine · Announcement

---

## 정의

Announcement는 **운영 콘텐츠**다. Runtime Alert가 아니다.

---

## 예시

| 유형 | 예시 |
|---|---|
| 점검공지 | "내일 10시 소방시설 점검" |
| 장애공지 | "오늘 14~16시 서버 점검" |
| 업데이트공지 | "새 기능 추가" |
| 정책공지 | "이용약관 변경" |

---

## Announcement ≠ Incident

| 항목 | Announcement | Incident |
|---|---|---|
| 발생 주체 | 운영자 | 시스템 |
| 시점 | 예정 | 발생 시 |
| severity | 운영자 판단 | Policy 결정 |
| Runtime | ❌ | ✅ |
| Feed | 별도 Surface | 알림센터 Feed |

---

## 현재 상태

- Announcement 전용 테이블: 없음
- Announcement UI: 미구현
- Phase 2에서 Announcement Manager 구현 예정
