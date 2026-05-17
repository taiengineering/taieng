# Control Surface Boundary

작성일: 2026-05-17
범위: Notification Engine · 관리 경계

---

## 정의

Control Surface는 **운영 관리**다. Runtime을 조회하고 설정하는 것.

---

## 허용

| 항목 | 설명 |
|---|---|
| Visibility | Queue/Feed/Timeline/DLQ 조회 |
| Enable/Disable | Wiring/Adapter/Channel 활성화 제어 |
| Wiring Control | event→policy→audience 매핑 관리 |
| Policy Tuning | cooldown, severity, channel 조정 |
| Feed Observation | 전체 Feed 검색/필터 |
| Digest Control | Digest policy enable/disable |

---

## 금지

| 항목 | 이유 |
|---|---|
| Runtime state mutation | Queue 상태 직접 변경 금지 |
| Manual queue override | Worker가 자동 처리 |
| Manual lifecycle rewrite | Lifecycle은 고정 |
| Direct DB manipulation | API 경유만 허용 |
| Adapter bypass | Control Surface에서 직접 발송 금지 |

---

## 핵심

**Control Surface는 Runtime을 관찰하고 설정하는 것이지, Runtime을 우회하는 것이 아니다.**
