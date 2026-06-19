# USER VISIBLE BRIDGE DECISION REPORT V1
# WO-USER-VISIBLE-BRIDGE-DECISION-001

**작성일**: 2026-06-19
**성격**: 배선 방식 결정. 새 탐색/구현 없음. 이미 확인된 사실 + 1건 구조 확인.

---

## 이번 WO 질문

```
"Adapter 결과를 사용자 결과페이지까지 어떻게 보낼 것인가?"
```

---

## 결정 전 확인한 구조적 사실 (1건)

```
anonymous_diagnosis_results 테이블에 factory_id 컬럼이 없다.

연결 키:
  public_token  — 익명 진단 식별자 (결과페이지 조회 키)
  input_data    — JSONB, 사업장 입력값 직접 담김 (ksic/workers 등)
  claimed_user_id — 나중 회원 연결 시

→ 익명 진단은 factory_id로 사업장을 참조하지 않고
  input_data JSONB에 입력을 직접 담는 구조.

이 사실이 A안 설계 방식에 영향:
  어댑터는 factory_id 기반인데
  결과페이지(anonymous_diagnosis_results)는 factory_id가 없음
  → A안은 "factory_id로 조인"이 아니라
    "진단 생성 시점에 어댑터를 호출해 full_result에 병합"이어야 함
```

---

## 3안 비교표

| 기준 | A안: full_result 병합 저장 | B안: 결과페이지가 Adapter 호출 | C안: Runtime Registry 경유 |
|---|---|---|---|
| 결과페이지 불변 | ✅ | ❌ (호출 코드 추가) | ❌ |
| 정제레이어 불변 | ✅ | ✅ | ❌ |
| public_token 구조 유지 | ✅ | ⚠️ (factory_id 필요) | ⚠️ |
| V4/Adapter 불변 | ✅ | ✅ | ❌ |
| 사용자 화면 최단 도달 | ✅ | 중간 | ❌ |
| 구현 복잡도 | 낮음 | 중간 | 높음 |
| factory_id 의존 문제 | 없음 (생성시점 처리) | 있음 (결과페이지가 factory_id 모름) | 있음 |

---

## B안의 결정적 문제

```
결과페이지는 public_token으로 조회한다.
factory_id를 모른다 (anonymous_diagnosis_results에 컬럼 없음).
→ 결과페이지가 어댑터(/obligation-adapter/{factory_id})를
  호출하려면 factory_id를 먼저 알아야 하는데, 그 연결이 없음.
→ B안은 추가 매핑 구조 필요 → 탈락
```

## C안의 결정적 문제

```
Runtime Obligation Registry(work_order 20,129건) 경유.
검증 안 된 세계 B에 V4 결과를 종속.
정제레이어/V4/Adapter 다수 변경.
→ 최고 위험 → 탈락
```

---

## 최종 판정: A안 (full_result 병합 저장)

```
추천: A안

방식 (구조 사실 반영):
  익명 진단 생성/평가 시점에
    1. 어댑터로 obligations 생성 (factory_id 또는 input_data 기반)
    2. full_result.rules_table에 병합
    3. anonymous_diagnosis_results에 저장
  → 결과페이지는 기존대로 public_token으로 full_result 읽음 (불변)

근거:
  1. 결과페이지 불변 (public_token 조회 구조 유지)
  2. 정제레이어 불변
  3. V4/Adapter 불변
  4. 사용자 화면에 가장 짧게 도달
  5. factory_id 의존 문제 없음 (생성 시점에 처리)
  6. 구현 복잡도 최저
```

---

## A안 구현 시 핵심 결정 사항 (다음 구현 WO 범위)

```
미해결 (구현 WO에서 확정):

1. 어댑터 호출 시점:
   - 익명 진단이 factory_id를 갖는가, input_data만 갖는가
   - factory_id 있으면 어댑터 직접 호출
   - input_data만 있으면 어댑터를 input_data 기반으로 호출하는
     경로 필요 (어댑터가 factory_id 전용이면 보강 검토)

2. full_result.rules_table 스키마 정합:
   - 어댑터 obligations[] → rules_table[] 필드 매핑
   - 결과페이지 _refine_rules_table()이 기대하는 필드
     (law_name, law_article, category, description) 충족 확인
   - 이미 OUTPUT_CONTRACT_COMPARISON에서 매핑 분석됨

3. 기존 rules_table과 병합 정책:
   - 덮어쓰기 vs 추가 vs dedupe
   - 결과페이지가 이미 _dedupe_rules_table 보유 → 중복 안전
```

---

## 결론

```
배선 방식 = A안 (full_result 병합 저장)

이유 (사장님 추천과 일치):
  결과페이지 불변 / 정제레이어 불변 / V4·Adapter 불변
  / public_token 구조 유지 / 화면 최단 도달

단, 구현 WO에서 먼저 확정할 것:
  익명 진단이 factory_id를 갖는지 / input_data만 갖는지
  (어댑터가 factory_id 전용이므로 이 연결이 A안 구현의 핵심)

다음: WO-USER-VISIBLE-BRIDGE-IMPL-001 (사장님 승인 시)
```
