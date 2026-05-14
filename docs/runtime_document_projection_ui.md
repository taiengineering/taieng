# Runtime document projection UI

## Purpose

The SAFE **Runtime Document Governance Viewer** (`/html/runtime/document-viewer.html`) renders **only** the JSON returned by `GET /api/v1/document-runtime/{document_type}` (or `POST /api/v1/document-runtime/render` with optional context overrides). It is **not** a PDF preview and does not embed static form layouts.

## Hierarchy

Document → Section → Field. Each field row is driven by the payload: `field_label`, `value`, `completeness`, evidence binding flags, `source_trace`, and `conditional_reason` when a conditional rule is not satisfied.

## Summary panel

- `total_fields`, `mandatory` / `recommended` completion percentages from `completeness`.
- Evidence: `evidence_summary.evidence_bound_mandatory_pct` and `orphan_evidence_count`.
- `creatable`: when `false`, a **CRITICAL** banner is shown at the top.

## Conditional sections / fields

The API evaluates `conditional_rule` per field and sets `visible`, `condition_result`, and `conditional_reason`. Fields with `visible: false` are rendered in a **SUPPRESSED** block (not removed from the DOM) so governance and audit trails stay visible.

## Explainability

Per-field **Explain** opens an off-canvas panel with `source_mapping`, `source_trace`, `conditional_rule`, `conditional_reason`, and `completeness` verbatim from the payload.

## Refresh

Manual refresh and optional polling re-call `GET` so runtime DB changes (evidence, facility condition, etc.) surface without a full page reload.

## Related

- `runtime_document_integrity_ui.md`
- `field_completeness_visualization.md`
- `runtime_document_viewer_handoff.md`
