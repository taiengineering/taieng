# Platform Core — Runtime Contract

## 목적
엔진이 플랫폼 위에서 동작하기 위한 최소 실행 규약.

---

## 1. Engine Lifecycle

```
REGISTER → INIT → RUNNING → PAUSE → STOP
```

| 상태 | 설명 |
|------|------|
| REGISTER | 엔진 등록 (코드 + 네임스페이스) |
| INIT | DB 연결 + 설정 로드 |
| RUNNING | 이벤트 수신/발신 가능 |
| PAUSE | 일시 정지 (이벤트 무시) |
| STOP | 종료 |

## 2. Engine Interface

모든 엔진은 아래 인터페이스를 구현:

```python
class EngineInterface:
    engine_namespace: str          # "watch", "marketing", "tai"
    engine_version: str            # SemVer

    def init(self, config: dict) -> bool
    def process_event(self, event: EventEnvelope) -> list[EventEnvelope]
    def health_check(self) -> dict  # {"status": "ok|degraded|error"}
    def shutdown(self) -> None
```

## 3. Tenant Isolation

| 규칙 | 설명 |
|------|------|
| 모든 이벤트에 tenant_id 필수 | 테넌트 없는 이벤트 금지 |
| 엔진은 자신의 tenant 데이터만 접근 | cross-tenant 접근 금지 |
| mock tenant은 production 차단 | environment 필터 필수 |

## 4. State Transition

엔진이 상태를 변경할 때:

```
1. 현재 상태 확인
2. 전이 가능 여부 검증
3. 상태 변경
4. Event 발신 (state_changed)
5. Audit 기록
```

## 5. Retry Policy

| 항목 | 기본값 |
|------|:---:|
| max_retries | 3 |
| backoff | exponential (1s, 2s, 4s) |
| timeout | 30s |
| dead_letter | 실패 이벤트 보관 |

## 6. Idempotency

```
idempotency_key = f"{trace_id}:{event_type}:{step_key}"
```

- 동일 key로 중복 이벤트 발생 시 무시
- TTL: 24시간 (\uae30\ubcf8)
- 엔진별 TTL 조정 가능

## 7. Priority

| 우선순위 | 의미 | 처리 |
|:---:|------|------|
| P1 | 즉시 대응 | 실시간 |
| P2 | 긴급 | 5분 이내 |
| P3 | 일반 | 1시간 이내 |
| P4 | 낮음 | 배치 |

## 8. Event Versioning

- 모든 이벤트에 version 필드 필수
- 버전 호환: 소비자는 자신이 이해하는 버전만 처리
- Breaking change: major 버전 증가
- 구버전 이벤트: 90일 보관 후 아카이브
