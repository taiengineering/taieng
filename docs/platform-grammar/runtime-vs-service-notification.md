# Runtime vs Service Notification

작성일: 2026-05-16

---

## 구분

| 구분 | Runtime Notification | Service Notification |
|---|---|---|
| 생성 주체 | 시스템 (엔진/스케줄러) | 운영자/사용자 |
| Trigger | Event 기반 (자동) | 수동/정적 가능 |
| 목적 | 운영 대응 | 사용자 커뮤니케이션 |
| Trace 존재 | 대부분 존재 | 없을 수 있음 |
| Queue Runtime | 공유 가능 | 공유 가능 |
| Severity | 외부 제공 (Watch/Alert Layer) | optional |
| Incident 연결 | 가능 | 없음 가능 |
| 예시 | WORKFLOW_STUCK alert, SLA_BREACH | 비밀번호 재설정 SMS, 결제 완료 |

## 핵심 철학

Runtime과 Service는 다르다.
하지만 Delivery Runtime은 공유 가능하다.

## TAI 현재 상태

- **Runtime Notification**: Notification Engine Pipeline (Telegram)
- **Service Notification**: SMS (MessageMi 직접), In-App (DB INSERT 직접)
- **통합 방향**: 두 유형 모두 Notification Engine Pipeline을 경유하되, source_type으로 구분
