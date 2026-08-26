-- WP-PERSISTENCE-02B B2 — DOWN (REV-2, concurrency-hardened rollback)
-- Reverts the single GENERAL bind on the target bridge back to NULL.
-- Mutation scope: runtime_form_schema_id ONLY (same as UP).
-- Concurrency   : bridge SHARE ROW EXCLUSIVE (blocks concurrent INSERT/UPDATE/DELETE, allows SELECT)
--                 prevents population drift during rollback.
-- Atomicity: UPDATE -> GET DIAGNOSTICS ROW_COUNT=1 assert -> target NULL + global 324/0/0 assert.
--            Any deviation -> ROLLBACK.

BEGIN;

-- Concurrency gate: freeze the bridge population for the whole transaction.
LOCK TABLE runtime_inspection_bridge IN SHARE ROW EXCLUSIVE MODE;

DO $$
DECLARE
  v_affected      int;
  v_target_schema uuid;
  v_total         int;
  v_with_schema   int;
  v_to_general    int;
BEGIN
  -- MUTATION (exactly the previously-bound target row) + exact affected-row assert
  UPDATE runtime_inspection_bridge
     SET runtime_form_schema_id = NULL
   WHERE inspection_set_id = '7fee7518-0e77-445c-b822-d5178d069b3c'
     AND runtime_form_schema_id = 'dc79ac3c-388c-42dc-b029-3dd9bda54a47';

  GET DIAGNOSTICS v_affected = ROW_COUNT;
  IF v_affected <> 1 THEN RAISE EXCEPTION 'DOWN fail: affected_rows=% (expected exactly 1)', v_affected; END IF;

  -- target-specific postcondition
  SELECT runtime_form_schema_id
    INTO v_target_schema
    FROM runtime_inspection_bridge
   WHERE inspection_set_id = '7fee7518-0e77-445c-b822-d5178d069b3c';

  IF v_target_schema IS NOT NULL THEN
    RAISE EXCEPTION 'DOWN post fail: target schema_id=% (expected NULL)', v_target_schema;
  END IF;

  -- global postcondition (back to baseline)
  SELECT COUNT(*),
         COUNT(*) FILTER (WHERE runtime_form_schema_id IS NOT NULL),
         COUNT(*) FILTER (WHERE runtime_form_schema_id = 'dc79ac3c-388c-42dc-b029-3dd9bda54a47')
    INTO v_total, v_with_schema, v_to_general
    FROM runtime_inspection_bridge;

  IF v_total <> 324 OR v_with_schema <> 0 OR v_to_general <> 0 THEN
    RAISE EXCEPTION 'DOWN post fail: total=% with_schema=% to_general=% (expected 324/0/0)', v_total, v_with_schema, v_to_general;
  END IF;
END $$;

COMMIT;
