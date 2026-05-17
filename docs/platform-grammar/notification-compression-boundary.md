# Notification Compression Boundary

작성일: 2026-05-17
범위: Notification Engine · 압축 경계

---

## 허용

| 방법 | 설명 |
|---|---|
| Grouping | 동일 source_type/event_type 묶음 |
| Batching | 시간창 내 복수 이벤트 한 번에 전달 |
| Delayed Delivery | Quiet Hour 등 시간대 억제 |
| Cooldown | 동일 이벤트 중복 억제 |
| List Mode | 제목 목록으로 나열 |

---

## 금지

| 방법 | 이유 |
|---|---|
| Event meaning rewrite | 이벤트 본래 의미 손실 |
| Severity rewrite | WARNING→INFO 강등 금지 |
| AI interpretation | LLM 기반 요약/해석 금지 |
| Incident merge | 사고 병합 금지 |
| CRITICAL digest | CRITICAL은 개별 즉시 전달 |
| Cross-tenant merge | 다른 회사 알림 묶음 금지 |

---

## 핵심

**압축은 전달 방식의 최적화이지, 전달 내용의 변형이 아니다.**
