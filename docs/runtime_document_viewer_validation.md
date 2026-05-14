# Runtime document viewer — validation checklist

Use a known `document_type` and `facility_id` with staging or production API (`RUNTIME_API_BASE` in `localStorage` optional override).

## Mandatory gaps

1. Clear a mandatory-bound field value in runtime data (or use a facility missing that condition).
2. Reload the viewer.
3. Expect: field **FAIL**, top **FAIL 요약**, `creatable=false`, **CRITICAL** banner.

## Recommended gaps

1. Clear only a recommended field.
2. Expect: **WARNING** on field, `creatable` remains `true` if all mandatory pass.

## Orphan evidence

1. Upload evidence for the facility that does not match any `evidence_ref` / `image` field binding.
2. Expect: `orphan_evidence_count` &gt; 0, integrity rows `orphan_evidence`, warning banner text references orphan evidence.

## Conditional visibility

1. Set `facility_condition` (or POST overrides) so a `conditional_rule` fails.
2. Expect: affected fields show **SUPPRESSED** with `conditional_reason`; if an entire section’s fields are suppressed, section badge **section 전체 조건부 비표시**.

## Refresh

1. Change backend data; trigger manual refresh or enable polling.
2. Expect: counts and rows update without hard reload.

## PDF / artifact

- **JSON snapshot** download must match the on-screen payload (artifact, not source of truth).
- **Print / Save as PDF** uses the browser print pipeline on the governance layout (no fake paper-form mimic).

## AI / static layout (must NOT occur)

- No invented fields: section count matches API `sections.length`.
- No hidden removal of orphan evidence or integrity rows.
