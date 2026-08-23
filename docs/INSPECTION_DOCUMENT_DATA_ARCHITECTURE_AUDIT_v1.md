# INSPECTION_DOCUMENT_DATA_ARCHITECTURE_AUDIT_v1

```
WP        = WP-DATA-ARCH-01
STAGE     = CANONICAL DOCUMENT (post CORR-01 PASS / CLOSED)
SOURCE REPO      = taiengineering/tai-api
SOURCE MAIN SHA  = e1506aa45d3b35bf4d99d3c123600e9f19ab6996
CANONICAL REPO   = taiengineering/taieng
CANONICAL PATH   = docs/
DATE      = 2026-08-23
MODE      = READ ONLY (문서화 전용)
MUTATION  = DB 0 / CODE 0 / DDL 0 / DEPLOY 0 / REAL CONFIRM 0
근거표기   = [실측]=DB 직독 / [코드근거]=repo 직독 / [판정]=아키텍처 판정 / [한계]=미특정
```

이 문서는 Inspection 실행계와 Runtime Document 생명주기 사이의 현재 데이터
아키텍처를 감사한 마스터 요약이다. 상세는 동반 4개 정본문서를 참조한다:
GROWTH_MODEL / CONNECTION_MAP / PARTITION_DECISION / EVENT_TAXONOMY.

---

## 1. 목적과 범위

- 목적: 점검(Inspection) → 문서(Document) 축의 현재 자산을 실측으로 확정하고,
  가장 크게 성장할 데이터 구조를 먼저 식별한다.
- 이 단계는 **감사·문서화 전용**이다. 신규 설계·구현·마이그레이션·활성화는 포함하지 않는다.
- 원칙: 검증은 법령/코드/DB 직독으로만 하며, 건수만으로 capacity를 판단하지 않는다.

---

## 2. 4계층 기준선 (실측 count)

```
DEFINITION
  inspection_sets            = 327     [실측]  (존재 factory = 7 / 5,459)
  inspection_set_items       = 5,184   [실측]
  inspection_master          = 1,246   [실측]

PLANNING
  work_schedules             = 66      [실측]  (존재 factory = 4 / 5,459)
  work_assignments           = 5,991   [실측]
  schedule_candidate         = 47,227  [실측]  (candidate/projection · SoT 아님)

EXECUTION
  safety_inspections         = 2       [실측]  ← CURRENT OPERATIONAL SoT
  safety_inspection_results  = 8       [실측]
  runtime_inspection_session = 0       [실측]  ← DORMANT PARALLEL
  runtime_checklist_execution= 0       [실측]
  runtime_inspection_evidence= 0       [실측]

EVIDENCE / DOCUMENT
  runtime_document_data      = 1       [실측]  ← mutable working SoT
  runtime_document_archive   = 0       [실측]  ← immutable confirmed SoT
  runtime_compliance_evidence= 50,301  [실측]  (mock 50,000 + stress 300 + upload 1)
  generated_document         = 1,544   [실측]  ← derived artifact index

WORKFORCE / IDENTITY
  factories                        = 5,476  [실측]  (active 5,459)
  worker_registry                  = 28     [실측]
  worker_registry.user_id linked   = 1      [실측]
  phone → users normalized match   = 3      [실측]  (매칭일 뿐, auth 연결 아님)
  phone → auth-linked users match  = 1      [실측]  (users.auth_id NOT NULL)
  roster → authenticated principal = 1      [실측]
```

[판정] 현재 최대 물리 데이터(schedule_candidate 47k, runtime_compliance_evidence 50k)는
1회성 배치/mock 산출물이며 실제 성장축이 아니다. Inspection 데이터는 전체 factory에
균일 분포된 운영 샘플이 아니라, 소수 factory(7/4)에 집중된 개발 샘플이다.

---

## 3. 핵심 발견 (6)

### F1. MISSING ORCHESTRATION BRIDGE  [판정]
점검 실행(safety_inspections/results)과 Runtime 문서 생명주기(runtime_document_data)를
잇는 orchestration이 없다.
- [코드근거] `document_engine_svc.create_document(form_schema_id, factory, company, creator)`:
  runtime_data_json={} 빈 DRAFT를 생성하며 inspection 계열 테이블을 일절 참조하지 않는다.
- 공유 키 부재: results에 document_id/form_schema_id 없음, doc_data에 inspection_id/session_id 없음.
- 정정: "데이터 reader 부재"가 아니다. Inspection fetcher와 Document lifecycle **양쪽 자산은 이미 존재**하나,
  이를 호출 순서 + identity/source contract로 잇는 orchestration이 없다.

### F2. IDENTITY BREAK  [판정]
명부(roster)와 인증계정(principal)이 대부분 미연결이다.
- [실측] worker_registry 28 / user_id linked 1 / phone→users match 3 / 그중 auth-linked 1 / roster→authenticated principal 1 / FK break cohort(users-unresolved) 25 / principal-unlinked roster 27.
- [코드근거] worker_registry 등록·초대·수정 경로 어디에도 user_id write 없음.
  유일한 연결 = `auth/verify-otp` 내부 `_link_worker_registry` (OTP 로그인 완료 시점만).
- [판정] Identity system 부재가 아니라 "연결률이 낮음". 두 테이블은 역할이 다르다(§4).

### F3. DORMANT PARALLEL IMPLEMENTATION  [판정]
Runtime 점검 실행 경로가 정교하게 구현되어 있으나 데이터 0으로 미가동이다.
- [코드근거] runtime_operational_work_order → runtime_inspection_session →
  runtime_checklist_execution → runtime_inspection_evidence → runtime_inspection_submission.
- [실측] session/exec/evidence 모두 0. FK+UNIQUE로 orphan/중복을 물리 차단하는 강한 설계.
- [판정] 현재 SoT 아님. CURRENT OPERATIONAL SoT는 legacy safety_inspections/results.

### F4. FEDERATED EVIDENCE / OWNERSHIP UNRESOLVED  [판정]
운영 증빙 저장계가 연합(federated)이며 통합 소유 계약이 없다.
```
Operational Evidence Stores / References
  = safety_inspection_results.photo_urls
    runtime_inspection_evidence
    runtime_compliance_evidence
    evidence_vault_link
Confirmed Evidence Snapshot (별도 범주 — 운영 스토어 아님)
  = runtime_document_archive.evidence_manifest   (Confirm 시점 immutable snapshot)
```
- [판정] FEDERATED OPERATIONAL EVIDENCE = YES / UNIFIED OWNERSHIP CONTRACT = NOT ESTABLISHED.
  단순 "N개 duplicate" 확정 금지. DUPLICATE 여부는 후속 Log/Evidence architecture에서 판단.

### F5. DATA MODEL INCONSISTENCY  [실측, 유지]
- [실측] `safety_inspections.assignment_id` (컬럼명) → FK 대상 = `work_schedules.id`.
- [코드근거] worker_check가 body.assignment_id(=work_assignments.id)를
  schedule_id→work_schedules.id로 변환 후 저장.
- [판정] assignment_id name ≠ physical referenced entity. 이번 단계에서 수정하지 않음(기록만).

### F6. STALE CROSS-DOMAIN BRIDGE CONTRACT  [판정]
- [코드근거] `inspection_bridge.py`가 "inspection_set_items=0 → runtime_checklist_item authoritative"를 전제.
- [실측] 현재 inspection_set_items = 5,184 / runtime_checklist_item = 802 → 전제 붕괴.
- [실측] `runtime_inspection_bridge`: mapping_status='MAPPED' 323건, runtime_form_schema_id populated 0.
- [판정] STALE CROSS-DOMAIN BRIDGE CONTRACT + STALE MAPPING STATE. CONNECTED 금지.
  단, runtime_checklist_item은 Document Schema(05A Confirm renderer)에서 실사용 → obsolete 아님.

---

## 4. Current Operational SoT (요약)

```
Inspection Definition        = inspection_sets + inspection_set_items
Document Form Schema          = runtime_form_schema + runtime_field
                                + runtime_checklist_item + runtime_evidence_field
Current Inspection Execution  = safety_inspections + safety_inspection_results
Runtime Inspection Execution  = DORMANT PARALLEL IMPLEMENTATION (SoT 아님)
Document Working              = runtime_document_data      (mutable)
Document Confirmed            = runtime_document_archive   (immutable, UNIQUE doc_version)
Generated Output              = generated_document         (derived artifact index)
```

---

## 5. 다음 단계 경계

- 이 문서 세트는 **ARCHITECTURE BASELINE = READY**를 확정한다.
- NEXT = WP-DATA-ARCH-02 (Inspection + Document Physical Design). 문서 리뷰 후 착수.
- 아직 금지: DB migration / 신규 column / bridge 구현 / Runtime inspection 활성화 /
  Evidence 통합 / Partition 적용 / 첫 실제 Confirm / LOG MERGE(deferred).
