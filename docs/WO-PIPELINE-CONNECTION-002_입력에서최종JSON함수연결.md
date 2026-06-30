# WO-PIPELINE-CONNECTION-002 — Consumer Input → Final Result(JSON) 함수 연결 추적

**작성일:** 2026-06-30 | **선행 무효화:** WO-PIPELINE-CONNECTION-001 폐기(Row count 기반 판단·runtime 테이블 조기 진입 — 무효).
**기준:** 함수 호출 Connection만. 숫자/COUNT/Row 수 사용 안 함. 범위 = Consumer Input → Final Result(JSON). runtime_obligation_assignment/runtime_task/safety_reports 분석 안 함.

> 결론: 이 범위(입력→최종 결과 JSON) 안에서 **함수 호출은 전 구간 직접 연결(CONNECTED)**. 함수 단절(BROKEN)은 없음.

---

## TASK-001 — 함수 호출 체인 (코드 직독, 한 줄)
```
routers/anonymous_diagnosis.py (엔드포인트)
  → services/anonymous_factory_service.run_anonymous_diagnosis(supabase, body, allowed_sectors)
      → normalize_consumer_inp(body)                         # 정규화
          → _merge_body_input(body) → input_normalizer.normalize_input(...)
      → _input_to_facility_context(sector_raw, inp)          # 표준 컨텍스트
      → create_temp_factory(supabase, body)                  # 임시 factories row
      → evaluate_single_factory(supabase, factory_id)        # 체크엔진
          → _load_sector_allowed_draft_ids(...)
          → _load_draft_slot_groups(...)
          → facility_applicability_eval.evaluate_draft_for_facility(...)
      → compiler_core_svc.fetch_compiler_candidates(supabase, factory_id)   # 후보 수집
      → _compiler_result_to_step1_format(compiler, ...)      # 최종 결과 JSON 생성
          → _task_to_rule_row / _applicability_to_rule_row
          → _load_draft_fallback_context(...)  (task 없을 때 조문제목 주입)
      → (finally) cleanup_temp_factory(supabase, factory_id)
  ← return result_data (Final Result JSON)
```

## TASK-002 — 단계별 함수 연결 상태 (CONNECTED / BROKEN / BYPASS)
```
Consumer Input → run_anonymous_diagnosis        CONNECTED  (엔드포인트가 직접 호출)
run_anonymous_diagnosis → normalize_consumer_inp CONNECTED  (직접 호출)
normalize_consumer_inp → normalize_input         CONNECTED  (직접 호출)
→ _input_to_facility_context                     CONNECTED
→ create_temp_factory                            CONNECTED
create_temp_factory → evaluate_single_factory    CONNECTED
evaluate_single_factory → evaluate_draft_for_facility  CONNECTED
→ fetch_compiler_candidates                      CONNECTED  (직접 호출)
fetch_compiler_candidates → _compiler_result_to_step1_format  CONNECTED
_compiler_result_to_step1_format → Final Result JSON          CONNECTED  (return)
```

## TASK-003 — BROKEN(함수 단절)만 추림
```
(없음) — 입력에서 최종 결과 JSON까지 함수 호출이 끊긴 지점 없음.
```

## TASK-004 — 가장 앞 BROKEN 함수 연결 1개
```
해당 없음. 이 범위 내 BROKEN 함수 연결 0건.
※ 이전에 "BROKEN"으로 본 것은 함수 단절이 아니라 데이터 결핍(평가 입력값·draft binding)이었음 →
  함수 Connection 기준에서는 CONNECTED. 데이터 품질은 이 WO 기준(함수 연결) 밖.
```

## TASK-005~006 — 연결/검증
```
연결할 함수 단절이 없으므로 이번 WO에서 추가 연결 작업 없음.
이 범위의 종료 조건(입력→Final Result JSON 함수 전 구간 연결) 충족.
```

## 함의 (다음 범위의 시작점 — 이번 WO 밖)
```
입력→Final Result(JSON)는 함수로 닫혀 있음(run_anonymous_diagnosis가 result_data를 return).
따라서 "다음 연결점"은 이 범위가 아니라 그 다음 경계 —
  Final Result(JSON) → SaaS 진입 함수 호출 —
에서 함수 기준으로 다시 추적해야 함. (이번 WO는 입력→JSON까지만이므로 여기서 종료.)
```

## Boundary 준수
```
함수 호출 Connection 기준만. 숫자/COUNT/Row 수 0. runtime_obligation_assignment/runtime_task/safety_reports 미분석.
범위 = Consumer Input → Final Result(JSON). 코드/DB 수정 0(읽기 전용).
```

*WO-PIPELINE-CONNECTION-002 — 입력→Final Result(JSON) 함수 호출 전 구간 CONNECTED. BROKEN 함수 연결 0. (CONNECTION-001 무효: row count 기반이었음.) 다음 추적 경계 = Final Result(JSON) → SaaS 진입 함수.*
