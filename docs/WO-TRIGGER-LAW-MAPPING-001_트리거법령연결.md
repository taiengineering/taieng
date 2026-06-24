# WO-TRIGGER-LAW-MAPPING-001
# Trigger → 법령 연결

**작성일:** 2026-06-24 | **상태:** 완료 (첫 실제 연결 작업)
**선행:** WO-INPUT-TRIGGER-CLASSIFICATION-001
**금지:** 새 Trigger 생성 / 입력필드 추가 / 패턴 추가 / 구조 검증 / DDL
**목적:** 각 Trigger는 어떤 법령군을 발생시키는가? (입력 안 봄, Trigger→법령만)

> 17회차에서 계속 막혔던 구간. 입력→Trigger는 끝났고, 이제 Trigger→법령 연결.

---

## 결론 먼저

```
사업주 의무 1,572건을 Trigger로 분류한 결과:

CONNECTED (현 Trigger로 설명):
  UNIVERSAL  693 (44.1%)
  WORK       155 (9.9%)
  MATERIAL    68 (4.3%)
  FACILITY    62 (3.9%)
  EQUIPMENT   30 (1.9%)
  THRESHOLD   17 (1.1%)
  소계: 1,025건 (65.2%)

PARTIAL:
  FRAGMENT    27 (1.7%) — parent 연결 필요

NO_TRIGGER:
  520건 (33.1%) — 현 Trigger로 설명 안 됨 → 신규 Trigger 후보

→ 현재 Trigger 체계로 사업주 의무의 약 65% 설명.
→ 33%는 신규 Trigger 필요 (운반·전기·추락·기계방호 등).
```

---

## 산출물 A: Trigger → 법령군

### WORK_EXISTS L2별 법령군 (155건)

| L2 Trigger | 법령 조문수 | 입력필드 |
|---|---|---|
| DEMOLITION (해체) | 20 | has_demolition |
| DIVING (잠수) | 18 | has_diving |
| EXCAVATION (굴착) | 16 | has_excavation |
| DUST (분진) | 13 | has_dust_work |
| WELDING (용접) | 12 | has_welding |
| CONFINED_SPACE (밀폐) | 12 | has_confined_space |
| SCAFFOLD (비계) | 11 | has_scaffold |
| ASBESTOS (석면) | 11 | has_asbestos_demo |
| PILE_WORK (항타) | 6 | has_pile_work |
| RADIATION (방사선) | 5 | has_radiation |
| BLASTING (발파) | 2 | has_blasting |
| SURFACE_TREAT (도장·도금) | 2 | has_painting/has_plating |

### EQUIPMENT_EXISTS L2별 법령군 (30건 명시 + 267 기타)

| L2 Trigger | 법령 조문수 | 입력필드 |
|---|---|---|
| CRANE (크레인) | 5 | has_crane |
| CONVEYOR (컨베이어) | 5 | has_conveyor |
| LIFT (리프트) | 3 | has_elevator |
| PRESSURE_VESSEL (압력용기) | 2 | has_pressure_vessel |
| PRESS (프레스) | 2 | has_press |
| TOWER_CRANE (타워크레인) | 2 | has_tower_crane |
| GONDOLA (곤돌라) | 1 | has_gondola |
| ROLLING (롤러) | 1 | has_rolling |
| FORKLIFT (지게차) | 1 | has_forklift |

### MATERIAL_EXISTS L2별 법령군 (68건)

| L2 Trigger | 법령 조문수 | 입력필드 |
|---|---|---|
| HAZMAT (관리대상 유해물질) | 39 | has_hazardous_material |
| ASBESTOS (석면) | 14 | has_asbestos |
| CHEMICAL (화학) | 11 | has_chemical_substance |
| DUST (분진) | 6 | has_dust_work |
| HIGH_PRESSURE_GAS (고압가스) | — | has_high_pressure_gas |

---

## 산출물 B: CONNECTED / PARTIAL / NO_TRIGGER 분포

| 분류 | 건수 | 비율 |
|---|---|---|
| **UNIVERSAL** (CONNECTED) | 693 | 44.1% |
| **NO_TRIGGER** | 520 | 33.1% |
| **WORK** (CONNECTED) | 155 | 9.9% |
| **MATERIAL** (CONNECTED) | 68 | 4.3% |
| **FACILITY** (CONNECTED) | 62 | 3.9% |
| **EQUIPMENT** (CONNECTED) | 30 | 1.9% |
| **FRAGMENT** (PARTIAL) | 27 | 1.7% |
| **THRESHOLD** (CONNECTED) | 17 | 1.1% |
| **합계** | 1,572 | 100% |

```
CONNECTED 소계: 1,025 (65.2%)
PARTIAL:           27 (1.7%)
NO_TRIGGER:       520 (33.1%)
```

---

## 산출물 C: APPENDIX 목록

```
APPENDIX_THRESHOLD로 갈리는 입력:
  worker_count   → 안전관리자/관리담당자/관리규정 별표
  project_amount → 건설 안전관리자 별표
  building_grade → 건물 등급 기준

현 분류에서 THRESHOLD 17건 중 대부분은 DIRECT(본조 수치).
APPENDIX는 본조에 수치가 없어 별도 추적 필요 (appendix_condition 7건 병목).

→ APPENDIX는 이 매핑에서 분리하여 별도 트랙으로 관리.
→ worker_count 1개가 102개 별표 의무의 입구.
```

---

## 산출물 D: TRUE_UNIVERSAL 목록

```
UNIVERSAL 693건 = 사업주 의무의 44.1% (최대)

조건: 입력 없이 sector 소속만으로 발동
입력 대응: ksic_major/ksic_sub (sector 확정용 2개뿐)

성격:
  교육·보고·비치·게시·작성·점검 등 일반 의무
  → 제조업/건설업/건물 sector 선택 시 일괄 후보화

주의 (HIERARCHY-001에서 확인):
  UNIVERSAL 693 중 일부는 action_text에 숨은 조건 보유.
  진짜 TRUE_UNIVERSAL은 약 359건.
  나머지는 HIDDEN_ACTIVITY/THRESHOLD로 재분류 대상.
```

---

## 산출물 E: 신규 Trigger 필요 후보 (NO_TRIGGER 520건)

**이것이 이번 WO의 가장 중요한 산출물.** 법령은 있는데 현 Trigger로 설명 안 되는 것:

| 신규 Trigger 후보 | 조문수 | 설명 |
|---|---|---|
| **점검·정비** | 72 | "정기 점검·검사·정비" — 설비 무관 일반 점검 의무 |
| **일반기계방호** | 40 | "기계 방호장치·덮개" — 특정 설비 아닌 일반 기계 |
| **교육·보호** | 32 | "보호구 지급·건강관리" — UNIVERSAL과 경계 |
| **운반·하역작업** | 25 | "차량·하역·양중·줄걸이" — WORK 하위 신규 |
| **전기작업** | 16 | "감전·접지·절연·충전부" — 전기 특화 Trigger |
| **작업환경** | 12 | "소음·진동·온도·환기·조명" — 환경 측정 |
| **추락방지** | 10 | "개구부·난간·안전대·방망" — 고소 관련 |
| **화재·폭발** | 2 | "소화·인화·폭발 방지" |
| **기타** | 311 | 추가 정밀 분류 필요 |

### 신규 Trigger 후보 분석

```
명확한 신규 Trigger (입력필드 대응 가능):
  운반·하역 (25) → has_forklift/has_crane 일부 + 신규 has_lifting
  전기작업 (16) → has_temp_electric + 신규 has_electrical_work
  추락방지 (10) → has_high_place_work + has_scaffold

UNIVERSAL로 흡수 가능 (입력 불필요):
  점검·정비 (72) → 설비 보유 시 자동 + 일반 점검
  일반기계방호 (40) → 설비 보유 시 자동
  교육·보호 (32) → sector UNIVERSAL

→ NO_TRIGGER 520 중:
  약 60건은 신규 Trigger (운반/전기/추락)
  약 144건은 기존 EXISTS/UNIVERSAL로 흡수 가능
  311건 "기타"는 추가 정밀 분류 필요 (조문 직독)
```

---

## 핵심 발견

### 발견 1: 현 Trigger로 65% 설명, 33%는 미설명

```
CONNECTED 65.2% — 입력→Trigger→법령 작동
NO_TRIGGER 33.1% — 신규 Trigger 필요

→ 처음으로 "98개 입력이 몇 개 법령군을 발동하는가" 답:
  현재 약 1,025건 법령 발동 (사업주 의무의 65%).
  나머지 35%는 추가 Trigger/parent 연결 필요.
```

### 발견 2: UNIVERSAL이 절반 (44%)

```
사업주 의무의 44%가 sector만으로 발동.
→ 입력 거의 불필요. ksic_major 선택만으로 693건 후보.
→ 진단의 baseline은 sector 기반 UNIVERSAL.
→ has_* 입력은 그 위에 추가되는 특화 의무.
```

### 발견 3: NO_TRIGGER 520건이 진짜 발견

```
지금까지 분석을 위한 분석이었다면,
이번엔 "법령은 있는데 Trigger 없는 것"을 실제로 찾음.

명확한 신규 Trigger:
  운반·하역 / 전기작업 / 추락방지 (약 60건)
  → 입력필드 추가 필요 (has_lifting, has_electrical_work 등)

→ 이게 다음 입력필드 확장의 근거.
```

### 발견 4: EQUIPMENT가 의외로 적다 (30건 명시)

```
EQUIPMENT 입력은 20개인데 법령 조문은 30건만 명시 매칭.
대부분 "기타설비"(267)로 빠짐.

→ 설비 의무는 "특정 설비명"보다 "일반 기계 방호"로 서술됨.
→ has_crane/has_press 등 개별 설비보다
  "기계 일반" 의무가 많음 → 일반기계방호 Trigger 후보(40).
```

---

## 성공 기준 답변

> 98개 입력필드가 몇 개의 법령군을 발동시키는가?

```
현재 Trigger 체계로:
  CONNECTED 1,025건 (사업주 의무의 65.2%)
    UNIVERSAL 693 (sector 기반)
    WORK 155 / MATERIAL 68 / FACILITY 62 / EQUIPMENT 30 / THRESHOLD 17

  미연결 547건 (35%)
    NO_TRIGGER 520 (신규 Trigger 필요)
    FRAGMENT 27 (parent 연결 필요)

→ 입력 → Trigger → 법령 연결이 처음으로 완성됨.
→ 65% 커버. 35%는 신규 Trigger/parent로 확장 가능.
```

---

## 다음 단계

```
WO-TRIGGER-LAW-MAPPING-001 (현재) — 완료
      ↓
선택지 1: WO-TRIGGER-EXPANSION-001
  NO_TRIGGER 520건 정밀 분류 → 신규 Trigger 확정
  (운반/전기/추락 + 311 기타)
      ↓
선택지 2: WO-PATTERN-CANDIDATE-GENERATION-001
  현 65% CONNECTED로 후보군 생성 시작
  1순위: WORK/EQUIPMENT/MATERIAL EXISTS (가장 깨끗)
  baseline: UNIVERSAL sector 일괄
```

---

*WO-TRIGGER-LAW-MAPPING-001 완료. 첫 실제 Trigger→법령 연결.*
*사업주 의무 65% CONNECTED. UNIVERSAL 44% 최대. NO_TRIGGER 33%(신규 Trigger 후보).*
*핵심: 입력→Trigger→법령 연결 완성. 운반·전기·추락이 신규 Trigger 후보.*
