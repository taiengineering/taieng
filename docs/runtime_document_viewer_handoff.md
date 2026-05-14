# Runtime document viewer — engineering handoff

## Deploy path (SAFE)

Static file: `tai-admin/admin/full-version/html/runtime/document-viewer.html`  
Public URL (per work order): `https://safe.taieng.co.kr/html/runtime/document-viewer.html`

Legacy path `horizontal-menu-template/runtime/document-viewer.html` redirects to the canonical file.

## API (tai-api)

- `GET /api/v1/document-runtime/{document_type}?facility_id=` — returns sections, per-field binding, conditional flags, `completeness`, `evidence_summary`, `rendering_integrity`.
- `POST /api/v1/document-runtime/render` — body `{ "document_type", "facility_id"?, "context": { ...overrides } }` for deterministic re-evaluation without persisting overrides.

### Server changes bundled with this viewer

- `services/runtime_document_context.py` — merges `facility_id` + `facility_condition` + `runtime_facility_profile` into evaluation `context`.
- `services/rendering_integrity.py` — deterministic integrity rollup.
- `services/evidence_binding_engine.py` — evidence IDs used/unused → `orphan_evidence` list.
- `routers/document_runtime.py` — shared `_hydrate_runtime_payload` for GET/POST/integrity; evidence binding runs **before** completeness so `evidence_required` rules work.

## Auth

Viewer expects `access_token` in `localStorage` (same pattern as other SAFE HTML). Unauthenticated users are redirected to SAFE login.

## Operator toggles

- `localStorage.RUNTIME_API_BASE` — optional API prefix (default `https://api.taieng.co.kr/api/v1`).

## Follow-ups (not blocking viewer ship)

- Server-side PDF snapshot via Gotenberg from a **rendered HTML snapshot** of the payload (separate template service).
- Deeper Golden QA (schema-hash, section order, field-by-field semantic diff).
- `UNSUPPORTED` completeness branch for unknown bindings if product wants distinct UX from FAIL.

## Phase checklist (implementation truth)

| Phase | Delivered |
|-------|-------------|
| A — Payload viewer | Yes |
| B — Dynamic conditional | Yes (API + suppressed UI) |
| C — Field completeness | Yes |
| D — Evidence binding | Yes |
| E — Explainability panel | Yes |
| F — Completeness summary | Yes |
| G — Refresh | Yes (manual + poll) |
| H — PDF export | Partial (JSON artifact + browser print; no Gotenberg runtime route yet) |
| I — Integrity panel | Yes |
| J — Golden QA | Yes (shallow diff + publish blocking flags) |
