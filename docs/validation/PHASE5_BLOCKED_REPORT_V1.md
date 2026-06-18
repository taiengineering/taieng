# PHASE5 BLOCKED REPORT V1
# WO-BLOCK-MANAGEMENT-001

**작성일**: 2026-06-18  
**성격**: 상태 등록. 루프 중단. Construction 해결 아님.

---

## 핵심 문장

```
Phase 5 Construction은 현재 BLOCKED 상태이며,
추가 원문 추적 없이 다음 우선순위 재선정을 요청한다.
```

---

## Phase 5 상태 등록

```
Phase 5: CONSTRUCTION 안전관리자 확장
상태: BLOCKED
원인: 건설업 안전관리자 기준 구조화 불확정
근거:
  WO-V4-PHASE5-PRECHECK-001
  WO-CONSTRUCTION-CONSTRAINT-TRACE-001
  WO-PHASE5-CHARACTERIZATION-001
  WO-APPENDIX3-CONSTRUCTION-LOCATE-001
```

**이것은 "구현 실패"가 아니다. 정확한 상태는 BLOCKED다.**

---

## 왜 Block 되었는가

```
건설업 안전관리자 선임 기준이:
  의미 레이어(law_article_part, semantic_clause) ✅ 존재
  실행 레이어(constraint/rule/condition) ❌ 미도달

DB 내 수치가 상충:
  appendix_runtime_metadata 레코드 1: 건설업 50억
  appendix_runtime_metadata 레코드 2: 건설업 120억
  → 둘 다 요약, 별표3 본문 구간표 아님

120억의 의미:
  제17조제3항 "전담 안전관리자" 경계
  ≠ "선임 의무 발생" 최소 기준
```

---

## 어떤 정보가 부족한가

```
미확정:
  건설업 안전관리자 "선임 의무 발생" 최소 공사금액
  건설업 선임 인원 구간 (몇 명)
  전담/공동선임 구조

필요한 것:
  별표3 건설업란 원문(구간표) — 현재 DB 부재
```

---

## 현재 프로젝트 전체 위치

```
✅ 확정 (검증 완료):
  INDUSTRIAL 안전관리자 + 일반의무 8건 — MUST 커버 100%
  V4 정확도 (49/50명 경계, null, 업종범위 외) — 정확
  §8 검증 체계 — 케이스 8/8 완료
  Track A False Positive 93% — 측정 (표본 1)
  Coverage Gap — CONSTRUCTION 0%, BUILDING 0% 확인

⚠️ 미확정:
  건설업 안전관리자 선임 구간
  건설업 인원 구간
  전담/공동선임 구조

⛛️ BLOCKED:
  Phase 5 CONSTRUCTION 안전관리자 확장
```

---

## Block 해제 조건

```
다음 중 하나가 충족되면 Block 해제:

1. 별표3 건설업란 원문(구간표) 확보
   (국가법령정보센터 또는 사장님 공식 제공)

2. 건설업 안전관리자 선임 기준을
   신뢰할 수 있는 단일 출처로 확정

3. 충돌하는 50억/120억 중 어느 것이
   선임 기준인지 원문으로 확정
```

---

## 다음 우선순위 후보 (재선정 요청)

Construction이 BLOCKED이므로, 다음 중 선택:

```
후보 1: Obligation Layer
  V4 INDUSTRIAL 결과(MUST 8건)를 소비자에게
  문장으로 표시. 이미 검증된 영역이라 즉시 가능.
  → Block 없음, 가치 즉시 발생

후보 2: BUILDING Coverage
  법령 모집단 175 (최대). 단 별도 법령군
  (소방/승강기/에너지) Appendix 수집 필요.
  → Construction과 동일한 원문 확보 문제 재발 가능성

후보 3: INDUSTRIAL 심화
  보건관리자, 안전보건관리담당자 등
  이미 검증된 INDUSTRIAL 에서 의무 확장.
  → Block 없음, 기존 구조 재사용

후보 4: 건설업 원문 확보 (Block 해제)
  별표3 건설업란 원문을 사장님이 제공하거나
  공식 출처 확보 → Construction 재개
```

---

## 중단한 것 (재탐색 금지)

```
별표3 재탐색 ❌
appendix 재탐색 ❌
metadata 재탐색 ❌
law_attachment 재탐색 ❌
threshold 추정 ❌
50억/120억 논쟁 반복 ❌
```

---

## 결론

```
Phase 5 Construction = BLOCKED 공식 등록 완료.
루프 중단.

추가 원문 추적 없이
다음 우선순위 재선정을 요청한다.

권장: 후보 1 (Obligation) 또는 후보 3 (INDUSTRIAL 심화)
  — 둘 다 Block 없고 즉시 가치 발생
```
