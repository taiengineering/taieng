# Canonical Event Registry

Owner: **Control Runtime**

---

## Platform Core Events

### Workflow
| Event | Severity | ACK | 설명 |
|-------|:---:|:---:|------|
| `workflow.started` | INFO | ❌ | 워크플로우 시작 |
| `workflow.completed` | INFO | ❌ | 워크플로우 정상 완료 |
| `workflow.failed` | CRITICAL | ✅ | 워크플로우 실패 |
| `workflow.timeout` | WARNING | ✅ | 시간 초과 |
| `workflow.blocked` | WARNING | ✅ | 차단/대기 |
| `workflow.retried` | INFO | ❌ | 재시도 |

### Step
| Event | Severity | ACK | 설명 |
|-------|:---:|:---:|------|
| `step.started` | INFO | ❌ | 단계 시작 |
| `step.completed` | INFO | ❌ | 단계 완료 |
| `step.failed` | WARNING | ❌ | 단계 실패 |
| `step.skipped` | INFO | ❌ | 단계 건너뛰 |

### Payment
| Event | Severity | ACK | 설명 |
|-------|:---:|:---:|------|
| `payment.pending` | INFO | ❌ | 결제 대기 |
| `payment.completed` | INFO | ❌ | 결제 성공 |
| `payment.failed` | WARNING | ✅ | 결제 실패 |
| `payment.cancelled` | INFO | ❌ | 결제 취소 |
| `payment.refunded` | INFO | ❌ | 환불 |

### Document
| Event | Severity | ACK | 설명 |
|-------|:---:|:---:|------|
| `document.generated` | INFO | ❌ | PDF 생성 완료 |
| `document.failed` | WARNING | ❌ | PDF 생성 실패 |
| `document.template_missing` | WARNING | ❌ | HTML 템플릿 없음 |
| `document.downloaded` | INFO | ❌ | 다운로드 완료 |

### Subscription
| Event | Severity | ACK | 설명 |
|-------|:---:|:---:|------|
| `subscription.activated` | INFO | ❌ | 구독 활성 |
| `subscription.paused` | WARNING | ❌ | 구독 일시정지 |
| `subscription.cancelled` | WARNING | ✅ | 구독 취소 |
| `subscription.failed` | CRITICAL | ✅ | 구독 실패 |
| `subscription.ended` | INFO | ❌ | 구독 종료 |

### Runtime
| Event | Severity | ACK | 설명 |
|-------|:---:|:---:|------|
| `runtime.started` | INFO | ❌ | Runtime 시작 |
| `runtime.degraded` | WARNING | ✅ | Runtime 성능 저하 |
| `runtime.recovered` | INFO | ❌ | Runtime 복구 |
| `runtime.failed` | CRITICAL | ✅ | Runtime 실패 |

### Incident (Control 전용)
| Event | Severity | ACK | 설명 |
|-------|:---:|:---:|------|
| `incident.created` | WARNING+ | ✅ | 인시던트 생성 |
| `incident.escalated` | CRITICAL | ✅ | 위험 상향 |
| `incident.acknowledged` | INFO | ❌ | ACK 완료 |
| `incident.resolved` | INFO | ❌ | 해결 |
| `incident.closed` | INFO | ❌ | 종료 |

---

## Watch Engine Domain Events

| Event | Severity | 설명 |
|-------|:---:|------|
| `watch.integrity_detected` | WARNING/CRITICAL | 무결성 이슈 |
| `watch.alert_fired` | WARNING/CRITICAL | 알림 발송 |
| `watch.sla_violated` | WARNING/CRITICAL | SLA 위반 |
| `watch.tenant_risk_changed` | WARNING | 테넌트 위험도 변경 |
| `watch.stability_changed` | WARNING | 안정성 변경 |
| `watch.pattern_detected` | INFO | 패턴 탐지 |
| `watch.recovery_recommended` | INFO | 복구 추천 |
| `watch.synthetic_completed` | INFO | 합성 테스트 완료 |
| `watch.sovereignty_violation` | CRITICAL | Runtime 권한 위반 |

---

## 통계

| 카테고리 | 수 |
|----------|:---:|
| Platform Core Events | 30 |
| Watch Domain Events | 9 |
| **합계** | **39** |
