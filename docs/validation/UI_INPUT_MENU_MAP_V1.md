# UI INPUT MENU MAP V1
# WO-UI-INPUT-MENU-MAP-001

**작성일**: 2026-06-20
**목적**: 사용자 입력공간의 메뉴 축 확정 + IF/THEN으로 다음 WO 결정.
**범위**: 메뉴 존재 여부만. 상세 input 필드/DB/API/엔진 분석 안 함.
**근거**: 디렉토리 목록 실측(파일 존재) + 사장님 화면 캡처(메뉴 표시).

---

## 메뉴 4축 매핑표

| 메뉴 | 연결 파일 | 존재 | 입력대상 | 상태 |
|---|---|---|---|---|
| 회사정보 | my-company.html | **YES** | 회사 | **ACTIVE** |
| 시설목록 | factory-list.html | **YES** | 시설 | **ACTIVE** |
| 공정관리 | process-manage.html / process-select.html | **YES** | 공정 | **ACTIVE** |
| 설비관리 | my-equipment.html | **YES** | 설비 | **ACTIVE** |

```
파일 존재 근거 (디렉토리 실측):
  my-company.html        32,489 bytes  ✓
  factory-list.html      56,257 bytes  ✓
  process-manage.html    30,442 bytes  ✓
  process-select.html    34,086 bytes  ✓
  my-equipment.html      38,644 bytes  ✓

메뉴 ACTIVE 근거 (사장님 화면 캡처):
  시설관리 드롭다운에 4개 메뉴 모두 표시:
  회사정보 / 시설목록 / 공정관리 / 설비관리
  → 4축 전부 ACTIVE (숨김 아님).

숨김 메뉴:
  건설 = 메뉴에서 감춰짐 (HIDDEN). BLOCKED 상태와 정합.
  → 단 건설은 이 4축에 포함 안 됨. 4축은 전부 ACTIVE.
```

---

## 판정 규칙 적용 (IF/THEN)

```
규칙:
  IF 회사정보 / 시설목록 / 공정관리 / 설비관리 4축이 모두 존재
  THEN 다음 WO = WO-UI-FIELD-INVENTORY-001 (각 화면 입력필드 조사)
  ELSE 다음 WO = WO-UI-INPUT-SPACE-REDEFINE-001 (입력공간 재정의)

판정:
  회사정보  존재 ✓
  시설목록  존재 ✓
  공정관리  존재 ✓
  설비관리  존재 ✓
  → 4축 모두 존재 = IF 조건 TRUE

  ∴ 다음 WO = WO-UI-FIELD-INVENTORY-001
```

---

## 성공 기준 점검

```
MMM-01 메뉴 4축 존재 여부 확인 → ✅ (4/4 존재)
MMM-02 각 메뉴 입력대상 분류    → ✅ (회사/시설/공정/설비)
MMM-03 숨김 메뉴 여부 확인      → ✅ (건설=HIDDEN, 4축은 ACTIVE)
MMM-04 IF/THEN 판정 수행        → ✅ (IF TRUE)
MMM-05 다음 WO 자동 결정        → ✅ (WO-UI-FIELD-INVENTORY-001)
```

---

## 원칙 준수

```
화면 상세 input 필드 분석 안 함 ✅ (존재 여부만)
DB/API/엔진 추적 안 함 ✅
법령 검토/개선안 안 함 ✅
메뉴 축 확인 + IF/THEN 판정만 ✅
```

---

## 완료 문장

```
사용자 입력공간 메뉴 축은 4축으로 확인됨.
  (회사정보 / 시설목록 / 공정관리 / 설비관리 — 전부 ACTIVE)
  건설은 HIDDEN (BLOCKED 정합, 4축 외).

따라서 다음 WO는 WO-UI-FIELD-INVENTORY-001 이다.
  (각 화면의 실제 입력필드 조사)
```

---

## 다음 WO 예고 (이번 WO가 결정함)

```
WO-UI-FIELD-INVENTORY-001
  목적: 4개 화면(회사정보/시설목록/공정관리/설비관리)의
        실제 입력필드 전수 조사.
  현황: 회사정보·설비관리는 이미 V2에서 실측 완료.
        → 남은 것은 시설목록(factory-list) / 공정관리(process-manage).
  특히 시설목록 = "근로자수" 입력 위치 확정 지점
        (회사정보엔 근로자수 없었음 → 시설 단위로 추정).
```
