# WO-SAMPLE-003
# Condition Mapping 검증용 사업장 60개 설계서 (VCF-02)

**작성일:** 2026-06-23  
**상태:** 설계 완료 / INSERT 금지 / VCF-01 승인 후 적재  
**목적:** condition_mapping_candidate 설계 원칙 검증

---

## 구성 요약 (60개)

| 그룹 | 수량 | 목적 | 핵심 실험 |
|---|---|---|---|
| A. Golden Pair | 20개 (10쌍) | has_* 단독 효과 측정 | A건수 vs B건수 = 해당 조건 의무 건수 |
| B. PROC ONLY | 10개 | 공정명 단독 효과 | 공정명만으로 의무 발생하는가? |
| C. WORK ONLY | 10개 | has_* 단독 효과 | 공정·설비 없이 has_*만으로? |
| D. EQ Ambiguity | 20개 | 설비코드 모호성 | asset_name 파싱 필요성 |

---

## 그룹 A: Golden Pair (10쌍 = 20개)

**공통 고정 조건 (A/B 쌍 전체):**
- ksic_code: C20 (일부 예외: blast=F42, asb=F41, dive=F42)
- employee_count: 50
- 공정: 원료처리, 혼합, 반응, 증류, 포장 (5개고정)
- 설비: 반응기×2, 혼합기×1, 열교환기×1, 집진기×1 (고정)

### 쌍 목록

| 쌍 | 통제변수 | A (false) | B (true) | 예상 의무 차이 |
|---|---|---|---|---|
| PAIR-001 | chemical_substance | GP-001A | GP-001B | 화학물질 취급 의무 |
| PAIR-002 | high_pressure_gas | GP-002A | GP-002B | 고압가스 안전 조치 |
| PAIR-003 | confined_space | GP-003A | GP-003B | 밀폐공간 의무 전체 |
| PAIR-004 | tower_crane | GP-004A | GP-004B | 타워크레인 설치·지지 의무 |
| PAIR-005 | blasting (F42) | GP-005A | GP-005B | 발파 작업 의무 |
| PAIR-006 | boiler | GP-006A | GP-006B | 보일러 검사 의무 |
| PAIR-007 | asbestos (F41) | GP-007A | GP-007B | 석면 해체 의무 |
| PAIR-008 | diving (F42) | GP-008A | GP-008B | 잠수 작업 의무 |
| PAIR-009 | safety_manager (49vs50인) | GP-009A | GP-009B | 안전관리자 선임 |
| PAIR-010 | tc+asset_name (021코드) | GP-010A(mobile) | GP-010B(tower) | 타워 vs 이동식 의무 분기 |

---

## 그룹 B: PROC ONLY (10개)

**엄격한 고정 조건:**
- has_* **전체 false**
- 설비 **없음**
- ksic_code: C20 (단, PROC-006=F42, PROC-008/009=F41, PROC-010=H52)
- employee_count: 50 (고정)

| ID | 공정 | KSIC | 핵심 코을 |
|---|---|---|---|
| PROC-001 | 용접 | C20 | 공정명 단독 의무 발생하는가? |
| PROC-002 | 도금 | C20 | 위와 동일 |
| PROC-003 | 도장 | C20 | 위와 동일 |
| PROC-004 | 반응 | C20 | 위와 동일 |
| PROC-005 | 증류 | C20 | 위와 동일 |
| PROC-006 | 발파굴착 | F42 | vs WORK-004(발파) 비교 |
| PROC-007 | 밀폐공간작업 | C20 | vs WORK-002(cs=T) 비교 |
| PROC-008 | 타워크레인양중 | F41 | vs WORK-003(tc=T) 비교 |
| PROC-009 | 석면해체 | F41 | vs WORK-007(asb=T) 비교 |
| PROC-010 | 위험물보관 | H52 | 위험물 공정 의무 |

**핵심 예상:** 대부분 0건 (PROCESS 엔진 경로 없으면). PROC-006과 WORK-004 비교가 핵심.

---

## 그룹 C: WORK ONLY (10개)

**엄격한 고정 조건:**
- 공정 **없음**
- 설비 **없음**
- ksic_code: C20 (단, blast/dive=F42, asb=F41)
- employee_count: 50

| ID | has_* | 비교 대상 |
|---|---|---|
| WORK-001 | chem=T | PROC-002/003(chem=F, 공정만) |
| WORK-002 | cs=T | PROC-007(cs=F, 공정만) |
| WORK-003 | tc=T | PROC-008(tc=F, 공정만) |
| WORK-004 | blast=T | PROC-006(blast=F, 공정만) |
| WORK-005 | dive=T | (no PROC 비교) |
| WORK-006 | boiler=T | EQ-014-BOILER(설비만, has=F) |
| WORK-007 | asb=T | PROC-009(asb=F, 공정만) |
| WORK-008 | hpg=T | EQ-029-PRESSURE(설비만, has=F) |
| WORK-009 | chem+cs=T | WORK-001+WORK-002 합산 vs 복합의무 |
| WORK-010 | ALL=T | 최대치 측정 |

---

## 그룹 D: EQ Ambiguity (20개)

### 코드별 설비 의미 분류 (실DB 기반)

| 코드 | asset_name 유형 | 의무 경로 | 기대 분기 |
|---|---|---|---|
| 021 | 타워크레인 | has_tower_crane=T 연동 | 타워크레인 의무 |
| 021 | 이동식크레인 | equipment_type MOBILE | 이동식크레인 의무 |
| 021 | 곳돌라 | equipment_type GONDOLA | 곳돌라 의무 |
| 021 | 천장크레인 | equipment_type OVERHEAD | 주행크레인 의무 |
| 040 | 굴착기 | 차량계 | 굴착기 안전대의 |
| 040 | 발파기 | has_blasting 연동? | 발파 설비 의무 |
| 040 | 도금조 | has_chemical 연동? | 도금 안전 의무 |
| 040 | 덴프트럭 | 차량계 | 하역운반 의무 |
| 040 | CNC선반 | 기계계 | 과매핑 탐지 케이스 |
| 014 | 증기보일러 | has_boiler 연동 | 보일러 슬험 의무 |
| 014 | 건조로 | has_boiler과 무관? | 건조기기 의무 |
| 029 | 압력용기 | has_hpg 연동? | 압력용기 안전밸브 |
| 029 | 증류탑 | has_hpg? | 증류 열원 요건 |
| 029 | 화학탱크 | has_chemical? | 화학물질 저장 의무 |
| 036 | 집진기 | 분진 | 국소배기장치 의무 |
| 036 | 도장부스 | 유해물질 | 도장작업 안전 의무 |
| 036 | 음압기 | 석면 | 석면 해체 의무 |
| 036 | 배기설비 | 일반 환기 | 환기설비 일반 |
| 037 | 맨홈 | 밀폐공간 | 밀폐공간 제법 의무 |
| 037 | 오수처리시설 | 환경 | 수처리 의무 |

---

## 핵심 질문 3가지

```
1. 의무는 공정(PROC)으로 발생하는가, has_*(WORK)으로 발생하는가?
   → PROC-006 vs WORK-004, PROC-007 vs WORK-002, PROC-008 vs WORK-003 비교

2. 설비코드만으로 의무 식별이 가능한가?
   → 타워크레인 vs 이동식크레인 (021코드 동일)
   → 보일러 vs 건조로 (014코드 동일)
   → 맨홈 vs 오수처리 (037코드 동일)

3. asset_name 파싱이 필수인가?
   → 그룹 D 전체 실행 후 판단
```

---

## 적재 순서 (VCF-01 후)

```
VCF-01 (100개) INSERT → facility_applicability 실행
    ↓
VCF-02 (60개) INSERT → facility_applicability 실행
    ↓
그룹 A: Pair 의무 차이 집계
그룹 B: PROC 의무 건수 집계 (공정 경로 검증)
그룹 C: WORK 의무 건수 집계 (has_* 경로 검증)
그룹 D: EQ 설비코드 모호성 측정
    ↓
condition_mapping_candidate 설계 확정
```

*WO-SAMPLE-003 완료.*
