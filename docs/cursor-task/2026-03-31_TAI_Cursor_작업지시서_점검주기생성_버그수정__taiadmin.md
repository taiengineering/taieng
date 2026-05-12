# TAI Cursor 작업지시서 — 점검주기 생성 버그수정 (2026-03-31)

## 반영 내용 (tai-api)

### 버그1 — `legal_engine.py` `create-inspection-sets`
- `factories.legal_result_json`에 점검 목록이 없을 때 **fallback**:
  1. `legal_applications` 최신 `result_json.inspection_required`
  2. `factory_diagnosis_results`(최신 `is_latest`)의 `result_data.rules` → `rule_id`로 `master_building_legal_rules` 조회 후 `inspection_required` 또는 `obligation_type=INSPECT`인 룰만 `format_rule_result`로 변환

### 버그2 — `legal_engine.py` 주기 파싱
- `rule_id`로 마스터 조인 시 **`_cycle_unit_value_from_master_row`**: `inspection_cycle_unit_code` / `inspection_cycle_value` → `cycle_unit`·`cycle_value`
- 마스터 없을 때만 기존 **한글 라벨** `_cycle_unit_value_from_inspection_cycle_label` 사용
- 삽입 시 **`status_code: PENDING`**, **`anchor_confirmed: False`**, `cycle_base_guide`·`cycle_base_type`(마스터에 있으면)

### 버그3 — `schedule_engine.py` `POST /generate/{inspection_set_id}`
- `next_planned_date` 없을 때 **첫 일정 = `add_cycle(anchor, cycle_unit, cycle_value)`** (기준일 다음 주기)
- 생성한 마지막 일정 기준으로 **`next_planned_date`** 갱신, 응답에 `next_planned_date` 포함

### 버그5 — `inspection_checklist.py` `POST /generate-schedules/{factory_id}`
- **`anchor_confirmed is False`** 인 점검 세트는 루프에서 제외
- 응답 `data`에 **`skipped_anchor`** 카운트, `sets_total` / `sets_processed` 구분
