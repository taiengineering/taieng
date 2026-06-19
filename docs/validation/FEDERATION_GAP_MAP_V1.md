# FEDERATION GAP MAP V1
# WO-FEDERATION-GAP-MAP-001

**작성일**: 2026-06-19
**관점 전환**: "없는 계층(missing)" → "우회된 계층(bypassed)".
**금지 준수**: 코드/API/DB 추적·구현 제안·연결 설계·버그 분석 없음.
**근거**: LAW_ENGINE_DESIGN_RECONSTRUCTION_V1 / LAW_ENGINE_ARCHITECTURE_REBASE_V1

---

## 관점: 없음이 아니라 우회

```
"없다(missing)"  = 정적 결핍 (만들다 만 빈칸)
"우회(bypass)"   = 원 설계의 그 자리를 현재 파이프라인이
                   건너뛰고 지나간다 (흐름이 그 계층을 통과 안 함)

→ Check Engine / Machine Signal은 "안 만든 것"이 아니라
  현재 TAI 흐름이 "통과하지 않고 건너뛴" 계층이다.
  (45cminc/check 엔진은 실재함 — 즉 부재가 아니라 미경유)
```

---

## 1. 원 설계 파이프라인 (federation)

```
Input → Legal Engine → Check Engine → Machine Signal
      → Projection → Human Feed
      [+ Synthetic Reality: 전체 replay 검증층]
```

## 2. 현재 TAI 파이프라인

```
Input → V4 → Obligation Adapter → Transform → UI
      [+ VR: SQL 시뮬레이션]
```

---

## 3. 계층별 상태 분류 (4상태)

| 원 설계 계층 | 상태 | 현재 |
|---|---|---|
| Input | **IMPLEMENTED** | 소비자입력 → V4 입력계약 |
| Legal Engine | **IMPLEMENTED** | V4 (§8 8/8 판정) |
| Check Engine | **BYPASSED** | 흐름이 통과 안 함 (45cm check 미경유) |
| Machine Signal | **BYPASSED** | 의미제거/signal 경계 건너뜀 → 직접 obligations |
| Projection | **LOCAL_REPLACEMENT** | diagnosis_transform (federation projection 아님) |
| Human Feed | **LOCAL_REPLACEMENT** | UI 결과화면 (통합 운영피드 아님) |
| Synthetic Reality | **UNVERIFIED** | VR SQL (syn 엔진과 동일성 미검증) |

원설계 외 TAI 로컬 계층:
| TAI 계층 | 분류 | 성격 |
|---|---|---|
| Obligation Adapter | **LOCAL_REPLACEMENT** | Check+Signal 우회를 메우는 로컬 변환 |
| factory_diagnosis_results | **LOCAL_REPLACEMENT** | signal→projection 대신 영구저장 |
| diagnosis_transform | **LOCAL_REPLACEMENT** | Projection의 TAI 로컬판 |

---

## 4. 우회 계층 (BYPASSED) — 식별

```
BYPASS-1: Check Engine
  원 설계: Legal Engine 판정 → Check Engine이 Claim/Evidence/Chain
           연결상태 관찰 → 다음으로
  현재 TAI: V4 판정 → (Check Engine 안 거치고) 바로 Obligation Adapter
  = 연결상태 관찰 계층을 건너뜀.
    판정이 "증거로 뒷받침되는가"의 관찰 없이 의무로 직행.

BYPASS-2: Machine Signal
  원 설계: 엔진 경계에서 의미 제거 → machine signal(ACTION_REQUIRED 등)만
           내보냄 → projection이 의미 복원
  현재 TAI: V4 판정 → obligations(의미 가진 채) 직접 생성
  = 의미제거/signal 경계를 건너뜀.
    엔진이 인간의미(law_name/action_text)를 경계 밖으로 직접 내보냄.
    (federation 원칙 "엔진 외부엔 machine signal만" 우회)
```

---

## 5. 로컬 대체 계층 (LOCAL_REPLACEMENT) — 식별

```
LOCAL-1: Obligation Adapter
  원 설계 대응: (없음 — Check+Signal 자리)
  역할: V4 판정 → obligations 변환.
        Check Engine·Machine Signal 두 우회 계층의 빈자리를
        메우는 TAI 로컬 변환기.
  = "우회로 생긴 공백"을 채우는 로컬 부품.

LOCAL-2: factory_diagnosis_results
  원 설계 대응: signal → projection (영구저장 단계 아님)
  역할: 변환 결과 영구저장 + is_latest.
  = projection 흐름 대신 저장소를 둔 로컬 방식.

LOCAL-3: diagnosis_transform
  원 설계 대응: Projection 계층
  역할: obligations → 표현 스키마.
  = federation projection-engine의 TAI 로컬 축약판.
    (machine signal을 안 받으므로 "복원"이 아니라 "재포맷")
```

---

## 6. 최종 출력 (한 장)

```
[원 설계]                    [현재]                  [상태]
─────────────────────────────────────────────────────────
Input                ───→    Input                   IMPLEMENTED
  ↓                            ↓
Legal Engine         ───→    V4 (Legal Engine)       IMPLEMENTED
  ↓                            ↓
Check Engine         ╳        (건너뜀)                BYPASS
  ↓                            ↓
Machine Signal       ╳        (건너뜀)                BYPASS
  ↓                          Obligation Adapter       LOCAL REPLACEMENT
  ↓                            ↓                       (우회 공백 메움)
Projection           ───→    Transform                LOCAL REPLACEMENT
  ↓                            ↓
Human Feed           ───→    UI                       LOCAL REPLACEMENT

[Synthetic Reality]  ───→    VR (SQL)                 UNVERIFIED


[BYPASS]                     [LOCAL REPLACEMENT]
  Check Engine                 Obligation Adapter
  Machine Signal               factory_diagnosis_results
                               Transform
```

---

## 7. 핵심 통찰 (우회 관점이 드러내는 것)

```
"없다"로 봤을 때: L3·L4가 빈칸 → "만들어야 할 것"처럼 보임.

"우회"로 봤을 때: TAI 흐름이 Check Engine·Machine Signal을
  건너뛰고, 그 공백을 Obligation Adapter로 메워 돌아가고 있다.
  = 지금도 작동은 한다. 단 federation 원칙(의미제거→관찰→signal)을
    우회한 채 인간의미를 직접 흘리는 로컬 단축경로다.

따라서 질문이 바뀐다:
  (이전) "Check Engine을 어디에 붙일까?"
  (지금) "이 우회 단축경로를 유지할까,
          아니면 원 설계대로 Check Engine·Machine Signal을
          경유하도록 되돌릴까?"
  → 이건 방향 결정 (이 WO 범위 밖, 사장님/GPT 영역)
```

---

## 원칙 준수

```
코드/API/DB 추적 안 함 ✅
구현 제안 안 함 ✅
연결 설계 안 함 ✅
버그 분석 안 함 ✅
없음→우회 관점 재분류만 ✅
```

---

## 결론

```
원 설계 7계층을 우회 관점으로 재정렬:

  IMPLEMENTED:       Input, Legal Engine
  BYPASSED:          Check Engine, Machine Signal
  LOCAL_REPLACEMENT: Obligation Adapter, factory_diagnosis_results,
                     Transform (= Projection/Feed의 로컬판)
  UNVERIFIED:        Synthetic Reality (VR)

핵심: Check Engine·Machine Signal은 "없는" 게 아니라 "우회된" 것.
  TAI는 그 두 계층을 건너뛰고 Obligation Adapter로 공백을 메워
  지금도 작동하는 로컬 단축경로를 돌리고 있다.

다음은 "우회 유지 vs 원설계 복귀"의 방향 결정이다. (범위 밖)
```
