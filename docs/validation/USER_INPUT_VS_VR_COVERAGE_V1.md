# USER INPUT VS VR COVERAGE V1
# WO-USER-INPUT-VS-VR-COVERAGE-001

**작성일**: 2026-06-20
**목적**: 사용자 입력 현실(User Reality) vs VR 입력공간(VR Reality) 동일 기준 대조.
**질문**: "사용자가 입력하는 것을 VR이 얼마나 재현하는가?"
**금지 준수**: 부족/개선/버그/확장 판정 없음. 격차 측정만.

---

## STEP-1: 사용자 입력항목 (실측, UI_FIELD_INVENTORY 기준)

```
[회사]
  회사명, 사업자번호, 대표자명, 사업자유형, 업태, 업종명,
  전화, 팩스, 이메일, 주소, 사업자등록증

[시설]
  시설명, 시설유형, 근로자수(상시근무인원), 외주인원, 주소,
  전기수전용량(kW), 가스저장용량(kg), 보일러용량, 승강기수,
  연간에너지(TOE), 연면적, 층수, 건물등급, 가스(m3), 변압기(kVA),
  공장등록, 위험물시설, 다중이용, 안전관리자선임,
  고압가스취급, 화학물질취급, 보일러보유
  [건설] 공사금액, 건설유형, 하도급근로자수, 하도급업체수,
        타워크레인, 밀폐공간, 석면, 발파, 잠수

[공정]
  공정 선택 (lv1~4)

[설비]
  설비명, 수량, 설치연도, 설치위치, 법정점검대상, 운영상태
```

---

## STEP-2: VR 생성항목 (현재 generation_spec 기준)

```
현재 VR generation_spec (VR_BRIDGE_DESIGN/REPORT 확정):
  sector   : INDUSTRIAL/BUILDING/CONSTRUCTION
  ksic     : 업종코드
  workers  : 근로자수 (regular_workers)

= VR이 현재 생성하는 가상 사업장 속성 = 3개
  (그 중 판정에 쓰는 핵심 = ksic + workers = 2차원)
```

---

## STEP-3: 항목별 대조표

| 입력항목(영역) | 사용자입력 | VR생성 | 상태 |
|---|---|---|---|
| **근로자수** (시설) | YES | YES | **COVERED** |
| **KSIC/업종** (회사/시설유형) | YES | YES | **COVERED** |
| sector(산업/건물/건설) | YES(계약) | YES | **COVERED** |
| 외주/하도급 근로자수 | YES | NO | NOT_COVERED |
| 전기수전용량(kW) | YES | NO | NOT_COVERED |
| 가스저장용량(kg/m3) | YES | NO | NOT_COVERED |
| 보일러용량 | YES | NO | NOT_COVERED |
| 승강기수 | YES | NO | NOT_COVERED |
| 연간에너지(TOE) | YES | NO | NOT_COVERED |
| 연면적 | YES | NO | NOT_COVERED |
| 층수/건물등급 | YES | NO | NOT_COVERED |
| 변압기(kVA) | YES | NO | NOT_COVERED |
| 위험물시설 | YES | NO | NOT_COVERED |
| 화학물질취급 | YES | NO | NOT_COVERED |
| 고압가스취급 | YES | NO | NOT_COVERED |
| 안전관리자선임(체크) | YES | NO | NOT_COVERED |
| 공장등록/다중이용 | YES | NO | NOT_COVERED |
| 타워크레인/밀폐/석면/발파/잠수 | YES | NO | NOT_COVERED |
| 공사금액/건설유형 | YES | NO | NOT_COVERED |
| **공정** (lv1~4) | YES | NO | NOT_COVERED |
| **설비** (명/수량/연도/위치) | YES | NO | NOT_COVERED |
| 설비 법정점검/운영상태 | YES | NO | NOT_COVERED |

---

## 커버리지 측정 (판정 아님, 산술만)

```
사용자 입력 "판정 관련" 항목 수 (회사 식별정보 제외):
  근로자수, KSIC, sector,
  외주인원, 전기, 가스, 보일러, 승강기, 에너지, 연면적, 층수,
  건물등급, 변압기, 위험물, 화학물질, 고압가스, 안전관리자체크,
  공장등록, 다중이용, 건설5종(타워크레인등), 공사금액, 건설유형,
  공정, 설비, 설비속성
  ≈ 25개 항목군

COVERED (VR이 생성):
  근로자수, KSIC, sector = 3개

커버리지 = 3 / 25 ≈ 12%

※ 계산 방식에 따라 변동:
  - "핵심 판정 차원"만 보면 근로자수+KSIC = 2개
  - "전체 입력 항목군"으로 보면 25개 중 3개
  - 어느 기준이든 COVERED < 80% (명확)
```

---

## IF/THEN 판정

```
규칙:
  IF COVERED ≥ 80% THEN WO-VR-READING-ROUND-002 (독해 계속)
  ELSE WO-VR-INPUT-EXPANSION-MAP-001 (VR 미재현 입력공간 목록화)

측정:
  COVERED ≈ 12% (3/25)  →  80% 미만

  ∴ IF 조건 FALSE → ELSE 분기

  다음 WO = WO-VR-INPUT-EXPANSION-MAP-001
    (VR이 아직 재현하지 못하는 입력공간 목록화)
```

---

## 성공 기준 점검

```
UVC-01 사용자 입력목록 확보  → ✅ (4영역 실측)
UVC-02 VR 입력목록 확보      → ✅ (generation_spec 3속성)
UVC-03 항목별 대조 완료      → ✅ (25개 항목군)
UVC-04 COVERED/PARTIAL/NOT_COVERED 분류 → ✅
UVC-05 IF/THEN 판정         → ✅ (ELSE 분기)
```

---

## 완료 문장

```
VR은 사용자 입력공간의 약 12%를 재현한다. (3/25 항목군)
  = 근로자수, KSIC, sector 만 재현.

VR은 사용자 입력공간 중 다음 영역을 아직 재현하지 않는다:
  - 시설 물리속성 (전기/가스/보일러/승강기/에너지/연면적/층수/변압기)
  - 위험 속성 (위험물/화학물질/고압가스/안전관리자/타워크레인/석면/발파/잠수)
  - 공정 (lv1~4)
  - 설비 (명/수량/연도/위치/법정점검/운영상태)
  - 건설 속성 (공사금액/건설유형/하도급)

따라서 다음 WO는 WO-VR-INPUT-EXPANSION-MAP-001 이다.
```

---

## 측정 결과의 의미 (판정 아님, 사실 정리)

```
지금까지 모든 논의가 이 한 숫자로 수렴한다:

  사용자는 다차원(≈25개 항목군)을 입력한다.
  VR은 그 중 3개(근로자수/KSIC/sector)만 흔든다.
  = VR 재현율 약 12%.

이것은 "VR이 부족하다"는 판정이 아니다 (판정 금지).
이것은 "현재 VR과 사용자 현실의 격차가 12% 재현"이라는 측정값이다.

  ※ 별개 질문 (이 WO 범위 아님):
    "엔진이 그 25개 항목군 중 몇 개를 판정에 쓰는가"는
    엔진 분석 영역. 사용자 입력(25) ≠ VR 생성(3) ≠ 엔진 사용(?).
    이 셋은 각각 다른 숫자다. 이번엔 앞 둘만 비교했다.
```
