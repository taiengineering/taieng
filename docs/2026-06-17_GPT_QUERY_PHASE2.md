# GPT 질의 — Phase 2 WO 설계 요청

**작성일**: 2026-06-17  
**용도**: 16차 Phase 1 완료 후 GPT엔게 전달

---

## 한 문장 요약

> Phase 2는 FacilityProfile과 법령 별표 조건을 비교하여 ApplicabilityCondition을 생성하는 작업이다. 산안법 안전관리자 선임 의무를 파일럿로 먼저 한다.

---

## Phase 1 완료 상태

**구현 완료:**
- `facility_profiles` 테이블 — TriValue + Provenance + profile_snapshot JSON
- SC-01~05 전부 PASS (입력 손실 0%, UNKNOWN 보존, round trip 100%)
- factories = Source of Record 유지, FacilityProfile = Projection Layer 확인

**FacilityProfile 현재 구조 (실측):**
```json
{
  "sector": "INDUSTRIAL",
  "ksic_code": "C28",
  "workforce": {
    "regular_workers": { "state": "PRESENT", "value": 280, "provenance": "INPUT" }
  },
  "building": {
    "floor_area": { "state": "PRESENT", "value": 12500, "provenance": "INPUT" }
  },
  "metrics": {
    "construction_amount": { "state": "UNKNOWN", "value": null, "provenance": "INPUT" },
    "electrical_kw": { "state": "PRESENT", "value": 1400, "provenance": "INPUT" }
  },
  "provenance": {
    "input_fields": ["sector", "ksic_code", "workforce.regular_workers", "..."],
    "inferred_fields": [],
    "default_fields": []
  }
}
```

---

## 현재 appendix_condition 실측 (7건)

산안법 시행령 별표 3 — 안전관리자 선임기준:

| 업종 | threshold | 안전관리자 수 |
|---|---|---|
| 식료품·음료 등 고위험 제조업군 | ≥50명 | 1명 |
| 식료품·음료 등 고위험 제조업군 | ≥500명 | 2명 |
| 운수 및 창고업(49~52) | ≥50명 | 1명 |
| 운수 및 창고업(49~52) | ≥500명 | 2명 |
| 토사석 광업(071) | ≥50명 | 1명 |
| 제1호~27호 외의 사업 (일반) | ≥50명 | 1명 |
| 제1호~27호 외의 사업 (일반) | ≥1000명 | 2명 |

**현재 pilot_safety_manager_api.py:**
- appendix_condition 7건과 FacilityProfile 없이 직접 factories를 참조
- `verdict: REQUIRED, required_count: 1` 정상 작동 중
- Phase 2엔서 이것을 ApplicabilityCondition 체계로 대체 예정

---

## Phase 2 목표

```
appendix_condition(별표 조건) + FacilityProfile → ApplicabilityCondition 생성

FacilityProfile.workforce.regular_workers (TriValue)
  vs
appendix_condition.threshold_value + threshold_operator

→ APPLICABLE / NOT_APPLICABLE / UNKNOWN
```

---

## 질문 1. ApplicabilityCondition 생성 주체

현재 `appendix_condition` 7건은 수동 수집 데이터입니다. 이것을 ApplicabilityCondition으로 변환하는 작업이 어느 레이어(B4~B6 중 어디)인지 판정해주세요.

특히:
- appendix_condition 1건 = ApplicabilityCondition 1건인가, 아니면 다른 매핑이 필요한가
- `raw_condition` 텍스트에서 subject_raw를 어떻게 추출하는가
  - 예: "제1호~27호 외의 사업 50명 이상 999명 미만"에서 subject_raw = "상시근로자"

---

## 질문 2. FacilityProfile × ApplicabilityCondition 대조 방법

Phase 0A에서 확정된 C1 대조기 규칙:
```
actor ≠ OWNER → 즉시 NOT
TriValue UNKNOWN → 판단 보류 (UNKNOWN 반환)
```

안전관리자 선임 의무의 경우:
- `METRIC:EMPLOYEE_COUNT` vs `FacilityProfile.workforce.regular_workers`
- regular_workers.state = UNKNOWN이면 → APPLICABLE / NOT_APPLICABLE / UNKNOWN 중 무엇인가

판정 기준을 알려주세요.

---

## 질문 3. Phase 2 산출물 정의

Phase 2에서 생성해야 하는 것과 생성 금지 목록을 확정해주세요.

후보 산출물:
- `applicability_conditions` 테이블 (DB)
- appendix_condition → ApplicabilityCondition 변환 서비스
- FacilityProfile × ApplicabilityCondition 대조기 (C1 초안)
- 대조 결과 저장 테이블

---

## 질문 4. pilot_safety_manager_api 처리

현재 `pilot_safety_manager_api.py`는 TEMPORARY 자산입니다. Phase 2 완료 후:
- 삭제해야 하는가
- 유지하되 deprecated 표시만 하는가
- ApplicabilityCondition 체계로 내부 로직을 교체하는가

---

## 질문 5. Phase 2 성공 기준

화성 제2공장 (INDUSTRIAL, C28, 280명) 기준:
- ApplicabilityCondition 생성 결과
- FacilityProfile × ApplicabilityCondition 대조 결과
- pilot_safety_manager_api와 결과 일치 여부

Claude가 구현 후 검증 가능한 형태로 작성 바랍니다.

---

## 절대 금지 (범위 고정)

```
Phase 2 범위 박:
  Registry 완성 (EQUIP/PROC/MAT/ACT — Phase 0B)
  FacilityProfile 수정
  factories 수정
  Track A 수정
  전체 법령 적용 (산안법 안전관리자 파일럿만)
```

GPT는 WO 설계 문서 수준으로 답변해주세요.

---

## 참고 문서

- Phase 0A 확정: `docs/2026-06-16_WO_V4_PHASE0_001.md`
- Phase 1 WO: `docs/2026-06-17_WO_V4_PHASE1_001.md`
- 16차 핸드오프: `docs/2026-06-17_SESSION_HANDOFF_16A.md`
- 기획서: `docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md` (v2.1)
