# Digest vs Alert Boundary

작성일: 2026-05-17
범위: Notification Engine · 역할 경계

---

## 영역 구분

| 영역 | 책임 |
|---|---|
| **Alert** | 중요 승격 — severity 결정, 즉시 전달 |
| **Digest** | 전달 압축 — 묶음, 지연, 요약 |

---

## 핵심

**Digest는 중요도를 바꾸지 않는다.**

CRITICAL 알림을 Digest로 묶으면 안 된다.

---

## 규칙

| 규칙 | 설명 |
|---|---|
| CRITICAL은 Digest 대상 제외 | 즉시 전달 |
| WARNING Digest는 선택적 | 운영자 판단 |
| INFO Digest는 권장 | 피로 방지 |
| Digest는 event 의미를 변경하지 않음 | 본문 원본 유지 |
| Digest는 severity를 변경하지 않음 | WARNING을 INFO로 강등 금지 |

---

## 예시

| 상황 | Alert | Digest | 올바른가? |
|---|---|---|---|
| CRITICAL workflow_stuck | 즉시 TELEGRAM | ❌ Digest 대상 아님 | ✅ |
| WARNING 점검일 접근 5건 | 개별 IN_APP | ✅ 1시간 묶음 | ✅ |
| INFO 교육 완료 20건 | 개별 IN_APP | ✅ 일간 요약 | ✅ |
| CRITICAL을 Digest로 묶음 | ❌ | ❌ | ❌ 금지 |
