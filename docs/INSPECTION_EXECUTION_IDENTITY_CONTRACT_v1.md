# INSPECTION_EXECUTION_IDENTITY_CONTRACT_v1  (CANONICAL · WP-DATA-ARCH-02 PASS/CLOSED)

```
WP                 = WP-DATA-ARCH-02 · PD-3  (CORR-03)
STAGE              = CANONICAL DOCUMENT (post CORR-03 PASS · WP-DATA-ARCH-02 CLOSED)
SOURCE API SHA     = e1506aa45d3b35bf4d99d3c123600e9f19ab6996
CANONICAL ARCH SHA = e83feabd80c7c515f0bfb9a859579213e9de9342
MODE               = READ ONLY / PHYSICAL DESIGN · MUTATION 0
근거표기            = [실측] / [코드근거] / [설계]
```

---

## 1. 세 identity (정본 상속)

```
Workforce Roster       = worker_registry
Application User        = users
Authenticated Principal = Supabase Auth + users.auth_id
연결 상태 [실측] = roster 28 / user_id linked 1 / auth-linked principal 1
```

---

## 2. INSPECTOR = users.id 로 고정 (CORR-01)

```
[실측] safety_inspections.inspector_id  FK → users.id
```

```
INSPECTOR = safety_inspections.inspector_id = users.id  (고정)
  · inspector의 users.auth_id 존재는 필수 아님 (인증 미완 user도 inspector 가능)
  · worker_registry.id를 inspector_id에 직접 쓰는 fallback = 폐기 대상 (CORR-01)
```

### roster worker가 실제 점검자일 때 기록 순서
```
worker_registry → users identity provisioning / link → safety_inspections.inspector_id(users.id)
```
[근거] 현재 worker_check의 worker_registry.id fallback이 FK-break(cohort 25)의 원인.
inspector_id는 users.id 무결을 지키고, roster는 users로 provisioning 후 연결한다.

---

## 3. INSPECTION SUBMITTER 분리 — DEFER 아님 (CORR-01)

```
[실측] safety_inspections에 submitted_by 컬럼 없음 → inspector와 submitter 물리 미분리
```

```
ADDITIVE (설계)
  safety_inspections.submitted_by  uuid  FK → users.id

계약
  inspector_id  = 실제 점검자 identity
  submitted_by  = 점검 제출 요청의 authenticated principal
```

[실측] 현재 inspection 2건 중 inspector_id NULL = 1 → legacy backfill은 검증 대상.
단 미래 write contract는 (inspector_id, submitted_by) 분리로 명확히 정의한다.

### CANONICAL INSPECTION SUBMISSION write contract (CORR-02)
submitted_by 컬럼만 만들고 worker_check의 Authorization optional을 유지하면 계약이 닫히지 않는다.
따라서 write path 계약을 강제한다.

```
Authorization        = REQUIRED  (worker_check optional 폐기)
current_user.id      → safety_inspections.submitted_by
body.phone / worker_id = inspector identity resolution 용도만
                       = submitter identity로 신뢰 금지
token 없음 / invalid  → 401 → inspection write 없음 (fail-closed)
```
∴ inspector_id = 실제 점검자 users.id / submitted_by = 요청 제출 authenticated users.id 를 write contract로 강제.

[구현주의·비차단] authenticated submitter ≠ inspector 가능. body.phone/worker_id로 타인을 inspector_id 지정 시
임의 사칭 방지 위해 assignment/delegation 검증 필요(구현계획). schema 추가 문제는 아님.

---

## 4. 네 actor 역할 — 항상 같지 않음

```
INSPECTOR            = safety_inspections.inspector_id (users.id)
INSPECTION SUBMITTER  = safety_inspections.submitted_by (users.id, additive)
DOCUMENT SUBMITTER    = runtime_document_data.submitted_by
CONFIRMER            = runtime_document_archive.confirmed_by (NN)
```
네 값은 다를 수 있다 (현장 점검자 ≠ 제출자 ≠ 문서 확정자).

---

## 5. Document identity 계약 — role 고정 삭제 (CORR-01)

기존 05B 정본과 정합하게 교정한다. "관리자" 역할 단어 삭제.

```
Confirm 권한        = role 아님 (role allowlist 폐기)
DOCUMENT SUBMITTER  = authenticated principal
CONFIRMER          = document.submitted_by 와 동일한 authenticated principal (Submitter-as-Confirmer)
= runtime_document_data.submitted_by = confirmed_by = current_user.id
```

---

## 6. roster fallback 격리 — FK-break 비전파

```
문제 [실측]
  worker_check Authorization = optional
  users-unresolved roster → inspector_id에 worker_registry.id (users FK 위반 risk)
  FK break cohort = 25 / principal-unlinked = 27 (정본)

계약 [설계]
  ① INSPECTION 기록: inspector_id = users.id 고정. roster는 users provisioning 후 연결
     (worker_registry.id 직접 저장 fallback 폐기).
  ② DOCUMENT 승격: source_inspection_id로 점검 참조. runtime_document_data.submitted_by /
     archive.confirmed_by 에는 authenticated principal 만 기록.
  ③ 비전파: inspection측 신원 불완전이 confirmed_by로 전파되지 않음.
     문서 confirm 계보(confirmed_by NN)는 항상 인증 주체.
```

---

## 7. 제출 요약 (PD-3, CORR-01)

```
inspector            = safety_inspections.inspector_id = users.id (고정, roster direct fallback 폐기)
inspection submitter  = safety_inspections.submitted_by = users.id (ADDITIVE, DEFER 아님)
document submitter    = runtime_document_data.submitted_by = authenticated principal
confirmer            = archive.confirmed_by = document.submitted_by 와 동일 authenticated principal
actor binding         = 문서측 강제(Submitter-as-Confirmer) / 점검측 inspector=users.id 무결
roster fallback       = 폐기. roster는 users provisioning 경유. confirm에 비전파.
role 고정             = 삭제 ("관리자" 제거, role allowlist 폐기 정합)
canonical submission   = worker_check Authorization REQUIRED. current_user.id→submitted_by.
                        phone/worker_id는 inspector resolution만. token 없음→401(fail-closed).
```
