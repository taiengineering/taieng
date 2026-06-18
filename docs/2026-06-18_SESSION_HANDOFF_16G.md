# 세션 핸드오프 — 16G (§8 케이스 매트릭스 8/8 완료)

**작성일**: 2026-06-18

---

## §8 검증 체계 완성 — 케이스 매트릭스 8/8

| # | 케이스 | factory_id | 결과 | 분류 |
|---|---|---|---|---|
| 1 | 화성 제2공장 C28 280명 | e9c56af6 | MUST 8/8 MATCH | ✅ OK |
| 2 | C28 49명 | 462a8026 | 안전관리자/경보설비 NOT_MATCH, 일반의무 6 MATCH | ✅ OK |
| 3 | C28 50명 | 3dc479c7 | MUST 8/8 MATCH (경계값) | ✅ OK |
| 4 | 건설 49억 | 36fe88bd | 전체 UNKNOWN (Scope) | ✅ NO_RELEVANT_CONDITION |
| 5 | 건설 50억 | 0e06a34c | 전체 UNKNOWN (Scope) | ✅ NO_RELEVANT_CONDITION |
| 6 | 빈 입력 (C3000 null명) | b3ef791c | UNKNOWN (수치비교불가) | ✅ OK — null 보존 정확 |
| 7 | 전부 채운 입력 | =케이스 #1로 간주 | MUST 8/8 | ✅ OK |
| 8 | 건물 업무시설 100명 | d9857501 | 전체 UNKNOWN (Scope) | ✅ NO_RELEVANT_CONDITION |

---

## 핵심 발견: UNKNOWN 세 가지 유형 구분됨

```
유형 A — SCOPE UNKNOWN:
  건설/건물 (ksic_code=null)
  scope_result = UNKNOWN
  이유: INDUSTRY Scope 평가 불가

유형 B — METRIC UNKNOWN:
  빈 입력 (근로자수 null)
  scope_result = SCOPE_MATCH, evaluation = UNKNOWN
  이유: regular_workers.state=UNKNOWN 수치비교불가

유형 C — NOT_APPLICABLE:
  업종 범위 외 (C28이 고위험군 아님)
  scope_result = NOT_APPLICABLE
```

Phase 1 FacilityProfile null 보존 설계가 정확히 작동.

---

## §8 최종 측정값

```
Track A False Positive: 93% (화성 제2공장 114건 중 106건)
  원인: SUBJECT_UNRESOLVED actor 미분류

V4 MUST 커버율: 100% (WO-01 후)
  이전: 12.5% → 현재: 8/8
  C1 코드 수정: 0줄

V4 INDUSTRIAL 정확도:
  49명/50명 경계값 정확 처리
  null 입력 정확 처리
  업종 범위 외 정확 처리

V4 미구현 범위 (정상):
  CONSTRUCTION 전용 조건
  BUILDING 전용 조건
```

---

## 현재 applicability_conditions: 14건

```
안전관리자 선임: 7건 (업종군별)
일반 INDUSTRIAL 의무: 7건 (M-02~M-08)
```

---

## 다음 단계 (GPT 판단 요청)

```
§8 검증 체계 8/8 완료.
두 수치 확정:
  Track A 93% False Positive
  V4 100% MUST 커버 (INDUSTRIAL 한정)

GPT에게 다음 우선순위 판단 요청:
  A. CONSTRUCTION ApplicabilityCondition 확장
  B. BUILDING ApplicabilityCondition 확장
  C. Track A 93% 오염 수정
  D. Obligation 생성 (소비자 표시)
  E. Boolean/Equipment 연결
```

---

## 테스트 사업장 (P4_ 접두사, is_active=false)

```
e9c56af6 화성제2공장 (영구)
462a8026 P4_MFG49 (49명)
3dc479c7 P4_MFG50 (50명)
36fe88bd P4_CON49 (건설49억)
0e06a34c P4_CON50 (건설50억)
b3ef791c 인천공장 (빈입력)
d9857501 P4_BLD (건물100명)
P4_I01~I10, P4_C01, P4_B01 등
```

## 절대 금지 (유효)

```
Track A 수정 (GPT 판단 전)
GPT 전속 테이블 수정
CONSTRUCTION/BUILDING Scope 무단 구현
Boolean/Equipment 연결 (GPT 판단 전)
Obligation 생성 (GPT 판단 전)
```
