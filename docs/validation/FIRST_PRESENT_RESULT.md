# FIRST PRESENT — 최초 PRESENT 1건 시도 결과
# WO-FIRST-PRESENT-001

**작성일**: 2026-06-21
**목적**: PRESENT 0→1. 조사 아닌 변경-측정.
**결과**: PRESENT를 만드는 정확한 변경 지점을 핀포인트 확정. 단 그 변경 =
  binding_field 생성 = GPT 전담 → Claude 실행 불가. GPT 인계로 전환.

---

## 기준선

```
건설 PRESENT = 0 / MISSING 11종 / WRONG 98%
```

---

## 변경 대상 선정 (1순위 안전교육 → 실측으로 안전관리계획 전환)

### 안전교육 (1순위) — executable_draft 부재로 후보 탈락
```
산안법 제29조 "근로자에 대한 안전보건교육"      draft 0  ← 핵심의무인데 draft 없음
산안법 제31조 "건설업 기초안전보건교육"          draft 0
draft 있는 것 = "안전보건교육기관 등록"(행정) 뿐.
→ 안전교육은 binding 이전에 executable_draft 자체가 없음.
  PRESENT 만들려면 draft 생성부터 = Deterministic Compiler(GPT).
```

### 안전관리계획 (3순위) — ★ executable_draft 존재, 진입점 발견
```
"건설기술 진흥법 시행령 — 안전관리계획의 수립"  draft 5건 존재.
  law_sectors: {CONSTRUCTION}     ← sector 매핑 정상(건설 포함)
  slot_sections: IF_NUMERIC 등 존재
  binding_fields: (none)          ← ★ 전부 비어있음
```

---

## ★ PRESENT를 막는 정확한 지점 (핀포인트 확정)

```
"안전관리계획의 수립" draft가 결과에 안 나오는 이유:
  1. sector 매핑 = CONSTRUCTION 정상 → sector filter 통과함 (원인 아님)
  2. executable_draft 5건 존재 → draft 없음 아님 (원인 아님)
  3. draft_slot에 IF_NUMERIC section 존재 → section 없음 아님
  4. ★ binding_field = (none) → _load_draft_slot_groups가
     binding_field IS NOT NULL만 적재 → 이 draft는 평가 루프 미진입.

= PRESENT 0의 원인 = binding_field 부재. 정확히 이 한 지점.
  sector도 draft도 section도 정상. binding_field만 비어서 평가 안 됨.
```

---

## 변경 시도 판정

```
시도 가능한 변경:
  (가) binding_field 생성 → draft_slot에 binding 채움
       = PRESENT를 만드는 유일한 변경.
       = GPT 전담 (binding_field 생성 Claude 절대 금지).
       → Claude 실행 불가.
  (나) sector mapping 변경
       = 이미 CONSTRUCTION 정상. 변경 불필요/무효.
       = 직전 LOOP_001에서 "mapping은 PRESENT 못 만든다" 확정.

→ Claude가 실행 가능한 변경으로는 PRESENT 0→1 불가.
  판정: 변경 미실행 (실행 가능 카드 없음).
  무의미한 mapping 변경 반복 = LOOP_001의 C·롤백 재현일 뿐 → 안 함.
```

---

## ★ GPT 인계 (PRESENT 1건 핀포인트)

```
[최소 변경으로 PRESENT 1건 만드는 지점]
  대상 draft: executable_draft (article: "안전관리계획의 수립",
              law: 건설기술 진흥법 시행령), 5건.
  현재 상태: sector=CONSTRUCTION ✓, section=IF_NUMERIC 존재 ✓,
            binding_field=(none) ✗.
  필요 작업(GPT):
    이 draft_slot의 IF_NUMERIC/IF_CONDITION에 binding_field 부여.
    예: 안전관리계획은 "건설공사 + 일정 규모(공사금액/연면적)" 조건 →
        contract_amount/area_size 등 기존 binding_field 활용 가능
        (새 boolean 유형 아닐 수 있음 — 수치 조건이면 기존 메커니즘으로 가능).
  검증(Claude): binding 부여 후 factory-test-run(7b9bf18d) 재실행 →
    결과에 "안전관리계획의 수립" 등장 → PRESENT 0→1 측정.

[중요]
  안전관리계획은 IF_NUMERIC section이 이미 있음 → Boolean 신유형 불필요.
  기존 numeric binding(contract_amount 등)을 IF_NUMERIC slot에 연결하면
  TYPE-A(수치형, PASS 검증됨) 경로로 PRESENT 생성 가능.
  = 가장 빠른 PRESENT 1건 후보. 위험요소(Boolean 신유형)보다 쉬움.
```

---

## 성공 기준 대조

```
- 변경 1건 실행            → 미실행 (실행 가능 변경 없음, binding=GPT)
- PRESENT 0→1             → 미달 (binding 부재가 원인, Claude 권한 밖)
- 변경 지점 핀포인트       → ✅ (안전관리계획 draft, binding_field=none)
- GPT 인계                → ✅
```

---

## 완료 문장

```
최초 PRESENT 1건을 시도한 결과, 후보를 안전교육(draft 부재)에서
안전관리계획(draft 5건 존재)으로 전환하였고, PRESENT 0의 정확한 원인이
"건설기술 진흥법 시행령 안전관리계획" draft의 binding_field 부재(none)임을
핀포인트로 확정하였다. sector·draft·section은 모두 정상이며 binding_field만
비어 평가 루프에 미진입한다. 이 변경(binding_field 생성)은 GPT 전담이므로
Claude는 실행하지 않고, IF_NUMERIC 기존 메커니즘으로 PRESENT 생성이
가능한 핀포인트를 GPT에 인계하였다.
이로써 "PRESENT는 binding 계층에서만 생성된다"는 LOOP_001 결론이
draft 레벨에서 재확정되었다.
```
