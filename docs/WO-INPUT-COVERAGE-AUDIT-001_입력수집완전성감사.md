# WO-INPUT-COVERAGE-AUDIT-001
# 입력세계 수집 완전성 감사

**작성일:** 2026-06-24 | **상태:** 완료 (관찰·감사 전용)
**선행:** WO-INPUT-STAGING-001-APPLY / WO-INPUT-LANDSCAPE-001
**질문:** 현재 8,104건이 입력세계 전체의 몇 %인가?

---

## 결론 먼저

```
현재 input_staging_catalog 8,104건은 입력세계 전체가 아니다.

수집 완료: KSIC / 공정 / 설비(범용) / has_*(9) / numeric(10)
미수집:    위험물 / 고압가스 / 전기설비제품 / 건설표준작업 /
           안전관리자기준 / 진단입력필드마스터 / 시설 / 자격·허가 등

가장 중요한 누락:
  diagnosis_input_fields (128건) = 실제 "사용자 입력 필드 정의 마스터"
  → 이것이 진짜 입력 패턴의 원본. staging에 미포함.
```

---

## TASK: 입력원천 전수 확인

### 이미 수집됨 (input_staging_catalog 8,104건)

| 원천 | 수집 단위 | 건수 |
|---|---|---|
| ksic_process_map | KSIC | 501 |
| ksic_process_map | 공정 | 3,378 |
| process_equipment_map | 표준설비명 | 446 |
| equipment_assets | 설비 인스턴스 | 3,284 |
| factory_process | 사업장 공정 | 476 |
| factories | has_* boolean | 9 |
| factories | numeric | 10 |

### 미수집 — 입력 원천이나 staging에 없음 (핵심 발견)

| 원천 테이블 | row | 입력 의미 | 누락 영향도 |
|---|---|---|---|
| **diagnosis_input_fields** | **128** | **실제 진단 입력 필드 마스터 (sector/group/type)** | **최고 — 진짜 입력 패턴 원본** |
| kcsc_work_master | 243 | 건설표준 작업/공종 (KCSC) | 높음 — CONSTRUCTION 입력축 |
| kcsc_process_master | 161 | 건설표준 공정 | 높음 |
| master_products_elec | 122 | 전기설비 제품 (전압/용량/극수) | 중간 — 전기 NUMERIC 원천 |
| master_safety_certification | 50 | 안전인증 대상 (자격/인증) | 중간 — 자격 입력축 |
| master_dangerous_goods | 49 | 위험물 (지정수량/유별) | 높음 — 위험물 입력축 |
| master_highpressure_gas | 25 | 고압가스 (종류/수량) | 중간 — 고압가스 입력축 |
| master_safety_manager_criteria | 19 | 안전관리자 선임 기준 | 중간 — THRESHOLD 원천 |
| master_legal_inspection_target | 13 | 법정점검 대상 | 낮음 |
| master_fields | 118 | 마스터 필드 정의 | 검토 필요 |
| industry_master | 501 | 업종 마스터 (KSIC 중복?) | 중복 가능 |

### 수집 불가 / 데이터 없음 (0건)

| 원천 | 상태 |
|---|---|
| buildings | 1건 (거의 빔) |
| construction_sites | 0건 |
| sites | 4건 |
| equipment_model_master | 0건 |
| master_safety_manager_criteria 외 master_* 다수 | 0건 |

### 보류 (입력 원천 여부 불확실)

| 원천 | 사유 |
|---|---|
| draft_slot | 이전 WO에서 employee_count 오매핑 확인 — 입력 원천 부적합 |
| appendix_condition | 법령측 데이터 (입력 아님) |
| industry_master | KSIC와 중복 가능 — 대조 필요 |
| master_fields | 필드 정의이나 diagnosis_input_fields와 중복 가능 |

---

## 핵심 발견: diagnosis_input_fields가 진짜 입력 패턴 마스터

### 구조

```
diagnosis_input_fields (128건, is_active 기준):
  field_code      입력 필드 코드
  field_name      필드명
  field_group     입력 그룹 (기본정보/위험물/소방/전기/승강기/공정/설비/협력업체 등)
  field_type      타입 (number/boolean/select/text/table/multi_select)
  sector          INDUSTRIAL / CONSTRUCTION / BUILDING
  tier            입력 계층
  unit            단위
  input_options   선택 옵션
```

### sector × field_group 분포 (실제 입력세계 구조)

```
BUILDING (37개 필드):
  사업장정보 / 위험물 / 소방 / 전기 / 수질환경 / 특수시설 /
  승강기 / 다중이용 / 기본정보
  → 입력 타입: number, boolean, select, text, multi_select

CONSTRUCTION (15개 필드):
  기본정보 / 위험시설 / 공정(table) / 협력업체(table)
  → 공사금액, 위험시설 boolean, 공정 테이블, 협력업체 테이블

INDUSTRIAL (17개 필드):
  기본정보 / 위험물 / 전기 / 공정(table) / 설비(table)
  → 화학물질, 전기용량, 공정/설비 테이블
```

### 이것이 의미하는 것

```
지금까지 staging한 8,104건 = "코드 인벤토리" (KSIC/공정/설비 카탈로그)

diagnosis_input_fields 128건 = "입력 패턴" (사용자가 실제 입력하는 필드)

→ 두 개는 다른 레이어다.
→ 8,104건은 "선택지 풀(pool)"
→ 128건은 "입력 양식(form)"
→ 법령 매핑은 128건의 field_code 단위에서 일어나야 한다.
```

---

## 수집률 평가

### "코드 인벤토리" 기준 수집률

| 영역 | 수집 | 미수집 |
|---|---|---|
| KSIC | ✅ 501 | — |
| 공정(제조) | ✅ 3,378 | — |
| 공정(건설 KCSC) | ❌ | 243 + 161 |
| 설비(범용) | ✅ 446 | — |
| 전기설비 제품 | ❌ | 122 |
| 위험물 | ❌ | 49 |
| 고압가스 | ❌ | 25 |
| 안전인증/자격 | ❌ | 50 |

**코드 인벤토리 수집률: 약 85%** (건설표준·위험물·전기제품 누락)

### "입력 패턴" 기준 수집률

```
diagnosis_input_fields 128건 중
staging에 대응되는 것: has_* 9 + numeric 10 = 19건 직접 대응

입력 패턴 수집률: 약 15% (128건 중 19건만 staging 반영)
```

**→ 입력 패턴 관점에서는 아직 15%밖에 수집 안 됨.**

---

## 발견사항 종합

### 발견 1: 두 개의 입력 레이어 구분 필요

```
레이어 A: 코드 인벤토리 (8,104건) — 선택지 풀
  KSIC, 공정, 설비 카탈로그
  "사업장이 무엇을 보유/수행할 수 있는가"의 전체 목록

레이어 B: 입력 패턴 (128건) — 입력 양식
  diagnosis_input_fields
  "사용자가 실제 진단 시 입력하는 필드"
  법령 매핑의 실제 단위
```

### 발견 2: 사용자가 말한 "4,000여 개"의 정체 재해석

```
4,000여 개 = 레이어 A (코드 인벤토리, 선택지 풀)
128개      = 레이어 B (입력 패턴, 입력 양식)

법령 매핑은 레이어 B(128개 field_code)에서 시작해야 한다.
레이어 A(4,000개)는 레이어 B의 select 옵션 풀이다.

예:
  diagnosis_input_fields.field_code = 'ksic_code' (레이어 B, 1개 필드)
    → input_options = KSIC 501개 (레이어 A, 선택지 풀)
```

### 발견 3: 건설(CONSTRUCTION) 입력축 대량 누락

```
kcsc_work_master 243 + kcsc_process_master 161 = 404건
건설표준코드(KCSC) 기반 작업·공정이 staging에 전혀 없음.

→ 현재 staging의 공정 3,378은 전부 KSIC 기반(제조 중심)
→ 건설 공종은 KCSC 별도 체계 — 미수집
```

### 발견 4: 위험물·고압가스·전기설비 입력축 누락

```
master_dangerous_goods 49   위험물 (지정수량 기준 = NUMERIC THRESHOLD 원천)
master_highpressure_gas 25  고압가스
master_products_elec 122    전기설비 (전압/용량 = NUMERIC 원천)

→ 이전 WO에서 발견한 "전압(V) 불일치", "화학물질 100L" 문제의
  실제 원천 데이터가 여기 있었음.
```

---

## 성공 기준 답변

> 현재 8,104건이 입력세계 전체의 몇 %인가?

```
코드 인벤토리 기준: 약 85% (건설표준·위험물·전기 누락)
입력 패턴 기준:     약 15% (128개 field 중 19개만 반영)

→ "수집 90%"라는 이전 평가는 코드 인벤토리만 본 것.
→ 입력 패턴(diagnosis_input_fields)을 포함하면 수집 미완.
```

---

## 다음 단계 권고

```
WO-INPUT-COVERAGE-AUDIT-001 (현재) — 완료
      ↓
WO-INPUT-STAGING-002
  미수집 입력 원천 추가 staging:
    diagnosis_input_fields 128  ← 최우선 (입력 패턴 마스터)
    kcsc_work_master 243        ← 건설 작업축
    kcsc_process_master 161     ← 건설 공정축
    master_dangerous_goods 49   ← 위험물축
    master_highpressure_gas 25  ← 고압가스축
    master_products_elec 122    ← 전기설비축
    master_safety_certification 50 ← 자격·인증축
      ↓
WO-INPUT-LANDSCAPE-002
  레이어 A(코드 풀) vs 레이어 B(입력 양식) 관계 지형도
      ↓
WO-INPUT-PATTERN-DISCOVERY-001
  레이어 B(128 field) 기준 패턴 발견
```

---

## 핵심 교훈

```
이전 평가 "수집 90%"는 위험한 과신이었다.

실제로는:
  - 코드 인벤토리만 85% 수집
  - 입력 패턴(진짜 입력 단위)은 15%만 수집
  - 건설·위험물·전기·고압가스 입력축 전부 누락

패턴 발견을 지금 시작했으면,
제조 중심 KSIC/설비만 보고 건설·위험물·전기를 놓친
편향된 패턴이 나왔을 것이다.

수집 완전성 감사를 먼저 한 것이 옳았다.
```

---

*WO-INPUT-COVERAGE-AUDIT-001 완료.*
*수집률: 코드 인벤토리 85% / 입력 패턴 15%.*
*핵심 발견: diagnosis_input_fields(128) = 진짜 입력 패턴 마스터. 건설·위험물·전기 입력축 누락.*
