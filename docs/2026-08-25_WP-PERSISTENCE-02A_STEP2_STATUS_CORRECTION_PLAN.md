# WP-PERSISTENCE-02A STEP-2 — STATUS CORRECTION PLAN

- 작성일: 2026-08-25
- 성격: 지시서 §16. 잘못된 mapping_status 교정 **대상 산출만**. DB 수정 금지.
- 방식: DB SELECT only. 실행 SQL 작성 금지(§18) — pseudo-plan 만.

---

## 0. 정본 규칙 (지시서 §16)

```
MAPPED             = runtime_form_schema_id IS NOT NULL
                     AND 연결 schema.status = 'APPROVED_FOR_RUNTIME_USE'
NEEDS_HUMAN_REVIEW = 아직 결정되지 않음
NOT_MAPPABLE       = 운영자가 명시적으로 문서화 대상 아님 결정
```

## 1. 실측 — false MAPPED 대상

```
runtime_inspection_bridge total = 324
  mapping_status='MAPPED' AND runtime_form_schema_id IS NULL   = 323   ← false MAPPED
  mapping_status='MAPPED' AND runtime_form_schema_id IS NOT NULL = 0    (true MAPPED 없음)
  mapping_status='PARTIAL'                                     = 1
  기타 상태                                                    = 0
```

→ **현재 'MAPPED' 라벨 323건 전부가 정본 규칙 위반**(schema_id NULL). true MAPPED 는
0건. 즉 라벨과 실데이터가 전면 불일치.

## 2. 교정 방향 (pseudo-plan, 실행 아님)

지시서 §16: STEP-2 는 count/id list 산출까지. 실행은 향후 APPLY WP.

기본 교정 후보:
```
FALSE MAPPED (mapping_status='MAPPED' AND runtime_form_schema_id IS NULL)
  → 기본값 NEEDS_HUMAN_REVIEW 로 교정
  단, 운영자가 특정 set 을 DOCUMENT_NOT_REQUIRED 로 결정한 경우 → NOT_MAPPABLE
```

pseudo-plan (미실행, 참고용 형태만):
```
-- APPLY 단계에서만, 운영 승인 후 실행
-- 1) 전면 false MAPPED → NEEDS_HUMAN_REVIEW
--    UPDATE runtime_inspection_bridge
--    SET mapping_status='NEEDS_HUMAN_REVIEW'
--    WHERE mapping_status='MAPPED' AND runtime_form_schema_id IS NULL;
-- 2) 이후 운영자 결정분만 개별 반영:
--    NOT_MAPPABLE (DOCUMENT_NOT_REQUIRED 로 확정된 set id 리스트)
--    MAPPED       (schema 승인 + 매핑 승인 완료된 set 만, schema_id 동시 기록)
```
위는 **작성 금지된 실행 SQL 이 아니라 방향 스케치**다. 실제 production SQL 은 운영
승인 이후 별도 WP 로 작성한다(§18).

## 3. 교정 시 반드시 지킬 순서 (§17 승인 분리)

```
schema 승인 없이는 어떤 row 도 MAPPED 로 못 감:
  MAPPED 로 승격하려면 (a) schema.status='APPROVED_FOR_RUNTIME_USE' AND
                         (b) 매핑 승인(운영자) 둘 다 충족.
현재 (a)=0건(전건 CANDIDATE), (b)=0건 → MAPPED 승격 대상 0.
따라서 이번 교정의 현실적 결과 = 323건 대부분 NEEDS_HUMAN_REVIEW,
운영자 DOCUMENT_NOT_REQUIRED 결정분만 NOT_MAPPABLE.
```

## 4. PARTIAL 1건

- mapping_status='PARTIAL' 1건도 schema_id NULL 로 확인(STEP-1). 정본 규칙상 MAPPED
  아님. NEEDS_HUMAN_REVIEW 계열로 함께 검토 대상.

## 5. 산출 요약

```
FALSE MAPPED ROWS      = 323 (교정 대상)
TRUE MAPPED ROWS       = 0
PARTIAL                = 1  (검토 대상)
교정 실행               = 이번 STEP 아님 (APPLY WP, 운영 승인 후)
기본 교정 후보          = NEEDS_HUMAN_REVIEW
예외                   = 운영자 DOCUMENT_NOT_REQUIRED → NOT_MAPPABLE
```

DB MUTATION = 0. 이 문서는 대상 정의와 방향만 제시한다.
