# Trans Engine Overview

## 정의

Trans Engine은 **Operational Translation Engine**이다.

Control Runtime(관제엔진)이 생성한 Operational Truth를
비개발자 운영자/관리자도 이해할 수 있는 **운영 언어**로 변환한다.

## Trans Engine은 다음이 아니다

| 아닌 것 | 이유 |
|---------|------|
| AI Agent | 판단하지 않는다 |
| Chatbot | 대화하지 않는다 |
| Notification Engine | 전달을 결정하지 않는다 |
| Report Generator | 보고서를 만들지 않는다 |

## 핵심 변환

```
Operational Truth → Human Operational Meaning → Operational Awareness
```

| Runtime 언어 | 운영 언어 |
|---|---|
| workflow.failed | 작업이 완료되지 못했습니다 |
| degradation | 서비스 안정성이 낮아지고 있습니다 |
| repeated_failure | 같은 문제가 반복되고 있습니다 |
| escalation | 운영 위험이 증가하고 있습니다 |
| step.failed | 처리 단계에서 문제가 발생했습니다 |
| runtime.degraded | 시스템 성능이 저하되고 있습니다 |

## 아키텍처 위치

```
Control Runtime (Truth 생성)
    ↓
Intelligence (해석/분석)
    ↓
Trans Engine (사람 언어 변환)  ← 여기
    ↓
UI (표시)
    ↓
Notification (전달)
```

Trans Engine은 **Projection/Interpretation Layer**다.
Runtime이 생성한 Truth를 읽기만 하고, 절대 수정하지 않는다.

## 절대 금지

- Truth 생성
- Severity 생성
- Incident 생성
- Escalation 판단
- Runtime Ownership 침범
- Notification 발송 결정

## 코드 위치

```
tai-api/watch_engine/trans_engine/
```

## API

```
POST /trans/translate   — event → human message
POST /trans/summary     — events → 상황 요약
GET  /trans/examples    — 샘플 반환
```
