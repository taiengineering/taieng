# INSPECTION_DOCUMENT_PARTITION_DECISION_v1

```
WP        = WP-DATA-ARCH-01
STAGE     = CANONICAL DOCUMENT (post CORR-01 PASS / CLOSED)
SOURCE REPO      = taiengineering/tai-api
SOURCE MAIN SHA  = e1506aa45d3b35bf4d99d3c123600e9f19ab6996
CANONICAL REPO   = taiengineering/taieng
CANONICAL PATH   = docs/
DATE      = 2026-08-23
MODE      = READ ONLY (문서화 전용)
MUTATION  = 0 (NO ALTER · 판단만)
근거표기   = [실측]=DB 직독 / [코드근거]=repo 직독 / [판정]=아키텍처 판정
```

work_schedules 및 그 child physical design은 기존 정본을 상속한다. 이 문서에서 재설계하지 않는다.

---

## 1. Partition Pruning 개념 분리 (동일시 금지)

세 문제는 서로 독립이며 하나로 취급하지 않는다.

```
A. Partition Pruning
   = partition key predicate로 결정.
     RANGE(checked_at) / RANGE(inspection_date) / RANGE(scheduled_date)이면
     factory_id 없이도 time pruning 가능.

B. Tenant / Factory Scoped Query
   = factory key 필요 (별개 문제).

C. Composite FK to Partitioned Parent
   = 상위 파티션 부모 FK 정합 (별개 문제).
```

[판정] "factory_id 없음 → partition pruning 불가" 주장은 폐기한다.
factory_id 부재는 B / C에만 관련하며 A(time pruning)와 무관하다.

---

## 2. 테이블별 결정

### work_schedules — EXISTING PHYSICAL DESIGN INHERITED
```
PARTITION  = PARTITION BY HASH(factory_id) MODULUS 16   (기존 정본 확정)
REDESIGN   = NO
child 구조 = (schedule_id, factory_id) → work_schedules(id, factory_id)  (상속)
```

### safety_inspection_results — P0 / DESIGN NOW
```
근거          = F × S × E × I, 최대 실운영 성장축 (현재 8건이라는 이유로 낮추지 않음)
time candidate= checked_at (RANGE)          [실측: timestamp with time zone 보유]
tenant candidate = 명시적 factory key 선택 시에만 필요 (단정 금지)
현재 제약     = PK(id), FK inspection_id→safety_inspections(nullable),
                inspection_set_item_id FK 없음(논리참조)  [실측]
```

### safety_inspections — P1 / DESIGN NOW
```
time축        = inspection_date 보유  [실측: timestamp without time zone]
factory_id    = 직접 컬럼 없음  [실측]
연계          = work_schedules partition migration FK 연계 → factory_id additive 설계 존재 표시
현재 제약     = assignment_id→work_schedules.id, inspector_id→users.id, asset_id→equipment_assets.id [실측]
```

### work_assignments — P2
```
Growth        = HIGH LINEAR APPEND
current cron   = INACTIVE  [실측]
판정          = row 증가만으로 자동 파티션 필수는 아님.
                기존 physical design의 child FK 변경(factory_id additive)과 함께 판단.
현재 제약     = schedule_id→work_schedules, assigned_user_id→users, asset_id→equipment_assets
                UNIQUE(schedule_id, scheduled_date) 부재  [실측]
```

### runtime_document_archive — DEFER PHYSICAL DESIGN
```
DEFER 이유
  1. 실제 row = 0  [실측]
  2. 실제 growth 미검증
  3. direct tenant key(factory_id/company_id) 없음  [실측]
  4. immutable + UNIQUE(runtime_document_id, document_version) Confirm 무결성 계약 보존 필요  [실측]
  5. time partition 적용 시 UNIQUE/PK 계약 영향 재검토 필요
주의: 05B(Confirm)를 partition 때문에 재오픈하지 않는다.
```

### runtime_compliance_evidence — DEFER (NO PARTITION NOW)
```
rows = 50,301 = MOCK_POPULATION 50,000 + SIMULATION_STRESS 300 + WORKER_UPLOAD 1  [실측]
판정 = mock 시딩. 성장 근거 아님 → 지금 partition 불필요.
```

### schedule_candidate — NO PARTITION / PURGE CANDIDATE
```
rows = 47,227 (1회성 candidate 생성)  [실측]
CLASS = Candidate / Projection · SoT 아님
판정 = partition 대상 아님. Retention / Purge 정책 후보.
```

---

## 3. 요약

```
EXISTING DESIGN INHERITED
  = work_schedules (HASH factory_id MOD 16) + child factory_id additive

DESIGN NOW
  = safety_inspection_results (P0) · safety_inspections (P1)

CONDITIONAL
  = work_assignments (P2, cron-gated + child FK 연동)

DEFERRED
  = runtime_document_archive (무결성 계약 보존) · runtime_compliance_evidence (mock)
  · schedule_candidate (purge)
```

[판정] 실행계 테이블(safety_inspections/results 등)의 factory_id 직접 부재는 A(pruning)의
차단 사유가 아니다. 단, B(tenant scope) / C(composite FK)를 위해서는 child에 factory_id를
additive하는 기존 설계 방향을 따른다. 물리 적용은 WP-DATA-ARCH-02에서 승인 후 진행.
