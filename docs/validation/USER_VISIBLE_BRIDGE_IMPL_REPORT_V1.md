# USER VISIBLE BRIDGE IMPL REPORT V1
# WO-USER-VISIBLE-BRIDGE-IMPL-001

**작성일**: 2026-06-19
**성격**: 구현 착수 중 구조적 충돌 발견 → STOP + 정확한 보고 (PROJECT_POLICY §6).
**상태**: 구현 보류. 우회 구현 안 함.

---

## 결론 먼저

```
A안(full_result 병합 저장)을 구현하려 했으나,
구현 지점 코드를 읽은 결과 A안의 전제가 실제 코드와 불일치.

핵심 충돌:
  어댑터       = factory_id + V4 평가 기반
  익명 진단     = factory_id 없음 + V4 안 씀 + ksic 없음 + 별도 엔진

→ "진단 생성 시점에 어댑터 호출"이 현재 코드에서 성립 안 함.
→ 우회 구현(추정/임시 매핑) 금지 원칙에 따라 STOP하고 보고.
```

---

## 실측한 구조적 사실

### 사실 1: 익명 진단은 factory_id가 없다
```
routers/anonymous_diagnosis.py · _build_step1_body()
  모든 sector에서 factory_id=None 명시
  사용자 입력 = site_kind / scale / workers / region 뿐
  ksic_major = "" (빈 문자열)
  scale → SCALE_PRESETS로 floor_area 등 프리셋 매핑
```

### 사실 2: 익명 진단은 V4를 쓰지 않는다
```
진단 실행 = run_anonymous_diagnosis() (services/anonymous_factory_service)
  = 법령엔진 step1 (컴파일러 기반, ANONYMOUS_COMPILER_ENGINE_VERSION)
  ≠ V4 applicability_api.evaluate()

→ 어댑터가 호출하는 V4와 익명 진단 엔진은 다른 엔진.
```

### 사실 3: 두 세계는 데이터 위치가 다르다
```
화성 제2공장 (factory_id=e9c56af6):
  factories 테이블에 존재 (1건) ← V4/어댑터 세계
  anonymous_diagnosis_results에는 없음

익명 진단 40건 (ACTIVE 40):
  anonymous_diagnosis_results에만 존재 ← 결과페이지 세계
  factory_id 컬럼 자체가 없음
```

---

## 왜 A안 결정이 코드와 어긋났나

```
A안 결정 시점 전제 (USER_VISIBLE_BRIDGE_DECISION):
  "진단 생성 시점에 어댑터를 호출해 full_result에 병합"
  → 이때 "어댑터가 factory_id 기반인데 익명 진단이 factory_id를
    갖는지/input_data만 갖는지 구현 WO에서 확정"이라고 단서를 달았음

구현 WO에서 확정된 사실:
  익명 진단은 factory_id를 갖지 않을 뿐 아니라
  V4 엔진 자체를 호출하지 않는다.
  → 어댑터(V4 출력 변환기)를 끼울 V4 호출 지점이 익명 흐름에 없음.
```

---

## 화성 제2공장 MUST 8건은 어디서 보이나 (정확히)

```
화성 제2공장은 factories의 등록 사업장 (SaaS 가입 사업장 경로).
익명 무료진단(anonymous_diagnosis_results)과 다른 트랙.

→ 화성 8건을 사용자에게 보이려면
  "익명 진단 결과페이지"가 아니라
  "등록 사업장(SaaS) 진단 결과 화면"이 타깃이어야 함.

이 화면이 존재하는지는 이번 WO에서 미확인
(diagnosis_result_web은 public_token 기반 = 익명/유료 익명 트랙).
```

---

## 판정: A안 구현 보류 (구조 재확인 필요)

```
A안은 "익명 진단 트랙"을 가정했으나
화성 제2공장 MUST 8건은 "등록 사업장(factory_id) 트랙"이다.

두 트랙이 다르므로, USER_VISIBLE 달성 경로를 먼저 명확히 해야 함:

  경로 1: 등록 사업장(factories) 트랙
    factory_id 있음 → 어댑터 그대로 사용 가능
    단 이 트랙의 사용자 결과 화면이 무엇인지 확인 필요
    (SaaS 대시보드? 별도 진단 결과 페이지?)

  경로 2: 익명 진단 트랙
    factory_id 없음 + V4 안 씀
    → 어댑터를 쓰려면 익명 입력을 V4 입력으로 변환하는
      추가 레이어 필요 (= 새 작업, 이번 범위 밖)
```

---

## 다음 판단 필요 (사장님/GPT)

```
질문: 화성 제2공장 MUST 8건을 어느 화면에서 보이게 할 것인가?

  옵션 A: 등록 사업장(factories) 진단 결과 화면
    → 그 화면이 무엇인지 1건 확인 후 어댑터 연결
    → 어댑터는 이미 factory_id 기반이라 정합

  옵션 B: 익명 무료진단 결과페이지
    → 익명 입력(site_kind/scale/workers) → V4 입력 변환 레이어 필요
    → 어댑터 앞단에 입력 변환기 추가 (새 작업)

이번 WO는 구조 충돌 발견까지.
어느 화면이 타깃인지가 정해지면 그 경로로 구현 재개.
```

---

## 원칙 준수 확인

```
PROJECT_POLICY §6: 발견 → 즉시 구현 금지 → 측정/기록/보고
  구현 중 전제 불일치 발견 → 우회(추정 매핑) 안 하고 STOP ✅
추정으로 factory_id 임의 생성 / 익명-등록 강제 매핑: 안 함 ✅
정제레이어 / 결과페이지 / V4 / Adapter: 수정 0줄 ✅
```

---

## 결론

```
USER_VISIBLE = 아직 NO.

이번 WO에서 새로 확정한 사실:
  어댑터(factory_id/V4)와 익명 진단(token/컴파일러엔진)은
  입력 모델·엔진·식별자가 모두 다른 두 트랙이다.

A안의 "진단 생성 시점 어댑터 호출"은
익명 트랙에선 성립하지 않는다 (V4 호출 지점 부재).

→ 화성 8건의 타깃 화면(등록 사업장 트랙 vs 익명 트랙)을
  먼저 정해야 구현 경로가 확정된다.

구현 보류, 우회 안 함, 정확히 보고.
```
