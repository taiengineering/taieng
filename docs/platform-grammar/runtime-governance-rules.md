# Runtime Governance Rules

작성일: 2026-05-17
범위: Notification Engine · Governance

---

## 허용

| 항목 | 조건 |
|---|---|
| 신규 Adapter 추가 | Adapter Interface 준수 (`send(message, context) → (success, error)`) |
| 신규 Feed UI 추가 | Feed Contract 필드만 사용 |
| 신규 Surface 추가 | 동일 API 사용 (Feed/Unread/Timeline) |
| Recipient Rule 추가 | 기존 channel_key 범위 내 |
| Event Registry 추가 | source_type 신규 등록 |

---

## 금지

| 항목 | 이유 |
|---|---|
| Queue mutation | Runtime 안정성 위협 |
| Runtime branching | 단일 파이프라인 원칙 위반 |
| Channel-specific lifecycle | 채널별 상태 분기 금지 |
| Adapter-specific severity | severity는 Event 수준에서 결정 |
| Feed Reality 왜곡 | UX는 Runtime Reality를 그대로 반영 |
| Lifecycle 상태 추가 | Phase 1 Freeze |
| Queue 타입 추가 | 단일 큐 원칙 |

---

## 변경 절차

1. Platform Grammar 문서에 변경 사유 기록
2. Phase 2 Boundary 범위 내인지 확인
3. Freeze Manifest 해제 필요 시 별도 승인
4. 변경 후 Runtime Consistency 검증 필수
