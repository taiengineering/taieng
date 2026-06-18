# CONSTRUCTION RULE SOURCE REPORT V1
# WO-V4-PHASE5-PRECHECK-001

**작성일**: 2026-06-18  
**성격**: 원문 확인 전용. 구현/추정 금지.  
**목적**: CONSTRUCTION 안전관리자 선임 기준을 원문으로 확인 가능한지 YES/NO 판정

---

## 완료 조건 답변

```
Q: 건설업 안전관리자 기준을 원문 기준으로 재현 가능한가?
A: 현재 NO — DB에 원문이 없음
```

---

## 확인 결과

### 1. appendix_condition (구조화된 조건)
```
INDUSTRIAL 7건만 존재 (안전관리자 선임)
  토사석광업, 고위험제조업군, 운수창고업, 일반사업
건설업 조항: 없음
```

### 2. law_article (조문 원문)
```
제16조 "안전관리자의 선임 등"
  → "별표 3과 같다"로 참조만 함
  → 구체적 공사금액 구간은 별표3에 있음

제59조 "기술지도계약":
  공사금액 1억~120억 (토목 150억) — 이건 기술지도 기준이지
  안전관리자 선임 기준이 아님 (혼동 주의)
```

### 3. law_appendix (별표 원문)
```
별표 3 "안전관리자를 두어야 하는 사업의 종류·규모..."
  레코드 존재 ✅
  appendix_text = NULL ❌
  → 제목만 수집, 본문 비어있음
```

---

## 핵심 발견

```
WO-APPENDIX-COLLECT-001에서 별표3 INDUSTRIAL 부분은
 appendix_condition으로 구조화됨 (7건)

그러나 건설업 부분은:
  - appendix_condition에 없음
  - law_appendix.appendix_text가 NULL
  → 건설업 공사금액 구간 원문이 DB에 존재하지 않음
```

---

## 구조 표현 가능성 (원문 확보 시)

건설업 안전관리자가 공사금액 기반이라면 V4 구조로 표현 가능:
```
scope_type = SECTOR, scope_values = ['CONSTRUCTION']
metric = METRIC:CONSTRUCTION_AMOUNT
operator = >=, threshold = (원문 구간)
```
→ 새 Scope 체계 불필요, 기존 구조로 수용 가능  
→ **단, threshold 값은 원문 없이 확정 불가**

---

## 사장님 확인 요청

```
건설업 안전관리자 공사금액 구간 원문이 DB에 없습니다.
추정 금지 원칙에 따라 멈춤습니다.

원문 확보 방법 선택:
  A. 국가법령정보센터 API로 별표3 재수집 (law_appendix.appendix_text 채우기)
  B. 사장님이 직접 원문 제공
  C. 기존 수집 경로(WO-APPENDIX-COLLECT) 재실행
```

---

## 결론

```
Phase 5 착수 조건: 미충족
  이유: 건설업 공사금액 구간 원문 부재

다음 단계:
  ApplicabilityCondition 설계 아님
  → 먼저 별표3 건설업 원문 확보
  → 구간 확정
  → 그 다음에 설계
```
