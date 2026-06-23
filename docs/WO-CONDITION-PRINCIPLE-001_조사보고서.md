# WO-CONDITION-PRINCIPLE-001
# 의무 발생 원인 구조 조사 보고서

**작성일:** 2026-06-23  
**상태:** 조사 완료 / 구현 금지  

---

## 핵심 발견 (먼저)

> 현재 DB에서 KSIC × 공정 × 설비 × 작업 × 규모를 완전히 교차 보유한 실사업장은 **1개**듰이다.  
> condition_code 체계 설계 전에 반드시 직면해야 할 사실이다.

---

## Deliverable A: 사업장 12개 프로파일

| No | sector | KSIC | 인원 | HPG | CHEM | TC | CS | BLAST | 의무매칭 |
|---|---|---|---|---|---|---|---|---|---|
| INS-01 | INDUSTRIAL | NULL | 80 | T | T | T | T | T | **0건** |
| INS-02 | INDUSTRIAL | C20 | 80 | T | T | NULL | NULL | NULL | **5건** |
| INS-03 | INDUSTRIAL | NULL | 5 | F | F | F | F | F | 0건 |
| INS-04 | INDUSTRIAL | NULL | 1000 | F | F | F | T | F | 0건 |
| INS-05 | INDUSTRIAL | NULL | 120 | F | F | F | F | F | 0건 |
| BLD-01 | BUILDING | NULL | 49 | F | F | F | T | F | 0건 |
| BLD-02 | BUILDING | NULL | 50 | T | T | F | F | F | 0건 |
| BLD-03 | BUILDING | NULL | 80 | F | F | T | F | F | 0건 |
| BLD-04 | BUILDING | NULL | 1000 | F | T | T | F | F | 0건 |
| CON-01 | CONSTRUCTION | NULL | 5 | F | F | F | T | F | 0건 |
| CON-02 | CONSTRUCTION | NULL | 30 | F | F | T | F | F | 0건 |
| CON-03 | CONSTRUCTION | NULL | 50 | T | T | T | T | T | 0건 |

**12개 중 의무가 발생한 것: 1개 (INS-02, KSIC=C20)**

---

## Deliverable C: 의무 발생 원인 분류표

| 원인 유형 | 12개 중 해당 | 현재 엔진 출력 |
|---|---|---|
| KSIC | 1개 (INS-02 C20) | **작동 (5건)** |
| PROCESS | 0개 | 경로 없음 |
| EQUIPMENT | 0개 | 경로 없음 |
| WORK (has_*) | 11개 | 0건 (facility_applicability 없음) |
| THRESHOLD | 12개 | INS-02만 부분 작동 |
| MULTI_FACTOR | 1개 | INS-02 (KSIC+WORK+THRESHOLD 복합) |
| UNKNOWN | 11개 | 0건, 원인 분석 불가 |

---

## Deliverable D: 원인 분류 체계 초안

```
의무 발생 원인 5계층

LAYER 1: 존재 조건 (NONE/A_UNIVERSAL) ← 없음
  모든 사업장 적용

LAYER 2: 규모 조건 (THRESHOLD)
  employee_count >= N

LAYER 3: 업종 조건 (INDUSTRY)
  ksic_code, sector
  ← 현재 엔진에서 유일하게 작동 (INS-02)

LAYER 4: 작업/설비/물질 조건 (WORK_ACT/EQUIPMENT_ACT/MATERIAL_ACT)
  has_confined_space, has_chemical_substance, equipment_type_code 등
  ← 현재 거의 작동 안함

LAYER 5: 공정 조건 (PROCESS_ACT, 향후 추가 필요)
  factory_process.process_lv1
  ← 현재 경로 없음
```

---

## condition_code 설계 전 선결 과제

```
1위  KSIC + has_* 동시 입력 샘플 사업장 생성 (최소 10개)
2위  공정 → 의무 매핑 경로 설계
3위  설비코드 → 조건코드 매핑 설계 (equipment_type_code 021 세분화)
4위  condition_mapping_candidate 테이블 생성
5위  검증 사업장 체크엔진 재실행
```

---

## 부록: equipment_type_code 021 내 세분 타입 혼재 문제

현재 equipment_type_code 021에 다음이 혼재됨:
- 타워크레인 (has_tower_crane 발생 조건)
- 이동식크레인 (equipment_type_code = MOBILE_CRANE 발생)
- 곳돌라 (gondola 발생)

asset_name 파싱 없이는 코드만으로 의무 매핑 불가.

*WO-CONDITION-PRINCIPLE-001 완료.*
