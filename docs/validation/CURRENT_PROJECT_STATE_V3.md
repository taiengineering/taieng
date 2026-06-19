# CURRENT PROJECT STATE V3
# WO-PROJECT-REBASE-V3

**작성일**: 2026-06-19
**성격**: 전체 재정렬. 새 탐색/구현/버그추적 없음. 완료된 WO 결과만 사용.
**대체**: CURRENT_PROJECT_STATE_V2 (이 문서가 최신 기준)

---

## 한 페이지 요약

```
Track A (등록 사업장 진단 체인) = 사실상 완료.
  법령수집→의미절→Applicability→V4→Adapter→Storage→Transform 전부 DONE.
  검증된 법령 의무가 사용자 결과 데이터로 흐르는 체인이 완성됨.

남은 것은 "다음 버그"가 아니라 "다음 우선순위 선택"이다.
  - Authorization: 별도 이슈(AUTH-001), 데이터 흐름과 무관
  - Construction/Building: BLOCKED/미착수 (원문 데이터 의존)
```

---

## 4단계 분류표

| # | 항목 | 상태 | 근거 |
|---|---|---|---|
| 1 | Track A (등록사업장 체인) | **DONE** | V4→Adapter→Storage→Transform 데이터흐름 PASS |
| 2 | V4 엔진 | **DONE** | §8 8/8, INDUSTRIAL MUST 100% |
| 3 | Obligation (어댑터) | **DONE** | MUST 8건 obligations 변환·저장·추출 검증 |
| 4 | Golden Case | **DONE** | HS2 v1.0 (화성 제2공장) |
| 5 | Decision Chain | **DONE** | PROJECT_DECISION_CHAIN_V1 |
| 6 | Governance Documents | **DONE** | Decision Chain + Policy(가상현실엔진) |
| 7 | Virtual Reality Engine | **DONE (도구)** | 1000개 시뮬, 로드맵 변경권 없음(Policy) |
| 8 | Authorization | **ACTIVE (별도 AUTH-001)** | created_by null, company_id 기반 권한 미정 |
| 9 | Construction (Phase5) | **BLOCKED** | 별표3 건설업란 원문 부재 (주차) |
| 10 | Building | **PARKING** | 별도 법령군 Appendix 미수집 (미착수) |

---

## DONE (완료, 더 건드리지 않음)

```
법령 수집            DONE
의미절 분해          DONE
Applicability        DONE
V4 검증              DONE (§8 8/8)
Golden Case          DONE (HS2 화성)
Adapter              DONE
Storage              DONE (factory_diagnosis_results)
Transform            DONE (컬럼버그 v1.0.2 수정)
Decision Chain       DONE
Governance Docs      DONE
Virtual Reality Eng  DONE (검증 도구)

→ Track A 데이터 흐름 = 완성.
  "검증된 법령 의무 8건이 사용자 결과 데이터로 흐른다" 달성.
```

## ACTIVE (실제 진행 가능, BLOCKED 제외)

```
AUTH-001 — 회사 소유 권한 모델 (company_id 기반)
  : transform 권한을 company_id로. 데이터 흐름과 분리됨.
  : 착수 = 사장님 지시 시.

(잠재) INDUSTRIAL 의무 확장 — P2
  : 보건관리자/안전보건관리담당자 등.
  : 기존 V4 구조 재사용 가능, 새 의무별 Golden Case 필요.

→ BLOCKED 제외 실제 ACTIVE = 2개 (AUTH-001, INDUSTRIAL 확장).
  단 둘 다 "지금 당장 필수"는 아님 — Track A가 이미 동작하므로.
```

## BLOCKED (주차, 재탐색 금지)

```
Construction (Phase5)
  : 별표3 건설업란 원문(공사금액 구간표) DB 부재
  : 해제조건 = 원문 확보 / 신규 데이터 / 사장님 지시
```

## PARKING (미착수, 의도적 보류)

```
Building
  : 소방/승강기/에너지 별도 법령군 Appendix 미수집
  : Construction과 동일한 원문 확보 리스크

익명 진단 트랙 (Track B)
  : site_kind→V4 입력 변환 레이어 필요, 별도 Phase
  : 현재 Track A에 집중

실 배포 HTTP 최종 확인
  : AUTH-001 확정 후 그 권한으로 호출하면 종결
  : 데이터 흐름은 이미 검증됨
```

---

## 필수 질문 답변

### Q1. 현재 실제 사용자 가치가 발생하는 기능은?
```
- Track A 등록 사업장 진단: V4가 INDUSTRIAL 사업장의 법적 의무를
  정확히(§8 8/8) 판정하고, 사용자 결과 데이터(obligations)로 변환.
- 기존 운영 기능: Track A 현행 엔진(diagnosis), 익명 무료진단(Track B),
  work_order 운영(runtime_obligation 20,129건) — 이미 운영 중.

→ 신규로 더해진 가치: V4 검증 엔진의 정확한 의무 판정이
  사용자 결과 데이터 경로에 연결됨 (이번 일련의 WO 성과).
```

### Q2. 다음 30일 가장 성공확률 높은 작업은?
```
후보 비교 (BLOCKED 제외):
  A. AUTH-001 (회사 권한 모델)
     — 작음, Track A 실사용 위해 필요, 성공확률 높음
  B. INDUSTRIAL 의무 확장 (P2)
     — 중간, 새 Golden Case 선행, 커버 확대
  C. 실 배포 HTTP 검증
     — AUTH-001 의존

추천: A (AUTH-001) 먼저.
  이유: Track A가 데이터상 완성됐으므로, 실사용 전환의
  유일한 실질 장애물이 권한임. 작고 성공확률 높음.
  단 "권한 모델 정교화"가 아니라 "company_id 1줄 연결"로 최소화.
```

### Q3. 지금 즉시 멈춰야 할 루프는?
```
"발견 → 추적 → 발견 → 추적" 루프.
  USER_VISIBLE / persist / transform / created_by 주변을
  계속 돌고 있었음.

멈추는 법:
  Track A를 DONE으로 확정 (이 문서).
  남은 건 버그가 아니라 "우선순위 선택"임을 인정.
  새 추적 WO 대신 우선순위 결정 WO로 전환.
```

### Q4. BLOCKED 제외 실제 ACTIVE는 몇 개?
```
2개:
  1. AUTH-001 (회사 권한 모델) — 작음
  2. INDUSTRIAL 의무 확장 — 중간

그 외는 전부 DONE 또는 PARKING/BLOCKED.
→ 프로젝트는 "수렴" 상태. 할 일이 적게 남음 = 좋은 신호.
```

---

## 재정렬의 핵심 메시지

```
작업 로그는 "모든 게 진행 중"처럼 보이지만,
실제 상태는:

  Track A = 거의 완료
  Construction = BLOCKED (주차)
  Authorization = 별도 이슈 (작음)
  Building/익명 = PARKING

다음은 "탐구 재개"가 아니라 "우선순위 1개 선택"이다.
AUTH-001을 작게 끝내거나, INDUSTRIAL 확장으로 가거나,
아니면 여기서 Track A를 출시 가능 상태로 선언하거나.

이 셋 다 "새 루프"가 아니다. 수렴된 선택지다.
```

---

## 다음 WO 후보 (사장님 선택, 새 탐색 아님)

```
1. WO-AUTH-001-IMPL: company_id 기반 권한 1줄 연결 + 실 HTTP 검증
   → Track A 실사용 전환 완료
2. WO-INDUSTRIAL-EXPAND: 보건관리자 등 의무 확장 (Golden Case 선행)
   → 커버 의무 증가
3. (선언) Track A DONE 확정 → 출시/영업 단계로 전환
```
