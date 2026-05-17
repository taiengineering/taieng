# Notification Runtime Forbidden Actions

작성일: 2026-05-17
범위: Notification Intelligence 금지 행위

---

## 금지 목록

| 금지 | 이유 |
|---|---|
| Anomaly 판단 | Control Runtime 영역 |
| Severity 생성 | Control Runtime이 결정한 값만 소비 |
| Incident 생성 | Control Runtime 영역 |
| Operational Truth 생성 | Control Runtime 영역 |
| Shutdown 판단 | Control Runtime 영역 |
| Root Cause 판단 | Control Runtime 영역 |
| Queue 구조 변경 | Delivery Runtime 영역 |
| Adapter 직접 호출 | Delivery Runtime 영역 |
| Transport 직접 실행 | Delivery Runtime 영역 |

---

## 핵심

**Notification은 상태를 생성하지 않는다.**

Control Runtime이 생성한 severity/incident를 **소비**하여 전달 방법을 결정할 뿐.
