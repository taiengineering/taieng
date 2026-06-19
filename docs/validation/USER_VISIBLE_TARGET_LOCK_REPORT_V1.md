# USER VISIBLE TARGET LOCK REPORT V1
# WO-USER-VISIBLE-TARGET-LOCK-001

**작성일**: 2026-06-19
**성격**: 트랙 확정 + 등록 사업장 트랙 결과 저장 경로 실측.

---

## 확정 선언

> **USER_VISIBLE 검증 대상은 등록 사업장 트랙으로 확정한다.**
> **익명 진단 트랙은 별도 Phase로 분리한다.**

---

## 두 트랙 (재확인)

```
Track A — 등록 사업장 트랙 (USER_VISIBLE 대상) ✅
  factories 기반 / factory_id 있음
  화성 제2공장 존재
  V4 / Adapter와 정합

Track B — 익명 진단 트랙 (범위 밖, 별도 Phase) ⛔
  anonymous_diagnosis_results / public_token 기반
  factory_id 없음 / V4 안 씀 / compiler 엔진
```

---

## 확정 근거 (6)

```
1. §8 Golden Case 기준 사업장 = 화성 제2공장
2. 화성 제2공장은 factories에 존재 (실측: 1건)
3. V4 / Adapter는 factory_id 기반
4. 익명 진단은 V4 입력 구조와 다름
5. 익명 진단 연결엔 별도 입력 변환 레이어 필요
6. 현재 목표 = 새 입력 변환기가 아니라 검증된 V4 결과의 가시화
```

---

## 등록 사업장 트랙 결과 저장 경로 (실측 완료)

핵심 발견: **Track A 전용 결과 저장소가 이미 존재하고, 정제레이어가 이미 읽는다.**

```
factory_diagnosis_results 테이블:
  factory_id   (uuid)   ← 어댑터와 정합 ✅
  result_data  (jsonb)  ← 정제레이어가 읽는 바로 그 필드 ✅
  is_latest    (bool)   ← 최신 결과 관리
  sector / diagnosis_stage / rule_count / created_by / expires_at

정제레이어 (diagnosis_transform.py):
  GET /diagnosis/transform/latest/{factory_id}
    → _fetch_latest_row(factory_id) → factory_diagnosis_results 조회
    → result_data 읽음 → _extract_obligations() → obligations[] 반환
  GET /diagnosis/transform/{diagnosis_id}
    → _fetch_row_by_id → 동일 테이블

→ 정제레이어는 factory_id로 factory_diagnosis_results.result_data를 읽는다.
  익명 트랙(anonymous_diagnosis_results)과 완전히 별개의, 이미 정합된 경로.
```

---

## Track A 체인 (정합 확인)

```
어댑터 (factory_id + V4)            ← 구현 완료 (services/obligation_adapter_service)
  ↓ obligations[] 생성
factory_diagnosis_results.result_data 기록   ← 마지막 갭 (여기만 비어있음)
  ↓
정제레이어 transform_latest(factory_id)       ← 이미 존재, factory_id로 읽음
  ↓ _extract_obligations()
obligations[] → 화면                          ← 이미 존재

세 칸 중 두 칸(어댑터, 정제레이어)은 이미 있다.
가운데 한 칸(어댑터 결과를 factory_diagnosis_results에 기록)만 비어있다.
```

---

## 마지막 갭의 정확한 위치 (실측)

```
factory_diagnosis_results 총 3건
화성 제2공장(e9c56af6) 결과: 0건  ← 여기가 빈 칸

즉 USER_VISIBLE의 마지막 1개 작업:
  "화성 제2공장의 어댑터 obligations를
   factory_diagnosis_results.result_data에 기록"

이것만 하면:
  정제레이어 GET /diagnosis/transform/latest/e9c56af6...
  → result_data 읽음 → MUST 8건 obligations 반환 → 화면
```

---

## 어댑터 출력 ↔ 정제레이어 입력 정합 (재확인)

```
어댑터 obligations 필드:
  id / category / title / law_name / rule_type
  / risk_level / description / evidence / required_count

정제레이어 _obligation_from_item이 읽는 필드:
  obligation_summary/title/name / law_name / rule_type
  / risk_level / description / evidence/legal_basis / category

→ 필드명 정합. category도 어댑터가 정제레이어 CATEGORY_MAP
  (선임/점검/신고/교육/서류)에 맞춰 생성함.
→ 어댑터 출력을 result_data.obligations로 넣으면 정제레이어가 그대로 변환.
```

---

## 다음 작업 (구현 WO, 범위 명확)

```
WO-USER-VISIBLE-BRIDGE-IMPL-002 (Track A 전용, 사장님 승인 시):
  1. 어댑터로 화성 제2공장 obligations 생성 (factory_id 기반, 이미 검증됨)
  2. result_data = {obligations: [...], sector, rule_count, ...} 조립
  3. factory_diagnosis_results에 INSERT (factory_id=화성, is_latest=true)
  4. 정제레이어 transform_latest로 MUST 8건 반환 확인 (UV 검증)

원칙:
  V4 불변 / 어댑터 불변 / 정제레이어 불변 / 결과페이지 불변
  익명 트랙(anonymous_diagnosis_results) 손대지 않음
  새로 하는 일 = factory_diagnosis_results에 1건 기록 + 검증
```

---

## 범위 밖 (별도 Phase로 분리 — 금지 준수)

```
⛔ 익명 진단 트랙 수정
⛔ anonymous_diagnosis_results 수정
⛔ public_token 경로 연결
⛔ site_kind → V4 변환 설계
⛔ 무료진단 결과페이지 수정

이들은 "Track B (익명) Phase"로 분리. 현재 다루지 않음.
```

---

## 결론

```
USER_VISIBLE 검증 대상은 등록 사업장 트랙으로 확정한다.
익명 진단 트랙은 별도 Phase로 분리한다.

확정 후 실측으로 추가 확인된 것:
  Track A 결과 저장소(factory_diagnosis_results)와
  정제레이어 읽기 경로(transform_latest/factory_id)는 이미 정합.
  마지막 갭은 "화성 어댑터 결과를 이 테이블에 기록" 1건뿐.

이전 STOP(BRIDGE-IMPL-001)이 옳았다:
  익명 트랙으로 우회했다면 입력 변환기라는 불필요한 작업을 만들었을 것.
  트랙을 등록 사업장으로 고정하니 경로가 이미 90% 정합 상태로 존재.
```
