-- WP-PERSISTENCE-02B B2 — VERIFY (REV-1, read-only, run AFTER UP)
-- Read-only. No mutation. Confirms the 1-row bind landed on exactly the target row
-- AND that the architecture side-effect invariant held (zero side effect).
-- Expected values (all must be true):
--   target_bridge_rows        = 1
--   target_schema_id          = dc79ac3c-388c-42dc-b029-3dd9bda54a47
--   target_mapping_status     = MAPPED           (unchanged)
--   bridge_total              = 324
--   bridge_with_schema        = 1
--   bridge_to_general         = 1
--   runtime_document_data_total = 1               (side-effect zero, baseline)
--   generated_document_total    = 1544            (side-effect zero, baseline)

SELECT
  (SELECT COUNT(*)
     FROM runtime_inspection_bridge
    WHERE inspection_set_id = '7fee7518-0e77-445c-b822-d5178d069b3c')                         AS target_bridge_rows,
  (SELECT runtime_form_schema_id
     FROM runtime_inspection_bridge
    WHERE inspection_set_id = '7fee7518-0e77-445c-b822-d5178d069b3c')                         AS target_schema_id,
  (SELECT mapping_status
     FROM runtime_inspection_bridge
    WHERE inspection_set_id = '7fee7518-0e77-445c-b822-d5178d069b3c')                         AS target_mapping_status,
  (SELECT COUNT(*) FROM runtime_inspection_bridge)                                            AS bridge_total,
  (SELECT COUNT(*) FROM runtime_inspection_bridge WHERE runtime_form_schema_id IS NOT NULL)   AS bridge_with_schema,
  (SELECT COUNT(*) FROM runtime_inspection_bridge
    WHERE runtime_form_schema_id = 'dc79ac3c-388c-42dc-b029-3dd9bda54a47')                     AS bridge_to_general,
  (SELECT COUNT(*) FROM runtime_document_data)                                                AS runtime_document_data_total,
  (SELECT COUNT(*) FROM generated_document)                                                   AS generated_document_total;
