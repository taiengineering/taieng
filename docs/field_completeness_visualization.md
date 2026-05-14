# Field completeness visualization

## Status colors (UI)

| API `completeness.status` | Color / label |
|---------------------------|----------------|
| PASS | Green |
| WARNING | Amber (recommended empty, etc.) |
| FAIL | Red (mandatory empty, invalid numeric/date, missing signature/evidence per rules) |
| UNSUPPORTED | Grey (reserved for client; server returns FAIL/WARNING/PASS today) |

## Reason codes

Mapped in the viewer for the FAIL summary list (Korean labels), including:

- `mandatory_field_empty`, `recommended_field_empty`
- `invalid_numeric_value`, `invalid_date`
- `signature_missing`, `evidence_missing`

Rules come from `validation_rule` on each field in the runtime payload. Evidence-required checks use `evidence_bound` after the server binds evidence **before** completeness evaluation.

## Document-level summary

`completeness.creatable` is `true` only when all **visible** mandatory fields pass. Recommended gaps produce warnings but do not force `creatable=false`.
