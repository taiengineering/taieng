# LAW ENGINE DESIGN RECONSTRUCTION V1
# WO-LAW-ENGINE-DESIGN-READ-001

**작성일**: 2026-06-19
**성격**: 원 설계문서 재구성. 코드/API/DB 추적 없음. 설계문서 읽기만.
**읽은 문서**: 45cminc 본가 설계문서 (아래 §출처)

---

## 읽은 설계문서 (직접 URL)

```
1. 45CM Federation Architecture v1
   https://github.com/taiengineering/tai-api/blob/main/docs/45CM_Federation_Architecture_v1.md

2. 45CM Federation Architecture v2 (확정판)
   https://github.com/45cminc/federation-contracts/blob/main/docs/45CM_Federation_Architecture_v2.md

3. 법령진단 로직 정책 V1 (대표 확정 SSOT)
   https://github.com/45cminc/federation-contracts/blob/main/docs/LEGAL_DIAGNOSIS_LOGIC_POLICY_V1.md

4. Check Engine (체크엔진) README + 계약
   https://github.com/45cminc/check/blob/main/README.md
   https://github.com/45cminc/check/blob/main/src/types.ts

5. Synthetic Reality Engine (합성현실/가상현실)
   https://github.com/45cminc/syn/blob/main/README.md
```

**주의**: "가상현실 포함 설계문서"의 정확한 1장은 아래 §미해결에 정리.
syn은 합성현실 "운영 replay" 엔진 README이지, 법령 파이프라인+가상현실을
한 장에 담은 설계문서인지 확정 못 함. 사장님 확인 필요.

---

## 원 설계 파이프라인 (재구성, 1장)

```
                [소비자 입력]
        시설·공정·설비 (KSIC 등 표준코드 선택)
        ※ SaaS 입력 = 유료진단 입력 (동일)
                     ↓
        [백오피스 선행수정: 추가 / 삭제 / 매핑]
        엔진이 쓰는 유효값만 들어가도록 정리
                     ↓
        ┌─────────────────────────────┐
        │   법령엔진 (Legal Engine)     │  ← 판정 (V4)
        │   = 도메인 의미 런타임          │
        └─────────────────────────────┘
                     ↓
        ┌─────────────────────────────┐
        │   체크엔진 (Check Engine)      │  ← 연결상태 관찰
        │   = ownerless 범용 관찰 인프라  │
        │   Claim/Evidence/Chain 관찰     │
        │   (판단/증명/추론 안 함=abstain) │
        └─────────────────────────────┘
                     ↓
        [Machine Federation Contract]
        엔진 경계에서 의미 제거 → machine signal만
        (INFO/WARNING/CRITICAL/ACTION_REQUIRED/...)
                     ↓
        ┌─────────────────────────────┐
        │  Projection / Monitoring      │  ← 의미 복원
        │  = 인간 언어 생성 (유일 지점)    │
        └─────────────────────────────┘
                     ↓
              [Human Operational Feed]
        오늘 상태 / 위험 / 승인대기 / 이벤트 / 운영흐름

        ┌─ 가상현실(Synthetic Reality, syn) ─┐
        │  엔진들을 시간압축 운영현실로 replay  │
        │  (deterministic, 720h)             │
        │  = 파이프라인 위에서 "태워보는" 검증층 │
        └────────────────────────────────────┘
```

---

## 확인 항목 7개 (원 설계 기준)

```
1. 입력부:
   소비자 입력 = 시설·공정·설비 (KSIC 표준코드).
   SaaS = 유료진단 = 동일 입력. (LEGAL_DIAGNOSIS_LOGIC_POLICY §1)
   백오피스 3가지(추가/삭제/매핑) 선행 정리.

2. 판정부:
   법령엔진(Legal Engine, 도메인 의미 런타임) = V4.
   "법령엔진 + 체크엔진 2개로 법령추출 가능" (정책 §0).

3. Check Engine 위치:
   법령엔진 다음. 단 역할은 "증명 생성"이 아니라
   "Claim↔Evidence↔Chain 연결상태 관찰" (check README).
   ownerless 범용 인프라, abstain. 도메인-blind.

4. Obligation 위치:
   ★ 원 설계문서에는 "Obligation 레이어"가 독립 단계로
   명시되지 않음. 법령엔진 판정 결과 자체가 의무이고,
   인간 표현은 Projection이 생성.
   (TAI 측 obligation_adapter는 federation 원설계엔 없는
    TAI 로컬 구현 — 원설계는 "판정→signal→projection")

5. 정제 위치:
   원 설계의 "정제"에 해당 = Projection/Monitoring 레이어.
   federation: 엔진은 machine signal만 내보내고,
   projection-engine이 유일하게 인간 언어로 복원.
   (TAI의 diagnosis_transform = 이 Projection의 TAI 로컬판)

6. VR Engine(가상현실) 위치:
   syn = Synthetic Reality Engine.
   파이프라인 "안"의 단계가 아니라, 파이프라인 전체를
   시간압축으로 replay하는 "검증/운영현실" 층.
   = 엔진을 태워보는 무대. (정책 권한상 Level 4)

7. 최종 출력물:
   Human Operational Feed (운영 피드).
   도메인 메뉴(법령/마케팅 탭) 금지.
   오늘상태/위험/승인대기/이벤트/운영흐름 = 전부 signal projection.
```

---

## 현재 TAI 구현 vs 원 설계 (핵심 차이)

```
원 설계 (federation):
  법령엔진 → machine signal → projection → 인간피드
  체크엔진 = 연결상태 관찰 (ownerless, abstain)
  엔진 간 = machine contract만, 의미 제거

현재 TAI 구현 (내가 이번 세션에 다룬 것):
  V4(법령엔진) → obligation_adapter → factory_diagnosis_results
    → diagnosis_transform → 화면
  = TAI 로컬 파이프라인. federation machine-signal/projection 미적용.
  = 체크엔진 미연결 (TAI는 adapter만 있고 45cm check 엔진 안 씀)

차이 요약:
  - 원 설계: 법령엔진 → [체크엔진 관찰] → signal → projection
  - TAI 현재: V4 → adapter → transform → 화면 (체크엔진·signal·projection 생략)
  → TAI는 federation 원 설계의 "축약/로컬판"을 돌리고 있고,
    체크엔진과 projection 레이어가 원설계대로는 안 끼어 있음.
```

---

## 미해결 (사장님 확인 필요)

```
"가상현실 내용이 포함된 두 번째 설계문서"의 정확한 1장:

  내가 읽은 것 중 가상현실 관련 =
    45cminc/syn README (Synthetic Reality Engine, 운영 replay)

  그러나 이것은 "법령 파이프라인 + 가상현실"을 한 장에 담은
  설계문서라기보다 syn 엔진의 실행 README다.

  사장님이 말한 "두 번째 설계문서"가:
    (a) 45cminc/syn 의 docs/ 안 설계문서인지
    (b) federation-contracts/docs 의 특정 문서인지
    (c) 다른 위치인지
  → 한 줄 알려주시면 그 문서를 읽어 재구성 완성.

  현재 재구성은 federation v1/v2 + 법령진단 정책 + check + syn README
  기준이며, 가상현실 "설계문서" 본체는 아직 못 특정했다.
```

---

## 결론 (원 설계 파이프라인 1줄)

```
입력(시설·공정·설비)
  → 법령엔진(판정)
  → 체크엔진(연결상태 관찰, abstain)
  → machine signal (의미 제거)
  → projection (의미 복원, 인간언어)
  → 운영 피드

가상현실(syn) = 이 파이프라인 전체를 시간압축 replay하는 검증층.

★ 현재 TAI 구현은 이 원 설계의 축약판:
  V4 → adapter → transform → 화면.
  체크엔진·machine signal·projection 레이어가 원설계대로는 미적용.
  이것이 이번 세션 내내 "체크엔진이 어디 붙는지" 혼선의 근본 원인 —
  TAI 로컬 파이프라인과 federation 원 설계가 다른 층위였기 때문.
```
