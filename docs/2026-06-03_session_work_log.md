# 세션 작업 로그 — 2026-06-03 (LEG/Check/Quality 검증 완결)

> 분류: 운영 세션 작업 로그\
> 작성 기준: 실제 터미널 실행 로그 기반. 추측 없음.\
> 연관 문서: `docs/TAI_HANDOFF_2026-06.md` (상태 요약)

---

## Phase 8B 최종 — raw EvidenceReport 캡처

**목적:** zsh-safe 명령(`${=CHECK_RUNNER_CMD}`)으로 실제 Check 엔진에 normal 케이스를 통과시켜 EvidenceReport를 캡처.

**실제 캡처된 관측값:**
```
claim c1    → CLAIM_PRESENT
evidence e1 → EVIDENCE_ATTACHED
chain ch1   → EVIDENCE_CHAIN_COMPLETE
inventory   → claims_received 1 / evidence_received 1 / chains_received 1
engine      → check 0.1.0 / schema v1 / output_kind evidence_report
report_id   → rpt_17kvms9y3hain
```

**레포:** `45cminc/leg` | `reports/PHASE8B_LIVE_VALIDATION.md` 갱신 (commit `b7c54183` → 최종 `fd323b2`)

---

## Phase 9 — Quality Evaluator 검증

**테스트 실행:**
```
python -m pytest tests/test_obligation_quality_evaluator.py -v
```
**결과 (실제 로그):** `6 passed in 0.02s` (Python 3.14.3, pytest 9.0.3)

검증된 항목 (35 fixture 전수):
- READY / TRACE_REQUIRED / CORRECTION_REQUIRED 전 케이스
- 중복(DUPLICATE_OBLIGATION) / 근거누락(EVIDENCE_INSUFFICIENT) / 조치누락(ACTION_INSUFFICIENT)
- `is_schedulable` 게이트 판정

**레포:** `taiengineering/tai-api` | 브랜치 `obligation-quality/phase9-mvp` | PR #89 (Draft)

---

## Phase 10 — Quality Store Backfill Smoke Test

> ⚠️ 이름 정정: 원래 "Quality Runtime Activation"이었으나 실제 수행 범위와 달라 수정.

### DB 조회 전 소스 탐색

**문제:** `factory_diagnosis_results.result_data.inspection_required` = 없음. schedule_pipeline과 키 불일치.

**실제 진단 구조 (DB 직접 확인):**
```
result_data.rules[]        → 1,000 룰
result_data.inspection_required → 존재하지 않음
```

**work_schedules 조회 결과:**
```
total: 60건 (MANUAL 58 / LEGAL 2)
rule_code: 0건 (law 연결 없음) → 의무 원장 아님
```

→ 배치 소스를 `result_data.rules[]`로 확정.

### 배치 실행

**migration 적용:** `sql/20260603_obligation_quality_layer.sql` → Supabase `taieng`

**배치 실행 (railway run 사용 — service_role 키 주입):**
```
railway run sh -c 'PYTHONPATH=. python scripts/run_quality_batch.py --commit'
```

**RLS 이슈 및 해결:**
- `--commit` 시 `42501 new row violates row-level security policy` 발생
- 원인: `get_supabase()`가 로컬에서 `SUPABASE_KEY`(anon) 사용 → RLS 차단
- 해결: `railway run`으로 Railway 환경의 `SUPABASE_SERVICE_KEY`(service_role) 주입

**검증 결과 (실제 실행 로그):**
```json
{
  "source": "diagnosis",
  "mode": "commit",
  "source_rows": 1,
  "obligation_count": 1000,
  "conflicts": 0,
  "coverage": {
    "total": 1000,
    "distribution": { "READY": 0, "TRACE_REQUIRED": 1000, "CORRECTION_REQUIRED": 0 },
    "fully_classified": true
  },
  "persisted": 1000
}
```

**테이블 재확인:**
```json
{ "obligation_quality_rows": 1000, "admin_obligation_queue_total": 0 }
```

**레포:** `taiengineering/tai-api` | 브랜치 `quality-runtime/phase10-activation` | PR #90 (Draft)

---

## Phase 10A — LEG→Check Output Verification

### 발생 버그 및 수정

**버그 1: `build_check_input` 시그니처 불일치**
- 실제 시그니처: `build_check_input(leg_output, *, diagnosis_id, now, request_ref, observer, runtime_owner)`
- 내가 호출한 방식: `scope_ref=...` (없는 파라미터), `now=` 누락
- 수정: `diagnosis_id=f"phase10a-{tag}"`, `now=_NOW` 추가, `scope_ref` 제거

**버그 2: V4 결정론성 테스트 실패**
- 원인: `_build(ob, "case-a-d1")`과 `_build(ob, "case-a-d2")`로 서로 다른 `diagnosis_id` → `scope_ref` 달라짐 → claims 불일치
- 수정: 두 호출 모두 동일 `case_tag` 사용 → 진짜 결정론성 검증

### 최종 검증 결과 (실제 실행 로그, check_available: true)

**Case A — 진단 룰 (evidence.chain 없음):**
```
V1 claim_ref: "leg:obligation:ELEVATORSAFETYACT-003-2-COMMON-003-V2" → PASS
V2 evidence_chains: 0 → PASS
V3 Check 출력: CLAIM_PRESENT=1, EVIDENCE_CHAIN_NOT_DECLARED=1
V4 adapter_deterministic: true, check_deterministic: true
```

**Case B — LEG 의무 (evidence.chain 1개, attached:True):**
```
V1 claim_ref: "leg:obligation:OB-LEG-ELEV-001" → PASS
V2 evidence_chains: 1 → PASS
V3 Check 출력: CLAIM_PRESENT=1, EVIDENCE_ATTACHED=1, EVIDENCE_CHAIN_COMPLETE=1
V4 adapter_deterministic: true, check_deterministic: true
```

**→ READY 경로 실증:** evidence.chain + attached:True → CHAIN_COMPLETE → evaluate_quality → READY

**레포:** `45cminc/leg` | 브랜치 `quality-verification/phase10a-leg-check` | PR #4 (Draft)

---

## Phase 10B — Check→Quality Verification

**실행:**
```
PYTHONPATH=. python3 verification/phase10b_check_quality_verification.py
```

**결과 (실제 로그):** `11/11 PASS`

| ID | 검증 항목 | 결과 |
|----|-----------|------|
| V1a | CLAIM_PRESENT+EVIDENCE_ATTACHED+CHAIN_COMPLETE → READY | ✅ PASS |
| V1b | EVIDENCE_REF_RESOLVED+CHAIN_COMPLETE → READY | ✅ PASS |
| V2a | EVIDENCE_NOT_ATTACHED → TRACE_REQUIRED | ✅ PASS |
| V2b | CHAIN_NOT_DECLARED → TRACE_REQUIRED (ACTION_INSUFFICIENT) | ✅ PASS |
| V2c | CHAIN_BROKEN → TRACE_REQUIRED | ✅ PASS |
| V2d | 관측로그 0건 → TRACE_REQUIRED | ✅ PASS |
| V3a | CLAIM_REF_MISSING → CORRECTION_REQUIRED | ✅ PASS |
| V3b | status_summary 누락 → CORRECTION_REQUIRED (DATA_ERROR) | ✅ PASS |
| V3c | 리포트 None → CORRECTION_REQUIRED (DATA_ERROR) | ✅ PASS |
| V3d | 법령 연결 누락 → CORRECTION_REQUIRED (LAW_LINK_ERROR) | ✅ PASS |
| V4a | duplicate=True → CORRECTION_REQUIRED (DUPLICATE_OBLIGATION) | ✅ PASS |
| V5 | 결정론성 (run1=READY, run2=READY) | ✅ PASS |

**레포:** `taiengineering/tai-api` | 브랜치 `quality-verification/phase10b-check-quality` | PR #91 (Draft)

---

## Phase 11 — Real User Simulation (50개 사업장 관찰)

**산출물 (taiengineering/tai-api PR #92):**
- `REAL_USER_SIMULATION_DATASET.md` — 건설업 12 / 건축물 운영 10 / 제조·기타 28
- `LEGAL_ENGINE_OBSERVATION_REPORT.md`
- `CHECK_OBSERVATION_REPORT.md`
- `REFINEMENT_OBSERVATION_REPORT.md`
- `TOP_30_FINDINGS.md` (중요도 순 30건)

**핵심 관찰 (실제 데이터 기준):**

| 발견 # | 내용 | 중요도 |
|--------|------|--------|
| #1 | READY 0건 (전 사업장) | 🔴 |
| #2 | result_data.rules ↔ schedule_pipeline inspection_required 키 불일치 | 🔴 |
| #3 | LEG 의무 스키마에 evidence.chain 없음 | 🔴 |
| #4 | 압력용기·크레인 사양 일반 사용자 입력 불가 | 🟠 |
| #6 | law_system="NOT_MAPPED" 룰 실제 확인 | 🟠 |

---

## 이번 세션 종합

| 구분 | 상태 |
|------|------|
| 코드 변경 | 없음 (관찰 단계) |
| 새 엔진 | 없음 |
| 테스트 실행 | Phase 9(6 pass) + Phase 10B(11 pass) + Phase 10A(adapter+Check 전 pass) |
| DB 변경 | obligation_quality 1,000건 적재 (TRACE_REQUIRED), admin_queue 0건 |
| 미결 결정 | enforce_quality 기본값, evidence.chain 연결 방식, 스키마 키 불일치 해소 |
| Merge | 없음 (전 PR Draft 유지) |
