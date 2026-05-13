# Engine Integrity Monitoring
## 2026-05-13

---

## 목적

"서버 장애"보다 **"deterministic requirement system의 조용한 오염"** 탐지.

## 9종 Detector

| # | Detector | 탐지 대상 | Severity |
|---|----------|----------|----------|
| A | Obligation Drift | 동일 입력 → 다른 obligation 결과 | CRITICAL |
| B | Completeness Drift | mandatory 누락인데 creatable=true | CRITICAL |
| C | Hidden Mandatory Drift | recommended가 사실상 mandatory 동작 | HIGH |
| D | Mapping Mutation | requirement mapping 변경 | WARNING |
| E | AI Contamination | AI가 법적 판단 개입 | CRITICAL |
| F | Unsupported Inference | 지원안되는 영역 추론 시도 | HIGH |
| G | Checklist Explosion | obligation 대비 checklist 이상 증가 | HIGH |
| H | Notification Storm | 알림 폭증 | WARNING |
| I | Explainability Loss | source_trace 없는 결과 존재 | CRITICAL |

## API

| Endpoint | 역할 |
|----------|------|
| GET /integrity/run-audit | 전체 감사 실행 |
| GET /integrity/events | 이벤트 조회 |
| GET /integrity/mapping-audit | 매핑 변경 감사 |

## DB

- `engine_integrity_event`: 무결성 이벤트 로그
- `mapping_mutation_audit`: 매핑 변경 감사 로그
