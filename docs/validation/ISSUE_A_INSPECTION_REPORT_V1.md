# ISSUE A INSPECTION REPORT V1
# WO-USER-VISIBLE-FINAL-VERIFY 후속: transform_latest 컬럼 불일치 점검

**작성일**: 2026-06-19
**성격**: 이슈 규명(점검)만. 수정은 승인 후. 추정 없음 — 전부 DB/코드 실측.

---

## 결론 먼저

```
이슈 A 확정 + 더 큼.

transform_latest / transform_by_id는 현재 호출하면 깨진다.
원인: SELECT하는 컬럼 3개가 factory_diagnosis_results에 없음.
  tier ❌ / company_name ❌ / user_id ❌

→ 이건 내 어댑터가 만든 문제 아님.
  정제레이어(diagnosis_transform.py)에 원래 있던 버그.
  단, 이걸 고치지 않으면 USER_VISIBLE 불가능.
```

---

## 실측 1: factory_diagnosis_results 실제 컬럼

```
존재: id, factory_id, sector, diagnosis_stage, input_data, result_data,
      rule_count, is_latest, created_by, created_at, schema_version,
      expires_at, refund_at, refund_reason

이 중 transform이 SELECT하는 것과 대조:
```

## 실측 2: transform_latest SELECT vs 실제 컬럼

```
diagnosis_transform._fetch_latest_row / _fetch_row_by_id:
  .select("id, sector, tier, company_name, created_at, result_data, user_id")

대조 결과:
  id           ✅
  sector       ✅
  tier         ❌ 없음
  company_name ❌ 없음
  created_at   ✅
  result_data  ✅
  user_id      ❌ 없음 (created_by만 있음)

→ PostgREST는 없는 컬럼 SELECT 시 에러 반환.
  transform_latest / transform_by_id 모두 현재 깨짐.
```

## 실측 3: 권한 체크도 깨짐

```
_fetch_latest_row:
  if str(row.get("user_id") or "") != str(user_id): → 403

user_id 컬럼이 없으므로:
  - SELECT 단계에서 먼저 에러 (위 실측 2)
  - 설령 통과해도 row.get("user_id")=None → "" != user_id → 무조건 403

→ 어떤 경로로도 화성 결과 반환 불가.
```

---

## 영향 범위 (정확히)

```
영향 받는 것:
  GET /diagnosis/transform/latest/{factory_id}  (FV-02 대상)
  GET /diagnosis/transform/{diagnosis_id}

영향 없는 것:
  diagnosis_result_web.py (GET /diagnosis/result/{public_token})
    → 익명 트랙, anonymous_diagnosis_results 읽음, 컬럼 다름
    → 이건 Track B라 이번 USER_VISIBLE 대상 아님
  내 어댑터 (obligation_adapter)
    → factory_diagnosis_results에 정상 INSERT (실측 완료)
    → 저장은 정상, 읽기(transform)만 깨짐
```

---

## 왜 지금까지 안 드러났나

```
factory_diagnosis_results 기존 3건은 legacy 스키마.
transform_latest를 통한 실 조회가 운영에서 안 쓰였거나,
다른 경로(diagnosis_result_web=익명)로만 화면이 돌았을 가능성.

내 SQL 검증(IMPL-002)은 _extract_obligations 로직만 재현했고
_fetch_latest_row의 SELECT 컬럼 목록은 검증 안 했음.
→ 이번 점검에서 비로소 드러남. (점검 WO의 가치)
```

---

## 수정안 (승인 후, 최소 변경)

```
대상: routers/diagnosis_transform.py
  _fetch_latest_row / _fetch_row_by_id의 SELECT + 권한 체크

수정 A (최소): SELECT 컬럼을 실제 존재 컬럼으로 교정
  "id, sector, tier, company_name, created_at, result_data, user_id"
  → "id, sector, created_at, result_data, created_by, factory_id"
  (tier/company_name은 result_data 내부 값으로 대체 — _build_transform이
   이미 rd에서 company_name/tier 폴백 읽음)

수정 B (권한): user_id → created_by 로 교정
  if str(row.get("created_by") or "") != str(user_id): → 403
  단 어댑터 persist는 created_by를 안 넣음(null) →
  null이면 소유자 체크 불가 → 정책 결정 필요:
    (b1) created_by null이면 통과 (등록 사업장 공개 결과)
    (b2) persist가 factory 소유자를 created_by로 기록
    → 어느 쪽인지 사장님/GPT 판단

영향:
  V4 / 어댑터 / 결과페이지(익명) : 무영향
  정제레이어만 수정 (USER_VISIBLE 위해 불가피)
  → "정제레이어 불변" 원칙의 예외가 되므로 명시적 승인 필요
```

---

## 판단 필요 사항 (사장님/GPT)

```
1. 정제레이어 수정 승인 여부
   - 지금까지 "정제레이어 불변"이 원칙이었음
   - 그러나 이 버그(없는 컬럼 SELECT)를 안 고치면 USER_VISIBLE 불가
   - 이건 어댑터가 만든 게 아니라 원래 있던 버그

2. 권한 정책 (위 b1 vs b2)
   - b1: created_by null = 공개 (등록 사업장 결과 누구나 조회)
   - b2: persist가 소유자 기록 (factory 소유자만 조회)
```

---

## 원칙 준수

```
이슈 규명만, 수정 안 함 ✅ (점검 WO 범위)
추정 없음 — SELECT 컬럼·권한·테이블 컬럼 전부 실측 ✅
정제레이어 수정은 승인 후로 보류 (원칙 예외라 명시 승인 필요) ✅
새 설계/Construction/Building 안 건드림 ✅
```

---

## 결론

```
이슈 A는 실재하고, 예상보다 크다:
  transform_latest는 없는 컬럼 3개(tier/company_name/user_id)를
  SELECT하여 현재 호출하면 깨진다.
  = FV-02가 막히는 정확한 원인.

이건 USER_VISIBLE의 마지막 진짜 장애물이다.
어댑터·저장은 정상. 읽기 경로(정제레이어)의 기존 버그가 문제.

수정은 정제레이어 SELECT 컬럼 교정 + 권한 컬럼 교정 (최소 변경).
단 "정제레이어 불변" 원칙의 예외이므로 명시적 승인 필요.

다음: 사장님 승인 시 WO-TRANSFORM-COLUMN-FIX-001 (정제레이어 최소 수정)
```
