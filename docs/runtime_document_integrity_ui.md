# Runtime document integrity UI

## API source

The viewer reads `rendering_integrity` from the same runtime payload as the document (computed server-side together with evidence binding).

## Rollup status

- **PASS**: no issues.
- **WARNING**: issues such as orphan evidence or missing source mapping (non-blocking for `creatable` by design).
- **CRITICAL**: mandatory unresolved binding, hidden mandatory field while suppressed, or missing mandatory evidence linkage.

## Issue types (examples)

| type | severity | Meaning |
|------|----------|---------|
| `missing_source_mapping` | WARNING | Field has no `source` / mapping |
| `mandatory_unresolved` | CRITICAL | MANDATORY field not resolved from runtime |
| `hidden_mandatory_field` | CRITICAL | Mandatory field not visible after conditional evaluation |
| `orphan_evidence` | WARNING | Evidence rows not bound to any field |
| `missing_evidence` | CRITICAL | Mandatory evidence-type field has no bound evidence |

## Orphan evidence

Orphan evidence is **never hidden**. It appears in the integrity table and in the **Evidence** tab JSON (`evidence_summary.orphan_evidence`).

## Golden QA tab

Shallow JSON diff between an operator-supplied **expected** payload and the last **actual** response. **Publish blocking** is indicated when `creatable` is false, integrity rollup is CRITICAL, or the diff reports mismatches.
