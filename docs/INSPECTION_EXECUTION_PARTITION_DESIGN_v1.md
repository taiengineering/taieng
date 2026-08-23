# INSPECTION_EXECUTION_PARTITION_DESIGN_v1  (CANONICAL · WP-DATA-ARCH-02 PASS/CLOSED)

```
WP                 = WP-DATA-ARCH-02 · PD-4  (CORR-03 · WP-RETENTION-01 포함)
STAGE              = CANONICAL DOCUMENT (post CORR-03 PASS · WP-DATA-ARCH-02 CLOSED)
SOURCE API SHA     = e1506aa45d3b35bf4d99d3c123600e9f19ab6996
CANONICAL ARCH SHA = e83feabd80c7c515f0bfb9a859579213e9de9342
MODE               = READ ONLY / PHYSICAL DESIGN · MUTATION 0
근거표기            = [실측] / [코드근거] / [설계]
```

상속: work_schedules = HASH(factory_id) MOD 16 = INHERITED (재설계 금지).
Pruning 분리: A Partition Pruning ≠ B Tenant Scope ≠ C Composite FK to Partitioned Parent.

---

## 0. 확정 전제 (CORR-02~03)

```
① safety_inspections            = DO NOT PARTITION (incoming FK 2 → RANGE 시 PK ripple)
② safety_inspection_results      = RANGE(checked_at) (incoming FK 0 → 독립) + 자기 PK 변경 계약(§3)
③ Retention                      = H(HOT window) / R(i)(per-inspection legal) 분리
④ retention_until                = effective not-before-delete (단일 timestamp, legal_hold_count 삭제)
⑤ COLD authoritative store       = detached PostgreSQL partition (evidence_vault_link 금지)
⑥ runtime_evidence_retention_policy = existing asset, reference/default, legal SoT 아님
⑦ confirmed snapshot             = 문서 재출력 독립성만. 법정 원본 보존 대체 아님.
```

---

## 1. 실쿼리 패턴

```
safety_inspections [코드근거]      · id · inspector_id + inspection_date 당일 · inspector_id + date DESC LIMIT
safety_inspection_results [코드근거] · WHERE inspection_id = ? ORDER BY created_at (InspectionFetcher)
```

---

## 2. safety_inspections = DO NOT PARTITION

```
[실측] incoming FK 2 = defects.inspection_id, safety_inspection_results.inspection_id → safety_inspections.id
RANGE(inspection_date) 채택 시 PK=(id, inspection_date) 강제 → defects/results/source_inspection_id composite FK ripple.
CHOSEN = REGULAR TABLE 유지 · PK(id) 유지 · inspection_date = index/retention anchor(파티션 키 아님) · P1 partition DEFER
```

---

## 3. safety_inspection_results = RANGE(checked_at) + PK 변경 계약 (CORR-03)

```
[실측] 현재 PK = (id). incoming FK = 0.
PostgreSQL partitioned table PK/UNIQUE는 partition key 포함 필수.

CHOSEN 물리 계약
  PARTITION BY RANGE(checked_at)
  checked_at NOT NULL              [실측 NULL 0 → 강화 가능]
  PRIMARY KEY = (id, checked_at)   ← 자기 PK 변경 (CORR-03)
  Application identity = id (유지)
  DB physical identity  = (id, checked_at)
  incoming FK = 0 → child ripple 없음
  PARTITION LOCAL INDEX = (inspection_id, created_at)  ← 주 조회 WHERE inspection_id=? 서빙
    · checked_at = PARTITION / RETENTION AXIS
    · created_at = CURRENT CHILD-RESULT ORDERING AXIS (InspectionFetcher: WHERE inspection_id=? ORDER BY created_at)
    · 두 축 동일할 필요 없음. (향후 코드를 ORDER BY checked_at으로 바꾸기로 별도 결정하면 checked_at 정렬축 인덱스도 가능하나,
      현재 코드 재사용 원칙상 인덱스를 현재 consumer에 맞춤)
  inspection_id FK → safety_inspections.id (regular table라 single-id FK 유지 가능)
  driver = retention 시간 생명주기 (RANGE detach 가능)
```

---

## 4. factory_id 계약

```
safety_inspections.factory_id = work_schedules composite FK companion ONLY (nullable)
  · canonical tenant key = NO · HASH partition key = NO · 업무 tenant filter 금지 (정본 상속)
safety_inspection_results.factory_id = 삭제 (불필요)
[실측] inspections 2건 중 assignment 無 1건 → factory 결정적 backfill 불가 row 존재
```

---

## 5. WP-RETENTION-01 (CORR-03)

전제: 문서 snapshot 독립(ORCHESTRATION §5)은 **문서 재출력 독립성**만 보장. 법이 원본 점검기록
보존을 요구하면 그 의무를 대체하지 않는다.

### 5-0. 기존 retention 자산 분류 (CORR-03, 기존자산 우선)
```
[실측] runtime_evidence_retention_policy (rows 8, evidence_type UNIQUE, source_trace=MANUAL_CONFIG, deletion_allowed=false)
  예: INSPECTION_RESULT 3Y(산안법 제36조) · MEASUREMENT 5Y(제125조) · REPORT 5Y(중대재해처벌법 제4조)
     · CERTIFICATE 5Y · PHOTO/SIGNATURE/TRAINING_RECORD/DOCUMENT_ATTACHMENT 3Y

판정
  = EXISTING RETENTION ASSET
  = REUSE AS REFERENCE / DEFAULT CANDIDATE
  = NOT LEGAL RETENTION SoT
이유
  - evidence_type 단위축 → inspection별 법률 차이 표현 불가
  - source_trace = MANUAL_CONFIG
  - 법령 정합 재검증 필요
```

### 5-1. 두 값 분리
```
H     = HOT operational window (운영 조회 창, 정책값)
R(i)  = inspection i 법정/정책 보존 만료 (evidence_type default = 위 policy에서 참조 + inspection 법적 provenance 확정)
```

### 5-2. HOT / COLD Boundary
```
age <= H → HOT (attached RANGE partition)
age >  H → COLD 이동 가능 (법정 보존은 계속)
경계 = 파티션 단위 시간. COLD 이동은 법정 보존 종료와 무관 — 물리 위치만 이동.
```

### 5-3. COLD Destination — 단일화 (CORR-03)
```
COLD authoritative store = DETACHED PostgreSQL partition (DB 안 계속 보존)
external export          = backup / disaster-recovery artifact = SoT 아님
evidence_vault_link      = 사용 금지
  [실측] document_data_id(NN) 키의 문서 evidence attachment link (bucket_id default 'company-docs')
        → inspection-result partition export registry 아님
장기 object storage 보관 = 별도 archive-storage WP (DEFER). 이번 WP는 신규 테이블/bucket 없이 닫음.
```

### 5-4. retention_until — 단일 계약 (CORR-03)
```
safety_inspections.retention_until  timestamptz  (ADDITIVE)
  = EFFECTIVE NOT-BEFORE-DELETE timestamp (모든 법정/정책/hold 반영한 최종 삭제 가능 시각)
  NULL   = retention unresolved OR active hold → 삭제 금지 (fail-closed)
  finite = 삭제 가능 시각
parent 보유: child results는 동일 법적 provenance 공유 → result마다 반복 저장 안 함.
[실측] safety_inspections hold 컬럼 = 0 → 별도 legal_hold source 없음.
       → legal_hold는 retention_until 연장/NULL 잠금으로 fail-closed 표현. 별도 legal_hold_count 조건 삭제.
[구현주의·비차단] runtime_evidence_retention_policy.deletion_allowed=false 실데이터 존재 → retention resolver는
       retention_period 숫자만 보고 삭제 허용 금지. legal resolution 전 retention_until=NULL(DELETE 금지) fail-closed.
```

### 5-5. Delete / Partition DROP — partition 전체 eligibility (CORR-03)
```
DELETE 절대 금지
  now < retention_until → 금지
  retention_until UNKNOWN(NULL) → 금지 (fail-closed)

PARTITION DROP ELIGIBLE  iff  (result partition p 전체)
  p LEFT JOIN safety_inspections i ON p.inspection_id = i.id
  unresolved_retention_count(i.retention_until IS NULL) = 0
  AND MAX(i.retention_until) < now
  AND export_verified = true
→ 만족 시 파티션 DETACH → export(backup) → DROP
(한 파티션에 3/5년·hold row 혼재 가능 → row 조건 아님, partition 전체 조건)
```

### 5-6. Partition Key 최종
```
safety_inspection_results = RANGE(checked_at), PK(id, checked_at), local index(inspection_id, created_at)
safety_inspections        = REGULAR TABLE (PK(id) 보존, inspection_date = index/anchor)
factory_id                = safety_inspections companion only
work_schedules            = HASH(factory_id) 상속·불변. child(results RANGE) ≠ parent — 허용.
```

---

## 6. work_assignments (재설계 금지)
```
partition 자동 필수 아님 (HIGH LINEAR APPEND, cron inactive) — P2
+factory_id companion + UNIQUE(schedule_id, scheduled_date) 멱등성 후보. 전부 DEFER.
```

## 7. runtime_document_archive — DEFER 유지 (재오픈 금지)

---

## 결론 (PD-4, CORR-03)
```
safety_inspections       = DO NOT PARTITION (regular, PK(id) 보존, P1 DEFER)
safety_inspection_results = RANGE(checked_at), PK(id, checked_at), local idx(inspection_id, created_at), checked_at NOT NULL
factory_id               = safety_inspections companion only (results.factory_id 삭제)
retention                = H/R(i) 분리 · retention_until(effective not-before-delete, NULL=fail-closed, legal_hold_count 삭제)
                           · COLD = detached PG partition(단일) · evidence_vault_link 금지 · external export=backup only
retention 자산            = runtime_evidence_retention_policy = reference/default, legal SoT 아님
남은 의존 = RETENTION POLICY RESOLUTION (inspection 유형/법령별, policy 참조 + 법령 직독) → retention_until 채움
```
