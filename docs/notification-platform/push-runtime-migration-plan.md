# Push Runtime Migration Plan

작성일: 2026-05-17
범위: 기존 Push → Runtime 수렴 단계별 전략

---

## 3단계 전략

### Phase A: Compat (현재 → 즉시)

| 항목 | 내용 |
|---|---|
| push.py mock → 실호출 | `fcm_utils.send_push()` 연결 |
| channel_registry PUSH enabled | true로 변경 |
| 기존 7개 호출처 | 그대로 유지 (이중 경로) |
| 효과 | Runtime으로 Push 발송 가능해짐 |

### Phase B: Hybrid (1~2주)

| 항목 | 내용 |
|---|---|
| 신규 이벤트 | wire_and_emit → PUSH channel 사용 |
| 기존 호출처 | 점진적 wire_and_emit 전환 (1개씩) |
| 이중 발송 방지 | wiring 등록 후 직접 호출 제거 |
| 효과 | Queue/Retry/Audit/Timeline 확보 |

### Phase C: Runtime-native (2~4주)

| 항목 | 내용 |
|---|---|
| 모든 Push | wire_and_emit 경유 |
| 직접 fcm_utils 호출 | fcm.py 전용 (토큰등록/테스트) 외 제거 |
| Legacy 필드 | fcm_sent, push_sent_at 제거 |
| 효과 | 완전 Runtime 수렴 |

---

## 전환 순서 (Phase B)

1. `overdue_checker.py` → wire_and_emit('schedule_overdue') (SMS+Push)
2. `tbm.py` → wire_and_emit('tbm_attendance')
3. `emergency_report.py` → wire_and_emit('accident_reported')
4. `equipment_checkins.py` → wire_and_emit('equipment_checkin')
5. `safety_reports.py` → wire_and_emit('safety_report')
6. `workers.py` → wire_and_emit 적절한 event_type

---

## 핵심

**점진적 수렴. 한 번에 전환하지 않는다.** 각 호출처를 1개씩 전환하고 검증.
