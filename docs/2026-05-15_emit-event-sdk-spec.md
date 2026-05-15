# Watch Engine SDK v1.1 — emitEvent() Thin Agent

**TASK 04 산출물 | 2026-05-15**

## SDK 구조

```
tai-api/watch_engine/
  __init__.py        → emit_event, create_trace, TraceContext
  emitter.py         → emit_event() — fail-safe, non-blocking
  trace.py           → TraceContext + contextvars 전파
  validation.py      → enum/필드 검증 (non-blocking)
  pii.py             → PII blacklist strip
  types.py           → EventPayload, enum constants
```

## 핵심 보장

- lightweight: dataclass 기반, 외부 의존성 0
- async-safe: contextvars 기반 trace 전파
- non-blocking: v1 동기 insert, v2 background queue
- fail-safe: 전체 try/except, 예외 swallow → return False

## 적용 대상 (3개 flow)

1. login — routers/auth.py
2. process_registration — routers/factory_process.py
3. diagnosis_submit — routers/diagnosis.py

자세한 적용 예시는 출력 문서 참조.