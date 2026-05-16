# Semantic Adapter — Legacy State → Canonical Grammar

## 아키텍처

```
[Legacy Runtime]              [Semantic Adapter]           [Canonical Grammar]
                                                           
factory_process.is_active  ──→  translate_state()  ──→  workflow_completed
payments.status_code       ──→                     ──→  payment_pending
subscriptions.status       ──→                     ──→  subscription_activated
generated_document.status  ──→                     ──→  document_ready
                                                           
                              translate_record()   ──→  LLM-friendly context
```

**\ud575\uc2ec: Legacy \uc0c1\ud0dc\uac12\uc744 \uc81c\uac70\ud558\uc9c0 \uc54a\ub294\ub2e4. \ubcc0\ud658 \uacc4\uce35\ub9cc \ucd94\uac00.**

---

## Canonical Events (22\uac1c)

| Source | Legacy | Canonical Event | Severity | Tenant Impact |
|--------|--------|----------------|:---------:|:------------:|
| factory_process | is_active=true | workflow_completed | INFO | NONE |
| factory_process | is_active=false | workflow_deactivated | INFO | NONE |
| payments | PENDING | payment_pending | INFO | NONE |
| payments | PAID | payment_completed | INFO | LOW |
| payments | FAILED | payment_failed | WARNING | MEDIUM |
| payments | CANCELLED | payment_cancelled | INFO | LOW |
| subscriptions | PENDING | subscription_pending | INFO | NONE |
| subscriptions | ACTIVE | subscription_activated | INFO | LOW |
| subscriptions | PAUSED | subscription_paused | WARNING | MEDIUM |
| subscriptions | CANCELLED | subscription_cancelled | WARNING | HIGH |
| subscriptions | FAILED | subscription_failed | CRITICAL | HIGH |
| subscriptions | ENDED | subscription_ended | INFO | MEDIUM |
| generated_document | PENDING | document_pending | INFO | NONE |
| generated_document | GENERATED | document_ready | INFO | NONE |
| generated_document | FAILED | document_failed | WARNING | MEDIUM |
| generated_document | TEMPLATE_MISSING | document_template_missing | WARNING | LOW |
| diagnosis_session | IN_PROGRESS | diagnosis_running | INFO | NONE |
| diagnosis_session | COMPLETED | diagnosis_completed | INFO | NONE |
| runtime_doc_activation | ACTIVATED | document_activated | INFO | NONE |
| runtime_doc_activation | NOT_ACTIVATED | document_not_activated | INFO | NONE |
| integrity_event | CRITICAL | incident_critical | CRITICAL | HIGH |
| integrity_event | WARNING | incident_warning | WARNING | MEDIUM |

## LLM Context \ucd9c\ub825 \uc608\uc2dc

```json
{
  "source": "payments",
  "operational_events": [
    {
      "event": "payment_pending",
      "severity": "INFO",
      "tenant_impact": "NONE",
      "recoverable": true
    }
  ],
  "payment": {
    "status": "PENDING",
    "plan": "BUILDING_TEST",
    "amount": "10000",
    "product_type": "SAAS_BUILDING"
  }
}
```

vs Legacy:
```json
{"status_code": "PENDING", "plan_code": "BUILDING_TEST", "total_amount": 10000}
```

## API

| API | \uc6a9\ub3c4 |
|-----|------|
| `GET /semantic/translate?source_table=&key=&value=` | \ub2e8\uc77c \uc0c1\ud0dc \ubcc0\ud658 |
| `GET /semantic/translate-record?source_table=&record_id=` | \ub808\ucf54\ub4dc \uc804\uccb4 \ubcc0\ud658 |
| `GET /semantic/mappings` | \uc804\uccb4 \ub9e4\ud551 \ubaa9\ub85d |
| `GET /semantic/coverage` | \ub9e4\ud551 \ucee4\ubc84\ub9ac\uc9c0 |
| `POST /semantic/invalidate-cache` | \uce90\uc2dc \ucd08\uae30\ud654 |

## \uaddc\uce59

1. **Watch/Governance/Notification/LLM\uc740 Legacy \uc0c1\ud0dc \uc9c1\uc811 \ucc38\uc870 \uae08\uc9c0** \u2014 Adapter\ub97c \ud1b5\ud574\uc11c\ub9cc \uc18c\ube44
2. **Legacy Runtime\uc740 \uc720\uc9c0** \u2014 Adapter\ub294 \ucd94\uac00 \uacc4\uce35
3. **\ub9e4\ud551 \uc5c6\ub294 \uc0c1\ud0dc\ub294 fallback** \u2014 `{source}_{key}_{value}` \ud615\uc2dd, `mapped=false`
4. **\uce90\uc2dc \uc0ac\uc6a9** \u2014 \uc11c\ubc84 \uc2dc\uc791 \uc2dc 1\ud68c \ub85c\ub4dc, invalidate-cache\ub85c \ucd08\uae30\ud654
