# TRANSFORM COLUMN FIX REPORT V1
# WO-TRANSFORM-COLUMN-FIX-001

**작성일**: 2026-06-19
**성격**: 정제레이어 스키마 불일치 버그 수정 (기능 추가 아님).
**권한 정책**: b2 (created_by 기준 소유자 확인, 우회 금지) — 사장님 지정.

---

## 결론 먼저

```
정제레이어 SELECT 컬럼 버그: 수정 완료 ✅ (TCF-01)
그러나 b2 권한 정책 적용 시 데이터 상태 문제 발견:
  화성 factory의 created_by = null
  → b2(소유자 확인) 하에서 누가 조회해도 403
  → 우회(아무 user_id 채우기)는 금지 → 사장님 판단 필요

즉 "코드 버그"는 고쳤으나
"b2를 화성에 적용하려면 소유자 데이터가 있어야 한다"는
새 사실이 드러남.
```

---

## 수정 완료 내용 (routers/diagnosis_transform.py v1.0.2)

### 1. SELECT 컬럼 정정 (TCF-01) ✅
```
_fetch_row_by_id / _fetch_latest_row:
  이전: "id, sector, tier, company_name, created_at, result_data, user_id"
  수정: "id, factory_id, sector, created_at, result_data, created_by"

삭제: tier ❌ / company_name ❌ / user_id ❌ (테이블에 없는 컬럼)
추가: created_by / factory_id (실재 컬럼)
→ 없는 컬럼 SELECT 0건
```

### 2. 권한 체크 정정 (b2) ✅
```
이전: if str(row.get("user_id") or "") != str(user_id): 403
수정: if str(row.get("created_by") or "") != str(user_id): 403
→ created_by 기준 소유자 확인. 우회 없음.
```

### 3. tier/company_name 폴백 (TCF: 컬럼 추가 금지 준수) ✅
```
_build_transform:
  company_name = rd.get("company_name") or rd.get("factory_name") or "(정보없음)"
  tier = rd.get("tier") or "FREE"
  → result_data 내부에서만 읽음. 테이블 컬럼 참조 제거.
  → 신규 컬럼 추가 0, DB 변경 0.
```

### 4. stage 파라미터 처리
```
이전 코드는 stage를 tier 컬럼으로 필터(.eq("tier", ...)) → tier 없으므로 제거.
현재: 인자는 받되 필터 안 함 (호환 유지, tier 컬럼 부재 명시).
```

---

## b2 적용 시 드러난 데이터 상태 (실측)

```
factory_diagnosis_results 화성 레코드(216fd7b0):
  created_by = null (persist/SQL이 created_by 안 넣음)

factories 화성 레코드(e9c56af6):
  created_by = null  ← factory 자체에 소유 사용자 없음
  company_id = a37d3b83-9d9a-4b07-8d79-5eda5a48898f (회사만 있음)

→ b2(created_by == user_id) 적용 시:
  화성 결과의 created_by가 null이므로
  어떤 user_id로 조회해도 "null != user_id" → 403
  = transform_latest가 SELECT 버그는 고쳐졌으나
    권한에서 막힘 (데이터에 소유자 없음)
```

---

## 성공 기준 점검

```
TCF-01 없는 컬럼 SELECT 0건       → ✅ 수정 완료
TCF-02 transform_latest 정상 조회 → ⚠️ SELECT는 정상, 권한(b2)에서 막힘
TCF-03 factory_id 기준 결과 반환   → ✅ SELECT 로직 정상 (권한 통과 시 반환)
TCF-04 화성 obligations 8건 반환   → ⚠️ b2 권한 막힘으로 미달 (데이터 문제)
TCF-05 law_name 누락 0건          → ✅ (데이터상 0건, IMPL-002 검증)
TCF-06 action_text 누락 0건       → ✅ (데이터상 0건, IMPL-002 검증)
```

---

## 판단 필요 (사장님) — b2 완성에 필요한 데이터 결정

```
정제레이어 코드는 b2로 정확히 고쳐졌다.
이제 b2가 작동하려면 "소유자 데이터"가 있어야 한다.
화성은 factory.created_by = null이라 막힌다.

선택지 (우회 아님, 데이터 정합 결정):

옵션 1: 화성 factory에 created_by(소유 user) 지정
  - factories.created_by를 실제 소유 계정으로 채움
  - persist가 factory.created_by를 result.created_by로 복사
  - → 그 계정 토큰으로 조회 시 b2 통과

옵션 2: 소유 단위를 company_id로 변경
  - 화성은 company_id가 있음 (a37d3b83...)
  - b2를 "user_id" 대신 "사용자가 속한 company_id == factory.company_id"로
  - → 더 정확한 소유 모델 (회사 단위)이나 권한 로직 추가 수정 필요

옵션 3: persist가 호출자(current_user)를 created_by로 기록
  - persist에 인증 추가 → 호출한 사용자가 소유자
  - 단 현재 persist는 인증 없음 (이전 보고 이슈 B)

어느 쪽도 "아무 값이나 채우기"가 아니라 소유 모델 결정.
→ 우회 금지 원칙 준수 위해 사장님 판단으로 진행.
```

---

## 원칙 준수

```
정제레이어 SELECT 버그: 최소 범위 수정 ✅ (요청된 WO 범위)
b2 권한: created_by 기준, 우회 없음 ✅
신규 컬럼/테이블/DB 변경: 없음 ✅
created_by 무시/임시 우회: 안 함 ✅ (그래서 데이터 결정을 사장님께 올림)
Construction/Building/Anonymous: 안 건드림 ✅
새 API/Adapter: 없음 ✅
```

---

## 결론

```
코드 버그(없는 컬럼 SELECT)는 수정 완료.
transform_latest의 SELECT는 이제 정상 작동한다.

그러나 b2(소유자 확인)를 화성에 적용하려면
화성의 소유자 데이터(created_by)가 필요한데 현재 null이다.
이건 코드가 아니라 데이터/소유모델 결정 사항이다.

우회(아무 user 채우기)는 금지이므로,
소유 모델 옵션(1/2/3)을 사장님이 정하면
그에 맞춰 persist의 created_by 기록 방식을 1줄 추가하면 끝난다.

다음: 소유 모델 결정 → persist created_by 기록 → 실 HTTP 검증 재개
```
