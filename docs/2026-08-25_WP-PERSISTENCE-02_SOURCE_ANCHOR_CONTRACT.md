# WP-PERSISTENCE-02 — SOURCE ANCHOR CONTRACT

- 작성일: 2026-08-25
- 상태: 부분 설계. form_schema_id 입력이 B1 로 BLOCKED 이므로 계약 미완결.
- 확정 가능한 부분(inspection_id, companion, tenant/actor)은 설계하되,
  BLOCKED 부분은 명시적으로 표시한다.

---

## 1. 계약 목표

점검 완료 확정 시점에, **명시적 현재 inspection.id** 로
`runtime_document_data.source_inspection_id` 를 정확히 기록하는 writer 계약.
스키마는 이미 LIVE(컬럼+FK+UNIQUE) — 이를 소비하는 orchestration 만 정의.

## 2. STEP 5 — WRITER INPUT CONTRACT (4열)

| INPUT | AUTHORITATIVE SOURCE | VALIDATION | WRITE FIELD |
|---|---|---|---|
| inspection_id | explicit id: result path param / worker submit 반환값 (manual complete 는 미보장 B3) | safety_inspections 존재 + status=완료계열 | runtime_document_data.source_inspection_id |
| form_schema_id | **BLOCKED (B1)** — 살아있는 SoT 없음 | (미정) | runtime_document_data.form_schema_id |
| factory_id | inspection_id 재조회 → safety_inspections.factory_id (client 미신뢰) | NOT NULL, 409 fail-closed | runtime_document_data.factory_id |
| company_id | factory_id → factories.company_id (server 파생) | NOT NULL | runtime_document_data.company_id |
| created_by | 인증 사용자 있으면 user.id, 없으면 NULL (created_by nullable) | phone inspector_id 를 actor 로 승격 금지 | runtime_document_data.created_by |

핵심: **inspection_id 하나만 신뢰 입력**으로 받고, 나머지 companion 은 전부
서버가 inspection row 재조회 + parent chain 으로 파생한다. 이 패턴은 이미
inspection writer(start/submit)의 factory_id 확보에서 확립되어 있어 재사용 가능.

## 3. 확정 가능한 항목

- **SOURCE ID CONTRACT** = explicit inspection.id ONLY (추론 전면 금지).
  날짜/factory/schedule/asset/최근/semantic 어느 것도 사용하지 않는다.
  단 explicit id 는 result / worker-submit 경로에서만 보장되고,
  manual-complete 경로는 단일 id 미보장(B3) → 그 경로는 anchor trigger 로 쓰지 않는다.
- **TENANT AUTHORITY** = server-derived (inspection → factory → company). CONFIRMED.
  client-provided factory/company 를 anchor truth 로 쓰지 않는다.
- **ACTOR AUTHORITY = PARTIAL.**
  - 웹(inspection_checklist): get_current_user 필수 → created_by = authenticated user.id.
  - 앱 인증(worker submit, 토큰 있음): created_by = authenticated user.id.
  - 앱 미인증(worker submit, _optional_auth 로 토큰 없음): created_by = NULL.
  - phone 으로 찾은 inspector_id 를 authenticated actor 로 승격하지 않는다
    (inspection.inspector_id ≠ "문서를 만든 인증 actor"). created_by nullable 이므로 정합적.
  - submitted_by(CD5-1)와 분리, 이번 WP 흡수 안 함.

## 4. BLOCKED 항목

- **form_schema_id** = 입력값의 정본 부재(B1). 이 필드 없이는:
  - UNIQUE(source_inspection_id, form_schema_id) 를 구성할 수 없다.
  - runtime_document_data INSERT 자체가 form_schema_id 를 요구(create_document
    시그니처: form_schema_id, factory_id, company_id, created_by).
  → 따라서 writer 는 form_schema_id 없이는 한 줄도 쓸 수 없다. 계약 미완결.

## 5. runtime_data_json 경계 (STEP 8)

- 이번 WP 에서 runtime_data_json = **자동채움 금지**.
- source_inspection_id / form_schema_id / factory / company / created_by 만 WRITE.
- inspection_results 전체를 JSON dump 하는 설계 금지 → 별도 후속 WP(payload mapping).

## 6. 미완결 사유 요약

source_inspection_id 기록 자체는 explicit id 로 안전하게 설계된다.
그러나 동일 row 에 **필수인 form_schema_id 의 정본이 없어**(B1), writer 를
완성하면 반드시 form_schema_id 를 어딘가에서 "추론"하게 된다. 그것은 지시서가
금지한 바로 그 로직이다. → 계약은 form_schema 매핑 SoT 확정 이후에만 완결 가능.
