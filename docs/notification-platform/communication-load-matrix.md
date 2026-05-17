# Communication Load Matrix

작성일: 2026-05-17
범위: Notification Engine · 수신 부하 분석

---

## 목적

**누가 얼마나 피곴한가** 가시화.

---

## Audience별 예상 부하

| Audience | 예상 일간 이벤트 | 주요 채널 | Digest 권장 | 부하 수준 |
|---|---|---|---|---|
| operator | 5~15 | TELEGRAM + IN_APP | 선택적 | NORMAL |
| safety_manager | 10~30 | IN_APP + TELEGRAM | ✅ 권장 | HIGH |
| company_admin | 3~10 | IN_APP | 선택적 | NORMAL |
| tenant_admin | 2~8 | IN_APP + SMS | 선택적 | LOW~NORMAL |
| worker | 1~5 | IN_APP | ✅ 권장 | LOW |
| system_admin | 5~20 | TELEGRAM + IN_APP | ✅ 권장 | HIGH |
| site_all | 0~3 (긴급) | TELEGRAM | ❌ (CRITICAL 전용) | LOW |

---

## 피로 위험 대상

1. **safety_manager** — 점검 + 공정 + 교육 + 스케줄 알림 중첩 → Digest 최우선
2. **system_admin** — 크론 + deadletter + API 디스커버리 → Digest 권장
3. **operator** — workflow_stuck CRITICAL은 즉시, 나머지 Digest 가능
