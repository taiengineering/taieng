# OUTPUT CONTRACT DECISION REPORT V1
# WO-OUTPUT-CONTRACT-DECISION-001

**작성일**: 2026-06-18
**성격**: 설계 결정. 새 탐색/추적/검증 없음. 코드 수정 없음.
**완료 후**: 탐구 종료 → 설계 결정 → 구현 WO → 연결 순서로 전환

---

## 이번 WO 질문

```
"어디에 어댑터를 둘 것인가?"
(문제가 무엇인가 ❌ — 그건 이미 비교 완료)
```

---

## 확정 사실 (재탐색 금지)

```
1. V4 검증 완료
2. ApplicabilityCondition 검증 완료 (14건, law_name/action_text 보유)
3. Obligation Metadata 존재
4. 정제레이어 존재 (diagnosis_transform.py)
5. 결과페이지 존재
6. 정제레이어는 factory_diagnosis_results.result_data 사용
7. V4 출력 계약 ≠ result_data 계약 (CASE B, 어댑터 필요)
```

---

## 3안 비교표

| 기준 | A안: V4 직접 변경 | B안: Adapter 분리 | C안: runtime_obligation 경유 |
|---|---|---|---|
| 구조 | V4→result_data | V4→Adapter→result_data | V4→runtime_obligation→기존체인 |
| 구조 영향도 | 높음 (V4 출력 계약 변경) | 낮음 (V4 불변) | 높음 (2개 모델 정합) |
| Track A 영향도 | 없음 | 없음 | 중간 (runtime 공유) |
| 재사용성 | 낮음 (V4 전용) | 높음 (sector별 재사용) | 중간 |
| Construction 확장성 | 나쁨 (V4마다 변경) | 좋음 (Adapter만 확장) | 중간 |
| 구현 복잡도 | 중간 | 낮음 | 높음 |
| 운영 복잡도 | 중간 (V4 책임 비대) | 낮음 (책임 분리) | 높음 (20,129 work_order 영향) |
| §8 검증 보존 | ⚠️ V4 변경 시 재검증 필요 | ✅ V4 불변 → 검증 그대로 | ✅ V4 불변 |

---

## 각 안의 결정적 리스크

```
A안 (V4 직접 변경):
  V4 evaluate()에 "obligation_result 생성 금지" 주석이 있음
  → V4를 정답 엔진으로 격리한 설계 철학을 깨뜨림
  → §8 검증된 V4 출력을 바꾸면 재검증 필요
  → Positive Space Engine 순수성 훼손

B안 (Adapter 분리):
  V4는 verdict만 생산 (불변, 검증 보존)
  Adapter가 verdict + 조건 레코드 조인 → result_data 변환
  → V4 책임은 "판정", Adapter 책임은 "표현"
  → 역할 분리 원칙(기획서)과 일치

C안 (runtime_obligation 경유):
  V4와 runtime_obligation_registry 정합 필요
  work_order 20,129건이 매달린 운영 테이블 건드림
  → 가장 위험. 검증 안 된 세계 B에 V4를 종속시킴
```

---

## 거버넌스 정합성 점검

```
PROJECT_POLICY 권한 체계:
  V4 = Level 3 검증엔진 (측정만, 방향 결정 안 함)
  → A안은 V4에 표현 책임까지 부과 → 권한 혼선

역할 분리 (기획서):
  V4 = 판정 / 정제레이어 = 표현
  → B안이 이 분리를 그대로 유지

§8 검증 자산 보존:
  A안 = V4 출력 변경 → §8 재검증
  B/C안 = V4 불변 → §8 그대로 유효
```

---

## 최종 판정: B안 (Adapter 분리)

```
추천: B안

V4
  ↓ (verdict + condition_id, 불변)
Adapter  ← 신규, 여기서 law_name/action_text 조인 + result_data 변환
  ↓ (result_data 스키마)
정제레이어 (diagnosis_transform.py, 불변)
  ↓
결과페이지 (불변)

근거:
  1. V4 불변 → §8 검증 자산 100% 보존
  2. 정제레이어 불변 → 기존 result_data 체인 재사용
  3. Construction 확장 시 Adapter만 확장 (V4/정제레이어 불변)
  4. 역할 분리 원칙 유지 (V4=판정, Adapter=변환, 정제=표현)
  5. 구현/운영 복잡도 최저
  6. Track A 무영향
```

---

## B안의 어댑터 책임 (다음 구현 WO 범위, 이번엔 정의만)

```
입력: V4 evaluate() 결과 (MATCH인 condition_id 목록)
처리:
  1. MATCH condition만 필터
  2. applicability_conditions에서 law_name/appendix_no/action_text 조인
  3. action_type → category 매핑 (CATEGORY_MAP 재사용)
  4. result_data.obligations 스키마로 변환
     {id, category, title, law_name, risk_level, description, evidence}
출력: factory_diagnosis_results.result_data 호환 JSON

미해결 (구현 WO에서 결정):
  risk_level — V4에 없음 (정제레이어 폴백 MEDIUM 사용 가능)
  headline — 정제레이어가 rule_count 기반 자동 생성
  → 둘 다 차단 요소 아님
```

---

## 결론

```
탐구 종료.

어댑터 위치 = B안 (V4와 정제레이어 사이 독립 Adapter)

다음 순서:
  설계 결정 (이 문서) → 구현 WO → 연결 작업

다음 WO 후보 (사장님 승인 시):
  WO-OBLIGATION-ADAPTER-IMPL-001
  - V4 verdict → result_data.obligations 변환 어댑터 구현
  - V4 불변, 정제레이어 불변, Adapter만 신규
```
