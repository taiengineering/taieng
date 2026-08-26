-- WP-PERSISTENCE-02B B2 — UP (REV-2, concurrency-hardened)
-- Purpose: bind the single ELIGIBLE inspection_set bridge to the approved GENERAL
--          presentation schema (GEN-INSPECT-RESULT-001).
-- Target set    : 7fee7518-0e77-445c-b822-d5178d069b3c (소방시설공사업법 점검, FIRE, INSPECT)
-- Target bridge : 3894ddb5-df96-4dc9-8cf0-940d3300b38a
-- GENERAL schema: dc79ac3c-388c-42dc-b029-3dd9bda54a47 (APPROVED_FOR_RUNTIME_USE, field_count 5)
-- Mutation scope: runtime_form_schema_id ONLY. Never mapping_status / mapping_detail /
--                 inspection_set_name / runtime_checklist_count / GENERAL schema /
--                 runtime_field / runtime_document_data / generated_document.
-- Concurrency   : bridge SHARE ROW EXCLUSIVE (blocks concurrent INSERT/UPDATE/DELETE, allows SELECT)
--                 holds precondition -> UPDATE -> postcondition -> COMMIT free of population drift;
--                 GENERAL schema target row FOR SHARE (blocks approval-state mutation in-tx).
-- Atomicity     : in-tx precondition assert -> UPDATE -> GET DIAGNOSTICS ROW_COUNT=1 assert
--                 -> target-specific + global postcondition assert. Any deviation -> ROLLBACK.

BEGIN;

-- Concurrency gate: freeze the bridge population for the whole transaction.
LOCK TABLE runtime_inspection_bridge IN SHARE ROW EXCLUSIVE MODE;

DO $$
DECLARE
  v_schema_status text;
  v_schema_fields int;
  v_target_rows   int;
  v_target_null   int;
  v_total         int;
  v_with_schema   int;
  v_to_general    int;
  v_affected      int;
  v_target_schema uuid;
  v_target_status text;
BEGIN
  -- 0) GENERAL schema: lock the exact target row (FOR SHARE), then assert (no aggregate+FOR SHARE)
  SELECT status, field_count
    INTO v_schema_status, v_schema_fields
    FROM runtime_form_schema
   WHERE id = 'dc79ac3c-388c-42dc-b029-3dd9bda54a47'
   FOR SHARE;
  IF NOT FOUND THEN RAISE EXCEPTION 'UP precond fail: GENERAL schema row not found'; END IF;
  IF v_schema_status <> 'APPROVED_FOR_RUNTIME_USE'
    THEN RAISE EXCEPTION 'UP precond fail: GENERAL status=% (expected APPROVED_FOR_RUNTIME_USE)', v_schema_status; END IF;
  IF v_schema_fields <> 5
    THEN RAISE EXCEPTION 'UP precond fail: GENERAL field_count=% (expected 5)', v_schema_fields; END IF;

  -- 1) PRECONDITION (before UPDATE)
  SELECT COUNT(*),
         COUNT(*) FILTER (WHERE runtime_form_schema_id IS NULL)
    INTO v_target_rows, v_target_null
    FROM runtime_inspection_bridge
   WHERE inspection_set_id = '7fee7518-0e77-445c-b822-d5178d069b3c';

  SELECT COUNT(*),
         COUNT(*) FILTER (WHERE runtime_form_schema_id IS NOT NULL),
         COUNT(*) FILTER (WHERE runtime_form_schema_id = 'dc79ac3c-388c-42dc-b029-3dd9bda54a47')
    INTO v_total, v_with_schema, v_to_general
    FROM runtime_inspection_bridge;

  IF v_target_rows <> 1 THEN RAISE EXCEPTION 'UP precond fail: target bridge rows=% (expected 1)', v_target_rows; END IF;
  IF v_target_null <> 1 THEN RAISE EXCEPTION 'UP precond fail: target IS NULL rows=% (expected 1)', v_target_null; END IF;
  IF v_total       <> 324 THEN RAISE EXCEPTION 'UP precond fail: bridge_total=% (expected 324)', v_total; END IF;
  IF v_with_schema <> 0 THEN RAISE EXCEPTION 'UP precond fail: bridge_with_schema=% (expected 0)', v_with_schema; END IF;
  IF v_to_general  <> 0 THEN RAISE EXCEPTION 'UP precond fail: bridge_to_general=% (expected 0)', v_to_general; END IF;

  -- 2) MUTATION (runtime_form_schema_id only) + exact affected-row assert
  UPDATE runtime_inspection_bridge
     SET runtime_form_schema_id = 'dc79ac3c-388c-42dc-b029-3dd9bda54a47'
   WHERE inspection_set_id = '7fee7518-0e77-445c-b822-d5178d069b3c'
     AND runtime_form_schema_id IS NULL;

  GET DIAGNOSTICS v_affected = ROW_COUNT;
  IF v_affected <> 1 THEN RAISE EXCEPTION 'UP fail: affected_rows=% (expected exactly 1)', v_affected; END IF;

  -- 3) TARGET-SPECIFIC POSTCONDITION (exactly target row is GENERAL, status preserved)
  SELECT runtime_form_schema_id, mapping_status
    INTO v_target_schema, v_target_status
    FROM runtime_inspection_bridge
   WHERE inspection_set_id = '7fee7518-0e77-445c-b822-d5178d069b3c';

  IF v_target_schema IS DISTINCT FROM 'dc79ac3c-388c-42dc-b029-3dd9bda54a47'
    THEN RAISE EXCEPTION 'UP post fail: target schema_id=% (expected dc79ac3c...)', v_target_schema; END IF;
  IF v_target_status <> 'MAPPED'
    THEN RAISE EXCEPTION 'UP post fail: target mapping_status=% (expected MAPPED unchanged)', v_target_status; END IF;

  -- global postcondition
  SELECT COUNT(*),
         COUNT(*) FILTER (WHERE runtime_form_schema_id IS NOT NULL),
         COUNT(*) FILTER (WHERE runtime_form_schema_id = 'dc79ac3c-388c-42dc-b029-3dd9bda54a47')
    INTO v_total, v_with_schema, v_to_general
    FROM runtime_inspection_bridge;

  IF v_total <> 324 OR v_with_schema <> 1 OR v_to_general <> 1 THEN
    RAISE EXCEPTION 'UP post fail: total=% with_schema=% to_general=% (expected 324/1/1)', v_total, v_with_schema, v_to_general;
  END IF;
END $$;

COMMIT;
