# TAI 법령엔진 검증 마스터플랜 V1
# MASTER VALIDATION PLAN V1

**작성일**: 2026-06-20
**성격**: 상위 검증계획서. 이후 모든 WO는 본 계획서의 하위 작업으로만 생성한다.
**구속력**: 중간에 새 탐구가 나와도 본 계획서 밖으로 나가지 않는다.

---

## 목적

```
법령엔진의 품질을 검증한다.
```

## 원칙

```
- 조사와 검증을 분리한다.
- 검증 없이 개선하지 않는다.
- 원인분석은 이상패턴 수집 이후 수행한다.
- 모든 검증은 체크리스트 기반으로 진행한다.
- WO는 본 계획서의 하위 작업으로만 생성한다.
```

---

## PHASE 0. 기준선 고정 — ✅ 완료

```
목적: 현재 상태를 기준선(Baseline)으로 고정한다.

산출물 (고정 버전):
  FacilityProfile v2         (commit 09d13b4)
  VR Generation Spec v2      (commit c78040b)
  VR Variation Generator v1  (commit 06307244, sha 7a5848a)

성공조건: 기준선 버전 고정 / 이후 모든 테스트는 동일 기준선 사용.
완료상태: 완료.
```

---

## PHASE 1. Input Integrity — ✅ 완료

```
질문: 사용자 입력과 VR 입력은 동일 계약으로 엔진에 들어가는가?
검증대상: 사용자 입력 / VR 생성 데이터 / FacilityProfile
검증방법:
  사용자 입력 → FacilityProfile
  VR 입력 → FacilityProfile
  비교.
성공조건: 입력계약 동일.
산출물: INPUT_INTEGRITY_REPORT
  (관련: INPUT_CONTRACT_REALITY_CHECK_V1, UI_FIELD_INVENTORY_V1,
   FACILITYPROFILE_FIELD_INVENTORY_V1, INPUT_VR_ENGINE_TRIANGLE_V1)
상태: 완료.
```

---

## PHASE 2. Coverage Integrity — ✅ 완료

```
질문: 입력공간 전체가 생성 가능한가?
검증대상: 57차원 입력
검증방법: 1,000개 생성
측정: 필드 존재 / UNKNOWN / NULL / PRESENT
성공조건: 57차원 전부 생성.
산출물: COVERAGE_REPORT
  (관련: VR_57D_SMOKE_TEST_REPORT_V1 — 3샘플 57차원 무손실 적재)
상태: 완료.
```

---

## PHASE 3. Variation Integrity — ✅ 완료

```
질문: 템플릿 반복인가?
검증대상: 57차원 생성기
검증방법: 1,000개 생성
측정: Distinct / 중복률 / 조합수
성공조건: 중복률 1% 이하 / Boolean 커버 / 조합 다양성 확보.
산출물: VARIATION_REPORT
  (관련: VR_DIVERSITY_AUDIT_REPORT_V1, VR_VARIATION_GENERATOR_REPORT_V1,
   VR_VARIATION_GENERATOR_CLOSEOUT_REPORT_V1)
  결과: 중복률 0% / boolean 20/20 커버 / distinct>10 필드 22개.
상태: 완료.
```

---

## PHASE 4. Result Diversity — ⬜ 미착수 (현재 다음 단계)

```
질문: 입력이 달라지면 결과도 달라지는가?
목적: 결과 공간의 크기를 측정한다.
검증방법:
  5,000~10,000개 생성
  엔진 실행
  결과 Fingerprint 생성
    예: 적용법령 집합 / 의무 집합 / 진단결과 집합
측정: 결과 패턴 수 / 패턴 빈도 / Top N 패턴
금지: 원인분석 / 버그판정
성공조건: 결과 공간 구조 파악.
산출물: RESULT_DIVERSITY_REPORT
상태: 미착수.
다음 WO: WO-RESULT-DIVERSITY-001
```

---

## PHASE 5. Reading Review — ⬜ 미착수

```
질문: 사람이 읽었을 때 이상한 결과가 존재하는가?
목적: 문제 발견.
입력: PHASE 4 결과
검증방법: 대표 패턴 추출 → 진단서 출력 → 사람 독해
수집대상:
  PATTERN-A 경계값 점프
  PATTERN-B 중복 의무
  PATTERN-C 설명 불가 공백
  PATTERN-D 업종 역전
  PATTERN-E 상식 역행
  PATTERN-F 표현 오류
금지: 수정 / 코드변경 / 원인분석
성공조건: 이상패턴 수집.
산출물: READING_REVIEW_REPORT
상태: 미착수.
```

---

## PHASE 6. Root Cause Analysis — ⬜ 미착수

```
진입조건: PHASE 5 완료
질문: 왜 발생하는가?
목적: 원인 식별.
허용: 조건 분석 / 입력 분석 / 엔진 분석
산출물: ROOT_CAUSE_REPORT
상태: 미착수.
```

---

## PHASE 7. Remediation — ⬜ 미착수

```
진입조건: ROOT_CAUSE_REPORT 승인
목적: 수정.
산출물: FIX_PLAN
상태: 미착수.
```

---

## 현재 위치 / 다음 작업

```
현재 위치: PHASE 3 완료
다음 단계: PHASE 4
다음 WO: WO-RESULT-DIVERSITY-001
  목표: 결과 공간 크기 측정
  금지: 독해 / 버그판정 / 수정 / 원인분석
```

---

## 진행 규칙 (구속)

```
이제부터 "무엇을 할까?"가 아니라
  현재 위치 → 다음 단계 → 다음 WO
로만 움직인다.

입력부 조사 / VR 조사 / FacilityProfile 조사 같은
이미 완료된(PHASE 0~3) 영역으로 되돌아가지 않는다.

PHASE는 순서대로만 진입한다 (4→5→6→7).
원인분석(PHASE 6)은 이상패턴 수집(PHASE 5) 이후에만.
수정(PHASE 7)은 원인보고 승인 이후에만.
```
