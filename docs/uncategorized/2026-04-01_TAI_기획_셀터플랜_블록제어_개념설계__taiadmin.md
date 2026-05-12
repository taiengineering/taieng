# TAI Safe 섹터 × 플랜 블록 제어 개념 설계

> 작성일: 2026-04-01  
> 구분: 기획서

---

## 1. 핵심 콘셀트

**틀은 하나, 블록을 셀터+플랜으로 열거나 잠근다.**

```
입력값 2개:
  sector    = INDUSTRY / BUILDING / CONSTRUCTION / SPECIAL
  plan_code = STARTER(1) / BUSINESS(2) / ENTERPRISE(3) / CUSTOM(4)

제어 결과 3가지:
  open   = 세터 일치 + 플랜 충족 → 정상 표시
  locked = 셀터 일치 + 플랜 부족 → 잠김 UI
  hidden = 셀터 불일치       → 완전 숨김
```

---

## 2. 사업장 셀터 정의

| 코드 | 대상 | 예시 |
|------|------|------|
| INDUSTRY | 제조업, 공장, 물류센터 | 공장, 창고, 운수업 |
| BUILDING | 다중이용시설, 교육의료 | 사무소, 병원, 학교 |
| CONSTRUCTION | 건설현장 | 아파트, 도로, 산업시설 |
| SPECIAL | 특수다중이용, 교통시설 | 지하철, 복합용도 |

---

## 3. 플랜 4단계 정의

| 플랜 | 대상 | 구독료 | 핵심 기능 |
|------|------|----------|----------|
| STARTER(1)    | 5~30인 겸직타겟 | 49,000원/월 | 할당·분산, 누락알림, 이력 6개월 |
| BUSINESS(2)   | 30~100인 | 99,000원/월 | STARTER + 공정/설비, 이력무제한, API |
| ENTERPRISE(3) | 100인+ | 협의 | BUSINESS + 자동화, 종합리포트 |
| CUSTOM(4)     | 대형고객 | 협의 | 맞춤형 설계 |

---

## 4. Feature Flag 매핑 표

| feature_code | 설명 | sector | min_plan |
|-------------|------|--------|----------|
| DASHBOARD | 대시보드 | ALL | STARTER |
| LEGAL_DIAGNOSIS_BASIC | 기초진단(무료) | ALL | STARTER |
| LEGAL_DIAGNOSIS_PROCESS | 공정진단 | ALL | BUSINESS |
| LEGAL_DIAGNOSIS_FULL | 종합리포트 | ALL | ENTERPRISE |
| WORK_ASSIGN | 업무할당·분산 | ALL | STARTER |
| EDUCATION_BASIC | 교육관리 | ALL | STARTER |
| REPORT_FORM | 신고서식 | ALL | BUSINESS |
| REPORT_AUTO | 전자제출 | ALL | ENTERPRISE |
| API_CONNECT | API연동 | ALL | BUSINESS |
| HISTORY_6M | 이력 6개월 | ALL | STARTER |
| HISTORY_UNLIMITED | 이력 무제한 | ALL | BUSINESS |
| FACILITY_BASIC | 시설관리 | INDUSTRY | STARTER |
| FACILITY_PROCESS | 공정관리 | INDUSTRY | BUSINESS |
| FACILITY_EQUIPMENT | 설비관리 | INDUSTRY | BUSINESS |
| WORK_TBM | TBM | INDUSTRY | BUSINESS |
| WORK_RISK | 위험성평가 | INDUSTRY | BUSINESS |
| WORKER_BASIC | 작업자관리 | INDUSTRY | STARTER |
| BUILDING_INSPECTION | 점검관리 | BUILDING | STARTER |
| BUILDING_EQUIPMENT | 설비관리 | BUILDING | BUSINESS |
| BUILDING_FIRE | 소방관리 | BUILDING | BUSINESS |
| CONSTRUCTION_SITE | 건설현장관리 | CONSTRUCTION | STARTER |
| CONSTRUCTION_PROCESS | 공정관리 | CONSTRUCTION | STARTER |
| CONSTRUCTION_PTW | 위험작업허가 | CONSTRUCTION | BUSINESS |
| CONSTRUCTION_ENTRY | 작업자입입관리 | CONSTRUCTION | BUSINESS |
| CONSTRUCTION_SAFETY | 안전점검 | CONSTRUCTION | STARTER |

---

## 5. 데이터 흐름

```
로그인
  ↓
GET /auth/me → { plan_code, factory_id }
  ↓
GET /factories/{id} → { sector }
  ↓
GET /feature-flags?sector=CONSTRUCTION&plan=BUSINESS
  → { open: [...], locked: [...], hidden: [...] }
  ↓
TAIFeatureFlags.apply()
  → data-feature 속성 기준으로 DOM 제어
  → hidden → d-none
  → locked → 잠금 오버레이 + 업그레이드 버튼
  → open   → 정상 표시
```

---

## 6. 구현 로드맵

| 단계 | 작업 | 우선순위 |
|------|------|----------|
| 1단계 | DB: factories.sector + factory_features 테이블 + plan_code | 현재 |
| 2단계 | API: GET /feature-flags 기본 리터너 | 현재 |
| 3단계 | 프론트: feature-flags.js 공통 모듈 + 메뉴 data-feature 적용 | 다음 |
| 4단계 | 섹터별 메뉴/화면 실제 분기 적용 | 추후 |
| 5단계 | 잠금 UI + 업그레이드 안내 (LTV 평가 후) | 추후 |

---

## 7. 참고: 필요 DB 변경

```sql
-- factories.sector 컨럼 (B-FEAT-001에서 처리)
-- factories.plan_code 컨럼 (B-FEAT-001에서 처리)
-- factory_features 테이블 (신규, B-FEAT-001에서 처리)
-- system_codes: plan_code 4개, sector 4개 (B-FEAT-001에서 처리)
```
