# INSPECTION_DOCUMENT_GROWTH_MODEL_v1

```
WP        = WP-DATA-ARCH-01
STAGE     = CANONICAL DOCUMENT (post CORR-01 PASS / CLOSED)
SOURCE REPO      = taiengineering/tai-api
SOURCE MAIN SHA  = e1506aa45d3b35bf4d99d3c123600e9f19ab6996
CANONICAL REPO   = taiengineering/taieng
CANONICAL PATH   = docs/
DATE      = 2026-08-23
MODE      = READ ONLY (문서화 전용)
MUTATION  = 0
근거표기   = [실측]=DB 직독 / [코드근거]=repo 직독 / [판정]=아키텍처 판정 / [한계]=미특정
```

절대치 extrapolation을 사용하지 않는다. 성장은 변수식으로만 표현하며, 현재 데이터는
개발 샘플로만 취급한다.

---

## 1. 변수 정의

```
F = active factories                     = 5,459   [실측]
S = active inspection sets / factory     = 미확정   (327 sets가 7 factory에만 집중 [실측] — 균일분포 아님)
I = inspection items / set               = OBSERVED SAMPLE ≈ 16 (5,184/327) — 운영평균 아님
E = executions / set / year              = 미확정   (점검주기 의존)
D = active schedules / factory           = 미확정   (66 schedules가 4 factory에만 [실측])
C = confirmed documents / factory / year = 미확정   (현재 archive 0)
O = generated outputs / confirmed doc    = 미확정
```

---

## 2. 성장식

```
work_assignments / year          = F × D × 365     [daily-instance 모델, cron 활성 시]
safety_inspections / year        = F × S × E
safety_inspection_results / year = F × S × E × I
runtime_document_archive / year  = F × C
generated_document / year        = F × C × O
```

---

## 3. Observed Sample (일반화 금지)

```
inspection_set_items / populated set ≈ 16   → OBSERVED DEVELOPMENT SAMPLE
inspection_sets 존재 factory = 7 / 5,459
work_schedules 존재 factory  = 4 / 5,459
```

[판정] DO NOT GENERALIZE — 현재 Inspection 데이터는 전체 factory에 걸친 운영 샘플이 아니라
소수 factory에 집중된 개발/시딩 국소 샘플이다. factory당 계수(S,I,E,D,C,O)를 현 데이터로
확정하지 않는다.

---

## 4. Daily Assignment Generator (원천 확정)

```
function      = public.generate_daily_assignments()                     [실측 존재, 인자 없음]
behavior      = active work_schedules → 하루 1 work_assignment
                / scheduled_date = current_date / status_code = READY    [코드근거]
cron          = jobname 'daily_assignments'
                schedule '10 0 * * *'
                command  'SELECT generate_daily_assignments()'           [실측]
```

### 실행 이력 (CONFIRMED)

```
first run     = 2026-04-28   [실측: cron.job_run_details]
last run      = 2026-08-22   [실측]
total runs    = 117          [실측]
succeeded     = 117          [실측]
failed        = 0            [실측]
current state = active = FALSE (비활성)  [실측]
```

[판정]
```
GROWTH CLASS     = HIGH LINEAR APPEND
GENERATING MODEL = active work schedule × daily execution instance
HISTORICAL CRON  = CONFIRMED   (117 runs, 무결)
CURRENT CRON     = INACTIVE
```

- 현재 work_assignments 5,991 = 62 schedules × 경과일 누적(과거 가동분). schedule당 max 100일, avg 96.6 [실측].
- growth dimension = active schedules × elapsed days.
- "UNBOUNDED / 멱등성 없는 미확인 generator" 판정은 폐기됨(원천·이력 확정).

---

## 5. Duplicate Risk (Growth와 분리)

```
DUPLICATE OBSERVED    = 0
                        (schedule_id, scheduled_date) 실제 중복 = 0  [실측]
DUPLICATE PROTECTION  = ABSENT
                        UNIQUE(schedule_id, scheduled_date) 제약 부재  [실측]
```

[판정]
- DAILY GROWTH ≠ DUPLICATE BUG. 현재 중복은 발생하지 않았다.
- [DUPLICATE RISK] same-day generator 재실행 시 중복 row 생성 가능(제약 부재).
- 이는 성장 문제가 아니라 멱등성 보호 부재 문제로, 별도 관리한다.

---

## 6. 테이블별 Growth Class

```
Table                         Growth Class            성장 차원
----------------------------  ----------------------  ------------------------------
work_assignments              HIGH LINEAR APPEND      active schedules × elapsed days (cron-gated)
safety_inspection_results     P0 (최대 실운영 성장축)  F × S × E × I
safety_inspections            HIGH                    F × S × E
runtime_document_archive      confirm × retention     F × C   (현재 0, 미검증)
generated_document            document × export       F × C × O
inspection_sets / _items      factory-linear (국소)    현재 7 factory 집중
work_schedules                factory-linear (국소)    현재 4 factory 집중
schedule_candidate            1회성 배치 (정지)         projection/candidate — SoT 아님, purge 대상
runtime_compliance_evidence   비성장 (mock)            50,301 = mock 50,000 + stress 300 + upload 1
```

[판정] 실제 지속 누적·고성장 위험축은 (a) work_assignments의 HIGH LINEAR APPEND(cron 재활성 시),
(b) 미래 safety_inspection_results의 F×S×E×I 성장이다. 대용량 두 테이블
(schedule_candidate, runtime_compliance_evidence)은 과거 1회성/mock 산출물로 성장축이 아니다.
