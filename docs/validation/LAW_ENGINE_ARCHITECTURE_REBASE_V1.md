# LAW ENGINE ARCHITECTURE REBASE V1
# WO-LAW-ENGINE-ARCHITECTURE-REBASE-001

**작성일**: 2026-06-19
**목적**: 현재 구현이 아니라 원 설계 기준으로 파이프라인 재배치 + 누락 계층 표시.
**금지 준수**: 코드/API/DB 수정·신규구현·버그추적 없음. 구현 여부 판단 안 함(누락만 표시).
**근거 문서**: Federation Architecture v2 / Legal Diagnosis Logic Policy V1 / Check Engine / Synthetic Reality Engine (LAW_ENGINE_DESIGN_RECONSTRUCTION_V1 참조)

---

## 1. 원 설계 기준 계층 정의 (7계층)

```
L1. Input            소비자 입력 (시설·공정·설비, KSIC 표준코드)
                     SaaS = 유료진단 동일 입력
L2. Legal Engine     법령엔진 = 도메인 의미 런타임 (판정)
L3. Check Engine     체크엔진 = Claim/Evidence/Chain 연결상태 관찰
                     (ownerless, abstain, 도메인-blind)
L4. Machine Signal   엔진 경계에서 의미 제거 → machine signal만
                     (INFO/WARNING/CRITICAL/ACTION_REQUIRED/...)
L5. Projection       의미 복원 = 인간 언어 생성 (유일 지점)
L6. Human Feed       운영 피드 (오늘상태/위험/승인대기/이벤트/운영흐름)
L7. Synthetic Reality 파이프라인 전체를 시간압축 replay하는 검증층 (syn)
```

---

## 2. 현재 구현 (TAI 로컬, 이번 세션에 다룬 것)

```
V4 (applicability_api.evaluate)        판정
Obligation Adapter                     판정 → obligations 변환
factory_diagnosis_results              결과 저장 (result_data)
diagnosis_transform                    obligations → 표현 스키마
UI (결과 화면)                          사용자 표시
VR (시뮬레이션, SQL 재현)               가상 사업장 평가
```

---

## 3. 매핑표 (원 설계 ↔ 현재 구현)

| 원 설계 계층 | 현재 구현 | 매핑 상태 |
|---|---|---|
| **L1 Input** | 소비자 입력(시설·공정·설비) → V4 입력계약(ksic/workers/sector) | ✅ 있음 (단 백오피스 추가/삭제/매핑 선행은 별개) |
| **L2 Legal Engine** | V4 (applicability_api) | ✅ 있음 (판정 = §8 8/8 검증됨) |
| **L3 Check Engine** | — | ❌ 누락 (45cminc/check 미연결, TAI는 adapter만) |
| **L4 Machine Signal** | — | ❌ 누락 (TAI는 signal 경계 없음, 직접 obligations) |
| **L5 Projection** | diagnosis_transform | ⚠️ 부분 (TAI 로컬 표현변환만, federation projection-engine 아님) |
| **L6 Human Feed** | UI (진단 결과 화면) | ⚠️ 부분 (도메인 화면, federation 통합 운영피드 아님) |
| **L7 Synthetic Reality** | VR (SQL 시뮬레이션) | ⚠️ 부분 (TAI 로컬 SQL 재현, syn 엔진 replay 아님) |
| (원 설계에 없음) | Obligation Adapter | ★ TAI 로컬 추가 (federation 원설계엔 독립 의무계층 없음) |
| (원 설계에 없음) | factory_diagnosis_results | ★ TAI 로컬 저장 (원설계는 signal→projection, 영구저장 단계 아님) |

---

## 4. Missing Layer (현재 없는 계층만, 구현 여부 판단 안 함)

```
완전 누락 (L3, L4):
  L3 Check Engine    — 45cminc/check 엔진이 TAI 파이프라인에 안 끼어 있음
  L4 Machine Signal  — 엔진 경계 의미제거/signal 단계 없음

부분/대체 (L5, L6, L7):
  L5 Projection         — diagnosis_transform이 대신하나
                          federation projection-engine 계약은 아님
  L6 Human Feed         — 도메인 결과화면이 대신하나
                          통합 운영피드(오늘상태/위험/...) 아님
  L7 Synthetic Reality  — VR SQL이 대신하나 syn replay 엔진 아님

원설계 외 추가 (TAI 로컬):
  Obligation Adapter / factory_diagnosis_results
  = 원 설계엔 없는 TAI 로컬 계층
    (원설계: 판정 → signal → projection.
     TAI: 판정 → obligation → 저장 → transform)
```

---

## 5. 한 장 다이어그램 (원 설계 → 현재 구현 → 누락 계층)

```
원 설계 (federation)          현재 구현 (TAI 로컬)         상태
─────────────────────────────────────────────────────────────
L1 Input             ───→     소비자입력 → V4 입력계약       ✅
       ↓                            ↓
L2 Legal Engine      ───→     V4 (판정, §8 8/8)             ✅
       ↓                            ↓
L3 Check Engine      ───→     ❌ 없음                        ⛔ 누락
   (연결상태 관찰)                  ↓                       (45cm check 미연결)
       ↓                      [Obligation Adapter]          ★ 원설계 외 TAI 추가
L4 Machine Signal    ───→     ❌ 없음                        ⛔ 누락
   (의미 제거)                      ↓                       (signal 경계 없음)
       ↓                      [factory_diagnosis_results]   ★ 원설계 외 TAI 저장
L5 Projection        ───→     diagnosis_transform           ⚠️ 부분
   (의미 복원)                      ↓                       (로컬 변환, projection계약 아님)
       ↓                            ↓
L6 Human Feed        ───→     UI 결과화면                    ⚠️ 부분
   (통합 운영피드)                                          (도메인화면, 통합피드 아님)

L7 Synthetic Reality ───→     VR SQL 시뮬레이션              ⚠️ 부분
   (replay 검증층)                                          (SQL재현, syn 엔진 아님)
```

---

## 6. 한 줄 결론: 우리는 원 설계의 어디까지 와 있는가

```
원 설계 7계층 중:
  완성:   L1 Input, L2 Legal Engine (판정) — 2개
  누락:   L3 Check Engine, L4 Machine Signal — 2개 (완전 없음)
  부분:   L5 Projection, L6 Human Feed, L7 Synthetic Reality — 3개
         (TAI 로컬 버전이 대신하나 federation 계약은 아님)
  추가:   Obligation Adapter, factory_diagnosis_results
         (원설계 외 TAI 로컬 계층)

즉:
  TAI는 원 설계의 "앞 2계층(입력·판정)"을 federation 정신과 다른
  로컬 방식으로 완성했고,
  중간 2계층(체크엔진·machine signal)은 통째로 비어 있으며,
  뒤 3계층(projection·feed·synthetic)은 federation 계약이 아닌
  TAI 로컬 축약판으로 대체돼 있다.

  이번 세션의 "체크엔진 어디 붙나" 혼선의 정체:
    L3(Check Engine)과 L4(Machine Signal)가 통째로 비어 있는데,
    TAI 로컬 파이프라인 안에서 그 자리를 찾으려 했기 때문.
    원설계 기준으로 보면 그 두 계층은 "아직 안 만든 칸"이다.
```

---

## 원칙 준수

```
코드/API/DB 수정 안 함 ✅
신규 구현 안 함 ✅
버그 추적 안 함 ✅
구현 여부 판단 안 함 — 누락 계층만 표시 ✅
원 설계 ↔ 현재 구현 매핑 + 누락 표시만 ✅
```

---

## 결론

```
"우리가 지금 원 설계의 어디까지 와 있는가" = 재배치 완료.

원 설계 7계층 기준:
  L1·L2 완성 / L3·L4 누락 / L5·L6·L7 TAI 로컬 부분대체
  + Obligation/Storage = TAI 로컬 추가 계층

이 재배치가 보여주는 것:
  Check Engine 연결을 논하기 전에,
  TAI 파이프라인에는 원설계의 L3(체크엔진)·L4(machine signal)
  두 칸이 아예 비어 있다.
  = 다음 논의는 "그 빈 칸을 federation 원설계대로 채울지,
    TAI 로컬 방식을 유지할지"의 방향 결정. (이 WO 범위 밖)
```
