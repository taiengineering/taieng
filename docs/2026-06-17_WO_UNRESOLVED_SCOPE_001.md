# WO-UNRESOLVED-SCOPE-001: UNRESOLVED_SCOPE 215건 분류

**작성일**: 2026-06-17  
**성격**: 관찰 전용. 수정/구현 없음.

---

## 관찰 결과

### IF_SCOPE 전체 현황

```
equipment_type   260건  (EQUIPMENT_SCOPE)
facility_type    220건  (FACILITY_SCOPE)
process_type      33건  (PROCESS_SCOPE)
UNRESOLVED       215건  (binding_field = null)
```

### UNRESOLVED_SCOPE raw_token 분포

| raw_token | draft 수 | 연결 대상 |
|---|---|---|
| 보호구 | 29건 | ACTIVITY/EQUIP Scope |
| 안전검사 | 26건 | EQUIPMENT_SCOPE 연결 실패 |
| 물질안전보건자료 | 21건 | has_chemical_substance (Boolean) |
| 건강진단 | 14건 | PROCESS/MAT Scope |
| 안전보건교육 | 13건 | 사업장 일반 |
| 유해위험방지계획서 | 12건 | 공사금액/설비 복합 조건 |
| 성능위주설계 | 10건 | BLDG Scope (건물용도/구모) |
| 안전보건관리규정 | 4건 | employee_count (이미 가능) |
| 위험성평가 | 4건 | 사업장 일반 |
| 안전보건표지 | 2건 | 사업장 일반 |

### 분류 결과

| 분류 | draft 수 | 현재 연결 상태 |
|---|---|---|
| EQUIP Scope 연결 필요 | ~55건 | IF_SCOPE equipment_type 연결 실패 |
| Boolean 연결 필요 | ~21건 | has_chemical_substance 미저장 |
| PROCESS/ACTIVITY Scope 필요 | ~43건 | process_type/activity 링크 없음 |
| BLDG Scope 필요 | ~10건 | building_use_type 미구현 |
| 인원/규모 기반 (이미 가능) | ~8건 | employee_count 이미 연결 |
| 사업장 일반 | ~15건 | sector/general 조항 |

---

## GPT 판정 확인

```
GPT 예측: UNRESOLVED = 법령 → 사업장 연결점 생성 실패
실측 확인: 정확함

보호구(29) → 작업/설비 유형 알아야 판단 가능
안전검사(26) → 설비 유형 필요 (equipment_type 연결 실패)
물질안전보건자료(21) → has_chemical_substance (Boolean 저장 누락)
유해위험방지계획서(12) → 공사금액/설비 복합
성능위주설계(10) → BUILDING 전용
```

---

## 다음 WO 우선순위 (GPT 판정)

```
1순위: WO-UNRESOLVED-SCOPE-001 분류 ✅ (완료)
2순위: Boolean 연결 (has_chemical_substance 등 create_temp_factory 누락)
3순위: EQUIP Scope 연결 (equipment_type 260건 + UNRESOLVED 55건)
4순위: PROCESS Scope 연결 (process_type 33건 + UNRESOLVED 43건)
5순이후: Phase 0B 시작 여부 결정
```

---

## 절대 금지 (유효)

```
Track A 수정 금지
GPT 전속 테이블 수정 금지
Boolean 즉시 연결 금지 (GPT Phase 판단 전)
Equipment/Process Scope 구현 금지 (GPT Phase 판단 전)
obligation_result 생성 금지
```
