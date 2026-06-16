# GPT 질의 — Phase 1 WO 설계 요청

**작성일**: 2026-06-16  
**용도**: 다음 세션 시작 전 GPT에게 전달

---

## 배경

15차 세션 종료 기준:
- D-001~007 완료
- Appendix 수집 완료
- Actor Resolution Overlay 완료
- Domain Filter 완료
- Phase 0A Schema Freeze 사장님 승인 완료

15차의 가장 중요한 결론은 정확도 문제가 아니라 **입력 정보 손실 문제**였습니다.

실측 결과:
- Track A는 사업장 입력을 factories row로 평탄화
- 일부 값은 중간 레이어에서 소실
- 미입력과 0값이 혼재
- 나중에 "사용자가 실제 무엇을 입력했는가"를 재현하기 어려움

**Phase 1 목표는 아래 한 가지뿐입니다:**

> 소비자 입력을 FacilityProfile 형태로 손실 없이 보관한다.

정확도 개선은 범위 밖입니다.

---

## 질문 1. FacilityProfile 필수/선택 필드 구분

FacilityProfile v1.0 생성 시 필수 필드와 선택 필드를 구분해주세요.

현재 확정된 골격:
- building
- workforce
- processes
- equipment
- materials
- activities
- metrics
- provenance

이 중 Phase 1에서 반드시 구현해야 하는 것과 Phase 2 이후로 미뤄도 되는 것을 구분해주세요.

---

## 질문 2. FacilityProfile 저장 전략

FacilityProfile 저장 전략을 제안해주세요.

후보:
- A. JSON 단일 객체 저장
- B. profile + child table 구조
- C. 둘 다 (JSON snapshot + 정규화)

판정 기준:
- 소비자 입력 재현 가능성
- 디버깅 용이성
- 향후 Registry 연동 용이성

---

## 질문 3. TriValue / TriList 구현 범위

TriValue / TriList 구현 범위를 확정해주세요.

```
TriValue:
  PRESENT
  ABSENT
  UNKNOWN

TriList:
  confirmed
  denied
  unknown_rest
```

모든 필드에 적용할지, 일부 필드만 적용할지, Phase 1 최소 구현 범위를 알려주세요.

---

## 질문 4. Phase 1 성공 기준

Phase 1 성공 기준을 정의해주세요.  
Claude가 구현 후 검증 가능한 형태로 작성 바랍니다.

예시:
- 입력 → FacilityProfile → 저장 → 재로드 → deep equal
- 입력 손실률 0%
- UNKNOWN 유지
- provenance 유지

위와 같은 형태로 정량 기준을 제시해주세요.

---

## 중요 — 범위 고정

**Phase 1은 새로운 법령엔진 구현 단계가 아닙니다.**

목표:
- 입력 보존
- 입력 재현
- 입력 추적

금지:
- Check Engine 수정
- Registry 구현
- ApplicabilityCondition 구현
- 정확도 개선 작업
- Rule 개선 작업

**Phase 1은 오직 FacilityProfile 생성·보관·재현만 다룹니다.**

GPT는 구현 코드가 아니라 WO 설계 문서 수준으로 답변해주세요.

---

## 참고 문서

- Phase 0A 확정: `docs/2026-06-16_WO_V4_PHASE0_001.md`
- 15차 핸드오프: `docs/2026-06-16_SESSION_HANDOFF_15F.md`
- 기획서: `docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md` (v2.1)
