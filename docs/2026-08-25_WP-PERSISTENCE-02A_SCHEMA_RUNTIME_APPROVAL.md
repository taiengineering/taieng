# WP-PERSISTENCE-02A STEP-1 — SCHEMA RUNTIME APPROVAL

- 작성일: 2026-08-25
- 성격: runtime_form_schema 323건의 RUNTIME_ELIGIBILITY_RECOMMENDATION.
- 원칙(§13): 이번 STEP 에서 status 변경 금지. mapping 승인과 schema 승인은 분리.

---

## 1. 현재 상태

```
runtime_form_schema total = 323
status = CANDIDATE 전건 (APPROVED_FOR_RUNTIME_USE = 0)
```
지시서 §1 의 "runtime_form_schema.status = APPROVED_FOR_RUNTIME_USE 만 RUNTIME
ELIGIBLE" 기준에 따르면, **현재 runtime-eligible schema = 0건.**

## 2. RUNTIME_ELIGIBILITY_RECOMMENDATION (집계)

```
APPROVE_FOR_RUNTIME_USE  = 0
NEEDS_HUMAN_REVIEW       = 323
REJECT_FOR_THIS_MAPPING  = 0 (개별 mapping 확정 전이라 reject 대상 특정 불가)
NOT_APPLICABLE           = 0
```

이유:
- schema 자체 품질/완성도 검토(field/checklist/evidence 완결성, 법적 정확성)가
  이번 STEP 범위 밖이고, 어떤 schema 도 아직 사람 승인을 거치지 않았다.
- 매핑이 확정되지 않았으므로 "이 매핑에 대해 reject" 같은 개별 판정도 불가.
- 따라서 전건 **NEEDS_HUMAN_REVIEW** 로 권고. 자동 승인(CANDIDATE→APPROVED)은 §3 금지.

## 3. mapping 승인 ⊥ schema 승인 (분리 기록, §13)

지시서 예시대로 두 축을 분리한다. 현재는 양쪽 모두 미승인이라 조합이 단순하다:
```
MAPPING = HUMAN_REVIEW (전건)
SCHEMA_RUNTIME_APPROVAL = PENDING/NEEDS_HUMAN_REVIEW (전건)
```
설령 향후 어떤 set 의 매핑 근거가 사람 검토로 확정되더라도, 해당 schema 가
runtime 승인(APPROVE_FOR_RUNTIME_USE)을 별도로 받기 전에는 DB population 불가.
즉 population 게이트는 **매핑 승인 AND schema 승인** 두 개가 모두 필요.

## 4. 데이터 품질 관찰 (참고, 판정 아님)

- document_family = `UNRESOLVED` 인 schema 36건(CUSTOM 21 + OFFICIAL 15) 존재.
  이들은 문서 성격 자체가 미해결 → runtime 승인 시 우선 검토 대상(참고).
- form_type = CUSTOM 31건, INTERNAL 5건 → OFFICIAL 이 아닌 schema 는 점검
  결과 문서로서의 적합성을 사람이 더 면밀히 봐야 함(참고).
- 위는 관찰일 뿐, 이번 STEP 에서 어떤 schema 도 승인/거부하지 않는다.

## 5. 결론

runtime-eligible schema = 0 (전건 CANDIDATE). 매핑을 채우려 해도 **연결할
승인된 schema 자체가 없다.** 이는 B1 DATA POPULATION BLOCKED 의 두 번째 축이다
(첫 축 = exact key 부재). 두 축 모두 사람 판단이 선행되어야 해제된다.
