# GPT 질의 — Phase 3 WO 설계 요청 (v2)

**작성일**: 2026-06-17  
**버전**: v2 (사장님 방향 수정 반영 — KSIC 필터 아님, Condition Scope 구조)

---

## 한 문장 요약

> Phase 3은 B071을 넣는 작업이 아니다.  
> ApplicabilityCondition이 Scope를 가질 수 있는 구조인가를 확인하는 작업이다.

---

## 사장님 지적사항 (핵심)

**로컨 질문 (Phase 3이 지금 하려는 것):**
```
B071을 ksic_prefixes에 넣을까?
```

**전체 질문 (V4 엔진이 해야 하는 것):**
```
업종이라는 개념을 어디서 관리할 것인가?
그 구조가 나중에 PROCESS/ACTIVITY/EQUIP으로 확장될 수 있는가?
```

**미래 법령군에서 등장할 Scope 유형:**
```python
안전관리자 선임    → scope_type = INDUSTRY,  scope_values = ["C10", "B071"]
용접작업       → scope_type = PROCESS,   scope_values = ["용접"]
굴십작업       → scope_type = ACTIVITY,  scope_values = ["굴십"]
밀툗공간작업     → scope_type = ACTIVITY,  scope_values = ["밀툗공간"]
열림장치 설치   → scope_type = EQUIP,     scope_values = ["열림장치"]
```

즉 지금 파일럿에서 `ksic_prefixes`만 넣으면,
나중에 용접작업이 나오는 순간 또 다른 코럼을 못박아야 합니다.

---

## Phase 2에서 발견된 문제 (콘텍스트)

화성 제2공장 (C28, 280명) 평가 시 4건 MATCH:
```
토사석 광업(071)   → MATCH  ❌ (C28 해당 없음)
식료품 제조업    → MATCH  ❌ (C28 해당 없음)
운수창고업       → MATCH  ❌ (C28 해당 없음)
제1호~27호 외 일반  → MATCH  ✅ (C28은 일반 조항)
```

**원인**: ApplicabilityCondition에 Scope 정보가 없음.
C1 평가기가 수치만 비교하고 업종 필터 없음.

**이것은 엔진 버그가 아님:**
ApplicabilityCondition 데이터에 Scope가 없는 상태 (Condition Data Enrichment 문제).

---

## GPT엔게 질문

**질문 1. Condition Scope 구조 설계**

ApplicabilityCondition에 Scope를 부여하는 구조를 제안해주세요.

사장님 제안 방향:
```python
ConditionScope {
    scope_type:   INDUSTRY | PROCESS | ACTIVITY | EQUIP | NONE
    scope_values: list[str] | None
    is_general:   bool   # 배타집합 (명시 업종 제외한 모든 경우)
}
```

이 구조를 `applicability_conditions` 테이블에 저장하는 방법을 판정해주세요.

**금지**: industry_name 텍스트 런타임 해석 (B 방식)
```python
# 금지
if "식료품" in industry_name: ...

# 허용
if profile.ksic_code.startswith(prefix): ...
```

---

**질문 2. 일반 조항("제1호~27호 외의 사업") 처리**

일반 조항은 "모든 업종"이 아니라 "상위 업종에 해당하지 않는 업종"입니다.

```python
# 오해
def matches_general(facility_ksic):
    return True  # 모든 업종 X

# 정답
def matches_general(facility_ksic, special_groups):
    return facility_ksic not in special_groups  # 배타집합
```

즉 B071 사업장은:
- 토사석 광업 조건 → MATCH
- 일반 조항 → **NOT_APPLICABLE** (B071은 1호~27호 해당 업종)

이 배타집합 로직을 C1 평가기에서 어떻게 구현해야 하는지 판정해주세요.

---

**질문 3. Phase 3 산출물 정의**

Phase 3 WO의 성격:
```
Condition Data Enrichment
= 엔진 수정 아님
= 조건 객체에 Scope 정보 추가
```

생성해야 하는 것:
- `applicability_conditions.scope_type` 코럼
- `applicability_conditions.scope_values` 코럼
- `applicability_conditions.is_general` 코럼
- C1 평가기 Scope 필터 로직
- `evaluation_reason`에 Scope 실패 이유 모함

생성 금지:
- Registry 대규모 구축
- 산안법 전체 업종 코드화
- 동시에 법령 확장

---

**질문 4. Phase 3 성공 기준**

**SC-01: 화성 제2공장 (C28, 280명)**
```
MATCH        = 1건 ("제1호~27호 외의 사업" 만)
NOT_APPLICABLE = 3건 (토사석/식료품/운수창고 — Scope 블록)
verdict = REQUIRED 1명 (기존과 동일)
```

**SC-02: 토사석 광업 (B071, 60명)**
```
토사석 광업 조건  → MATCH
일반 조항      → NOT_APPLICABLE (B071은 1호~27호 해당)
verdict = REQUIRED 1명
```

**SC-03: 빈 사업장 (null명)**
```
전체 7건 UNKNOWN
verdict = UNKNOWN
```

**SC-04: Scope 확장 가능성 검증**
```
지금은 INDUSTRY Scope만 실제 데이터 있음.
PROCESS/ACTIVITY/EQUIP는 scope_type에 코드가 있지만
실제 데이터는 Phase 0B에서 수집합니다.

판정 기준:
  구조에 scope_type이 존재하는가? (yes)
  scope_type = INDUSTRY일 때 평가 정상 작동하는가? (yes)
  후에 scope_type = PROCESS로 바꿳서도 구조가 유지되는가? (yes)
```

---

**질문 5. INDUSTRY Scope 파일럿 용 KSIC 코드**

파일럿 7건에 필요한 최소한의 KSIC 코드만 확정해주세요.

전체 등재 화 금지. 산안법 시행령 별표3 제1호~27호 전체 코드화 금지.

현재 파일럿에서 필요한 것만:
```
"토사석 광업(071)"
  scope_type = INDUSTRY
  scope_values = ["B071"]
  is_general = false

"식료품 제조업, 음료 제조업 등 고위험 제조업군"
  scope_type = INDUSTRY
  scope_values = [법령 원문에서 정의된 KSIC 코드만]
  is_general = false

"운수 및 창고업(49~52)"
  scope_type = INDUSTRY
  scope_values = ["H49", "H50", "H51", "H52"]
  is_general = false

"제1호~27호 외의 사업"
  scope_type = INDUSTRY
  scope_values = null
  is_general = true
```

"식료품 제조업" KSIC 코드 정확한 정의는 GPT가 판정해주세요.
산안법 시행령 별표3 제1호~17호 업종에서 대분류 코드만 (C10, C11 수준).

---

## 절대 금지 (범위 고정)

```
Phase 3 범위 밖:
  산안법 전체 업종 코드화
  용접/굴십/밀혗공간 등 확장
  obligation_result 생성
  diagnosis_result 생성
  Registry 대규모 구축
  FacilityProfile 수정
  factories 수정
  pilot_safety_manager_api 삭제
  industry_name 텍스트 런타임 해석 (B 방식)
```

GPT는 WO 설계 문서 수준으로 답변해주세요.

---

## 참고 문서

- Phase 2 WO: `docs/2026-06-17_WO_V4_PHASE2_001.md`
- Phase 0A: `docs/2026-06-16_WO_V4_PHASE0_001.md`
- 기획서: `docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md` (v2.1)
