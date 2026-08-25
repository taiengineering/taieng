# WP-PERSISTENCE-02 — TRANSACTION / IDEMPOTENCY / CARDINALITY

- 작성일: 2026-08-25
- 상태: 구조 설계는 가능하나, 최종 확정은 form_schema_id(B1) 해제에 종속.

---

## 1. STEP 3 — CARDINALITY

현재 제약: `UNIQUE(source_inspection_id, form_schema_id)`

- 이 UNIQUE 는 "한 inspection 이 schema 별로 여러 문서"(B안)를 **구조적으로 지원**한다.
- 그러나 "지원 가능"과 "intended design"은 다르다.
- intended cardinality 를 확정할 architecture/registry 증거:
  - inspection → form_schema 매핑이 1:1 인지 1:N 인지 정하는 SoT 자체가 없음(B1).
  → **CARDINALITY = NOT PROVEN.** (UNIQUE 는 N 을 허용하나 실제 설계 의도는 미확정)
  - 02A STEP-1 정책결정으로 CARDINALITY = inspection_set → schema 0..1 로 확정됨
    (단 이는 매핑 단위 cardinality; source_inspection→document row 는 여전히 B1 종속).

## 2. STEP 6 — IDEMPOTENCY

중복 호출(같은 inspection 완료 이벤트가 2번 도착)은 반드시 안전해야 한다.

가용 수단: `UNIQUE(source_inspection_id, form_schema_id)` — DB 레벨 중복 차단 가능.

설계 후보:
- (A) APPLICATION CHECK ONLY: SELECT 후 없으면 INSERT
  → race 시 두 요청이 동시에 "없음" 판정 → 중복 INSERT 시도 → UNIQUE 가 2번째를 거부.
- (B) DB UNIQUE GUARDED: INSERT 시도 후 unique_violation 을 잡아 기존 row 반환(get-or-create).
  → race 를 UNIQUE 가 흡수. 현재 stack(supabase-py, 단건 INSERT)에서 최소 변경.
- (C) ATOMIC UPSERT (on_conflict): PostgREST upsert 로 (source_inspection_id, form_schema_id)
  충돌 시 무시/반환.

권고(잠정): **DB UNIQUE GUARDED (B)** — 기존 UNIQUE 를 그대로 활용, 새 RPC/트랜잭션
엔진 불필요(지시서 원칙: NEW SYSTEM 금지). 단 이 판정도 form_schema_id 가 있어야
UNIQUE 키가 성립하므로 B1 해제 전에는 **적용 불가**.

→ IDEMPOTENCY = DB UNIQUE GUARDED (설계 후보 확정, 적용은 B1 종속).

## 3. STEP 7 — TRANSACTION / FAILURE SEMANTICS

상황: inspection COMPLETE = 성공 / runtime document anchor = 실패.

후보:
- (A) HARD-COUPLED ATOMIC: 둘 다 성공해야 완료. anchor 실패 시 inspection 완료 rollback.
- (B) INSPECTION AUTHORITATIVE: inspection 완료는 유지, anchor 는 retry 대상.
- (C) OUTBOX/QUEUE: NEW SYSTEM → 지시서상 쉽게 제안 안 함.

평가:
- 현재 inspection writer 는 supabase-py 단건 호출들의 나열이며, **명시적 다중테이블
  트랜잭션 경계가 없다**(start/submit 모두 순차 execute). 따라서 (A) hard-atomic 을
  적용하려면 트랜잭션 래핑(RPC/함수) 신설이 필요 → 최소변경 원칙과 충돌.
- 안전관리 도메인 의미상 "점검은 됐는데 문서만 실패"는 데이터 손실이 아니라
  "문서 미생성" 상태다. inspection 결과 자체는 이미 저장됨.
- → 잠정 권고: **(B) INSPECTION AUTHORITATIVE** (inspection 완료 유지 + anchor 재시도).
  단 이 선택도 anchor row 를 쓰려면 form_schema_id 가 필요(B1). 그리고 재시도 시
  IDEMPOTENCY(§2)가 duplicate 를 막아야 한다.

→ TRANSACTION SEMANTICS = DECISION REQUIRED (근거상 B 우세, 그러나 B1·트랜잭션경계
  확인 전 확정 불가). 지시서 §12 규칙대로 DECISION REQUIRED 로 남긴다.
  명시적 DB atomic transaction 경계 부재 → **B2 TRANSACTION_BOUNDARY_UNCLEAR = OPEN.**
  (참고: worker submit 의 INSERT 2건도 atomic 아님 — INSPECTION_WRITER_TRACE 와 일관)

## 4. 종속 관계 요약

```
form_schema_id(B1) 해제
  └→ UNIQUE 키 성립
       └→ IDEMPOTENCY(DB UNIQUE GUARDED) 적용 가능
            └→ TRANSACTION SEMANTICS(A/B) 확정 가능
                 └→ CARDINALITY intended 확정 가능
```
즉 B1 이 최상위 blocker이고, 나머지 운영 결정들은 그 아래에 순차 종속된다.
