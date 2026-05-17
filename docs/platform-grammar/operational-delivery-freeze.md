# Operational Delivery Freeze

작성일: 2026-05-17
상태: **공식 선언**

---

## 선언

**Delivery Runtime 전달 안정화 단계에 진입한다.**

---

## Freeze 대상

| 대상 | Freeze 내용 |
|---|---|
| Push | 새 Push 시스템 구축 금지, 기존 FCM 유지 |
| SMS | 새 SMS 시스템 구축 금지, MessageMi 유지 |
| Telegram | 새 Bot 구축 금지, 기존 Bot 유지 |
| Queue | Queue 구조 변경 금지 |
| Adapter | Adapter Interface 변경 금지 |
| Lifecycle | Delivery Lifecycle 변경 금지 |
| Runtime | Notification Runtime 변경 금지 |

---

## 허용

| 항목 | 조건 |
|---|---|
| Compat convergence | 직접 호출 → wire_and_emit 전환 |
| Adapter stabilization | 버그 수정, timeout 설정 |
| Operational validation | 실사용 검증 |
| 파라미터 튜닝 | cooldown, retry interval 조정 |
| 신규 wiring 등록 | 실이벤트 기반 |

---

## 핵심

**지금은 전달 안정화 단계.** 더 만들지 않고 안정적으로 전달한다.
