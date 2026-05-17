# Operational Intelligence v1

## \ubaa9\uc801

\ub2e8\uc21c Event \uac10\uc9c0\uac00 \uc544\ub2cc, \uc6b4\uc601 \ud750\ub984\uc758 \uc758\ubbf8\ub97c \ud574\uc11d\ud558\ub294 Intelligence \uacc4\uce35.

## \uc5ed\ud560 \uacbd\uacc4

| \ud5c8\uc6a9 | \uae08\uc9c0 |
|------|------|
| recommendation | Incident \uc0dd\uc131 |
| prediction | Severity \uacb0\uc815 |
| correlation | Notification \ubc1c\uc1a1 |
| interpretation | Operational Truth \uc218\uc815 |

Intelligence\ub294 **Truth \uc18c\ube44\uc790**. \uc0dd\uc131 \uae08\uc9c0.

## 4\uac1c Intelligence

### 1. Repeated Failure Intelligence
\ub3d9\uc77c flow/event \ubc18\ubcf5 \ud0d0\uc9c0 + \ucd94\uc138.

```python
from watch_engine.intelligence import analyze_repeated_failures
results = analyze_repeated_failures(sb, hours=24)
# [{intelligence_type, risk_score, confidence, summary, recommendations, evidence}]
```

Risk \uacc4\uc0b0: count*8 + critical_ratio*40 + tenant_spread*10

### 2. Pattern Intelligence
\uc2dc\uac04\ub300\ubcc4 \uc774\uc288 \ucd94\uc138 \ubcc0\ud654 \uac10\uc9c0.

```python
from watch_engine.intelligence import analyze_patterns
results = analyze_patterns(sb, hours=48)
```

Trend: NEW_ISSUE / ACCELERATING / STABLE / IMPROVING

### 3. Tenant Degradation Intelligence
\ud14c\ub10c\ud2b8 \uc0c1\ud0dc \uc545\ud654 \uc870\uae30 \uac10\uc9c0.

```python
from watch_engine.intelligence import analyze_tenant_degradation
results = analyze_tenant_degradation(sb, hours=24)
```

\uc774\uc804 stability_status\uc640 \ube44\uad50\ud558\uc5ec degrading \ud0d0\uc9c0.

### 4. Recovery Recommendation
\uacfc\uac70 action \uc131\uacf5\ub960 \uae30\ubc18 \ubcf5\uad6c \ucd94\ucc9c.

```python
from watch_engine.intelligence import recommend_recovery
results = recommend_recovery(sb, event_type="field_mismatch")
```

action_log + recovery_registry \uae30\ubc18.

## IntelligenceResult

```json
{
  "intelligence_type": "repeated_failure",
  "severity": "WARNING",
  "risk_score": 64,
  "confidence": 0.8,
  "summary": "login: timeout_exceeded 8\ud68c \ubc18\ubcf5",
  "recommendations": ["timeout \uc784\uacc4\uac12 \uc870\uc815"],
  "evidence": [{"flow_key": "login", "count": 8}]
}
```

## \ud5a5\ud6c4 \ud655\uc7a5

| Phase | \ub0b4\uc6a9 |
|:---:|------|
| v1 | \ud1b5\uacc4 \uae30\ubc18 (frequency, trend, correlation) \u2705 |
| v2 | \uc2dc\uacc4\uc5f4 \ubd84\uc11d (\uc2dc\uac04\ub300, \uc694\uc77c, \uc8fc\uae30) |
| v3 | LLM \uae30\ubc18 \uc790\uc5f0\uc5b4 \ud574\uc11d |
