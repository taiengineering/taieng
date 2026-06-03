# TAI 프로젝트 핸드오프 — 2026년 6월

> 문서 분류: **운영 핸드오프** (엔진 문서 아님)\
> 작성 기준: 2026-06-03\
> 대상: 다음 세션, 다음 담당자, 또는 장기 보관

---

## 현재 상태 한 줄 요약

```
LEG / Check / Quality는 검증 완료.
현재는 엔진 개발 단계가 아니라
실제 사업장 데이터를 통한 관찰·분석 단계.
```

---

## 완료된 검증 내역

### Phase 8A — LEG→Check 어댑터 MVP
- 레포: `45cminc/leg` | 브랜치: `leg-check-integration/phase8-adapter-mvp` | PR #2
- `build_check_input`, `adapt_obligation` — LEG 의무를 Check 입력으로 변환
- **테스트 결과 (실제 실행):** 17 passed, 1 skipped

### Phase 8B — 라이브 Check 통합 검증
- 레포: `45cminc/leg` | 브랜치: `leg-check-integration/phase8b-live-validation` | PR #3 (Draft)
- 실제 `runCheck()` 를 통한 end-to-end 검증
- **테스트 결과 (실제 실행):** 22 passed, 0 skipped, 0 failed
- 실제 EvidenceReport 캡처: CLAIM_PRESENT=1, EVIDENCE_ATTACHED=1, CHAIN_COMPLETE=1

### Phase 9 — Obligation Quality Layer MVP
- 레포: `taiengineering/tai-api` | 브랜치: `obligation-quality/phase9-mvp` | PR #89 (Draft)
- `obligation_quality` / `admin_obligation_queue` 테이블 설계 + 마이그레이션
- `evaluate_quality`, `evaluate_batch`, `is_schedulable` — 순수 함수 평가기
- Schedule Gate (`enforce_quality` 파라미터, 기본값 False — 무중단)
- Admin Queue API (`GET/PATCH /admin/obligations/queue`)
- **테스트 결과 (실제 실행):** 6 passed (35 fixture 전수 검증)

### Phase 10 — Quality Store Backfill Smoke Test
> ⚠️ 이름 정정: 원래 "Quality Runtime Activation"으로 명명했으나 실제 수행한 것과 달라 정정.

- 레포: `taiengineering/tai-api` | 브랜치: `quality-runtime/phase10-activation` | PR #90 (Draft)
- 실제 DB 적재: 1,000건 upsert (전부 TRACE_REQUIRED)
- **검증된 사실 (실제 실행):**
  - obligation_quality_rows: 1,000
  - READY: 0 / TRACE_REQUIRED: 1,000 / CORRECTION_REQUIRED: 0
  - fully_classified: true
  - admin_obligation_queue_total: 0

### Phase 10A — LEG→Check Output Verification
- 레포: `45cminc/leg` | 브랜치: `quality-verification/phase10a-leg-check` | PR #4 (Draft)
- **검증된 사실 (실제 실행):**
  - V1 claim_ref 매핑: PASS (rule_code → `leg:obligation:{rule_code}`)
  - V2 evidence_refs 전달: PASS (chain 없음→0, chain 있음→1)
  - V3 Check 실제 출력: PASS
    - Case A (evidence 없음): CLAIM_PRESENT=1, CHAIN_NOT_DECLARED=1 → TRACE_REQUIRED
    - Case B (evidence.chain + attached:True): CLAIM_PRESENT=1, EVIDENCE_ATTACHED=1, CHAIN_COMPLETE=1 → **READY**
  - V4 결정론성: PASS (adapter + Check 모두)
- **핵심 발견:** evidence.chain에 attached:True 항목이 있으면 READY 경로가 실제로 작동함을 실증

### Phase 10B — Check→Quality Verification
- 레포: `taiengineering/tai-api` | 브랜치: `quality-verification/phase10b-check-quality` | PR #91 (Draft)
- **검증된 사실 (실제 실행):** 11/11 PASS
  - CLAIM_PRESENT + EVIDENCE_ATTACHED + CHAIN_COMPLETE → READY ✅
  - EVIDENCE_NOT_ATTACHED → TRACE_REQUIRED (EVIDENCE_INSUFFICIENT) ✅
  - CHAIN_NOT_DECLARED → TRACE_REQUIRED (ACTION_INSUFFICIENT) ✅
  - CLAIM_REF_MISSING → CORRECTION_REQUIRED (CLAIM_ERROR) ✅
  - DATA_ERROR / LAW_LINK_ERROR / DUPLICATE_OBLIGATION → CORRECTION_REQUIRED ✅
  - 결정론성 ✅

---

## 실제 데이터 기반 관찰 결과

> 출처: Phase 10 실제 DB 조회 + Phase 11 시뮬레이션 관찰 (추측 아님)

### 실제 DB 현황 (`taieng` Supabase)
- `factory_diagnosis_results`: 2건 (is_latest=1건)
- `work_schedules`: 60건 (MANUAL 58 / LEGAL 2, **rule_code 0건**)
- `legal_obligations`: 0건
- `obligation_quality`: 1,000건 (전부 TRACE_REQUIRED)
- `admin_obligation_queue`: 0건
- `evidence_candidate`: 접근 권한 없음 (별도 role 필요)

### 실제 진단 결과 구조
- `result_data.rules[]`: 1,000 룰 (승강기 안전관리법 등)
- `result_data.inspection_required`: **존재하지 않음** (schedule_pipeline이 기대하는 키와 불일치)
- `law_system = "NOT_MAPPED"` 룰 포함됨 (법령 매핑 미완성 의무 존재)

### Phase 11 — 50개 사업장 시뮬레이션 관찰 (Top 발견)

전체 발견 30건은 `taiengineering/tai-api` PR #92 참조.

🔴 **심각 (운영 블로킹):**
1. **READY 0건** — 50개 사업장 어디서도 스케줄 생성 불가. 원인: evidence.chain 미연결
2. **스키마 키 불일치** — `result_data.rules` vs schedule_pipeline이 읽는 `inspection_required`
3. **evidence.chain LEG 의무에 없음** — READY를 만들려면 evidence.chain이 필요하나 현재 의무 스키마에 없음

🟠 **높음 (데이터 품질):**
4. 압력용기·크레인 사양은 일반 관리자가 입력 불가 (전문가 확인 필요)
5. 이동형 사업장(운송업·소방공사·전기공사) 입력 체계 없음
6. `law_system = "NOT_MAPPED"` 룰이 실제 데이터에 존재

---

## PR / 브랜치 현황

| 레포 | PR | 브랜치 | 상태 | Merge |
|------|------|--------|------|-------|
| 45cminc/leg | #1 | phase7-design | Open | 금지 |
| 45cminc/leg | #2 | phase8-adapter-mvp | Open | 금지 |
| 45cminc/leg | #3 | phase8b-live-validation | Draft | 금지 |
| 45cminc/leg | #4 | phase10a-leg-check | Draft | 금지 |
| taiengineering/tai-api | #89 | obligation-quality/phase9-mvp | Draft | 금지 |
| taiengineering/tai-api | #90 | quality-runtime/phase10-activation | Draft | 금지 |
| taiengineering/tai-api | #91 | quality-verification/phase10b-check-quality | Draft | 금지 |
| taiengineering/tai-api | #92 | simulation/phase11-real-user | Draft | 금지 |

Merge 순서 권장 (전부 사람 결정):
`45cminc/leg` PR #1 → #2 → #3 → #4\
`taiengineering/tai-api` PR #89 → #90 → #91 → #92

---

## 보류 중인 결정 (사람이 결정)

1. **`enforce_quality` 기본값** — 현재 False(무중단). READY 0건인 상태에서 True로 바꾸면 스케줄 0건이 됨. evidence.chain 연결 후 전환 권장
2. **evidence.chain 연결 방식** — LEG의 constraint_node/constraint_edge를 evidence.chain에 어떻게 연결할지 (다음 단계의 핵심 설계 결정)
3. **1개 사업장 1,000 룰 적정 여부** — 판단 기준이 없어 판단 불가. 법령 전문가 검토 필요
4. **PR Merge 시점** — 모든 PR은 Draft 상태이며 사람이 판단 후 Merge

---

## 다음 단계 후보 (결정하지 않음, 관찰 기반 나열)

```
A. evidence.chain을 LEG 의무에 연결 (constraint_node → evidence.chain)
   → READY 발생 가능성의 첫 번째 조건

B. result_data.rules ↔ schedule_pipeline 스키마 키 불일치 해소
   → generate-schedules 실제 동작 가능

C. 업종별 의무 수 벤치마크 정의
   → 1,000건 과다 여부 판단 가능

D. 이동형 사업장 입력 체계 설계
   → 운송업·공사업 사용자 경험 개선

E. 입력 불가 정보(압력용기 사양 등) 처리 방식 결정
   → 사용자 안내 vs 전문가 대리입력 vs 생략
```

이 문서는 **무엇을 해야 하는지 결정하지 않습니다.** 현재 상태와 관찰 결과를 기록한 것입니다.

---

## 인프라 참조

| 항목 | 값 |
|------|-----|
| Supabase (taieng) | `vwlahtguyggrhvslabax` |
| 의무 배치 실행 | `railway run sh -c 'PYTHONPATH=. python scripts/run_quality_batch.py --commit'` |
| Coverage 확인 (로컬) | `railway run sh -c 'PYTHONPATH=. python scripts/quality_coverage_report.py'` |
| Phase 10A Check 환경 | `check-10a/` (phase6 빌드), `leg-10a/check-runner/runner.mjs` |
| RLS 참고 | obligation_quality / admin_obligation_queue 모두 RLS 활성화. 쓰기는 service_role 키 필요 |
