# Real Usage Boundary

작성일: 2026-05-17
범위: Notification Engine · 개발 경계

---

## 현재 단계

**실사용 검증** 단계다.

---

## 금지

| 금지 항목 | 이유 |
|---|---|
| Speculative optimization | 실데이터 없이 최적화 무의미 |
| Future abstraction | 사용되지 않는 추상화 금지 |
| Unused governance expansion | 거버넌스는 실문제 발생 후 확장 |
| Policy explosion | 사용되지 않는 정책 추가 금지 |
| Audience type 확장 | 실사용자 유형 확인 후 |
| Wiring 과잉 등록 | 실이벤트 발생 후 등록 |

---

## 허용

| 허용 항목 | 조건 |
|---|---|
| 버그 수정 | 즉시 |
| 파라미터 튜닝 | 관찰 근거 기반 |
| 실사용 기반 wiring 추가 | 실이벤트 확인 후 |
| 관찰 로그 기록 | 항상 |

---

## 핵심

**지금은 더 만들 때가 아니라 운영할 때.**
