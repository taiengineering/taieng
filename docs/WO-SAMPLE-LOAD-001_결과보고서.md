# WO-SAMPLE-LOAD-001
# VCF-02 적재 및 실행 결과 보고서

**작성일:** 2026-06-23 | **상태:** 완료

---

## 적재 현황

| 항목 | 수량 |
|---|---|
| factories | **60개** |
| factory_process | **110건** |
| equipment_assets | **59건** |

---

## 핵심 결과

### 결론 1: 의무는 has_*로 발생한다

```
PROC (공정명만, has_*=F): 0건
WORK (공정없음, has_*=T): 2~38건

→ 현재 엔진에서 의무 발생 원인 = 오직 has_* 입력값
→ 공정명은 의무 발생에 기여 없음
```

### 결론 2: 설비코드는 의무 발생에 기여하지 않는다

```
EQ-021-TOWER (has_tc=T): 4건 → has_tc 때문
EQ-021-MOBILE (has_tc=F): 0건
EQ-021-GONDOLA (has_tc=F): 0건

→ asset_name 파싱 없어도 됨 (현재 엔진)
→ 설비코드/asset_name → 의무 경로 없음
```

### 결론 3: THRESHOLD는 별도 경로 필요

```
PAIR-009: 49인 vs 50인 → 0건 차이
→ 인원수 기반 의무는 condition_text 키워드 없음
→ appendix_condition + draft_slot IF_NUMERIC 경로 필요
```

---

## Golden Pair 차이표

| PAIR | 변수 | A | B | 증가 |
|---|---|---|---|---|
| 001 | chemical | 0 | 38 | +38 |
| 002 | hpg | 0 | 22 | +22 |
| 003 | cs | 0 | 19 | +19 |
| 004 | tc | 0 | 4 | +4 |
| 005 | blast | 0 | 2 | +2 |
| 006 | boiler | 0 | 2 | +2 |
| 007 | asb | 0 | 14 | +14 |
| 008 | dive | 0 | 20 | +20 |
| 009 | 49 vs 50인 | 0 | 0 | **0** (THRESHOLD 별도 경로) |
| 010 | 이동식 vs 타워 | 0 | 4 | +4 (has_tc 때문) |

## PROC vs WORK 비교표

| 공정 | PROC | WORK | 판정 |
|---|---|---|---|
| 발파굴착 | 0 | 2 | **has_* 경로만** |
| 밀폐공간작업 | 0 | 19 | **has_* 경로만** |
| 타워크레인양중 | 0 | 4 | **has_* 경로만** |
| 석면해체 | 0 | 14 | **has_* 경로만** |
| 용접/도금/도장 | 0 | N/A | has_* 없음 |

## condition_mapping 설계 방향 (확정)

```
우선순위 1: has_* 기반 매핑 (즉시 작동)
  input_field = 'has_confined_space' | input_value = 'true'
  → condition_text 키워드 매칭

우선순위 2: THRESHOLD 매핑
  input_field = 'employee_count' | operator = '>=' | value = '50'
  → 안전관리자 선임 의무군

우선순위 3: 설비 asset_name → has_* 변환 규칙 (신규)
  '타워크레인' in asset_name → has_tower_crane 트리거

우선순위 4: 공정명 → 의무 매핑 (신규 엔진 로직 필요)
```

## 다음 조치

1. condition_mapping_candidate DDL 승인 (WO-CONDITION-DDL-001)
2. has_* 기반 초기 매핑 적재
3. THRESHOLD 매핑 적재
4. VCF-02 재실행 (condition_mapping 적재 후)
5. VCF-01 (100개) 적재

*WO-SAMPLE-LOAD-001 완료. 60개 적재 / 핵심: 의무 발생 원인 = has_* 수독*
