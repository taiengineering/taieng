# Runtime Payload Contract v1.0

Canonical payload structure for all RuntimeCandidateInput.

## Structure

```json
{
  "core": {
    "title": "string (required)",
    "description": "string",
    "priority": "critical|high|medium|low",
    "severity": "string",
    "confidence": "0.0-1.0"
  },
  "domain": {
    "domain_type": "legal|construction|manufacturing|marketing|manual",
    "data": {}
  },
  "runtime": {
    "requires_activation": true,
    "schedule_supported": true,
    "evidence_required": true,
    "document_required": true,
    "auto_assignable": false
  },
  "governance": {
    "escalation_enabled": true,
    "digest_enabled": true,
    "storm_protection": false,
    "governance_level": "standard"
  }
}
```

## Rules

1. `core` — engine-agnostic 필수 필드. Binding Engine이 직접 읽는 영역
2. `domain` — engine-specific 데이터. Binding Engine은 이 영역을 해석하지 않음
3. `runtime` — runtime behavior 플래그. Binding Engine이 projection 시 참조
4. `governance` — watch/governance 정책. Watch Engine이 참조

## domain.domain_type

| type | 설명 | domain.data 예시 |
|------|------|------------------|
| legal | 법령엔진 | rule_kind, law_name, article |
| construction | 건설 | site_type, work_type |
| manufacturing | 제조 | equipment_type, process_type |
| marketing | 마케팅 | campaign_id, lead_source |
| manual | 수동 | (free-form) |

## Binding Engine Behavior

- Binding Engine reads `core` + `runtime` only
- `domain` is stored opaquely in runtime_candidate.payload
- `governance` is forwarded to Watch Engine via EventEnvelope
