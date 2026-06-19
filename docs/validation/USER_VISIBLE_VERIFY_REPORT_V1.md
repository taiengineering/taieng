# USER VISIBLE VERIFY REPORT V1
# WO-USER-VISIBLE-VERIFY-001

**작성일**: 2026-06-19
**성격**: 실제 호출·렌더링 확인만. 구현/새 설계/새 API/새 Adapter 없음.
**검증 대상**: 화성 제2공장 (C28, 280명, 12,500㎡)

---

## 최종 질문 답변

```
Q: 사용자가 실제로 MUST 8건을 볼 수 있는가?
A: NO (현재 시점)

판정: CASE B — API/어댑터는 존재, 화면 연결 없음
정확한 위치: Adapter 출력 → 결과페이지 입력 사이 배선 단절
```

---

## Layer별 상태표

| Layer | 상태 | 증거 |
|---|---|---|
| 1. 어댑터 변환 로직 | ✅ 검증됨 | 14건 BUILDABLE, MUST 8건 SQL 재현 성공 |
| 2. 어댑터 API | ⚠️ 코드 존재 / 미배포·미확인 | routers/obligation_adapter.py 등록됨, 실 호출 미검증 |
| 3. 정제레이어 | ✅ 존재 | diagnosis_transform / diagnosis_result_web |
| 4. 결과페이지 | ✅ 존재 | GET /diagnosis/result/{public_token} |
| 5. **배선 (Adapter→화면)** | ❌ **없음** | 결과페이지가 어댑터를 호출하지 않음 |

---

## 결정적 발견: 어댑터와 결과페이지는 다른 데이터 소스를 본다

```
어댑터 (/obligation-adapter/{factory_id}):
  입력 키: factory_id
  데이터:  factories → applicability_conditions
  출력:    obligations[] (MUST 8건)

결과페이지 (/diagnosis/result/{public_token}):
  입력 키: public_token  ← factory_id 아님
  데이터:  anonymous_diagnosis_results.full_result.rules_table
  렌더링:  raw_rules = full_result.get("rules_table")

→ 두 경로가 만나지 않는다.
  결과페이지는 어댑터를 호출하지 않고,
  anonymous_diagnosis_results 테이블의 full_result를 읽는다.
```

---

## 즉, 체인의 실제 모습

```
[어댑터 세계]
  factory_id → V4 → Adapter → obligations[]
                                  │
                                  ▼  ◀── 여기서 끊김
                          (full_result.rules_table에
                           기록하는 코드 없음)

[결과페이지 세계]
  public_token → anonymous_diagnosis_results.full_result.rules_table → 화면
```

어댑터는 obligations를 **반환**하지만,
그 결과를 결과페이지가 읽는 위치(`full_result.rules_table`)에
**기록(write)하는 코드가 없다.**

---

## CASE B 확정 (CASE C 아님)

```
CASE C (API부터 없음) 아님:
  어댑터 라우터 등록됨 (router_registry/diagnosis.py)
  변환 로직 검증됨 (MUST 8건)

CASE B (API 존재, 화면 없음) 확정:
  어댑터는 obligations를 만들 수 있으나
  결과페이지가 읽는 anonymous_diagnosis_results.full_result로
  흘려보내는 배선이 없음
```

---

## 추가 관찰: 어댑터 라우터의 잠재 이슈 (기록만, 수정 안 함)

```
routers/obligation_adapter.py가
v4_evaluate(factory_id=..., save=False)로 호출하는데
evaluate()는 FastAPI 엔드포인트 함수(save=Query(False)).

엔드포인트 함수를 직접 호출하면 save 인자가 Query 객체가 됨.
실 배포 시 동작 확인 필요 (이번 WO는 관찰만, 수정은 별도 판단).
```

---

## 상태 최종 확정 (BUILT/VERIFIED/CONNECTED/USER_VISIBLE)

| 구성요소 | BUILT | VERIFIED | CONNECTED | USER_VISIBLE |
|---|---|---|---|---|
| V4 엔진 | YES | YES | YES | NO |
| Obligation Adapter | YES | YES (변환로직) | 부분 (V4→obligations) | **NO** |
| 결과페이지 | YES | YES | YES (자체 경로) | YES (단 full_result 기반) |
| **Adapter→결과페이지 배선** | **NO** | NO | NO | NO |

```
USER_VISIBLE = NO

이유: 어댑터 obligations가
     결과페이지가 읽는 full_result.rules_table에
     도달하는 경로가 없음
```

---

## 다음 단계 (관찰 결과, 구현은 별도 WO + 승인)

```
USER_VISIBLE 도달에 필요한 배선 (둘 중 하나, 판단 필요):

옵션 1: 어댑터 결과를 full_result 형식으로 기록
  factory_id 평가 → obligations → anonymous_diagnosis_results
  (또는 진단 생성 시점에 어댑터 호출해 rules_table 채움)

옵션 2: 결과페이지가 factory_id 기반 어댑터 경로도 읽도록 확장
  (단 결과페이지는 public_token 기반 익명 진단 구조라
   factory_id 직접 연결은 구조 변경 수반)

→ 어느 쪽이든 PROJECT_POLICY §6: 측정→기록→비교→승인 후 구현.
  이번 WO는 USER_VISIBLE = NO 확정까지.
```

---

## 결론

```
질문: 사용자가 실제로 MUST 8건을 볼 수 있는가?
답: NO.

어댑터는 obligations를 만들 수 있다 (검증됨).
그러나 그 결과가 사용자 화면(결과페이지)이 읽는
데이터 소스로 흐르지 않는다.

CONNECTED(V4→Adapter)까지 도달했으나
USER_VISIBLE은 아직 아니다.
마지막 배선 1개가 남았다.
```
