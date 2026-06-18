# WO-GOLDEN-CASE-PRIORITY-001

**작성일**: 2026-06-17  
**상태**: ✅ 사장님 승인 완료  

---

## 승인 내용

현재 모든 구현 및 연결 논의를 중단한다.

**중단 대상:**
```
Boolean 연결
Equipment Scope 연결
Process Scope 연결
Phase 0B 착수
Phase 5 착수
Obligation 생성
Track A 수정
```

**이유:**
기획서 §8의 정답지(Golden Case) 구축이 아직 완료되지 않았다.  
현재 단계의 목표는 엔진 개선이 아니라 **정답 기준 확정**이다.

---

## 현재 위치

```
§8 GOLDEN CASE 구축 단계
```

---

## 실행 순서

```
1. GOLDEN_CASE_HS2 v1.0 확정
   (MUST / MUST_NOT 사장님 글읽기 후 확정)

2. Track A 114건 × v1.0 비교
   → True Positive
   → False Positive
   → Unknown

3. V4 결과 × v1.0 비교
   → 동일 기준으로 측정

4. 실제 누락 원인 분석
   (어디서 틀렸는가, 왜 틀렸는가)

5. 그 이후에만:
   Boolean 연결
   Equipment 연결
   Process 연결
   의 우선순위를 결정
```

---

## 절대 금지 (승인 즉시 발효)

```
정답지 없는 상태에서의 엔진 수정 논의
Boolean/Equipment/Process 연결 착수
Phase 5 / Phase 0B 착수
Obligation 생성
Track A 수정
```

---

## 비고

GOLDEN_CASE_HS2 v0.2는 초안 상태.  
MUST 7건의 과소/과대 여부는 글읽기 단계에서 조정.  
v1.0 확정 전까지 정답지 기반 비교 실행 보류.
